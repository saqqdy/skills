---
name: frontend-error-analyze
description: 分析前端监控平台的错误数据（GlitchTip 错误追踪 + OpenReplay 会话回放），交叉关联错误堆栈、用户操作路径与源码，快速定位并修复前端问题。当用户需要排查前端错误、分析 JS 异常、查看用户会话回放、定位线上 Bug 时触发。
metadata:
  author: saqqdy
  version: "2026.06.17"
---

# 前端错误分析器

基于 GlitchTip + OpenReplay 监控平台，交叉关联错误追踪、会话回放与源码仓库，快速定位并修复前端问题。

## 核心分析流程

```
GlitchTip Issues ──→ 错误分类 & 聚合
       │                    │
       │ openreplay_session_id tag
       ▼                    ▼
OpenReplay Sessions ──→ 用户操作路径还原
                            │
                            ▼
                    源码仓库 ──→ 定位代码行 & 生成修复
```

三源交叉是本 skill 的核心价值：
- **GlitchTip** 告诉你 **WHAT**（什么错误、频率、影响范围）
- **OpenReplay** 告诉你 **WHY**（用户做了什么触发了这个错误）
- **源码仓库** 告诉你 **HOW**（Claude 直接读取代码并修复）

---

## 阶段 1：错误获取与分类

### 1.1 从 GlitchTip 获取错误列表

GlitchTip API 与 Sentry 完全兼容，使用 `/api/0/` 前缀。

```bash
# 获取项目最近的 Issues（按频率排序）
curl -H "Authorization: Bearer ${GLITCHTIP_TOKEN}" \
  "${GLITCHTIP_URL}/api/0/projects/${ORG_SLUG}/${PROJECT_SLUG}/issues/?query=is:unresolved&sort=freq&statsPeriod=24h"

# 获取某个 Issue 的最新 Event（含堆栈）
curl -H "Authorization: Bearer ${GLITCHTIP_TOKEN}" \
  "${GLITCHTIP_URL}/api/0/issues/${ISSUE_ID}/events/latest/"
```

环境变量要求：

| 变量 | 说明 | 示例 |
|------|------|------|
| `GLITCHTIP_URL` | GlitchTip 实例地址 | `https://errors.example.com` |
| `GLITCHTIP_TOKEN` | API Token（组织级别） | `glitchtip-api-xxx` |
| `ORG_SLUG` | 组织标识 | `my-team` |
| `PROJECT_SLUG` | 项目标识 | `web-app` |

### 1.2 错误分级

按以下维度对错误排序，优先处理高影响错误：

| 优先级 | 条件 | 行动 |
|--------|------|------|
| 🔴 P0 | 用户数 > 100 且 24h 内持续发生 | 立即分析修复 |
| 🟠 P1 | 用户数 > 10 或错误率 > 1% | 当天处理 |
| 🟡 P2 | 频率低但影响关键流程 | 排入迭代 |
| ⚪ P3 | 降级错误、第三方脚本 | 观察或忽略 |

### 1.3 错误分类

将错误归入以下类别，每类有不同的分析策略：

| 类别 | 典型错误 | 分析重点 |
|------|----------|----------|
| `js_runtime` | TypeError, ReferenceError, RangeError | 定位空值/未定义的根因 |
| `network` | NetworkError, CORS, 502/503/504 | 接口状态、超时、跨域配置 |
| `resource` | ChunkLoadError, CSS/JS加载失败 | 部署版本、CDN、缓存策略 |
| `framework` | Hydration mismatch, Max update depth | SSR/CSR 一致性、渲染循环 |
| `memory` | Out of memory, 页面卡死 | 内存泄漏、事件监听、闭包 |
| `third_party` | SDK 报错、广告/分析脚本 | try-catch 隔离、沙箱化 |
| `promise` | UnhandledRejection | 异步错误处理遗漏 |

---

## 阶段 2：交叉关联 — 错误 ↔ 会话回放

### 2.1 关联方式

**方式一：Tag 注入（推荐，精度最高）**

前端代码中初始化 SDK 时，将 OpenReplay session ID 写入 GlitchTip tag：

```javascript
import * as Sentry from '@sentry/browser';
import Tracker from '@openreplay/tracker';

const tracker = new Tracker({ projectKey: 'xxx' });
tracker.start();

// 关键：把 OpenReplay session ID 注入 GlitchTip
Sentry.setTag('openreplay_session_id', tracker.getSessionID());
```

关联后，Event 数据中 `tags` 字段会包含 `openreplay_session_id`。

**方式二：时间 + 用户匹配**

无 tag 时，按 `timestamp ± 30s` + `userId` + `URL` 在 OpenReplay 中搜索匹配的会话。

### 2.2 获取 OpenReplay 会话

```bash
# 获取某个用户的会话列表
curl -H "Authorization: Bearer ${OPENREPLAY_TOKEN}" \
  "${OPENREPLAY_URL}/api/v1/sessions?userId=${USER_ID}&sort=createdAt:desc&limit=5"

# 获取会话详情（含事件流）
curl -H "Authorization: Bearer ${OPENREPLAY_TOKEN}" \
  "${OPENREPLAY_URL}/api/v1/sessions/${SESSION_ID}/events"
```

环境变量要求：

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENREPLAY_URL` | OpenReplay 实例地址 | `https://replay.example.com` |
| `OPENREPLAY_TOKEN` | API Token | `or-xxx` |

### 2.3 用户操作路径还原

从 OpenReplay 事件流中提取关键操作序列：

```
时间线：
  10:23:01  页面加载 /dashboard
  10:23:03  点击 "导出报表" 按钮 ← 关键操作
  10:23:04  发起 POST /api/reports/export 请求
  10:23:05  接口返回 502 Bad Gateway ← 触发条件
  10:23:05  ⚡ Uncaught TypeError: Cannot read 'url' of undefined ← 错误发生
```

---

## 阶段 3：堆栈还原与源码定位

### 3.1 Source Map 还原

线上环境堆栈通常是压缩后的代码（如 `main.abc123.js:1:23456`），需要还原到源码行。

手动还原步骤：
1. 在项目构建产物中找到对应的 `.map` 文件
2. 使用 `source-map` 库或在线工具还原
3. 得到原始文件名、行号、列号

```bash
# 使用脚本自动还原
python scripts/resolve_stacktrace.py --sourcemap-dir ./dist --stacktrace '{"frames": [...]}'
```

### 3.2 读取源码上下文

还原后，Claude 直接读取仓库中对应的源文件并根据堆栈信息定位问题：

```
还原结果：
  文件: src/components/ReportExport.vue
  行号: 42
  列号: 15

→  Claude 读取该文件的 35-55 行，理解上下文
→  分析出错变量为何为 undefined
→  结合用户操作路径（接口 502），确定根因
```

---

## 阶段 4：诊断与修复

### 4.1 诊断报告格式

对每个错误输出结构化诊断：

```markdown
## 🔴 P0 | TypeError: Cannot read 'url' of undefined

**影响范围**：24h 内 342 位用户，错误率 2.3%
**文件**：`src/components/ReportExport.vue:42`
**触发路径**：仪表盘 → 导出报表 → 接口 502 → 未处理空值

### 根因分析
导出接口返回 502 时，`response.data` 为 null，代码直接访问 `response.data.url`，
缺少空值校验。

### 修复方案
\`\`\`diff
- const downloadUrl = response.data.url
+ const downloadUrl = response.data?.url
  if (!downloadUrl) {
    message.error('导出失败，请稍后重试')
    return
  }
\`\`\`

### 防御加固
1. 在 `fetchExportReport` 中对 5xx 响应统一处理
2. 添加 `response.data` 类型校验（zod / TypeScript guard）
```

### 4.2 批量分析模式

当用户要求"分析所有未解决的错误"时：

1. 拉取全部 unresolved issues
2. 按 P0→P3 排序
3. 对 P0/P1 逐个走完阶段 1-4 流程
4. 对 P2/P3 输出摘要和趋势
5. 生成整体报告含：修复优先级、共性问题、系统建议

---

## 常见前端错误诊断速查

### JS 运行时错误

| 错误 | 典型原因 | 检查点 |
|------|----------|--------|
| `TypeError: Cannot read props of undefined` | 异步数据未到就渲染 | 可选链 `?.`、加载态守卫 |
| `TypeError: xxx is not a function` | 动态导入失败或版本不匹配 | 检查 import 路径、包版本 |
| `ReferenceError: xxx is not defined` | 变量作用域/拼写错误 | 检查声明位置、闭包引用 |
| `RangeError: Maximum call stack` | 无限递归 | 检查递归终止条件 |

### 网络错误

| 错误 | 典型原因 | 检查点 |
|------|----------|--------|
| `NetworkError` | 请求被阻断或网络断开 | 检查请求 URL、CSP 策略 |
| `CORS error` | 缺少 Access-Control 头 | 服务端配置 CORS |
| `502/504` | 网关超时或后端不可用 | 检查后端服务状态 |
| `ChunkLoadError` | 部署后旧 chunk 被删除 | 版本回退策略、路由错误边界 |

### 框架特定错误

| 错误 | 典型原因 | 检查点 |
|------|----------|--------|
| `Hydration mismatch` | SSR/CSR 渲染不一致 | 检查服务端/客户端数据差异 |
| `Maximum update depth exceeded` | 渲染中触发状态更新 | 检查 effect 依赖、state 嵌套 |
| `Invalid hook call` | Hook 在非组件中调用 | 检查条件渲染中的 Hook |
| `v-if / v-for 冲突` | 模板编译错误 | 检查 Vue 模板语法 |

---

## 使用方法

### 分析最近的前端错误

```
分析前端最近的未解决错误
```

### 分析特定错误

```
分析这个 GlitchTip Issue：https://errors.example.com/org/project/issues/12345/
```

### 关联会话回放分析

```
这个错误的 OpenReplay session ID 是 abc123，帮我还原用户操作路径
```

### 从粘贴的错误信息分析

```
分析这段前端错误堆栈：

TypeError: Cannot read properties of undefined (reading 'map')
  at UserList (src/components/UserList.vue:25:18)
  at renderComponentRoot (node_modules/vue/dist/vue.runtime.esm.js:1234:5)
```

### 批量分析报告

```
输出最近 7 天所有 P0/P1 前端错误的诊断报告
```

---

## 参考资料

| 主题 | 参考 |
|------|------|
| 前端错误模式库 | [frontend-error-patterns.md](references/frontend-error-patterns.md) |
| GlitchTip API | [glitchtip-api.md](references/glitchtip-api.md) |
| OpenReplay API | [openreplay-api.md](references/openreplay-api.md) |
| Source Map 指南 | [source-map-guide.md](references/source-map-guide.md) |

## 辅助脚本

| 脚本 | 用途 |
|------|------|
| `fetch_errors.py` | 从 GlitchTip 拉取 Issues/Events |
| `fetch_sessions.py` | 从 OpenReplay 拉取会话数据 |
| `correlate.py` | 错误与会话的关联匹配 |
| `resolve_stacktrace.py` | Source Map 堆栈还原 |
| `generate_report.py` | 生成分析报告 |
