#!/usr/bin/env python3
"""生成前端错误分析报告。

读取前面步骤产出的 JSON 文件，生成 Markdown 格式的诊断报告。

用法:
    python generate_report.py --errors errors.json --sessions sessions.json --correlations correlations.json
    python generate_report.py --input-dir ./analysis_output
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class ErrorSummary:
    """错误摘要。"""
    issue_id: str = ""
    title: str = ""
    priority: str = "P3"
    category: str = "unknown"
    count: int = 0
    user_count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    session_id: str = None
    root_cause: str = ""
    fix_suggestion: str = ""


def load_json(path: Path) -> dict:
    """加载 JSON 文件。"""
    if not path or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_error_summaries(errors_data, correlations_data=None, sessions_data=None):
    """构建错误摘要列表。"""
    session_map: dict = {}
    if sessions_data:
        sessions = sessions_data.get("sessions", sessions_data) if isinstance(sessions_data, dict) else sessions_data
        if isinstance(sessions, list):
            for s in sessions:
                sid = s.get("sessionId", s.get("session_id", ""))
                if sid:
                    session_map[sid] = s

    correlation_map: dict = {}
    if correlations_data:
        results = correlations_data.get("results", [correlations_data]) if isinstance(correlations_data, dict) else correlations_data
        if isinstance(results, list):
            for c in results:
                issue_id = str(c.get("issueId", c.get("issue_id", "")))
                session_id = c.get("sessionId", c.get("session_id"))
                if issue_id and session_id:
                    correlation_map[issue_id] = session_id

    issues = errors_data.get("issues", errors_data) if isinstance(errors_data, dict) else errors_data
    if isinstance(issues, dict):
        issues = [issues]
    if not isinstance(issues, list):
        issues = []

    summaries = []
    for issue in issues:
        issue_id = str(issue.get("id", ""))
        session_id = correlation_map.get(issue_id) or issue.get("_session_id")

        summary = ErrorSummary(
            issue_id=issue_id,
            title=issue.get("title", ""),
            priority=issue.get("_priority", "P3"),
            category=issue.get("_category", "unknown"),
            count=int(issue.get("count", "0")),
            user_count=int(issue.get("userCount", 0)),
            first_seen=issue.get("firstSeen", ""),
            last_seen=issue.get("lastSeen", ""),
            session_id=session_id,
        )

        if session_id and session_id in session_map:
            session = session_map[session_id]
            summary.root_cause = f"用户 {session.get('userDisplayName', session_id)} 在 {session.get('url', '')} 触发"

        summaries.append(summary)

    return summaries


def identify_common_patterns(errors: list) -> list:
    """识别共性错误模式。"""
    category_counts: dict = {}
    for e in errors:
        category_counts[e.category] = category_counts.get(e.category, 0) + 1

    patterns = []
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        if count > 1:
            patterns.append(f"{category} 类错误出现 {count} 次，可能存在系统性{category}问题")
    return patterns


def generate_system_suggestions(errors: list, patterns: list) -> list:
    """生成系统级建议。"""
    suggestions = []

    categories = set(e.category for e in errors)
    if "resource" in categories:
        suggestions.append("存在资源加载错误，建议检查部署流程和 CDN 缓存策略")
    if "network" in categories:
        suggestions.append("存在网络错误，建议检查后端服务健康状态和跨域配置")
    if "promise" in categories:
        suggestions.append("存在未处理的 Promise 拒绝，建议全局添加 unhandledrejection 监听")
    if "memory" in categories:
        suggestions.append("存在内存相关错误，建议排查事件监听和定时器是否正确清理")

    correlated = sum(1 for e in errors if e.session_id)
    if errors and correlated / len(errors) < 0.5:
        suggestions.append(f"错误与会话的关联率仅 {correlated/len(errors):.0%}，建议完善 SDK 集成注入 openreplay_session_id tag")

    if not patterns and not suggestions:
        suggestions.append("当前错误模式下未发现系统性问题，继续保持监控即可")

    return suggestions


def render_markdown_report(errors: list, patterns: list, suggestions: list,
                           period: str = "24h", total_correlated: int = 0) -> str:
    """渲染 Markdown 格式报告。"""
    lines = []
    lines.append("# 前端错误分析报告")
    lines.append("")
    lines.append(f"- **生成时间**: {datetime.now().isoformat()}")
    lines.append(f"- **分析周期**: {period}")
    lines.append(f"- **总 Issues 数**: {len(errors)}")
    lines.append(f"- **已关联会话**: {total_correlated}")
    lines.append("")

    # 优先级汇总
    priority_counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for e in errors:
        priority_counts[e.priority] = priority_counts.get(e.priority, 0) + 1

    lines.append("## 优先级分布")
    lines.append("")
    lines.append("| 优先级 | 数量 |")
    lines.append("|--------|------|")
    lines.append(f"| P0 | {priority_counts.get('P0', 0)} |")
    lines.append(f"| P1 | {priority_counts.get('P1', 0)} |")
    lines.append(f"| P2 | {priority_counts.get('P2', 0)} |")
    lines.append(f"| P3 | {priority_counts.get('P3', 0)} |")
    lines.append("")

    # 错误详情
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    sorted_errors = sorted(errors, key=lambda e: priority_order.get(e.priority, 9))

    lines.append("## 错误详情")
    lines.append("")

    for error in sorted_errors:
        priority_icon = {"P0": "🔴", "P1": "🟠", "P2": "🟡", "P3": "⚪"}.get(error.priority, "⚪")
        lines.append(f"### {priority_icon} {error.priority} | {error.title}")
        lines.append("")
        lines.append(f"- **Issue ID**: {error.issue_id}")
        lines.append(f"- **类别**: `{error.category}`")
        lines.append(f"- **影响**: {error.count} 次错误，{error.user_count} 位用户")
        lines.append(f"- **时间**: {error.first_seen} ~ {error.last_seen}")
        if error.session_id:
            lines.append(f"- **关联会话**: `{error.session_id}`")
        if error.root_cause:
            lines.append(f"- **线索**: {error.root_cause}")
        lines.append("")

    # 共性模式
    if patterns:
        lines.append("## 共性模式")
        lines.append("")
        for pattern in patterns:
            lines.append(f"- {pattern}")
        lines.append("")

    # 系统建议
    if suggestions:
        lines.append("## 系统建议")
        lines.append("")
        for suggestion in suggestions:
            lines.append(f"- {suggestion}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="生成前端错误分析报告")
    parser.add_argument("--errors", type=Path, help="错误数据 JSON 文件")
    parser.add_argument("--sessions", type=Path, help="会话数据 JSON 文件")
    parser.add_argument("--correlations", type=Path, help="关联数据 JSON 文件")
    parser.add_argument("--input-dir", type=Path, help="输入目录")
    parser.add_argument("--period", type=str, default="24h", help="分析周期描述")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="输出格式")
    parser.add_argument("--output", "-o", type=Path, help="输出文件路径")
    args = parser.parse_args()

    if args.input_dir:
        errors_path = args.input_dir / "errors.json"
        sessions_path = args.input_dir / "sessions.json"
        correlations_path = args.input_dir / "correlations.json"
    else:
        errors_path = args.errors
        sessions_path = args.sessions
        correlations_path = args.correlations

    if not errors_path:
        print("错误: 需要指定 --errors 或 --input-dir", file=sys.stderr)
        sys.exit(1)

    errors_data = load_json(errors_path)
    sessions_data = load_json(sessions_path)
    correlations_data = load_json(correlations_path)

    errors = build_error_summaries(errors_data, correlations_data, sessions_data)
    patterns = identify_common_patterns(errors)
    suggestions = generate_system_suggestions(errors, patterns)

    if args.format == "markdown":
        output = render_markdown_report(errors, patterns, suggestions,
                                         args.period, sum(1 for e in errors if e.session_id))
    else:
        report = {
            "generated_at": datetime.now().isoformat(),
            "period": args.period,
            "total_issues": len(errors),
            "total_correlated": sum(1 for e in errors if e.session_id),
            "errors": [vars(e) for e in errors],
            "common_patterns": patterns,
            "system_suggestions": suggestions,
        }
        output = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"已写入 {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
