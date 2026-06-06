# @saqqdy/skills

Claude Code 技能集合，用于构建 AI 驱动的开发工具。

[English](README.md)

## 文档

- [DEVELOPMENT.md](DEVELOPMENT.md) - 开发说明文档（详细开发流程和最佳实践）
- [CHANGELOG.md](CHANGELOG.md) - 更新日志

## 什么是 Skills？

Skills 是 Claude Code 的专业化指令集，用于增强其在特定任务上的能力。每个 skill 是一个独立的目录，包含结构化指令的 `SKILL.md` 文件，以及可选的支持资源，如脚本、文档和测试用例。

### 为什么使用 Skills？

- **可复用性**：一次编写，跨项目使用
- **一致性**：常见任务的标准化模式
- **渐进式披露**：简单描述触发详细指令
- **可分发**：打包为 `.skill` 文件进行分享

## 项目结构

```
skills/
├── skills/              # 技能目录
│   ├── frontend-design/ # 前端设计指南
│   └── template/        # 模板技能，供参考
├── scripts/             # 技能开发工具（Python）
│   ├── package_skill.py       # 打包技能为 .skill 文件
│   ├── package_all.py         # 批量打包所有技能
│   ├── quick_validate.py      # 验证 SKILL.md 格式
│   ├── run_eval.py            # 运行触发评估
│   ├── aggregate_benchmark.py # 汇总基准测试结果
│   ├── improve_description.py # 优化技能描述
│   ├── run_loop.py            # 描述优化循环
│   ├── generate_report.py     # 生成 HTML 报告
│   └── utils.py               # 共享工具函数
├── agents/              # 测试子代理定义
│   ├── grader.md              # 评分测试输出
│   ├── comparator.md          # 盲比较两个输出
│   └── analyzer.md            # 分析基准测试结果
├── assets/              # 共享资源
│   └── eval_review.html       # 评估审查界面模板
├── references/          # 共享文档
│   └── schemas.md             # JSON 模式定义
├── eval-viewer/         # 评估查看工具
│   ├── generate_review.py     # 完整评估查看器（471行）
│   └── viewer.html            # 独立 HTML 查看器（43.9K）
├── package.json
├── pnpm-workspace.yaml
├── tsconfig.json
├── eslint.config.mjs
└── vitest.config.ts
```

## 快速开始

### 环境要求

- Node.js 18+
- pnpm 9+
- Python 3.11+（用于工具脚本）

### 安装

```bash
# 克隆仓库
git clone https://github.com/saqqdy/skills.git
cd skills

# 安装依赖
pnpm install

# 设置 Python 虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows 上: .venv\Scripts\activate
pip install pyyaml
```

### 创建新技能

1. **复制模板**：
   ```bash
   cp -r skills/template skills/my-skill
   ```

2. **编辑 SKILL.md**，填写技能配置：
   ```yaml
   ---
   name: my-skill
   description: 何时触发此技能以及它的功能。
   metadata:
     author: your-name
     version: "2026.01.01"
   ---
   ```

3. **添加指令**：在 SKILL.md 正文部分编写

4. **验证**技能：
   ```bash
   source .venv/bin/activate
   python scripts/quick_validate.py skills/my-skill
   ```

5. **打包**技能：
   ```bash
   python scripts/package_skill.py skills/my-skill
   ```

## 技能结构

每个技能遵循以下结构：

```
skill-name/
├── SKILL.md             # 必需：主要技能定义
│   ├── YAML frontmatter (name, description, metadata)
│   └── Markdown 指令
├── references/          # 可选：附加文档
│   └── *.md
├── scripts/             # 可选：辅助脚本
│   ├── *.py
│   ├── *.sh
│   └── *.js
├── assets/              # 可选：静态资源
│   └── 模板、图标、字体等
├── agents/              # 可选：子代理定义
│   └── *.md
├── evals/               # 可选：测试用例
│   ├── evals.json
│   └── files/
└── LICENSE.md           # 可选：技能特定许可证
```

### SKILL.md 格式

```markdown
---
name: skill-name
description: 何时触发此技能以及它的功能。保持在 1024 字符以内。
metadata:
  author: your-name
  version: "2026.01.01"
  compatibility: 可选的兼容性说明
---

# 技能标题

简要说明此技能的功能。

## 使用方法

如何使用此技能...

## 示例

使用场景示例...

## 参考资料

| 主题 | 参考 |
|-------|-----------|
| 详情 | [file.md](references/file.md) |
```

### Frontmatter 字段

| 字段 | 必需 | 说明 |
|-------|----------|-------------|
| `name` | 是 | 唯一技能标识符（kebab-case，最多 64 字符） |
| `description` | 是 | 何时触发、功能说明（最多 1024 字符） |
| `metadata.author` | 否 | 技能作者 |
| `metadata.version` | 否 | 技能版本 |
| `metadata.compatibility` | 否 | 兼容性说明 |

### 编写优质描述

描述对于触发至关重要。遵循以下指南：

1. **说明何时使用**："当...时使用此技能"
2. **聚焦用户意图**：用户想要达成什么
3. **独特性**：与其他技能区分开来
4. **保持在 1024 字符以内**

描述示例：

```
用于 PDF 表单填写和数据提取。处理可填写 PDF，提取字段数据，支持多页文档。当用户提到 PDF、表单或表单字段时触发。

从电子表格和 CSV 文件提取数据。支持 Excel、Google Sheets、CSV 格式。当用户提到电子表格、Excel、CSV 或表格数据时使用。

Vue.js 组件开发和最佳实践。创建 Vue 组件、设置 Vue 项目或讨论 Vue 模式时使用。
```

## Python 工具脚本详解

### 1. quick_validate.py - 验证技能格式

验证 SKILL.md 文件的格式和结构是否正确。

**用法**：
```bash
# 验证单个技能
python scripts/quick_validate.py skills/my-skill

# 验证所有技能
python scripts/quick_validate.py skills/
```

**检查内容**：
- SKILL.md 文件是否存在
- YAML frontmatter 格式是否有效
- 必需字段（name, description）是否存在
- 名称是否遵循 kebab-case 命名规范
- 描述是否在 1024 字符以内

**输出示例**：
```
✅ my-skill: Skill is valid!
❌ bad-skill: Missing 'description' in frontmatter
```

### 2. package_skill.py - 打包技能

将技能目录打包为可分发的 `.skill` 文件（zip 格式）。

**用法**：
```bash
# 打包单个技能
python scripts/package_skill.py skills/my-skill

# 指定输出目录
python scripts/package_skill.py skills/my-skill ./dist
```

**功能**：
- 自动验证技能格式
- 排除不必要的文件（node_modules, __pycache__, .DS_Store）
- 排除 evals 目录（测试数据不打包）
- 创建 `.skill` 文件

**输出示例**：
```
📦 Packaging skill: skills/my-skill
🔍 Validating skill...
✅ Skill is valid!
  Added: my-skill/SKILL.md
  Added: my-skill/references/guide.md
✅ Successfully packaged skill to: /path/to/my-skill.skill
```

### 3. package_all.py - 批量打包技能

批量打包 `skills/` 目录下的所有技能。

**用法**：
```bash
# 打包所有技能到 dist 目录
python scripts/package_all.py

# 指定输出目录
python scripts/package_all.py --output ./release
```

**输出示例**：
```
📦 Found 5 skill(s) to package
==================================================
📦 Packaging skill: skills/vue
✅ Successfully packaged skill to: ./dist/vue.skill
...
📊 Summary: 5/5 skills packaged successfully
```

### 4. run_eval.py - 运行触发评估

测试技能描述是否能正确触发 Claude 使用该技能。

**用法**：
```bash
python scripts/run_eval.py \
  --eval-set evals/trigger_eval.json \
  --skill-path skills/my-skill
```

**参数**：
| 参数 | 说明 |
|------|------|
| `--eval-set` | 评估用例 JSON 文件路径 |
| `--skill-path` | 技能目录路径 |
| `--description` | 覆盖测试的描述文本 |
| `--num-workers` | 并行工作进程数（默认 10） |
| `--timeout` | 每个查询超时时间（默认 30 秒） |
| `--runs-per-query` | 每个查询运行次数（默认 3） |
| `--trigger-threshold` | 触发率阈值（默认 0.5） |
| `--model` | 使用的模型 ID |

**工作原理**：
1. 创建临时命令文件让技能出现在 available_skills
2. 运行 `claude -p` 执行查询
3. 监控流式输出检测技能是否被触发
4. 返回 JSON 格式的评估结果

**输出示例**：
```json
{
  "skill_name": "my-skill",
  "description": "Skill description...",
  "results": [
    {
      "query": "How do I create a Vue component?",
      "should_trigger": true,
      "trigger_rate": 1.0,
      "triggers": 3,
      "runs": 3,
      "pass": true
    }
  ],
  "summary": {
    "total": 5,
    "passed": 4,
    "failed": 1
  }
}
```

### 5. aggregate_benchmark.py - 汇总基准测试结果

从多个运行目录汇总基准测试结果，计算统计数据。

**用法**：
```bash
python scripts/aggregate_benchmark.py ./workspace/iteration-1 \
  --skill-name my-skill
```

**功能**：
- 读取所有 `grading.json` 文件
- 计算通过率、时间、token 的统计数据
- 生成 `benchmark.json` 和 `benchmark.md`

**输出示例**：
```
Generated: ./workspace/iteration-1/benchmark.json
Generated: ./workspace/iteration-1/benchmark.md

Summary:
  With skill: 85.0% pass rate
  Without skill: 35.0% pass rate
  Delta:         +0.50
```

### 6. improve_description.py - 优化技能描述

基于评估结果自动优化技能描述。

**用法**：
```bash
python scripts/improve_description.py \
  --eval-results results.json \
  --skill-path skills/my-skill \
  --model claude-sonnet-4-20250514
```

**功能**：
- 分析触发失败的查询
- 调用 Claude 生成改进的描述
- 避免重复之前的失败尝试
- 保持描述在 1024 字符以内

### 7. run_loop.py - 描述优化循环

自动运行多轮评估和优化循环，找到最佳描述。

**用法**：
```bash
python scripts/run_loop.py \
  --eval-set evals/trigger_eval.json \
  --skill-path skills/my-skill \
  --model claude-sonnet-4-20250514 \
  --max-iterations 5
```

**参数**：
| 参数 | 说明 |
|------|------|
| `--eval-set` | 评估用例 JSON 文件 |
| `--skill-path` | 技能目录路径 |
| `--max-iterations` | 最大迭代次数（默认 5） |
| `--holdout` | 测试集比例（默认 0.4） |
| `--runs-per-query` | 每个查询运行次数 |

**工作流程**：
1. 将评估集分为训练集和测试集
2. 评估当前描述
3. 分析失败案例
4. 生成改进描述
5. 重复直到全部通过或达到最大迭代次数
6. 返回测试集上表现最好的描述

**输出示例**：
```json
{
  "exit_reason": "all_passed (iteration 3)",
  "original_description": "Old description...",
  "best_description": "Improved description...",
  "best_score": "18/20",
  "iterations_run": 3
}
```

### 8. generate_report.py - 生成 HTML 报告

生成优化过程的 HTML 可视化报告。

**用法**：
```bash
python scripts/generate_report.py \
  --eval-set evals/trigger_eval.json \
  --skill-path skills/my-skill
```

### 9. utils.py - 共享工具函数

提供其他脚本使用的共享工具函数。

**主要函数**：
```python
from scripts.utils import parse_skill_md, get_skill_metadata, find_skill_dirs

# 解析 SKILL.md 文件
name, description, content = parse_skill_md(skill_path)

# 获取技能元数据
metadata = get_skill_metadata(skill_path)

# 查找所有技能目录
skill_dirs = find_skill_dirs(base_path)
```

## eval-viewer 评估查看器

### generate_review.py - 完整评估查看器

启动交互式 Web 服务器查看评估结果。

**用法**：
```bash
# 启动服务器并打开浏览器
python eval-viewer/generate_review.py ./workspace/iteration-1 \
  --skill-name my-skill

# 生成静态 HTML 文件
python eval-viewer/generate_review.py ./workspace/iteration-1 \
  --skill-name my-skill \
  --static ./report.html
```

**功能**：
- 自动发现所有运行目录
- 嵌入输出文件（文本、图片、PDF）
- 显示评分结果
- 收集用户反馈
- 支持查看上一轮结果对比

### viewer.html - 独立 HTML 查看器

一个完整的单文件 HTML 查看器，无需服务器即可使用。

**特性**：
- 响应式设计
- 输出内容渲染（代码高亮、图片预览）
- 评分结果展示
- 反馈表单
- 键盘导航支持

## Agents 子代理

### grader.md - 评分代理

评估测试输出是否符合预期。

**输入**：
- `expectations`: 预期结果列表
- `transcript_path`: 执行日志路径
- `outputs_dir`: 输出文件目录

**输出**：
```json
{
  "expectations": [
    {
      "text": "输出包含 X",
      "passed": true,
      "evidence": "在输出第 3 行找到..."
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  }
}
```

### comparator.md - 比较代理

盲比较两个输出，判断哪个更好。

**输入**：
- `output_a_path`: 输出 A 路径
- `output_b_path`: 输出 B 路径
- `eval_prompt`: 原始任务

**输出**：
```json
{
  "winner": "A",
  "reasoning": "输出 A 更完整...",
  "rubric": {
    "A": {"overall_score": 9.0},
    "B": {"overall_score": 5.4}
  }
}
```

### analyzer.md - 分析代理

分析基准测试结果，找出模式和问题。

**输出**：
```json
{
  "winner_strengths": ["指令清晰", "包含验证脚本"],
  "loser_weaknesses": ["指令模糊", "缺少错误处理"],
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "添加明确的步骤说明"
    }
  ]
}
```

## JSON 数据格式

### evals.json - 评估用例定义

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "用户的测试提示",
      "expected_output": "预期结果描述",
      "files": ["evals/files/input.pdf"],
      "expectations": [
        "输出包含 X",
        "使用了脚本 Y"
      ]
    }
  ]
}
```

### grading.json - 评分结果

```json
{
  "expectations": [
    {
      "text": "预期描述",
      "passed": true,
      "evidence": "证据引用"
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "timing": {
    "total_duration_seconds": 23.5
  }
}
```

### benchmark.json - 基准测试汇总

```json
{
  "metadata": {
    "skill_name": "my-skill",
    "timestamp": "2026-06-06T12:00:00Z"
  },
  "runs": [...],
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08}
    },
    "delta": {
      "pass_rate": "+0.50"
    }
  }
}
```

完整 JSON 模式请参考 [references/schemas.md](references/schemas.md)。

## 开发

### 代码风格

```bash
pnpm lint --fix
```

使用 `@eslint-sets/eslint-config`，支持 TypeScript 和 Python。

### 测试

```bash
pnpm test
```

使用 Vitest 运行测试。

### Git Hooks

Pre-commit hooks 通过 `simple-git-hooks` 和 `lint-staged` 自动运行代码检查。

## 发布

技能可以作为 npm 包发布，或作为 `.skill` 文件分发。

### npm 包发布

```bash
pnpm package
pnpm publish
```

### .skill 文件分发

```bash
python scripts/package_skill.py skills/my-skill ./dist
```

分发 `.skill` 文件供手动安装。

## 最佳实践

### 保持 SKILL.md 在 500 行以内

将详细内容移至 `references/` 目录，确保技能高效加载。

### 使用渐进式披露

1. **元数据**（名称 + 描述）- 始终可见
2. **SKILL.md 正文** - 触发时加载
3. **参考资料** - 按需加载

### 添加测试用例

创建 `evals/evals.json` 验证技能行为：

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "用户的测试提示",
      "expected_output": "预期结果",
      "expectations": [
        "输出包含 X",
        "使用了脚本 Y"
      ]
    }
  ]
}
```

### 包含辅助脚本

将可复用脚本放在 `scripts/` 目录：

```python
#!/usr/bin/env python3
# scripts/helper.py

def main():
    print("辅助脚本运行中...")

if __name__ == "__main__":
    main()
```

在 SKILL.md 中引用：

```markdown
使用辅助脚本：

\`\`\`bash
python scripts/helper.py --input data.json
\`\`\`
```

## 许可证

Apache License 2.0 © 2026 saqqdy