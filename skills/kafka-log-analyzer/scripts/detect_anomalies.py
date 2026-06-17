#!/usr/bin/env python3
"""Kafka 日志异常检测。

检测错误率突增、消费积压、频繁 Rebalance、Leader 频繁切换、
副本同步延迟、序列化异常、错误率趋势上升等。

用法:
    python detect_anomalies.py <events_json_file>
    python detect_anomalies.py <events_json_file> --lag-threshold 10000
    python detect_anomalies.py <events_json_file> --rebalance-threshold 3
"""

import argparse
import json
import sys
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Anomaly:
    """异常条目。"""
    anomaly_type: str
    severity: str  # critical, high, medium, low
    description: str
    evidence: list = field(default_factory=list)
    suggestion: str = ""
    count: int = 1


def detect_error_rate_spike(events: list, threshold: float = 0.05) -> list:
    """检测错误率突增。"""
    anomalies = []
    if not events:
        return anomalies

    error_count = sum(1 for e in events if e.get("level") == "ERROR")
    error_rate = error_count / len(events)

    if error_rate > 0.10:
        severity = "critical"
    elif error_rate > 0.05:
        severity = "high"
    elif error_rate > 0.02:
        severity = "medium"
    else:
        return anomalies

    error_types = Counter()
    for e in events:
        if e.get("level") == "ERROR":
            error_types[e.get("event_type", "unknown")] += 1

    top_errors = error_types.most_common(3)
    evidence = [f"{t}: {c}次" for t, c in top_errors]

    anomalies.append(Anomaly(
        anomaly_type="error_rate_spike",
        severity=severity,
        description=f"错误率 {error_rate:.1%}（阈值 {threshold:.0%}），共 {error_count} 条 ERROR 日志",
        evidence=evidence,
        suggestion="检查网络连通性、Broker 健康状态和最近部署变更",
        count=error_count,
    ))
    return anomalies


def detect_consumer_lag(events: list, threshold: int = 10000) -> list:
    """检测消费积压。"""
    anomalies = []
    lag_events = [e for e in events if e.get("event_type") == "consumer_lag"]

    for e in lag_events:
        raw = e.get("raw_message", "")
        lag_count = None

        m = re.search(r'(\d+)\s*messages', raw)
        if m:
            lag_count = int(m.group(1))

        actual_lag = lag_count or e.get("offset_lag", 0)

        if actual_lag > threshold * 10:
            severity = "critical"
        elif actual_lag > threshold:
            severity = "high"
        else:
            continue

        anomalies.append(Anomaly(
            anomaly_type="consumer_lag",
            severity=severity,
            description=f"消费积压 {actual_lag} 条（阈值 {threshold}）",
            evidence=[raw[:200] if raw else f"topic={e.get('topic', '?')}"],
            suggestion="增加 Consumer 实例数、优化消费逻辑或增大 max.poll.records",
            count=1,
        ))
    return anomalies


def detect_rebalance_storm(events: list, threshold: int = 3) -> list:
    """检测频繁 Rebalance（Rebalance 风暴）。"""
    anomalies = []
    rebalance_events = [e for e in events if e.get("event_type") == "rebalance"]

    if len(rebalance_events) < threshold:
        return anomalies

    severity = "critical" if len(rebalance_events) > 10 else "high"
    anomalies.append(Anomaly(
        anomaly_type="rebalance_storm",
        severity=severity,
        description=f"检测到 {len(rebalance_events)} 次 Rebalance（阈值 {threshold}），可能存在 Rebalance 风暴",
        evidence=[e.get("raw_message", "")[:100] for e in rebalance_events[:5]],
        suggestion="增大 session.timeout.ms（建议 30000+）、使用静态成员 group.instance.id、检查消费者处理逻辑是否过慢",
        count=len(rebalance_events),
    ))
    return anomalies


def detect_leader_instability(events: list, threshold: int = 3) -> list:
    """检测 Leader 频繁切换。"""
    anomalies = []
    leader_events = [e for e in events if e.get("event_type") == "leader_change"]

    if len(leader_events) < threshold:
        return anomalies

    severity = "high" if len(leader_events) > 5 else "medium"
    topics = set(e.get("topic", "?") for e in leader_events)

    anomalies.append(Anomaly(
        anomaly_type="leader_instability",
        severity=severity,
        description=f"检测到 {len(leader_events)} 次 Leader 切换（阈值 {threshold}），涉及 topic: {', '.join(topics)}",
        evidence=[e.get("raw_message", "")[:100] for e in leader_events[:5]],
        suggestion="检查 Broker 健康状态、磁盘 I/O 和网络延迟；考虑启用 auto.leader.rebalance.enable",
        count=len(leader_events),
    ))
    return anomalies


def detect_replica_lag(events: list) -> list:
    """检测副本同步延迟。"""
    anomalies = []
    replica_events = [e for e in events
                      if e.get("event_type") == "unknown"
                      and "replica" in e.get("raw_message", "").lower()
                      and e.get("level") in ("WARN", "ERROR")]

    if not replica_events:
        return anomalies

    severity = "high" if len(replica_events) > 5 else "medium"
    anomalies.append(Anomaly(
        anomaly_type="replica_sync_lag",
        severity=severity,
        description=f"检测到 {len(replica_events)} 条副本相关问题日志",
        evidence=[e.get("raw_message", "")[:100] for e in replica_events[:5]],
        suggestion="检查 ISR 状态；考虑增大 num.replica.fetchers 或检查 Broker 间网络",
        count=len(replica_events),
    ))
    return anomalies


def detect_serialization_errors(events: list, threshold: int = 3) -> list:
    """检测序列化/反序列化异常聚类。"""
    anomalies = []
    ser_events = [e for e in events
                  if "serialization" in e.get("raw_message", "").lower()
                  or "serializ" in str(e.get("error", "")).lower()]

    if len(ser_events) < threshold:
        return anomalies

    error_types = Counter()
    for e in ser_events:
        err = e.get("error", "")
        if err:
            error_types[err] += 1

    severity = "high" if len(ser_events) > 10 else "medium"
    evidence = [f"{t}: {c}次" for t, c in error_types.most_common(3)]

    anomalies.append(Anomaly(
        anomaly_type="serialization_errors",
        severity=severity,
        description=f"检测到 {len(ser_events)} 次序列化异常（阈值 {threshold}），可能存在 Schema 不兼容",
        evidence=evidence or [e.get("raw_message", "")[:100] for e in ser_events[:3]],
        suggestion="检查 Schema Registry 兼容性设置、确认 Producer/Consumer Serializer 配置一致",
        count=len(ser_events),
    ))
    return anomalies


def detect_error_rate_trend(events: list) -> list:
    """检测错误率趋势上升。"""
    anomalies = []
    if len(events) < 20:
        return anomalies

    mid = len(events) // 2
    first_half_errors = sum(1 for e in events[:mid] if e.get("level") == "ERROR")
    second_half_errors = sum(1 for e in events[mid:] if e.get("level") == "ERROR")

    first_half_total = max(mid, 1)
    second_half_total = max(len(events) - mid, 1)

    first_rate = first_half_errors / first_half_total
    second_rate = second_half_errors / second_half_total

    if second_rate > first_rate * 2 and second_rate > 0.05:
        anomalies.append(Anomaly(
            anomaly_type="error_rate_trend_up",
            severity="high",
            description=f"错误率呈上升趋势：前半段 {first_rate:.1%} → 后半段 {second_rate:.1%}",
            evidence=[f"前半段: {first_half_errors}/{first_half_total}",
                      f"后半段: {second_half_errors}/{second_half_total}"],
            suggestion="检查是否有部署变更、流量突增或基础设施退化",
            count=second_half_errors,
        ))
    return anomalies


def run_all_detectors(events: list,
                      lag_threshold: int = 10000,
                      rebalance_threshold: int = 3) -> list:
    """运行所有检测器。"""
    all_anomalies = []
    detectors = [
        lambda: detect_error_rate_spike(events),
        lambda: detect_consumer_lag(events, lag_threshold),
        lambda: detect_rebalance_storm(events, rebalance_threshold),
        lambda: detect_leader_instability(events),
        lambda: detect_replica_lag(events),
        lambda: detect_serialization_errors(events),
        lambda: detect_error_rate_trend(events),
    ]

    for detector in detectors:
        try:
            all_anomalies.extend(detector())
        except Exception as e:
            print(f"检测器异常: {e}", file=sys.stderr)

    return all_anomalies


def main():
    parser = argparse.ArgumentParser(description="Kafka 日志异常检测")
    parser.add_argument("input", type=Path, help="事件 JSON 文件")
    parser.add_argument("--lag-threshold", type=int, default=10000, help="消费积压阈值")
    parser.add_argument("--rebalance-threshold", type=int, default=3, help="Rebalance 次数阈值")
    parser.add_argument("--output", "-o", type=Path, help="输出文件")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"错误: 文件不存在 {args.input}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.input.read_text(encoding="utf-8"))
    events = data.get("events", data) if isinstance(data, dict) else data
    if not isinstance(events, list):
        events = [events]

    anomalies = run_all_detectors(events, args.lag_threshold, args.rebalance_threshold)

    result = {
        "total_anomalies": len(anomalies),
        "critical": sum(1 for a in anomalies if a.severity == "critical"),
        "high": sum(1 for a in anomalies if a.severity == "high"),
        "medium": sum(1 for a in anomalies if a.severity == "medium"),
        "low": sum(1 for a in anomalies if a.severity == "low"),
        "anomalies": [vars(a) for a in anomalies],
    }

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
