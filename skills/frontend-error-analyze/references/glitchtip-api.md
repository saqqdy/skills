# GlitchTip API 参考

GlitchTip API 与 Sentry API 完全兼容，使用 `/api/0/` 前缀。本文档记录常用的 API 端点。

---

## 认证

所有请求需携带 Authorization Header：

```bash
curl -H "Authorization: Bearer ${GLITCHTIP_TOKEN}" \
  "https://errors.example.com/api/0/..."
```

Token 获取方式：
1. 登录 GlitchTip → Settings → API Keys
2. 创建组织级别的 Token，勾选所需权限

---

## Organizations

### 获取组织列表
```bash
GET /api/0/organizations/

# 响应
[
  {
    "id": 1,
    "slug": "my-team",
    "name": "My Team"
  }
]
```

---

## Projects

### 获取项目列表
```bash
GET /api/0/organizations/{org_slug}/projects/

# 响应
[
  {
    "id": 1,
    "slug": "web-app",
    "name": "Web App",
    "platform": "javascript-vue"
  }
]
```

---

## Issues（核心）

### 获取 Issue 列表
```bash
GET /api/0/projects/{org_slug}/{project_slug}/issues/

# 查询参数
# query      - 搜索过滤（Sentry 搜索语法）
# sort       - 排序: freq（默认）, new, date, user
# statsPeriod - 时间范围: 1h, 24h, 7d, 30d, 90d
# limit      - 返回数量（默认 100，最大 1000）

# 示例：获取最近 24h 未解决的按频率排序的 Issues
GET /api/0/projects/my-team/web-app/issues/?query=is:unresolved&sort=freq&statsPeriod=24h

# 响应
[
  {
    "id": "12345",
    "shortId": "WEB-ABC",
    "title": "TypeError: Cannot read properties of undefined (reading 'map')",
    "culprit": "UserList.vue in map",
    "level": "error",
    "status": "unresolved",
    "type": "error",
    "count": "342",
    "userCount": 89,
    "firstSeen": "2026-06-16T08:23:45Z",
    "lastSeen": "2026-06-17T10:15:30Z",
    "tags": [
      {"key": "environment", "value": "production"},
      {"key": "release", "value": "v2.3.1"},
      {"key": "openreplay_session_id", "value": "abc123def456"},
      {"key": "url", "value": "/dashboard/reports"}
    ]
  }
]
```

### 搜索语法

| 过滤器 | 示例 | 说明 |
|--------|------|------|
| `is:unresolved` | `is:unresolved` | 状态过滤 |
| `level:error` | `level:error` | 级别过滤 |
| `release:v2.3.1` | `release:v2.3.1` | 版本过滤 |
| `environment:production` | `environment:production` | 环境过滤 |
| `url:/dashboard` | `url:/dashboard*` | URL 匹配 |
| `user.id:123` | `user.id:123` | 特定用户 |
| `message:TypeError` | `message:*TypeError*` | 消息匹配 |
| `has:openreplay_session_id` | `has:openreplay_session_id` | 有 OpenReplay 关联 |

### 获取 Issue 详情
```bash
GET /api/0/issues/{issue_id}/

# 响应中额外字段
{
  ...,
  "metadata": {
    "type": "TypeError",
    "value": "Cannot read properties of undefined (reading 'map')",
    "filename": "app:///_nuxt/assets/UserList.vue"
  }
}
```

### 更新 Issue 状态
```bash
PUT /api/0/issues/{issue_id}/
Content-Type: application/json

{"status": "resolved"}
```

---

## Events

### 获取 Issue 的 Event 列表
```bash
GET /api/0/issues/{issue_id}/events/?full=true

# 查询参数
# full=true - 返回完整上下文（含面包屑、tag 详情）

# 响应
[
  {
    "id": "abc123eventid",
    "eventID": "abc123eventid",
    "title": "TypeError: Cannot read properties of undefined (reading 'map')",
    "message": "TypeError: Cannot read properties of undefined (reading 'map')",
    "timestamp": "2026-06-17T10:15:30Z",
    "contexts": {
      "browser": {"name": "Chrome", "version": "126.0"},
      "os": {"name": "macOS", "version": "15.4"}
    },
    "tags": [
      {"key": "openreplay_session_id", "value": "abc123def456"},
      {"key": "url", "value": "/dashboard/reports"},
      {"key": "release", "value": "v2.3.1"}
    ],
    "entries": [
      {
        "type": "exception",
        "data": {
          "values": [
            {
              "type": "TypeError",
              "value": "Cannot read properties of undefined (reading 'map')",
              "stacktrace": {
                "frames": [
                  {
                    "filename": "app:///_nuxt/assets/UserList.vue",
                    "lineno": 25,
                    "colno": 18,
                    "function": "renderList",
                    "inApp": true,
                    "absPath": "https://cdn.example.com/_nuxt/assets/UserList.abc123.js"
                  },
                  {
                    "filename": "node_modules/vue/dist/vue.runtime.esm.js",
                    "lineno": 1234,
                    "colno": 5,
                    "function": "renderComponentRoot",
                    "inApp": false
                  }
                ]
              }
            }
          ]
        }
      },
      {
        "type": "breadcrumbs",
        "data": {
          "values": [
            {"type": "navigation", "category": "navigation", "data": {"to": "/dashboard"}},
            {"type": "http", "category": "xhr", "data": {"url": "/api/reports", "method": "GET"}},
            {"type": "ui", "category": "ui.click", "message": "button.export"}
          ]
        }
      }
    ]
  }
]
```

### 获取最新 Event
```bash
GET /api/0/issues/{issue_id}/events/latest/?full=true
```

---

## Releases

### 获取 Release 列表
```bash
GET /api/0/organizations/{org_slug}/releases/

# 响应
[
  {
    "version": "v2.3.1",
    "dateReleased": "2026-06-15T12:00:00Z",
    "newGroups": 3,
    "projects": [{"slug": "web-app"}]
  }
]
```

---

## 分页

列表接口支持分页：

```bash
# 使用 cursor 分页
GET /api/0/projects/.../issues/?cursor=100:0:1

# 响应 Header
Link: <https://errors.example.com/api/0/.../?cursor=100:0:0>; rel="previous"
Link: <https://errors.example.com/api/0/.../?cursor=100:0:1>; rel="next"
```

---

## 速率限制

- 未认证：不可访问
- 认证请求：默认 1000 请求/小时
- 429 响应时检查 `X-RateLimit-Remaining` Header

---

## 常用组合查询

```bash
# 最近 1 小时的高频错误（用户数 > 50）
curl -H "Authorization: Bearer ${GLITCHTIP_TOKEN}" \
  "${GLITCHTIP_URL}/api/0/projects/${ORG}/${PROJ}/issues/?query=is:unresolved level:error&sort=freq&statsPeriod=1h"

# 特定版本的新增错误
curl -H "Authorization: Bearer ${GLITCHTIP_TOKEN}" \
  "${GLITCHTIP_URL}/api/0/projects/${ORG}/${PROJ}/issues/?query=is:unresolved firstRelease:v2.3.1&sort=new"

# 有回放关联的错误
curl -H "Authorization: Bearer ${GLITCHTIP_TOKEN}" \
  "${GLITCHTIP_URL}/api/0/projects/${ORG}/${PROJ}/issues/?query=is:unresolved has:openreplay_session_id&sort=freq"
```
