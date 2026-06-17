#!/usr/bin/env python3
"""从 OpenReplay 拉取会话数据。

用法:
    python fetch_sessions.py --list --user-id user-123        # 拉取用户最近的会话
    python fetch_sessions.py --detail --session-id abc123     # 获取会话详情
    python fetch_sessions.py --events --session-id abc123     # 获取会话事件流
    python fetch_sessions.py --by-error "TypeError:xxx"       # 按错误查找会话
    python fetch_sessions.py --journey --session-id abc123    # 提取用户操作路径
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
    url = os.environ.get("OPENREPLAY_URL", "").rstrip("/")
    token = os.environ.get("OPENREPLAY_TOKEN", "")
    missing = []
    if not url:
        missing.append("OPENREPLAY_URL")
    if not token:
        missing.append("OPENREPLAY_TOKEN")
    if missing:
        print(f"错误: 缺少环境变量 {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)
    return url, token


def api_get(url: str, token: str, params: dict = None) -> dict:
    """发送 GET 请求到 OpenReplay API。"""
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


def fetch_sessions(base_url: str, token: str, user_id: str = None,
                   start_date: str = None, end_date: str = None,
                   issue_id: str = None, limit: int = 25) -> dict:
    """拉取会话列表。"""
    url = f"{base_url}/api/v1/sessions"
    params = {"sort": "createdAt:desc", "limit": str(limit)}
    if user_id:
        params["userId"] = user_id
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    if issue_id:
        params["issueId"] = issue_id
    return api_get(url, token, params)


def fetch_session_detail(base_url: str, token: str, session_id: str) -> dict:
    """获取会话详情。"""
    url = f"{base_url}/api/v1/sessions/{session_id}"
    return api_get(url, token)


def fetch_session_events(base_url: str, token: str, session_id: str) -> dict:
    """获取会话事件流。"""
    url = f"{base_url}/api/v1/sessions/{session_id}/events"
    return api_get(url, token)


def extract_user_journey(events_data: dict, around_error_seconds: int = 30) -> list:
    """从事件流中提取用户操作路径。

    过滤出关键事件（点击、网络请求、异常、控制台错误），
    并在异常前后截取指定时间窗口的事件。
    """
    events = events_data.get("events", [])
    if not events:
        return []

    # 找到异常事件的时间戳
    error_timestamp = None
    for event in events:
        if event.get("type") == "exception":
            error_timestamp = event.get("timestamp")
            break

    # 过滤关键事件
    key_events = []
    for event in events:
        etype = event.get("type")
        payload = event.get("payload", {})
        ts = event.get("timestamp", 0)

        # 如果有错误时间戳，只取前后 N 秒
        if error_timestamp:
            diff_ms = abs(ts - error_timestamp)
            if diff_ms > around_error_seconds * 1000:
                continue

        if etype == "mouse" and payload.get("type") == "click":
            key_events.append({
                "time": payload.get("time"),
                "type": "click",
                "label": payload.get("label", ""),
                "target": payload.get("target", ""),
            })
        elif etype == "network":
            key_events.append({
                "time": payload.get("time"),
                "type": "network",
                "method": payload.get("method"),
                "url": payload.get("url"),
                "status": payload.get("status"),
                "duration": payload.get("duration"),
            })
        elif etype == "exception":
            key_events.append({
                "time": payload.get("time"),
                "type": "exception",
                "error_type": payload.get("type"),
                "message": payload.get("message"),
            })
        elif etype == "console" and payload.get("level") == "error":
            key_events.append({
                "time": payload.get("time"),
                "type": "console_error",
                "value": payload.get("value"),
            })
        elif etype == "location":
            key_events.append({
                "time": payload.get("time"),
                "type": "navigation",
                "url": payload.get("url"),
            })

    key_events.sort(key=lambda e: e.get("time", 0))
    return key_events


def main():
    parser = argparse.ArgumentParser(description="从 OpenReplay 拉取会话数据")
    parser.add_argument("--list", action="store_true", help="拉取会话列表")
    parser.add_argument("--detail", action="store_true", help="获取会话详情")
    parser.add_argument("--events", action="store_true", help="获取会话事件流")
    parser.add_argument("--by-error", type=str, help="按错误类型查找会话")
    parser.add_argument("--user-id", type=str, help="用户 ID")
    parser.add_argument("--session-id", type=str, help="会话 ID")
    parser.add_argument("--start-date", type=str, help="开始时间 (ISO 8601)")
    parser.add_argument("--end-date", type=str, help="结束时间 (ISO 8601)")
    parser.add_argument("--limit", type=int, default=25, help="返回数量")
    parser.add_argument("--journey", action="store_true", help="提取用户操作路径")
    parser.add_argument("--around-error", type=int, default=30, help="错误前后截取秒数")
    parser.add_argument("--output", "-o", type=Path, help="输出文件路径")
    args = parser.parse_args()

    base_url, token = get_env()

    if args.list or args.by_error:
        issue_id = args.by_error if args.by_error else None
        result = fetch_sessions(base_url, token, args.user_id, args.start_date,
                                args.end_date, issue_id, args.limit)
    elif args.detail:
        if not args.session_id:
            print("错误: 需要指定 --session-id", file=sys.stderr)
            sys.exit(1)
        result = fetch_session_detail(base_url, token, args.session_id)
    elif args.events or args.journey:
        if not args.session_id:
            print("错误: 需要指定 --session-id", file=sys.stderr)
            sys.exit(1)
        events_data = fetch_session_events(base_url, token, args.session_id)
        if args.journey:
            journey = extract_user_journey(events_data, args.around_error)
            result = {"sessionId": args.session_id, "journey": journey}
        else:
            result = events_data
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
