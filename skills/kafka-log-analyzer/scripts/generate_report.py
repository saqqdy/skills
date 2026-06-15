#!/usr/bin/env python3
"""生成 Kafka 日志分析报告。

用法:
    python generate_report.py <stats_json> [--format markdown]
"""

import argparse
import json
import sys
from pathlib import Path

def generate_markdown_report(stats: dict) -> str:
    lines = ['# Kafka 日志分析报告', '', '## 概览', '', f'- 总事件数: {stats.get("total_lines", 0)}', f'- 解析事件数: {stats.get("parsed_events", 0)}', '']
    if stats.get('by_type'):
        lines.extend(['## 事件类型分布', '', '| 类型 | 数量 |', '|------|------|'])
        for t, c in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
            lines.append(f'| {t} | {c} |')
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='生成报告')
    parser.add_argument('stats', type=Path, help='统计 JSON 文件')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown')
    parser.add_argument('--output', '-o', type=Path)
    args = parser.parse_args()
    if not args.stats.exists():
        sys.exit(1)
    stats = json.loads(args.stats.read_text())
    output = generate_markdown_report(stats)
    if args.output:
        args.output.write_text(output)
    else:
        print(output)

if __name__ == '__main__':
    main()