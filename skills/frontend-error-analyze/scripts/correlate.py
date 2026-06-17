#!/usr/bin/env python3
"""关联 GlitchTip 错误与 OpenReplay 会话。

用法:
    python correlate.py --from-tag --issue-id 12345       # 从 GlitchTip tag 获取 session ID
    python correlate.py --by-time --issue-id 12345        # 按时间+用户匹配会话
    python correlate.py --batch --period 24h              # 批量关联所有未解决 Issues
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode


def get_env():
    """读取环境变量。"""
    glitchtip_url = os.environ.get("GLITCHTIP_URL", "").rstrip("/")
    glitchtip_token = os.environ.get("GLITCHTIP_TOKEN", "")
    openreplay_url = os.environ.get("OPENREPLAY_URL", "").rstrip("/")
    openreplay_token = os.environ.get("OPENREPLAY_TOKEN", "")
    org = os.environ.get("ORG_SLUG", "")
    project = os.environ.get("PROJECT_SLUG", "")

    missing = []
    if not glitchtip_url:
        missing.append("GLITCHTIP_URL")
    if not glitchtip_token:
        missing.append("GLITCHTIP_TOKEN")
    if not openreplay_url:
        missing.append("OPENREPLAY_URL")
    if not openreplay_token:
        missing.append("OPENREPLAY_TOKEN")
    if not org:
        missing.append("ORG_SLUG")
    if not project:
        missing.append("PROJECT_SLUG")
    if missing:
        print(f"错误: 缺少环境变量 {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    return glitchtip_url, glitchtip_token, openreplay_url, openreplay_token, org, project


def api_get(url: str, token: str, params: dict = None) -> dict:
    """通用 GET 请求。"""
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


def get_session_id_from_tag(glitchtip_url: str, token: str, issue_id: str) -> str:
    """从 GlitchTip Event 的 tag 中提取 OpenReplay session ID。"""
    event = api_get(f"{glitchtip_url}/api/0/issues/{issue_id}/events/latest/", token, {"full": "true"})
    tags = event.get("tags", [])
    for tag in tags:
        if tag.get("key") == "openreplay_session_id":
            return tag.get("value")
    return None


def find_matching_session(openreplay_url: str, token: str,
                          timestamp: str, user_id: str = None,
                          url: str = None) -> str:
    """按时间+用户+URL 匹配 OpenReplay 会话。"""
    ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    start = (ts - timedelta(seconds=30)).isoformat()
    end = (ts + timedelta(seconds=30)).isoformat()

    params = {"startDate": start, "endDate": end, "limit": "5", "sort": "createdAt:desc"}
    if user_id:
        params["userId"] = user_id

    result = api_get(f"{openreplay_url}/api/v1/sessions", token, params)
    sessions = result.get("sessions", [])

    if not sessions:
        return None

    if url:
        for session in sessions:
            if url in session.get("url", ""):
                return session.get("sessionId")

    return sessions[0].get("sessionId") if sessions else None


def correlate_issue(glitchtip_url: str, glitchtip_token: str,
                    openreplay_url: str, openreplay_token: str,
                    issue_id: str, method: str = "tag") -> dict:
    """关联单个 Issue。"""
    event = api_get(f"{glitchtip_url}/api/0/issues/{issue_id}/events/latest/",
                    glitchtip_token, {"full": "true"})

    session_id = None
    correlation_method = ""

    if method == "tag":
        tags = event.get("tags", [])
        for tag in tags:
            if tag.get("key") == "openreplay_session_id":
                session_id = tag.get("value")
                correlation_method = "tag"
                break

    if not session_id and method in ("tag", "by-time"):
        timestamp = event.get("timestamp", "")
        user_id = None
        url = None
        for tag in event.get("tags", []):
            if tag.get("key") == "user.id":
                user_id = tag.get("value")
            if tag.get("key") == "url":
                url = tag.get("value")
        session_id = find_matching_session(openreplay_url, openreplay_token,
                                           timestamp, user_id, url)
        correlation_method = "time_match"

    result = {
        "issueId": issue_id,
        "title": event.get("title", ""),
        "timestamp": event.get("timestamp", ""),
        "sessionId": session_id,
        "correlationMethod": correlation_method,
        "correlated": session_id is not None,
    }

    if session_id:
        session = api_get(f"{openreplay_url}/api/v1/sessions/{session_id}", openreplay_token)
        result["sessionDetails"] = {
            "userId": session.get("userId"),
            "userDisplayName": session.get("userDisplayName"),
            "startedAt": session.get("startedAt"),
            "duration": session.get("duration"),
            "errorsCount": session.get("errorsCount"),
            "url": session.get("url"),
        }

    return result


def main():
    parser = argparse.ArgumentParser(description="关联 GlitchTip 错误与 OpenReplay 会话")
    parser.add_argument("--from-tag", action="store_true", help="从 tag 获取 session ID")
    parser.add_argument("--by-time", action="store_true", help="按时间窗口匹配")
    parser.add_argument("--issue-id", type=str, help="GlitchTip Issue ID")
    parser.add_argument("--batch", action="store_true", help="批量关联所有未解决 Issues")
    parser.add_argument("--period", type=str, default="24h", help="批量关联时间范围")
    parser.add_argument("--output", "-o", type=Path, help="输出文件路径")
    args = parser.parse_args()

    glitchtip_url, glitchtip_token, openreplay_url, openreplay_token, org, project = get_env()

    method = "tag" if args.from_tag else "by-time"

    if args.batch:
        issues = api_get(f"{glitchtip_url}/api/0/projects/{org}/{project}/issues/",
                         glitchtip_token,
                         {"query": "is:unresolved", "sort": "freq", "statsPeriod": args.period})
        results = []
        for issue in issues[:50]:
            issue_id = issue.get("id")
            try:
                result = correlate_issue(glitchtip_url, glitchtip_token,
                                         openreplay_url, openreplay_token,
                                         issue_id, method)
                results.append(result)
                print(f"  Issue {issue_id}: {'已关联' if result['correlated'] else '未找到'}")
            except Exception as e:
                print(f"  Issue {issue_id}: {e}", file=sys.stderr)
        output_data = {"total": len(results), "correlated": sum(1 for r in results if r["correlated"]),
                       "results": results}
    elif args.issue_id:
        output_data = correlate_issue(glitchtip_url, glitchtip_token,
                                      openreplay_url, openreplay_token,
                                      args.issue_id, method)
    else:
        parser.print_help()
        sys.exit(1)

    output = json.dumps(output_data, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"已写入 {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
