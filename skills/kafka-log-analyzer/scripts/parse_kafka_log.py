#!/usr/bin/env python3
"""解析 Kafka 日志并提取结构化事件。

支持纯文本和 JSON 两种格式，自动检测。
可选时间线模式和实时监控模式。

用法:
    python parse_kafka_log.py <log_file>
    python parse_kafka_log.py <log_file> --format json
    python parse_kafka_log.py <log_file> --timeline          # 按分钟统计
    python parse_kafka_log.py <log_file> --timeline --timeline-window 1h  # 按小时
    python parse_kafka_log.py <log_file> --watch              # 实时监控
    python parse_kafka_log.py <log_dir>                       # 解析目录下所有 .log 文件
    python parse_kafka_log.py <log_file> -o output.json
"""

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


# 纯文本日志正则
TEXT_LOG_PATTERN = re.compile(
    r'\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] '
    r'(?P<level>\w+)\s+\[(?P<thread>[^\]]+)\] (?P<message>.+)'
)

# Kafka 事件模式
EVENT_PATTERNS = {
    'send_success': re.compile(r'Successfully sent record to topic (\w+) partition (\d+) offset (\d+)'),
    'send_failure': re.compile(r'Failed to send record.*topic (\w+).*error: (.+)'),
    'consumer_lag': re.compile(r'lag exceeded threshold \((\d+) messages\)'),
    'rebalance': re.compile(r'Consumer group (\w+).*rebalance|Revoking previously assigned|Re-)joining group'),
    'commit_failure': re.compile(r'CommitFailedException|Commit cannot be completed'),
    'buffer_exhausted': re.compile(r'BufferExhaustedException|Buffer is full'),
    'leader_change': re.compile(r'leader changed from \d+ to \d+|NotLeaderForPartition'),
    'offset_out_of_range': re.compile(r'OffsetOutOfRange|No offset for topic-partition'),
    'serialization_error': re.compile(r'SerializationException|Error serializ'),
    'network_error': re.compile(r'NetworkException|Connection.*refused|SSL handshake failed'),
    'auth_error': re.compile(r'TopicAuthorizationException|AuthenticationException|Authorization failed'),
}

# 时间窗口映射
WINDOW_MAP = {
    '1m': 60,
    '5m': 300,
    '15m': 900,
    '1h': 3600,
    '6h': 21600,
    '1d': 86400,
}


@dataclass
class KafkaLogEvent:
    """Kafka 日志事件。"""
    timestamp: str
    level: str
    thread: str
    event_type: str
    topic: Optional[str] = None
    partition: Optional[int] = None
    offset: Optional[int] = None
    error: Optional[str] = None
    offset_lag: Optional[int] = None
    raw_message: str = ""


def detect_format(line: str) -> str:
    """自动检测日志行格式。"""
    line = line.strip()
    if line.startswith('{') or line.startswith('['):
        return 'json'
    if TEXT_LOG_PATTERN.match(line):
        return 'text'
    return 'unknown'


def parse_text_line(line: str) -> Optional[KafkaLogEvent]:
    """解析纯文本日志行。"""
    match = TEXT_LOG_PATTERN.match(line.strip())
    if not match:
        return None
    timestamp, level, thread, message = match.groups()
    event_type = 'unknown'
    topic, partition, offset, error, offset_lag = None, None, None, None, None

    for pattern_name, pattern in EVENT_PATTERNS.items():
        pm = pattern.search(message)
        if pm:
            event_type = pattern_name
            if pattern_name == 'send_success':
                topic, partition, offset = pm.group(1), int(pm.group(2)), int(pm.group(3))
            elif pattern_name == 'send_failure':
                topic, error = pm.group(1), pm.group(2)
            elif pattern_name == 'consumer_lag':
                offset_lag = int(pm.group(1))
            elif pattern_name == 'rebalance':
                topic = pm.group(1) if pm.lastindex and pm.lastindex >= 1 else None
            break

    return KafkaLogEvent(timestamp, level, thread, event_type, topic, partition,
                         offset, error, offset_lag, message)


def parse_json_line(line: str) -> Optional[KafkaLogEvent]:
    """解析 JSON 日志行。"""
    try:
        obj = json.loads(line.strip())
    except json.JSONDecodeError:
        return None

    timestamp = obj.get("timestamp", obj.get("@timestamp", obj.get("time", "")))
    level = obj.get("level", obj.get("severity", "INFO")).upper()
    thread = obj.get("thread", obj.get("threadName", ""))
    message = obj.get("message", obj.get("msg", obj.get("formattedMessage", "")))
    topic = obj.get("topic", obj.get("meta", {}).get("topic"))
    error = obj.get("error", obj.get("exception", obj.get("stackTrace")))

    # 事件类型匹配
    event_type = 'unknown'
    for pattern_name, pattern in EVENT_PATTERNS.items():
        if pattern.search(str(message)):
            event_type = pattern_name
            break

    return KafkaLogEvent(
        timestamp=str(timestamp),
        level=level,
        thread=str(thread),
        event_type=event_type,
        topic=topic,
        error=str(error) if error else None,
        raw_message=message,
    )


def parse_log_line(line: str, fmt: str = "auto") -> Optional[KafkaLogEvent]:
    """解析单行日志，自动检测格式。"""
    line = line.strip()
    if not line:
        return None

    if fmt == "auto":
        fmt = detect_format(line)

    if fmt == 'json':
        return parse_json_line(line)
    elif fmt == 'text':
        return parse_text_line(line)
    return None


def compute_timeline(events: list, window_seconds: int = 60) -> dict:
    """计算时间线分布。"""
    if not events:
        return {}

    timeline = {}

    for event in events:
        ts = event.timestamp
        if not ts:
            continue

        try:
            from datetime import datetime
            if 'T' in ts:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            continue

        epoch = dt.timestamp()
        window_start = int(epoch // window_seconds) * window_seconds
        window_dt = datetime.fromtimestamp(window_start)
        window_key = window_dt.strftime("%Y-%m-%d %H:%M")

        if window_key not in timeline:
            timeline[window_key] = {}

        level = event.level
        timeline[window_key][level] = timeline[window_key].get(level, 0) + 1

        etype = event.event_type
        timeline[window_key][etype] = timeline[window_key].get(etype, 0) + 1

    return timeline


def analyze_file(file_path: Path, fmt: str = "auto",
                 timeline: bool = False, window_seconds: int = 60) -> dict:
    """分析单个日志文件。"""
    events = []
    stats = {
        'total_lines': 0,
        'parsed_events': 0,
        'by_type': {},
        'by_level': {},
        'by_topic': {},
        'errors': [],
    }

    # 检测文件格式
    actual_fmt = fmt
    if fmt == 'auto':
        with open(file_path) as f:
            first_line = f.readline()
            actual_fmt = detect_format(first_line)

    with open(file_path) as f:
        for line in f:
            stats['total_lines'] += 1
            event = parse_log_line(line, actual_fmt)
            if event:
                events.append(event)
                stats['parsed_events'] += 1
                stats['by_type'][event.event_type] = stats['by_type'].get(event.event_type, 0) + 1
                stats['by_level'][event.level] = stats['by_level'].get(event.level, 0) + 1
                if event.topic:
                    stats['by_topic'][event.topic] = stats['by_topic'].get(event.topic, 0) + 1
                if event.error:
                    stats['errors'].append(asdict(event))

    if timeline:
        stats['timeline'] = compute_timeline(events, window_seconds)

    return {'events': [asdict(e) for e in events], 'stats': stats, 'format': actual_fmt}


def watch_file(file_path: Path, fmt: str = "auto", interval: float = 1.0) -> None:
    """实时监控日志文件变化。"""
    actual_fmt = fmt
    print(f"监控 {file_path} (格式: {actual_fmt})，Ctrl+C 退出...")
    print("-" * 60)

    with open(file_path) as f:
        # 跳到文件末尾
        f.seek(0, 2)

        try:
            while True:
                line = f.readline()
                if line:
                    event = parse_log_line(line, actual_fmt)
                    if event:
                        level_icon = {"ERROR": "🔴", "WARN": "🟡", "INFO": "🟢"}.get(event.level, "⚪")
                        topic_info = f" [{event.topic}]" if event.topic else ""
                        print(f"{level_icon} {event.timestamp} {event.level}{topic_info} {event.event_type}: {event.raw_message[:80]}")
                else:
                    time.sleep(interval)
        except KeyboardInterrupt:
            print("\n监控已停止")


def main():
    parser = argparse.ArgumentParser(description="解析 Kafka 日志")
    parser.add_argument("input", type=Path, help="日志文件或目录路径")
    parser.add_argument("--format", choices=["auto", "text", "json"], default="auto",
                        help="日志格式（默认 auto 自动检测）")
    parser.add_argument("--timeline", action="store_true", help="生成时间线分布统计")
    parser.add_argument("--timeline-window", type=str, default="1m",
                        help="时间窗口 (1m/5m/15m/1h/6h/1d，默认 1m)")
    parser.add_argument("--watch", action="store_true", help="实时监控模式")
    parser.add_argument("--watch-interval", type=float, default=1.0, help="监控轮询间隔秒数")
    parser.add_argument("--output", "-o", type=Path, help="输出文件路径")
    args = parser.parse_args()

    if not args.input.exists():
        print(f'错误: {args.input} 不存在', file=sys.stderr)
        sys.exit(1)

    window_seconds = WINDOW_MAP.get(args.timeline_window, 60)

    if args.watch:
        if args.input.is_dir():
            print("错误: --watch 模式不支持目录", file=sys.stderr)
            sys.exit(1)
        watch_file(args.input, args.format, args.watch_interval)
        return

    if args.input.is_dir():
        all_stats = {'total_lines': 0, 'parsed_events': 0, 'by_type': {}, 'by_level': {},
                     'by_topic': {}, 'errors': [], 'files': []}
        all_events = []

        for log_file in sorted(args.input.glob("*.log")):
            result = analyze_file(log_file, args.format, args.timeline, window_seconds)
            stats = result['stats']
            all_stats['total_lines'] += stats['total_lines']
            all_stats['parsed_events'] += stats['parsed_events']
            all_stats['files'].append({'name': log_file.name, 'format': result['format'],
                                       'lines': stats['total_lines'], 'events': stats['parsed_events']})

            for k, v in stats['by_type'].items():
                all_stats['by_type'][k] = all_stats['by_type'].get(k, 0) + v
            for k, v in stats['by_level'].items():
                all_stats['by_level'][k] = all_stats['by_level'].get(k, 0) + v
            for k, v in stats['by_topic'].items():
                all_stats['by_topic'][k] = all_stats['by_topic'].get(k, 0) + v

            all_events.extend(result['events'])

        if args.timeline:
            timeline_events = [KafkaLogEvent(**{k: v for k, v in e.items() if k in KafkaLogEvent.__dataclass_fields__})
                              for e in all_events]
            all_stats['timeline'] = compute_timeline(timeline_events, window_seconds)

        result = {'events': all_events, 'stats': all_stats}
    else:
        result = analyze_file(args.input, args.format, args.timeline, window_seconds)

    output = json.dumps(result['stats'], indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f'Stats written to {args.output}')
    else:
        print(output)


if __name__ == "__main__":
    main()
