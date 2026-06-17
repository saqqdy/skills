#!/usr/bin/env python3
"""生成 Kafka 日志分析报告。

整合统计数据和异常检测结果，生成包含优先级排序、诊断建议和修复方案的完整报告。

用法:
    python generate_report.py --stats stats.json --anomalies anomalies.json
    python generate_report.py --input-dir ./analysis_output
    python generate_report.py --input-dir ./analysis_output --format json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


def load_json(path: Path) -> dict:
    """加载 JSON 文件。"""
    if not path or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class AnomalyEntry:
    """异常条目。"""
    anomaly_type: str
    severity: str
    description: str
    count: int = 1
    suggestion: str = ""
    evidence: list = field(default_factory=list)


def classify_event_priority(event_type: str, level: str, count: int = 1) -> str:
    """对单个事件类型分级。"""
    # P0: 影响数据完整性的严重错误
    p0_types = {"producer_fenced", "corrupt_message", "message_loss"}
    if event_type in p0_types:
        return "P0"
    # P0: 高频 ERROR
    if level == "ERROR" and count >= 100:
        return "P0"
    # P1: 持续 ERROR
    if level == "ERROR" and count >= 10:
        return "P1"
    # P1: 关键 WARN
    p1_types = {"consumer_lag", "commit_failure"}
    if event_type in p1_types:
        return "P1"
    # P2: 一般 WARN
    if level == "WARN" and count >= 5:
        return "P2"
    # P2: 偶发 ERROR
    if level == "ERROR":
        return "P2"
    # P3: 信息性
    return "P3"


def build_anomaly_entries(anomalies_data: dict) -> list:
    """从异常检测结果构建异常条目列表。"""
    entries = []
    raw_anomalies = anomalies_data.get("anomalies", [])

    for a in raw_anomalies:
        entry = AnomalyEntry(
            anomaly_type=a.get("anomaly_type", "unknown"),
            severity=a.get("severity", "medium"),
            description=a.get("description", ""),
            count=a.get("count", 1),
            suggestion=a.get("suggestion", ""),
            evidence=a.get("evidence", []),
        )
        entries.append(entry)

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    entries.sort(key=lambda e: severity_order.get(e.severity, 9))
    return entries


def build_event_priorities(stats: dict) -> dict:
    """为每种事件类型分配优先级。"""
    by_type = stats.get("by_type", {})
    priorities = {}
    for event_type, count in by_type.items():
        level = "WARN"
        if event_type in ("send_failure", "commit_failure", "buffer_exhausted",
                          "serialization_error", "network_error", "auth_error"):
            level = "ERROR"
        priorities[event_type] = classify_event_priority(event_type, level, count)
    return priorities


def identify_common_patterns(stats: dict, anomalies: list) -> list:
    """识别共性日志模式。"""
    patterns = []
    by_type = stats.get("by_type", {})
    type_groups = {}
    for event_type, count in by_type.items():
        category = event_type.split("_")[0] if "_" in event_type else event_type
        type_groups[category] = type_groups.get(category, 0) + count

    for category, count in sorted(type_groups.items(), key=lambda x: -x[1]):
        if count > 1 and category in ("send", "consumer", "rebalance", "leader", "buffer"):
            patterns.append(f"{category} 类事件合计 {count} 次，可能存在系统性{category}问题")

    anomaly_types = [a.anomaly_type for a in anomalies]
    if anomaly_types.count("rebalance_storm") >= 1:
        patterns.append("检测到 Rebalance 风暴，建议检查 Consumer 心跳和处理逻辑")
    if anomaly_types.count("error_rate_spike") >= 1:
        patterns.append("错误率突增，建议检查最近是否有部署变更或网络波动")
    return patterns


def identify_timeline_patterns(stats: dict) -> list:
    """基于时间线数据识别模式。"""
    patterns = []
    timeline = stats.get("timeline", {})
    if not timeline:
        return patterns

    error_peaks = []
    for ts, events in sorted(timeline.items()):
        error_count = events.get("ERROR", 0)
        total = sum(v for k, v in events.items() if k in ("INFO", "WARN", "ERROR"))
        if total > 0 and error_count / total > 0.3:
            error_peaks.append(ts)

    if len(error_peaks) >= 3:
        patterns.append(f"错误集中在 {error_peaks[0]} ~ {error_peaks[-1]} 时间段，建议检查该时段的部署或基础设施变更")
    return patterns


def generate_system_suggestions(stats: dict, anomalies: list, patterns: list) -> list:
    """生成系统级建议。"""
    suggestions = []
    by_type = stats.get("by_type", {})
    anomaly_types = {a.anomaly_type for a in anomalies}

    if "send_failure" in by_type and by_type["send_failure"] > 50:
        suggestions.append("Producer 发送失败频繁，建议检查网络连通性并调整 request.timeout.ms 和 retries 配置")
    if "consumer_lag" in by_type:
        suggestions.append("存在消费积压，建议增加 Consumer 实例数或优化消费逻辑")
    if "rebalance_storm" in anomaly_types:
        suggestions.append("频繁 Rebalance，建议增大 session.timeout.ms 或使用静态成员 group.instance.id")
    if "buffer_exhausted" in by_type:
        suggestions.append("缓冲区频繁耗尽，建议增大 buffer.memory 或降低 linger.ms")
    if "leader_change" in by_type and by_type.get("leader_change", 0) > 5:
        suggestions.append("Leader 频繁切换，建议检查 Broker 健康状态和磁盘 I/O")
    if not patterns and not suggestions:
        suggestions.append("当前日志模式下未发现系统性问题，继续保持监控即可")
    return suggestions


def render_markdown_report(stats: dict, anomalies_data: dict, period: str = "未指定") -> str:
    """渲染完整的 Markdown 分析报告。"""
    anomaly_entries = build_anomaly_entries(anomalies_data)
    priorities = build_event_priorities(stats)
    common_patterns = identify_common_patterns(stats, anomaly_entries)
    timeline_patterns = identify_timeline_patterns(stats)
    all_patterns = common_patterns + timeline_patterns
    system_suggestions = generate_system_suggestions(stats, anomaly_entries, all_patterns)

    lines = []
    lines.append("# Kafka 日志分析报告")
    lines.append("")
    lines.append(f"- **生成时间**: {datetime.now().isoformat()}")
    lines.append(f"- **分析周期**: {period}")
    lines.append(f"- **总行数**: {stats.get('total_lines', 0)}")
    lines.append(f"- **解析事件数**: {stats.get('parsed_events', 0)}")
    lines.append(f"- **检测到异常**: {len(anomaly_entries)} 项")
    lines.append("")

    # 优先级分布
    priority_counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for p in priorities.values():
        priority_counts[p] = priority_counts.get(p, 0) + 1

    lines.append("## 优先级分布")
    lines.append("")
    lines.append("| 优先级 | 含义 | 事件类型数 |")
    lines.append("|--------|------|-----------|")
    lines.append(f"| 🔴 P0 | 数据完整性/生产故障 | {priority_counts.get('P0', 0)} |")
    lines.append(f"| 🟠 P1 | 持续错误/关键告警 | {priority_counts.get('P1', 0)} |")
    lines.append(f"| 🟡 P2 | 一般告警 | {priority_counts.get('P2', 0)} |")
    lines.append(f"| ⚪ P3 | 信息性 | {priority_counts.get('P3', 0)} |")
    lines.append("")

    # 事件类型分布
    by_type = stats.get("by_type", {})
    if by_type:
        lines.append("## 事件类型分布")
        lines.append("")
        lines.append("| 类型 | 数量 | 优先级 |")
        lines.append("|------|------|--------|")
        for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
            p = priorities.get(t, "P3")
            p_icon = {"P0": "🔴", "P1": "🟠", "P2": "🟡", "P3": "⚪"}.get(p, "⚪")
            lines.append(f"| {t} | {c} | {p_icon} {p} |")
        lines.append("")

    # 日志级别分布
    by_level = stats.get("by_level", {})
    if by_level:
        lines.append("## 日志级别分布")
        lines.append("")
        lines.append("| 级别 | 数量 |")
        lines.append("|------|------|")
        for lvl, cnt in sorted(by_level.items(), key=lambda x: -x[1]):
            lines.append(f"| {lvl} | {cnt} |")
        lines.append("")

    # TOPIC 分布
    by_topic = stats.get("by_topic", {})
    if by_topic:
        lines.append("## Topic 分布")
        lines.append("")
        lines.append("| Topic | 事件数 |")
        lines.append("|-------|--------|")
        for topic, cnt in sorted(by_topic.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"| {topic} | {cnt} |")
        lines.append("")

    # 异常详情
    if anomaly_entries:
        lines.append("## 异常详情")
        lines.append("")
        for a in anomaly_entries:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}.get(a.severity, "⚪")
            lines.append(f"### {severity_icon} {a.severity.upper()} | {a.anomaly_type}")
            lines.append("")
            lines.append(f"- **描述**: {a.description}")
            lines.append(f"- **出现次数**: {a.count}")
            if a.suggestion:
                lines.append(f"- **建议**: {a.suggestion}")
            if a.evidence:
                lines.append(f"- **证据**:")
                for ev in a.evidence[:3]:
                    lines.append(f"  - `{ev}`")
            lines.append("")

    # 时间线
    timeline = stats.get("timeline", {})
    if timeline:
        lines.append("## 时间线分布")
        lines.append("")
        lines.append("| 时间 | 事件数 | ERROR | WARN | INFO |")
        lines.append("|------|--------|-------|------|------|")
        for ts in sorted(timeline.keys()):
            events = timeline[ts]
            total = sum(events.get(k, 0) for k in ("INFO", "WARN", "ERROR"))
            err = events.get("ERROR", 0)
            wrn = events.get("WARN", 0)
            inf = events.get("INFO", 0)
            lines.append(f"| {ts} | {total} | {err} | {wrn} | {inf} |")
        lines.append("")

    # 共性模式
    if all_patterns:
        lines.append("## 共性模式")
        lines.append("")
        for pattern in all_patterns:
            lines.append(f"- {pattern}")
        lines.append("")

    # 系统建议
    if system_suggestions:
        lines.append("## 系统建议")
        lines.append("")
        for suggestion in system_suggestions:
            lines.append(f"- {suggestion}")
        lines.append("")

    # 代码联动提示
    lines.append("## 源码联动")
    lines.append("")
    lines.append("如果项目源码在当前仓库中，可以让 Claude：")
    lines.append("1. 搜索 Kafka 配置文件（`application.yml` / `application.properties`）")
    lines.append("2. 定位出错的 Producer/Consumer 类")
    lines.append("3. 读取相关代码，给出配置+代码层面的修复方案")
    lines.append("4. 直接生成 diff 补丁")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="生成 Kafka 日志分析报告")
    parser.add_argument("--stats", type=Path, help="统计数据 JSON 文件")
    parser.add_argument("--anomalies", type=Path, help="异常检测结果 JSON 文件")
    parser.add_argument("--input-dir", type=Path, help="输入目录（包含 stats.json、anomalies.json）")
    parser.add_argument("--period", type=str, default="未指定", help="分析周期描述")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="输出格式")
    parser.add_argument("--output", "-o", type=Path, help="输出文件路径")
    args = parser.parse_args()

    if args.input_dir:
        stats_path = args.input_dir / "stats.json"
        anomalies_path = args.input_dir / "anomalies.json"
    else:
        stats_path = args.stats
        anomalies_path = args.anomalies

    if not stats_path:
        print("错误: 需要指定 --stats 或 --input-dir", file=sys.stderr)
        sys.exit(1)

    stats_data = load_json(stats_path)
    anomalies_data = load_json(anomalies_path)

    if args.format == "markdown":
        output = render_markdown_report(stats_data, anomalies_data, args.period)
    else:
        anomaly_entries = build_anomaly_entries(anomalies_data)
        priorities = build_event_priorities(stats_data)
        common_patterns = identify_common_patterns(stats_data, anomaly_entries)
        timeline_patterns = identify_timeline_patterns(stats_data)
        system_suggestions = generate_system_suggestions(
            stats_data, anomaly_entries, common_patterns + timeline_patterns
        )
        report = {
            "generated_at": datetime.now().isoformat(),
            "period": args.period,
            "total_lines": stats_data.get("total_lines", 0),
            "parsed_events": stats_data.get("parsed_events", 0),
            "anomaly_count": len(anomaly_entries),
            "priorities": priorities,
            "by_type": stats_data.get("by_type", {}),
            "by_level": stats_data.get("by_level", {}),
            "by_topic": stats_data.get("by_topic", {}),
            "anomalies": [vars(a) for a in anomaly_entries],
            "timeline": stats_data.get("timeline", {}),
            "common_patterns": common_patterns + timeline_patterns,
            "system_suggestions": system_suggestions,
        }
        output = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"已写入 {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
