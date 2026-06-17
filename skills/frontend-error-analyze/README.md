# Frontend Error Analyze 使用指南

基于 **GlitchTip + OpenReplay** 监控平台的前端错误分析 Claude Code Skill，交叉关联错误堆栈、用户操作路径与源码仓库，快速定位并修复前端线上问题。

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **三源交叉关联** | GlitchTip（错误追踪）× OpenReplay（会话回放）× 源码仓库，从 WHAT → WHY → HOW 闭环 |
| **自动分级排序** | P0 ~ P3 四级优先级，基于用户数和错误频率自动判定 |
| **7 类错误分类** | js_runtime / network / resource / framework / memory / third_party / promise，每类专属分析策略 |
| **用户路径还原** | 从 OpenReplay 事件流提取点击、网络请求、异常时间线，精确还原出错前 30s 操作 |
| **堆栈 Source Map 还原** | 内置纯 Python VLQ 解析器，零依赖还原压缩代码到源码行 |
| **智能诊断修复** | Claude 直接读取仓库代码，给出带 diff 的修复方案而非泛泛建议 |
| **批量分析报告** | 一键分析所有未解决错误，输出优先级分布 + 共性模式 + 系统建议的 Markdown 报告 |

---

## 工作原理

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   GlitchTip   │     │  OpenReplay   │     │   源码仓库     │
│   WHAT 出错   │────→│   WHY 出错    │────→│  HOW 修复     │
│               │     │               │     │               │
│ • 错误堆栈    │     │ • 用户操作路径 │     │ • 读取源码    │
│ • 频率/用户数 │     │ • 网络请求    │     │ • 理解上下文  │
│ • 版本/环境   │     │ • DOM 变更    │     │ • 生成修复    │
│ • Tags        │     │ • 控制台日志  │     │ • 可直接修改  │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │
        │  openreplay_session_id tag
        └─────────────────────┘
```

**关键关联点**：前端 SDK 初始化时，将 OpenReplay session ID 注入 GlitchTip tag，实现 Event → Session 的精确匹配。

---

## 快速开始

### 1. 配置环境变量

```bash
# GlitchTip
export GLITCHTIP_URL="https://errors.example.com"
export GLITCHTIP_TOKEN="glitchtip-api-xxx"
export ORG_SLUG="my-team"
export PROJECT_SLUG="web-app"

# OpenReplay
export OPENREPLAY_URL="https://replay.example.com"
export OPENREPLAY_TOKEN="or-xxx"
```

### 2. 前端 SDK 关联（推荐）

确保 GlitchTip 与 OpenReplay 已关联，在项目入口文件中：

```javascript
import * as Sentry from '@sentry/browser';
import Tracker from '@openreplay/tracker';

const tracker = new Tracker({ projectKey: 'xxx' });
tracker.start();

// 关键：注入 OpenReplay session ID 到 GlitchTip
Sentry.setTag('openreplay_session_id', tracker.getSessionID());
```

或使用 OpenReplay 官方 Sentry 插件自动关联：

```javascript
import Tracker from '@openreplay/tracker';
import trackerAssist from '@openreplay/tracker-assist';

const tracker = new Tracker({ projectKey: 'xxx' });
const trackerSentry = tracker.use(trackerAssist());
tracker.start();

Sentry.init({
  dsn: 'https://xxx@errors.example.com/1',
  integrations: [trackerSentry.sentryIntegration()],
});
```

---

## 使用方法

### 分析最近的错误

```
分析前端最近的未解决错误
```

Claude 会自动拉取 GlitchTip Issues，按频率排序，分级分类后逐个输出诊断。

### 分析特定 Issue

```
分析这个 GlitchTip Issue：https://errors.example.com/org/project/issues/12345/
```

### 关联会话回放

```
这个错误的 OpenReplay session ID 是 abc123，帮我还原用户操作路径
```

输出示例：

```
时间线：
  10:23:01  📄 页面加载 /dashboard
  10:23:03  👆 点击 "导出报表" 按钮
  10:23:04  🌐 POST /api/reports/export → 502 (30s)
  10:23:05  ⚡ TypeError: Cannot read 'url' of undefined

根因：导出接口返回 502 时 response.data 为 null，
代码直接访问 response.data.url 缺少空值校验。
```

### 粘贴堆栈直接分析

```
分析这段前端错误堆栈：

TypeError: Cannot read properties of undefined (reading 'map')
  at UserList (src/components/UserList.vue:25:18)
  at renderComponentRoot (node_modules/vue/dist/vue.runtime.esm.js:1234:5)
```

Claude 会直接读取 `src/components/UserList.vue` 第 25 行附近的代码，给出具体修复。

### 批量分析报告

```
输出最近 7 天所有 P0/P1 前端错误的诊断报告
```

生成包含优先级分布、错误详情、共性模式和系统建议的完整 Markdown 报告。

---

## 辅助脚本

### fetch_errors.py — 拉取 GlitchTip 错误

```bash
# 拉取最近 24h 未解决的 Issues（自动分类+分级）
python scripts/fetch_errors.py --issues

# 指定时间范围
python scripts/fetch_errors.py --issues --period 7d

# 拉取某 Issue 的最新 Event（含完整堆栈+面包屑）
python scripts/fetch_errors.py --events --issue-id 12345 --full

# 输出到文件
python scripts/fetch_errors.py --issues -o errors.json
```

### fetch_sessions.py — 拉取 OpenReplay 会话

```bash
# 拉取用户的最近 5 个会话
python scripts/fetch_sessions.py --list --user-id user-123 --limit 5

# 获取会话详情
python scripts/fetch_sessions.py --detail --session-id abc123

# 获取会话事件流
python scripts/fetch_sessions.py --events --session-id abc123

# 提取用户操作路径（错误前后 30s）
python scripts/fetch_sessions.py --journey --session-id abc123

# 按错误类型搜索会话
python scripts/fetch_sessions.py --by-error "TypeError:Cannot-read"
```

### correlate.py — 错误与会话关联

```bash
# 通过 tag 关联（推荐，精确匹配）
python scripts/correlate.py --from-tag --issue-id 12345

# 通过时间窗口+用户匹配（无 tag 时的降级方案）
python scripts/correlate.py --by-time --issue-id 12345

# 批量关联所有未解决 Issues
python scripts/correlate.py --batch --period 24h
```

### resolve_stacktrace.py — Source Map 堆栈还原

```bash
# 单帧还原
python scripts/resolve_stacktrace.py \
  --sourcemap ./dist/assets/main.abc123.js.map \
  --line 1 --column 23456

# 批量还原（传入 Event JSON）
python scripts/resolve_stacktrace.py \
  --sourcemap-dir ./dist/assets \
  --stacktrace-file ./event.json

# 只输出应用代码帧（过滤 node_modules）
python scripts/resolve_stacktrace.py \
  --sourcemap-dir ./dist/assets \
  --stacktrace-file ./event.json --app-only

# 文本格式输出
python scripts/resolve_stacktrace.py \
  --sourcemap-dir ./dist/assets \
  --stacktrace-file ./event.json --format text
```

还原示例：

```
还原前：
  at n (main.abc123.js:1:23456)
  at o (main.abc123.js:1:12345)

还原后：
  → at renderUserList (src/components/UserList.vue:25:18)
    at processOrder (src/utils/orderProcessor.ts:142:12)
```

### generate_report.py — 生成分析报告

```bash
# 从分别的 JSON 文件生成报告
python scripts/generate_report.py \
  --errors errors.json \
  --sessions sessions.json \
  --correlations correlations.json

# 从目录批量读取
python scripts/generate_report.py --input-dir ./analysis_output

# JSON 格式输出
python scripts/generate_report.py --input-dir ./analysis_output --format json
```

---

## 支持的错误分类

| 类别 | 典型错误 | 诊断策略 |
|------|----------|----------|
| `js_runtime` | TypeError, ReferenceError, RangeError | 追溯变量赋值链，定位空值/未定义根因 |
| `network` | NetworkError, CORS, 502/503/504 | 检查接口状态、超时配置、跨域头 |
| `resource` | ChunkLoadError, CSS/JS 加载失败 | 排查部署版本、CDN 缓存、路由错误边界 |
| `framework` | Hydration mismatch, Max update depth | 检查 SSR/CSR 数据一致性、渲染循环 |
| `memory` | Out of memory, 页面卡死 | 排查事件监听泄漏、定时器未清理、闭包引用 |
| `third_party` | SDK 报错、广告脚本崩溃 | try-catch 隔离、iframe 沙箱化 |
| `promise` | UnhandledRejection | 补充 catch / try-catch，使用 allSettled |

---

## 优先级分级

| 优先级 | 条件 | 行动 |
|--------|------|------|
| 🔴 **P0** | 用户数 > 100 且 24h 内持续发生 | 立即分析修复 |
| 🟠 **P1** | 用户数 > 10 或错误率 > 1% | 当天处理 |
| 🟡 **P2** | 频率低但影响关键流程 | 排入迭代 |
| ⚪ **P3** | 降级错误、第三方脚本 | 观察或忽略 |

---

## 诊断输出格式

每个错误输出结构化诊断报告：

```markdown
## 🔴 P0 | TypeError: Cannot read 'url' of undefined

**影响范围**：24h 内 342 位用户，错误率 2.3%
**文件**：`src/components/ReportExport.vue:42`
**触发路径**：仪表盘 → 导出报表 → 接口 502 → 未处理空值

### 根因分析
导出接口返回 502 时，`response.data` 为 null，
代码直接访问 `response.data.url`，缺少空值校验。

### 修复方案
​```diff
- const downloadUrl = response.data.url
+ const downloadUrl = response.data?.url
  if (!downloadUrl) {
    message.error('导出失败，请稍后重试')
    return
  }
​```

### 防御加固
1. 在 `fetchExportReport` 中对 5xx 响应统一处理
2. 添加 `response.data` 类型校验（zod / TypeScript guard）
```

---

## 典型使用场景

### 场景 1：线上告警快速响应

收到告警 → 告诉 Claude "分析前端最近的 P0 错误" → 一分钟内拿到根因和修复方案 → 直接让 Claude 改代码 → 提交 PR。

### 场景 2：版本发布后回归验证

```
分析 release:v2.3.1 新增的前端错误
```

Claude 使用 `firstRelease:v2.3.1` 搜索新增 Issues，确认是否有回归。

### 场景 3：排查难以复现的 Bug

用户反馈偶发崩溃 → 在 GlitchTip 找到对应 Issue → 拿到 `openreplay_session_id` → 让 Claude 还原用户操作路径 → 发现特定浏览器 + 特定操作组合触发了边界条件。

### 场景 4：周度质量回顾

```
输出最近 7 天所有未解决错误的诊断报告
```

生成分级报告，团队过 Review 时直接确定下个迭代的修复计划。

---

## 参考文档

| 文档 | 内容 |
|------|------|
| [frontend-error-patterns.md](references/frontend-error-patterns.md) | 前端错误模式库：JS 运行时 / 网络 / 资源 / 框架 / 内存泄漏 / 第三方脚本 |
| [glitchtip-api.md](references/glitchtip-api.md) | GlitchTip API 参考：Issues / Events / Releases / 搜索语法 |
| [openreplay-api.md](references/openreplay-api.md) | OpenReplay API 参考：Sessions / Events / 用户旅程提取 |
| [source-map-guide.md](references/source-map-guide.md) | Source Map 还原指南：原理 / 方法 / 部署安全 |

---

## 文件结构

```
frontend-error-analyze/
├── SKILL.md                              # 主指令文件（4 阶段分析流水线）
├── README.md                             # 本文档
├── references/
│   ├── frontend-error-patterns.md        # 前端错误模式库
│   ├── glitchtip-api.md                  # GlitchTip API 参考
│   ├── openreplay-api.md                 # OpenReplay API 参考
│   └── source-map-guide.md               # Source Map 还原指南
├── scripts/
│   ├── fetch_errors.py                   # GlitchTip Issues/Events 拉取
│   ├── fetch_sessions.py                 # OpenReplay 会话拉取
│   ├── correlate.py                      # 错误↔会话关联
│   ├── resolve_stacktrace.py             # Source Map 堆栈还原
│   └── generate_report.py               # 分析报告生成
└── evals/
    └── evals.json                        # 7 个测试用例
```

---

## 与 kafka-log-analyze 的对比

| 维度 | kafka-log-analyzer | frontend-error-analyze |
|------|-------------------|------------------------|
| 数据源 | 文本日志文件 | 结构化 REST API |
| 关联能力 | 单一数据源 | 错误 + 会话 + 源码三源交叉 |
| 修复能力 | 提供 Kafka 配置建议 | 直接读写源码，生成 diff |
| 时效性 | 离线分析 | 支持 1h 内近实时 |
| 专家知识 | Kafka Producer/Consumer/Broker | 前端错误模式 + 用户行为分析 |
| 适用场景 | 后端 Kafka 中间件日志 | 前端线上错误全流程排查 |

---

## 环境变量一览

| 变量 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `GLITCHTIP_URL` | ✅ | GlitchTip 实例地址 | `https://errors.example.com` |
| `GLITCHTIP_TOKEN` | ✅ | GlitchTip API Token | `glitchtip-api-xxx` |
| `ORG_SLUG` | ✅ | 组织标识 | `my-team` |
| `PROJECT_SLUG` | ✅ | 项目标识 | `web-app` |
| `OPENREPLAY_URL` | ✅ | OpenReplay 实例地址 | `https://replay.example.com` |
| `OPENREPLAY_TOKEN` | ✅ | OpenReplay API Token | `or-xxx` |

---

## 许可证

Apache License 2.0 © 2026 saqqdy
