#!/usr/bin/env python3
"""从 GlitchTip 拉取 Issues 和 Events。

用法:
    python fetch_errors.py --issues                     # 拉取未解决的 Issues
    python fetch_errors.py --issues --period 7d         # 最近 7 天
    python fetch_errors.py --events --issue-id 12345    # 拉取某 Issue 的最新 Event
    python fetch_errors.py --events --issue-id 12345 --full  # 含面包屑完整上下文
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode


def get_env():
    """读取环境变量。"""
    url = os.environ.get("GLITCHTIP_URL", "").rstrip("/")
    token = os.environ.get("GLITCHTIP_TOKEN", "")
    org = os.environ.get("ORG_SLUG", "")
    project = os.environ.get("PROJECT_SLUG", "")
    missing = []
    if not url:
        missing.append("GLITCHTIP_URL")
    if not token:
        missing.append("GLITCHTIP_TOKEN")
    if not org:
        missing.append("ORG_SLUG")
    if not project:
        missing.append("PROJECT_SLUG")
    if missing:
        print(f"错误: 缺少环境变量 {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)
    return url, token, org, project


def api_get(url: str, token: str, params: dict = None) -> dict:
    """发送 GET 请求到 GlitchTip API。"""
    if params:
        url = f"{url}?{urlencode(params)}"
    req = Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"API 请求失败 [{e.code}]: {body}", file=sys.stderr)
        sys.exit(1)


def fetch_issues(base_url: str, token: str, org: str, project: str,
                 period: str = "24h", query: str = "is:unresolved",
                 sort: str = "freq", limit: int = 100) -> list:
    """拉取 Issues 列表。"""
    url = f"{base_url}/api/0/projects/{org}/{project}/issues/"
    params = {"query": query, "sort": sort, "statsPeriod": period, "limit": str(limit)}
    return api_get(url, token, params)


def fetch_events(base_url: str, token: str, issue_id: str, full: bool = False) -> list:
    """拉取某 Issue 的 Event 列表。"""
    url = f"{base_url}/api/0/issues/{issue_id}/events/"
    params = {}
    if full:
        params["full"] = "true"
    return api_get(url, token, params)


def fetch_latest_event(base_url: str, token: str, issue_id: str, full: bool = True) -> dict:
    """拉取某 Issue 的最新 Event。"""
    url = f"{base_url}/api/0/issues/{issue_id}/events/latest/"
    params = {}
    if full:
        params["full"] = "true"
    return api_get(url, token, params)


def classify_issue(issue: dict) -> str:
    """对 Issue 进行简单分类。"""
    title = issue.get("title", "")
    culprit = issue.get("culprit", "")
    text = f"{title} {culprit}".lower()

    if "chunkloaderror" in text or "loading chunk" in text or "loading css" in text:
        return "resource"
    if "network" in text or "cors" in text or "502" in text or "503" in text or "504" in text:
        return "network"
    if "hydration" in text or "maximum update" in text or "invalid hook" in text:
        return "framework"
    if "out of memory" in text or "oom" in text:
        return "memory"
    if "unhandled" in text and "rejection" in text:
        return "promise"
    if "typeerror" in text or "referenceerror" in text or "rangeerror" in text:
        return "js_runtime"
    return "unknown"


def prioritize_issue(issue: dict) -> str:
    """对 Issue 优先级分级。"""
    user_count = int(issue.get("userCount", 0))
    count = int(issue.get("count", "0"))
    if user_count > 100:
        return "P0"
    if user_count > 10 or count > 1000:
        return "P1"
    if user_count > 1 or count > 100:
        return "P2"
    return "P3"


def enrich_issues(issues: list) -> list:
    """为 Issue 列表添加分类和优先级。"""
    for issue in issues:
        issue["_category"] = classify_issue(issue)
        issue["_priority"] = prioritize_issue(issue)
    return issues


def main():
    parser = argparse.ArgumentParser(description="从 GlitchTip 拉取错误数据")
    parser.add_argument("--issues", action="store_true", help="拉取 Issues 列表")
    parser.add_argument("--events", action="store_true", help="拉取 Events")
    parser.add_argument("--issue-id", type=str, help="指定 Issue ID")
    parser.add_argument("--period", type=str, default="24h", help="时间范围 (1h/24h/7d/30d)")
    parser.add_argument("--query", type=str, default="is:unresolved", help="搜索查询")
    parser.add_argument("--sort", type=str, default="freq", help="排序方式 (freq/new/date/user)")
    parser.add_argument("--limit", type=int, default=100, help="返回数量")
    parser.add_argument("--full", action="store_true", help="返回完整 Event 上下文")
    parser.add_argument("--output", "-o", type=Path, help="输出文件路径")
    args = parser.parse_args()

    base_url, token, org, project = get_env()

    if args.issues:
        issues = fetch_issues(base_url, token, org, project, args.period, args.query, args.sort, args.limit)
        issues = enrich_issues(issues)
        result = {"total": len(issues), "issues": issues}
    elif args.events:
        if not args.issue_id:
            print("错误: 拉取 Events 需要指定 --issue-id", file=sys.stderr)
            sys.exit(1)
        events = fetch_events(base_url, token, args.issue_id, args.full)
        result = {"total": len(events) if isinstance(events, list) else 1, "events": events}
    else:
        parser.print_help()
        sys.exit(1)

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"已写入 {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
