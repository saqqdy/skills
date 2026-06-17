# OpenReplay API 参考

OpenReplay 提供会话回放、用户追踪和性能监控功能。本文档记录常用的 API 端点。

---

## 认证

所有请求需携带 Authorization Header：

```bash
curl -H "Authorization: Bearer ${OPENREPLAY_TOKEN}" \
  "https://replay.example.com/api/v1/..."
```

Token 获取方式：
1. 登录 OpenReplay → Account → API Tokens
2. 创建 Token，勾选所需权限

---

## Sessions

### 获取会话列表
```bash
GET /api/v1/sessions

# 查询参数
# userId    - 用户 ID
# sort      - 排序: createdAt:desc（默认）
# limit     - 返回数量（默认 25，最大 100）
# offset    - 偏移量
# startDate - 开始时间 (ISO 8601)
# endDate   - 结束时间 (ISO 8601)
# issueId   - 包含特定错误的会话
# url       - 页面 URL 过滤
# browser   - 浏览器过滤
# os        - 操作系统过滤
# device    - 设备过滤
# country   - 国家代码

# 示例：获取特定用户最近的会话
GET /api/v1/sessions?userId=user-123&sort=createdAt:desc&limit=5

# 响应
{
  "sessions": [
    {
      "sessionId": "abc123def456",
      "userId": "user-123",
      "userUuid": "user-123",
      "metadata": {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
        "browser": "Chrome 126",
        "os": "macOS 15.4",
        "device": "Desktop",
        "country": "CN",
        "viewportWidth": 1920,
        "viewportHeight": 1080
      },
      "startedAt": "2026-06-17T10:20:00Z",
      "duration": 185000,
      "pagesCount": 8,
      "eventsCount": 342,
      "errorsCount": 3,
      "issuesCount": 1,
      "url": "/dashboard/reports",
      "platform": "web",
      "revision": "v2.3.1"
    }
  ],
  "total": 15
}
```

### 获取会话详情
```bash
GET /api/v1/sessions/{session_id}

# 响应（额外字段）
{
  ...,
  "userDisplayName": "张三",
  "userEmail": "zhangsan@example.com",
  "metadata": {
    ...,
    "UTM_source": "google",
    "UTM_medium": "cpc"
  }
}
```

### 获取会话事件流
```bash
GET /api/v1/sessions/{session_id}/events

# 响应 - 事件类型列表
{
  "events": [
    {
      "type": "dom",
      "timestamp": 12300000,
      "payload": {
        "time": 12300,
        "tag": "mutation",
        "mutation": { ... }
      }
    },
    {
      "type": "mouse",
      "timestamp": 12305000,
      "payload": {
        "time": 12305,
        "x": 940,
        "y": 520,
        "type": "click",
        "label": "button.export",
        "target": "button.btn-primary"
      }
    },
    {
      "type": "network",
      "timestamp": 12310000,
      "payload": {
        "time": 12310,
        "method": "POST",
        "url": "/api/reports/export",
        "status": 502,
        "requestBody": null,
        "responseBody": "<html>Bad Gateway</html>",
        "duration": 30001
      }
    },
    {
      "type": "exception",
      "timestamp": 12310500,
      "payload": {
        "time": 12310,
        "type": "TypeError",
        "message": "Cannot read properties of undefined (reading 'url')",
        "stack": "TypeError: Cannot read properties...\n  at ReportExport.vue:42:15",
        "source": "mouse"
      }
    },
    {
      "type": "console",
      "timestamp": 12310600,
      "payload": {
        "time": 12310,
        "level": "error",
        "trace": [ ... ],
        "value": "Uncaught TypeError: Cannot read properties of undefined (reading 'url')"
      }
    },
    {
      "type": "performance",
      "timestamp": 12300000,
      "payload": {
        "time": 12300,
        "metric": "LCP",
        "value": 2500
      }
    }
  ]
}
```

### 按错误搜索会话
```bash
# 查找包含特定错误的会话
GET /api/v1/sessions?issueId=TypeError:Cannot-read-properties-of-undefined-reading-map

# 查找时间段内有错误的会话
GET /api/v1/sessions?startDate=2026-06-17T10:00:00Z&endDate=2026-06-17T11:00:00Z&errorsCount=gt:0
```

---

## Users

### 获取用户列表
```bash
GET /api/v1/users?search=zhangsan&limit=10

# 响应
{
  "users": [
    {
      "userId": "user-123",
      "displayName": "张三",
      "email": "zhangsan@example.com",
      "sessionsCount": 45,
      "errorsCount": 12,
      "firstSeenAt": "2026-01-10T08:00:00Z",
      "lastSeenAt": "2026-06-17T10:15:30Z"
    }
  ],
  "total": 1
}
```

---

## 错误追踪

### 获取错误列表
```bash
GET /api/v1/issues?status=unresolved&sort=frequency&limit=20

# 响应
{
  "issues": [
    {
      "issueId": "TypeError:Cannot-read-properties-of-undefined-reading-map",
      "type": "TypeError",
      "message": "Cannot read properties of undefined (reading 'map')",
      "stack": "...\n  at UserList.vue:25:18",
      "status": "unresolved",
      "frequency": 342,
      "usersCount": 89,
      "firstSeenAt": "2026-06-16T08:23:45Z",
      "lastSeenAt": "2026-06-17T10:15:30Z",
      "sessions": ["abc123def456", "xyz789"]
    }
  ]
}
```

---

## Live Search

### 实时搜索
```bash
# 按 URL 路径搜索活跃会话
GET /api/v1/live/sessions?path=/dashboard

# 按 JS 错误搜索
GET /api/v1/live/sessions?error=TypeError
```

---

## 事件类型速查

| 事件类型 | type 值 | 关键字段 | 用途 |
|----------|---------|----------|------|
| DOM 变更 | `dom` | mutation | 还原页面状态 |
| 鼠标交互 | `mouse` | x, y, type(click/move/scroll), label | 操作路径还原 |
| 键盘输入 | `keyboard` | key, type(keydown/keyup) | 输入行为分析 |
| 网络请求 | `network` | method, url, status, duration, requestBody/responseBody | 接口问题定位 |
| JS 异常 | `exception` | type, message, stack | 错误根因 |
| 控制台日志 | `console` | level, value | 辅助调试 |
| 路由变化 | `location` | url, referrer | 页面跳转追踪 |
| 性能指标 | `performance` | metric(LCP/FID/CLS), value | 性能分析 |
| 自定义事件 | `custom` | name, payload | 业务追踪 |

---

## 提取用户操作路径的方法

从事件流中提取关键操作序列时，关注以下事件类型的组合：

```
1. location  → 页面跳转（上下文）
2. mouse(click) → 用户点击（关键操作）
3. network   → 接口请求（因果关系）
4. exception → 错误发生（结果）
5. console(error) → 伴随日志（辅助证据）
```

建议过滤流程：
1. 筛选 `type=mouse` 且 `payload.type=click` 的事件
2. 筛选 `type=network` 的事件
3. 筛选 `type=exception` 的事件
4. 按时间戳排序串联
5. 在错误前后各取 30s 的事件作为上下文

---

## 与 GlitchTip 关联

### 配置方式

```javascript
// 前端初始化时关联
import Tracker from '@openreplay/tracker';
import trackerAssist from '@openreplay/tracker-assist';
import * as Sentry from '@sentry/browser';

const tracker = new Tracker({
  projectKey: 'xxx',
});

// 使用 OpenReplay 的 Sentry 插件自动关联
const trackerSentry = tracker.use(trackerAssist());

tracker.start();

// Sentry 初始化时，OpenReplay session ID 会自动注入
Sentry.init({
  dsn: 'https://xxx@errors.example.com/1',
  integrations: [trackerSentry.sentryIntegration()],
});
```

### 通过 API 关联

无需前端集成时，可通过 API 匹配：

```bash
# 1. 从 GlitchTip Event 获取 tag
OPENREPLAY_SESSION_ID=$(curl -s -H "Authorization: Bearer ${GLITCHTIP_TOKEN}" \
  "${GLITCHTIP_URL}/api/0/issues/${ISSUE_ID}/events/latest/" | \
  jq -r '.tags[] | select(.key=="openreplay_session_id") | .value')

# 2. 用 session ID 获取 OpenReplay 会话
curl -H "Authorization: Bearer ${OPENREPLAY_TOKEN}" \
  "${OPENREPLAY_URL}/api/v1/sessions/${OPENREPLAY_SESSION_ID}"

# 3. 获取事件流
curl -H "Authorization: Bearer ${OPENREPLAY_TOKEN}" \
  "${OPENREPLAY_URL}/api/v1/sessions/${OPENREPLAY_SESSION_ID}/events"
```
