#!/usr/bin/env python3
"""解析 Kafka 日志并提取结构化事件。

用法:
    python parse_kafka_log.py <log_file>
    python parse_kafka_log.py <log_dir>
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

# 日志正则模式
TEXT_LOG_PATTERN = re.compile(
    r'\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] '
    r'(?P<level>\w+)\s+\[(?P<thread>[^\]]+)\] (?P<message>.+)'
)

# Kafka 事件模式
EVENT_PATTERNS = {
    'send_success': re.compile(r'Successfully sent record to topic (\w+) partition (\d+) offset (\d+)'),
    'send_failure': re.compile(r'Failed to send record.*topic (\w+).*error: (.+)'),
    'consumer_lag': re.compile(r'lag exceeded threshold \((\d+) messages\)'),
    'rebalance': re.compile(r'Consumer group (\w+).*rebalance'),
}

@dataclass
class KafkaLogEvent:
    timestamp: str
    level: str
    thread: str
    event_type: str
    topic: Optional[str] = None
    partition: Optional[int] = None
    offset: Optional[int] = None
    error: Optional[str] = None
    raw_message: str = ""

def parse_log_line(line: str) -> Optional[KafkaLogEvent]:
    match = TEXT_LOG_PATTERN.match(line)
    if not match:
        return None
    timestamp, level, thread, message = match.groups()
    event_type = 'unknown'
    topic, partition, offset, error = None, None, None, None
    for pattern_name, pattern in EVENT_PATTERNS.items():
        pm = pattern.search(message)
        if pm:
            event_type = pattern_name
            if pattern_name == 'send_success':
                topic, partition, offset = pm.group(1), int(pm.group(2)), int(pm.group(3))
            elif pattern_name == 'send_failure':
                topic, error = pm.group(1), pm.group(2)
            break
    return KafkaLogEvent(timestamp, level, thread, event_type, topic, partition, offset, error, message)

def analyze_file(file_path: Path) -> dict:
    events = []
    stats = {'total_lines': 0, 'parsed_events': 0, 'by_type': {}, 'by_level': {}, 'errors': []}
    with open(file_path) as f:
        for line in f:
            stats['total_lines'] += 1
            event = parse_log_line(line.strip())
            if event:
                events.append(asdict(event))
                stats['parsed_events'] += 1
                stats['by_type'][event.event_type] = stats['by_type'].get(event.event_type, 0) + 1
                stats['by_level'][event.level] = stats['by_level'].get(event.level, 0) + 1
                if event.error:
                    stats['errors'].append(asdict(event))
    return {'events': events, 'stats': stats}

def main():
    parser = argparse.ArgumentParser(description='解析 Kafka 日志')
    parser.add_argument('input', type=Path, help='日志文件路径')
    parser.add_argument('--output', '-o', type=Path, help='输出文件路径')
    args = parser.parse_args()
    if not args.input.exists():
        print(f'Error: {args.input} not found', file=sys.stderr)
        sys.exit(1)
    result = analyze_file(args.input)
    output = json.dumps(result['stats'], indent=2)
    if args.output:
        args.output.write_text(output)
        print(f'Stats written to {args.output}')
    else:
        print(output)

if __name__ == '__main__':
    main()