# 🚀 Claude Code Skills 方向与想法（基于已有技能延伸）

---

## 🔥 第一梯队：强烈推荐（AI 不可替代性强 + 市场需求大）

### 1. **CI/CD Failure Diagnoser** — CI 故障诊断器
> 读取 CI 日志（GitHub Actions / GitLab CI），定位失败根因，生成修复建议

- **为什么适合 AI**：CI 日志经常几千行，需要语义理解才能区分"真正的错误 vs 级联错误 vs 无关警告"
- **数据源**：GitHub Actions API、GitLab CI API、Jenkins
- **输出**：根因分析 + 最小修复 PR
- **扩展**：与 kafka-log-analyzer 思路一脉相承，从"分析日志"到"分析 CI 日志"

### 2. **Legacy Modernizer** — 遗留代码现代化
> Vue 2 → 3、Options API → Composition API、JS → TS、Webpack → Vite

- **为什么适合 AI**：迁移需要理解语义，不是简单正则替换。比如 `this.$refs` → `useTemplateRef()` 需要上下文判断
- **中国市场巨大**：大量 Vue 2 项目亟待升级
- **分场景 Skill**：可以拆成多个小 skill（vue2-to-vue3、js-to-ts、class-to-composition）
- **差异化**：不是跑 codemod，而是 AI 理解业务逻辑后做语义级迁移

### 3. **Incident Post-Mortem Generator** — 事故复盘报告生成器
> 读取多条数据源（日志 + 监控 + Git 变更 + 部署记录），自动生成 RCA 报告

- **为什么适合 AI**：需要交叉关联多源数据，综合判断因果关系，这是 AI 的核心优势
- **与现有 skill 的协同**：frontend-error-analyze + kafka-log-analyzer 的数据可供此 skill 消费
- **数据源**：Sentry/GlitchTip、Grafana、Git log、Deploy history
- **输出**：结构化 Post-Mortem（时间线 → 根因 → 影响 → 修复 → 预防措施）

---

## ⭐ 第二梯队：高价值方向

### 4. **API Contract Validator** — API 契约校验器
> 对比 OpenAPI Spec 与实际代码实现，发现 drift（遗漏字段、类型不一致、未文档化的端点）

- 微服务团队的刚需，手动对比几乎不可能
- 可以集成 Postman MCP 做契约测试

### 5. **Test Quality Analyzer** — 测试质量分析器
> 不只是覆盖率，而是分析测试是否真的能发现问题（断言有效性、边界条件覆盖、mock 合理性）

- 现有工具只看行覆盖率，AI 可以判断"这个测试到底有没有意义"
- 输出：脆弱测试标记、无效断言检测、缺失场景推荐

### 6. **i18n Health Checker** — 国际化健康检查
> 扫描硬编码字符串、遗漏翻译 key、翻译一致性、RTL 兼容性

- 对出海团队价值极高
- 需要语义理解（判断什么是应该翻译的文案，什么是代码标识符）

### 7. **Performance Regression Detector** — 性能回归检测器
> 对比分支间 Lighthouse 分数、bundle size、Core Web Vitals，关联到具体代码变更

- 类似 Changesets 但更智能，能说"这个 PR 让 LCP 变慢了 300ms，因为新增了 200KB 未懒加载的图片"

---

## 💡 第三梯队：细分机会

| 方向 | 亮点 | 目标用户 |
|------|------|----------|
| **Dependency Risk Radar** | 不只看 CVE，还评估维护者活跃度、license 风险、路人依赖 | 所有 JS 项目 |
| **DB Migration Safety** | 分析 migration 是否会导致锁表、数据丢失，生成回滚方案 | 后端团队 |
| **Accessibility (a11y) Auditor** | 不只跑 axe，而是理解设计意图，给出修复建议而非只报规则 | 前端团队 |
| **Feature Flag Analyzer** | 分析功能开关覆盖率、清理废弃 flag、评估 flag 间交互影响 | DevOps |
| **Git Archaeologist** | `git blame` 增强版，理解"这段代码为什么写成这样"而非只是"谁写的" | 全栈 |

---

## 🎯 选定方向的框架

```
你的优势 = 前端 + 可观测性 + 中国开发者社区
最大杠杆 = AI 做语义理解 vs 脚本做模式匹配
最快验证 = 能在 1-2 天内做出可以实用的 skill
```

## 排列优先级

1. 🥇 **CI/CD Failure Diagnoser** — 与现有 skill 互补性最强，需求最普遍，开发最快
2. 🥈 **Legacy Modernizer (Vue 2→3)** — 中国市场最大痛点，有 frontend-design 的基础
3. 🥉 **Incident Post-Mortem** — 长期价值最高，但需要更多数据源集成
