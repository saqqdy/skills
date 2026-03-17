# Agent Skills 开发指南

> 本文档介绍 Agent Skills 的工作原理、开发方法、发布流程和使用方式。

---

## 目录

1. [什么是 Agent Skills](#什么是-agent-skills)
2. [工作原理](#工作原理)
3. [Skill 结构](#skill-结构)
4. [开发流程](#开发流程)
5. [发布与分享](#发布与分享)
6. [使用方法](#使用方法)
7. [最佳实践](#最佳实践)

---

## 什么是 Agent Skills

**Agent Skills** 是一种模块化、自包含的能力扩展包，用于为 AI Agent（如 Codex、Claude Code 等）提供特定领域的专业知识、工作流程和工具。

可以把 Skills 理解为 AI 的"专业培训手册"——它们将通用 AI 转变为具备特定领域专业能力的专用 Agent。

### Skills 能做什么

| 能力类型 | 说明 | 示例 |
|---------|------|------|
| **专业工作流** | 特定领域的多步骤操作流程 | PDF 处理、代码审查、部署流程 |
| **工具集成** | 与特定文件格式或 API 的交互 | GitHub API、数据库查询、文档处理 |
| **领域知识** | 公司/项目特定的知识、schema、业务逻辑 | 内部 API 规范、数据库结构 |
| **资源 bundle** | 脚本、模板、参考资料 | Python 脚本、HTML 模板、配置示例 |

---

## 工作原理

### 三层渐进式加载系统

Skills 使用三层加载系统来高效管理上下文：

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: 元数据 (Metadata)                              │
│  - name + description                                    │
│  - 始终保持在上下文中 (~100 词)                           │
│  - 用于决定何时触发 Skill                                │
├─────────────────────────────────────────────────────────┤
│  Layer 2: SKILL.md 主体                                  │
│  - 触发后加载 (<5000 词)                                 │
│  - 包含使用说明和工作流程                                │
├─────────────────────────────────────────────────────────┤
│  Layer 3: 捆绑资源 (Bundled Resources)                   │
│  - 按需加载 (无限制)                                     │
│  - scripts/、references/、assets/                        │
│  - 脚本可直接执行，无需读入上下文                         │
└─────────────────────────────────────────────────────────┘
```

### 触发机制

当用户输入匹配 Skill 的 `description` 时，该 Skill 被触发：

```yaml
# SKILL.md 中的 frontmatter
---
name: pdf-processor
description: |
  PDF 文档处理工具，支持文本提取、页面旋转、合并拆分。
  当用户提到以下场景时触发：
  - "处理 PDF"、"提取 PDF 文本"
  - "旋转 PDF 页面"、"合并 PDF"
  - "PDF 转图片" 等
---
```

**关键点**：`description` 必须包含清晰的触发条件，因为 AI 只通过 description 来决定是否使用该 Skill。

---

## Skill 结构

一个标准的 Skill 目录结构：

```
my-skill/
├── SKILL.md              # 必需：核心说明文档
├── _meta.json            # 可选：发布元数据
├── metadata.json         # 可选：额外元数据
├── CHANGELOG.md          # 可选：版本历史
├── scripts/              # 可选：可执行脚本
│   ├── process.py
│   └── helper.sh
├── references/           # 可选：参考文档
│   ├── api-docs.md
│   └── examples.md
└── assets/               # 可选：资源文件
    ├── template.html
    └── logo.png
```

### SKILL.md 详解

SKILL.md 是唯一必需的文件，包含两部分：

#### 1. YAML Frontmatter（必需）

```yaml
---
name: skill-name                    # Skill 标识名（小写、连字符分隔）
description: |
  详细描述 Skill 的功能和触发条件。
  这是最重要的部分，决定 AI 何时使用该 Skill。
  应包含：
  1. Skill 能做什么
  2. 具体的触发场景和关键词
  3. 使用示例
metadata:                           # 可选：额外元数据
  openclaw:
    emoji: "🔧"                    # 图标
    always: true                   # 是否始终加载
---
```

#### 2. Markdown 主体（必需）

```markdown
# Skill 名称

## 何时使用此 Skill

明确说明触发条件和典型使用场景。

## 快速开始

提供最简单的使用示例。

## 详细功能

### 功能 A
详细说明...

### 功能 B
详细说明...

## 高级用法

- **场景 X**: 参见 [references/advanced.md](references/advanced.md)
- **场景 Y**: 参见 [references/examples.md](references/examples.md)

## 注意事项

- 重要提示 1
- 常见陷阱 2
```

### 资源目录说明

#### scripts/

存放可执行脚本（Python、Bash、Node.js 等）：

```python
# scripts/rotate_pdf.py
import sys
from pypdf import PdfReader, PdfWriter

def rotate_pdf(input_path, output_path, angle=90):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)
    
    with open(output_path, 'wb') as f:
        writer.write(f)

if __name__ == '__main__':
    rotate_pdf(sys.argv[1], sys.argv[2], int(sys.argv[3]))
```

**何时使用**：
- 相同代码被反复重写
- 需要确定性可靠性
- 复杂逻辑不适合放在文档中

#### references/

存放参考资料和详细文档：

```markdown
# references/api-schema.md

## 用户表结构

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | UUID | 主键 |
| name | VARCHAR(100) | 用户名 |
| email | VARCHAR(255) | 邮箱 |
```

**何时使用**：
- 大型 schema 或 API 文档
- 详细的配置选项
- 多框架/多场景变体
- 超过 100 行的内容

#### assets/

存放输出资源（模板、图片、字体等）：

```
assets/
├── web-template/           # React/Vue 项目模板
│   ├── package.json
│   ├── src/
│   └── README.md
├── report-template.docx    # Word 模板
└── logo.png                # 品牌 Logo
```

**何时使用**：
- 需要复制/修改的模板文件
- 输出中使用的图片/字体
- 示例项目脚手架

---

## 开发流程

### Step 1: 明确 Skill 的功能范围

通过具体例子理解 Skill 应该支持什么：

- "这个 Skill 要解决什么问题？"
- "用户会怎么描述他们的需求？"
- "有哪些典型的使用场景？"

**示例**：开发 `pdf-processor` Skill

用户可能会说：
- "帮我旋转这个 PDF"
- "把这两个 PDF 合并"
- "提取 PDF 里的文字"
- "把 PDF 转成图片"

### Step 2: 规划资源内容

分析每个场景，确定需要什么资源：

| 场景 | 分析 | 需要的资源 |
|-----|------|-----------|
| 旋转 PDF | 每次都要重写旋转代码 | `scripts/rotate_pdf.py` |
| 合并 PDF | 代码相对简单 | 直接写在 SKILL.md 中 |
| 提取文本 | 需要处理多种情况 | `scripts/extract_text.py` |
| PDF 转图片 | 需要模板项目 | `assets/pdf-to-image-template/` |

### Step 3: 初始化 Skill 目录

```bash
# 创建 Skill 目录结构
mkdir -p my-skill/{scripts,references,assets}

# 创建 SKILL.md 模板
cat > my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: |
  描述 Skill 的功能和触发条件。
  包含：
  1. 能做什么
  2. 何时触发（关键词、场景）
  3. 使用示例
---

# My Skill

## 何时使用此 Skill

...

## 快速开始

...

## 详细说明

...
EOF
```

### Step 4: 实现资源文件

先实现 scripts/、references/、assets/ 中的内容，再编写 SKILL.md。

**重要**：所有脚本必须实际测试，确保没有 bug。

### Step 5: 编写 SKILL.md

遵循以下原则：

1. **简洁优先**：只包含 AI 不知道的信息
2. **具体示例**：用代码示例代替冗长解释
3. **适当自由度**：
   - 高自由度：文本说明（多种方法都有效）
   - 中自由度：伪代码/参数化脚本（有推荐模式）
   - 低自由度：具体脚本（操作脆弱，需要一致性）

### Step 6: 验证和打包

```bash
# 验证 Skill 结构
# - 检查 YAML frontmatter
# - 验证文件组织
# - 检查资源引用

# 打包为 .skill 文件（zip 格式）
zip -r my-skill.skill my-skill/
```

---

## 发布与分享

### 发布到 Skill Registry

Skills 可以通过以下方式分享：

#### 方式 1: GitHub 发布

1. 创建 GitHub 仓库
2. 上传 Skill 目录
3. 打 Tag 发布版本
4. 用户通过 CLI 安装：
   ```bash
   npx skills add owner/repo@skill-name
   ```

#### 方式 2: Skill Hub

提交到官方 Skill Hub（如 https://skills.sh/）：

1. 注册开发者账号
2. 上传 `.skill` 文件
3. 填写 Skill 信息
4. 等待审核

#### 方式 3: 直接分享

直接分享 `.skill` 文件，用户手动安装：

```bash
npx skills install ./my-skill.skill
```

### 版本管理

使用语义化版本（SemVer）：

```json
// _meta.json
{
  "ownerId": "your-id",
  "slug": "my-skill",
  "version": "1.2.3",
  "publishedAt": 1704067200000
}
```

版本号规则：
- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向下兼容的功能添加
- **PATCH**: 向下兼容的问题修复

---

## 使用方法

### 安装 Skill

```bash
# 从 GitHub 安装
npx skills add owner/repo@skill-name

# 从本地文件安装
npx skills install ./my-skill.skill

# 全局安装（推荐）
npx skills add owner/repo@skill-name -g
```

### 查找 Skill

```bash
# 搜索 Skill
npx skills find pdf
npx skills find "react performance"

# 查看已安装
npx skills list
```

### 更新 Skill

```bash
# 检查更新
npx skills check

# 更新所有
npx skills update
```

### 在对话中使用

安装后，AI 会自动根据 `description` 中的触发条件来调用 Skill。

**示例对话**：

```
用户: 帮我旋转这个 PDF 文件

AI: [检测到 pdf-processor Skill 触发]
    [加载 SKILL.md]
    我来帮你旋转 PDF。请提供：
    1. 文件路径
    2. 旋转角度（默认 90°）
```

---

## 最佳实践

### 1. 保持简洁

- SKILL.md < 500 行
- 超过 100 行的内容移到 references/
- 每个段落都问："AI 真的需要这个吗？"

### 2. 清晰的触发描述

```yaml
# ✅ 好的描述
description: |
  PDF 处理工具，支持旋转、合并、拆分、文本提取。
  当用户提到以下场景时触发：
  - "处理 PDF"、"旋转 PDF"、"合并 PDF"
  - "提取 PDF 文字"、"PDF 转图片"
  - "修改 PDF"、"编辑 PDF" 等

# ❌ 差的描述
description: PDF processor  # 太简单，无法触发
```

### 3. 渐进式披露

```markdown
# ✅ 好的组织方式

## 快速开始
简单示例...

## 高级功能
- **功能 A**: 参见 [references/a.md]
- **功能 B**: 参见 [references/b.md]

# ❌ 差的组织方式
把所有内容都堆在 SKILL.md 里...
```

### 4. 避免重复

信息应该只存在于一个地方：
- 核心流程 → SKILL.md
- 详细文档 → references/
- 可执行代码 → scripts/
- 模板资源 → assets/

### 5. 测试脚本

所有 scripts/ 中的代码必须实际运行测试：

```bash
# 测试 Python 脚本
python scripts/my_script.py test-input.pdf output.pdf

# 测试 Bash 脚本
bash scripts/helper.sh arg1 arg2
```

### 6. 命名规范

- Skill 名称：小写字母、数字、连字符
- 目录名与 Skill 名一致
- 脚本名描述功能：`rotate_pdf.py` > `script.py`

### 7. 不要包含的文件

❌ 不要创建这些文件：
- README.md（SKILL.md 已经足够）
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- 测试文件（除非测试本身就是功能）

---

## 示例 Skill

### 简单 Skill：天气查询

```
weather-skill/
└── SKILL.md
```

```markdown
---
name: weather
description: |
  获取指定城市的当前天气和预报。
  当用户询问以下问题时触发：
  - "XX 天气怎么样"、"XX 今天天气"
  - "明天会下雨吗"、"气温多少度"
  - "天气预报" 等
---

# Weather Skill

## 使用方法

使用 wttr.in 服务获取天气：

```bash
# 当前天气
curl -s 'https://wttr.in/城市名?format=%l:+%c+%t+%w+%h&lang=zh'

# 完整预报（图形化）
curl -s 'https://wttr.in/城市名?lang=zh'
```

## 输出格式说明

- `%l` - 地点
- `%c` - 天气状况
- `%t` - 温度
- `%w` - 风速
- `%h` - 湿度
```

### 复杂 Skill：PDF 处理器

```
pdf-processor/
├── SKILL.md
├── scripts/
│   ├── rotate.py
│   ├── merge.py
│   └── extract_text.py
└── references/
    └── advanced.md
```

```markdown
---
name: pdf-processor
description: |
  PDF 文档处理工具，支持页面旋转、合并/拆分、文本提取、图片转换。
  当用户提到以下场景时触发：
  - "处理 PDF"、"旋转 PDF 页面"
  - "合并 PDF 文件"、"拆分 PDF"
  - "提取 PDF 文字"、"PDF 转图片"
  - "修改 PDF"、"编辑 PDF" 等
---

# PDF Processor

## 何时使用此 Skill

- 需要旋转 PDF 页面
- 需要合并多个 PDF
- 需要提取 PDF 中的文本
- 需要将 PDF 转换为图片

## 快速开始

### 旋转 PDF

```bash
python scripts/rotate.py input.pdf output.pdf 90
```

### 合并 PDF

```bash
python scripts/merge.py output.pdf input1.pdf input2.pdf ...
```

### 提取文本

```bash
python scripts/extract_text.py input.pdf > output.txt
```

## 高级功能

参见 [references/advanced.md](references/advanced.md) 了解：
- 批量处理
- 密码保护 PDF 处理
- 自定义输出格式
```

---

## 总结

Agent Skills 是一种强大的机制，让 AI Agent 能够：

1. **扩展能力**：通过模块化方式添加专业功能
2. **复用知识**：避免重复解决相同问题
3. **保持一致**：确保复杂操作按预期执行
4. **共享协作**：在社区中分享和发现 Skills

核心要点：
- ✅ 清晰的 `description` 是关键
- ✅ 保持 SKILL.md 简洁，资源外置
- ✅ 所有脚本必须测试
- ✅ 遵循渐进式披露原则

---

*文档版本: 1.0.0*
*最后更新: 2026-03-17*
