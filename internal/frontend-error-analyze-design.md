# 前端错误分析 Skill 设计文档

## 一、背景

前端基于 GlitchTip（错误追踪）+ OpenReplay（会话回放）组合搭建了监控平台，需要一个 Claude Code Skill 来：
- 自动获取和分析前端错误
- 交叉关联错误堆栈、用户操作路径与源码
- 快速定位问题甚至解决问题

## 二、核心架构：三源交叉

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

| 数据源 | 说明 | 价值 |
|--------|------|------|
| **GlitchTip** | Sentry 兼容 API，错误追踪 | WHAT - 什么错误、频率、影响范围 |
| **OpenReplay** | 会话回放，用户行为追踪 | WHY - 用户做了什么触发了这个错误 |
| **源码仓库** | Claude 可直接读取的项目代码 | HOW - 怎么修改代码修复问题 |

## 三、Skill 设计

### 3.1 目录结构

```
skills/frontend-error-analyze/
├── SKILL.md                          # 主指令文件
├── references/
│   ├── frontend-error-patterns.md    # 前端错误模式库
│   ├── glitchtip-api.md              # GlitchTip API 参考
│   ├── openreplay-api.md             # OpenReplay API 参考
│   └── source-map-guide.md           # Source Map 还原指南
├── scripts/
│   ├── fetch_errors.py               # 从 GlitchTip 拉取 Issues/Events
│   ├── fetch_sessions.py             # 从 OpenReplay 拉取会话
│   ├── correlate.py                  # 错误与会的关联匹配
│   ├── resolve_stacktrace.py         # Source Map 堆栈还原
│   └── generate_report.py           # 生成分析报告
└── evals/
    └── evals.json                    # 测试用例（7个）
```

### 3.2 分析流水线

```
阶段 1: 获取错误   → GlitchTip API 拉 Issues，自动分类 (js_runtime/network/resource/framework/memory/promise/third_party)
阶段 2: 交叉关联   → 通过 tag 或时间+用户匹配 OpenReplay 会话
阶段 3: 堆栈还原   → Source Map 映射到源码行
阶段 4: 诊断修复   → 读取源码上下文 + 用户操作路径 → 生成修复方案
```

### 3.3 关联机制

| 方式 | 精度 | 说明 |
|------|------|------|
| **Tag 注入**（推荐） | 高 | SDK 初始化时 `Sentry.setTag('openreplay_session_id', tracker.getSessionID())` |
| **时间+用户匹配** | 中 | `timestamp ± 30s` + `userId` + `URL` |
| **OpenReplay Sentry 插件** | 高 | `tracker.use(trackerAssist())` + `trackerSentry.sentryIntegration()` |

### 3.4 错误分级

| 优先级 | 条件 | 动作 |
|--------|------|------|
| P0 | 用户数 > 100 且持续发生 | 立即修复 |
| P1 | 用户数 > 10 或错误率 > 1% | 当天处理 |
| P2 | 频率低但影响关键流程 | 排入迭代 |
| P3 | 降级错误、第三方脚本 | 观察或忽略 |

### 3.5 错误分类

| 类别 | 典型错误 | 分析策略 |
|------|----------|----------|
| `js_runtime` | TypeError, ReferenceError | 定位空值/未定义根因 |
| `network` | NetworkError, CORS, 502/503/504 | 接口状态、超时、跨域配置 |
| `resource` | ChunkLoadError, CSS/JS加载失败 | 部署版本、CDN、缓存策略 |
| `framework` | Hydration mismatch, Max update depth | SSR/CSR 一致性、渲染循环 |
| `memory` | Out of memory, 页面卡死 | 内存泄漏、事件监听、闭包 |
| `third_party` | SDK 报错、广告/分析脚本 | try-catch 隔离、沙箱化 |
| `promise` | UnhandledRejection | 异步错误处理遗漏 |

## 四、辅助脚本

| 脚本 | 输入 | 输出 | 环境变量 |
|------|------|------|----------|
| `fetch_errors.py` | `--issues` / `--events --issue-id` | JSON | `GLITCHTIP_URL`, `GLITCHTIP_TOKEN`, `ORG_SLUG`, `PROJECT_SLUG` |
| `fetch_sessions.py` | `--list --user-id` / `--events --session-id` / `--journey` | JSON | `OPENREPLAY_URL`, `OPENREPLAY_TOKEN` |
| `correlate.py` | `--from-tag --issue-id` / `--batch` | JSON | 以上全部 |
| `resolve_stacktrace.py` | `--sourcemap` / `--sourcemap-dir --stacktrace-file` | JSON/Text | 无 |
| `generate_report.py` | `--errors` + `--sessions` + `--correlations` | Markdown/JSON | 无 |

## 五、与 kafka-log-analyzer 的差异

| 维度 | kafka-log-analyzer | frontend-error-analyze |
|------|-------------------|------------------------|
| 数据源 | 文本日志文件 | 结构化 API |
| 关联能力 | 单一数据源 | 错误 + 会话 + 源码三源关联 |
| 修复能力 | 给配置建议 | 直接改代码 |
| 时效性 | 离线分析 | 可近实时 |
| 关键价值 | Kafka 专业知识 | 用户行为 + 代码上下文 + 修复 |

## 六、评估用例

7 个测试用例覆盖：
1. JS 运行时错误分析（单堆栈）
2. 面包屑路径还原
3. OpenReplay 会话回放关联
4. 资源加载错误（ChunkLoadError）
5. CORS 跨域错误
6. Vue 框架特定错误
7. 批量错误分级排序

## 七、后续演进

1. **Phase 1**（当前）：SKILL.md + 参考文档 + Python 脚本
2. **Phase 2**：添加更多评估用例，迭代优化诊断准确性
3. **Phase 3**：封装为 MCP Server，提供原生工具调用体验
4. **Phase 4**：集成自动修复 + PR 创建能力

---

**创建时间**: 2026-06-17
**作者**: saqqdy
