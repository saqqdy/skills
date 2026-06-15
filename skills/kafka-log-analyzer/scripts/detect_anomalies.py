#!/usr/bin/env python3
"""Kafka 日志异常检测脚本。

用法:
    python detect_anomalies.py <events_json_file>
"""

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Anomaly:
    anomaly_type: str
    severity: str
    description: str
    evidence: list = field(default_factory=list)
    suggestion: str = ''
    count: int = 1

def detect_error_rate_spike(events: list) -> list:
    anomalies = []
    if len(events) == 0:
        return anomalies
    error_count = sum(1 for e in events if e.get('level') == 'ERROR')
    error_rate = error_count / len(events)
    if error_rate > 0.05:
        anomalies.append(Anomaly('error_rate_spike', 'high', f'错误率 {error_rate:.1%}', [], '检查 ERROR 日志', error_count))
    return anomalies

def detect_consumer_lag(events: list) -> list:
    anomalies = []
    for e in events:
        if e.get('event_type') == 'consumer_lag' and e.get('offset_lag', 0) > 10000:
            anomalies.append(Anomaly('consumer_lag', 'high', f'积压 {e["offset_lag"]} 条', [], '增加 Consumer 实例', 1))
    return anomalies

def run_all_detectors(events: list) -> list:
    all_anomalies = []
    for detector in [detect_error_rate_spike, detect_consumer_lag]:
        all_anomalies.extend(detector(events))
    return all_anomalies

def main():
    parser = argparse.ArgumentParser(description='异常检测')
    parser.add_argument('input', type=Path, help='事件 JSON 文件')
    parser.add_argument('--output', '-o', type=Path, help='输出文件')
    args = parser.parse_args()
    if not args.input.exists():
        sys.exit(1)
    events = json.loads(args.input.read_text())
    if isinstance(events, dict) and 'events' in events:
        events = events['events']
    anomalies = run_all_detectors(events)
    result = {'total_anomalies': len(anomalies), 'anomalies': [a.__dict__ for a in anomalies]}
    output = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(output)
    else:
        print(output)

if __name__ == '__main__':
    main()