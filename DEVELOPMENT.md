# 开发说明文档

本文档详细说明 `@saqqdy/skills` 项目的开发流程、架构设计和最佳实践。

## 目录

- [项目架构](#项目架构)
- [开发环境设置](#开发环境设置)
- [代码规范](#代码规范)
- [开发流程](#开发流程)
- [测试指南](#测试指南)
- [调试技巧](#调试技巧)
- [发布流程](#发布流程)
- [贡献指南](#贡献指南)
- [常见问题](#常见问题)

## 项目架构

### 整体设计

```
┌─────────────────────────────────────────────────────────────┐
│                      @saqqdy/skills                          │
├─────────────────────────────────────────────────────────────┤
│  skills/           - 技能目录（用户创建的技能）              │
│  scripts/          - Python 工具脚本                        │
│  agents/           - 子代理定义                             │
│  eval-viewer/      - 评估查看器                             │
│  references/       - 文档和模式定义                         │
│  assets/           - 静态资源                               │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. Skills 系统

技能是本项目的核心。每个技能是一个独立目录，包含：

```
skill-name/
├── SKILL.md         # 主文件：YAML frontmatter + Markdown 指令
├── references/      # 参考文档
├── scripts/         # 辅助脚本
├── assets/          # 静态资源
├── agents/          # 子代理
└── evals/           # 测试用例
```

**加载机制**：

```
用户查询 → Claude 读取可用技能列表（name + description）
         → 匹配到相关技能 → 加载 SKILL.md 正文
         → 按需加载 references/scripts
```

#### 2. Scripts 工具链

Python 脚本提供完整的技能开发工具链：

```
开发流程：
quick_validate.py → package_skill.py → run_eval.py
                         ↓
                  improve_description.py
                         ↓
                    run_loop.py
                         ↓
              aggregate_benchmark.py
                         ↓
              generate_review.py
```

#### 3. Agents 子代理系统

用于自动化测试和评估：

```
Grader Agent     - 评估输出是否符合预期
Comparator Agent - 盲比较两个输出
Analyzer Agent   - 分析基准测试结果
```

#### 4. Eval Viewer

交互式评估查看器：

```
generate_review.py  - Python 后端
viewer.html         - 前端界面
```

### 数据流

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  evals.json  │────→│  run_eval.py │────→│ results.json │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                     ┌──────────────────────────┘
                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ grader agent │────→│ grading.json │────→│ benchmark.md │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ eval-viewer  │
                     └──────────────┘
```

## 开发环境设置

### 系统要求

| 工具 | 版本要求 | 说明 |
|------|----------|------|
| Node.js | ≥ 18.0.0 | JavaScript 运行时 |
| pnpm | ≥ 9.0.0 | 包管理器 |
| Python | ≥ 3.11 | 工具脚本运行时 |
| Git | ≥ 2.0.0 | 版本控制 |

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/saqqdy/skills.git
cd skills
```

#### 2. 安装 Node.js 依赖

```bash
# 安装 pnpm（如果未安装）
npm install -g pnpm

# 安装项目依赖
pnpm install
```

#### 3. 设置 Python 环境

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 安装 Python 依赖
pip install pyyaml
```

#### 4. 验证安装

```bash
# 验证 Node.js
pnpm --version
node --version

# 验证 Python
python --version
pip show pyyaml

# 验证工具脚本
python scripts/quick_validate.py skills/template

# 验证 lint
pnpm lint
```

### IDE 配置

#### VS Code 推荐扩展

创建 `.vscode/extensions.json`：

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "editorconfig.editorconfig"
  ]
}
```

#### VS Code 设置

创建 `.vscode/settings.json`：

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  }
}
```

### 环境变量

创建 `.env` 文件（可选）：

```bash
# Python 路径
PYTHON_PATH=/path/to/python3

# 默认模型
DEFAULT_MODEL=claude-sonnet-4-20250514

# 日志级别
LOG_LEVEL=DEBUG
```

## 代码规范

### TypeScript/JavaScript

#### 命名规范

| 类型 | 命名风格 | 示例 |
|------|----------|------|
| 文件名 | kebab-case | `skill-utils.ts` |
| 变量/函数 | camelCase | `parseSkillMd` |
| 类/接口 | PascalCase | `SkillValidator` |
| 常量 | UPPER_SNAKE_CASE | `MAX_DESCRIPTION_LENGTH` |
| 私有成员 | _前缀 | `_internalState` |

#### 代码风格

```typescript
// ✅ 推荐
export function parseSkillMd(skillPath: Path): SkillMetadata {
  const content = skillPath.readText()
  const frontmatter = extractFrontmatter(content)
  return {
    name: frontmatter.name,
    description: frontmatter.description,
  }
}

// ❌ 避免
export function parse(md: any) {
  return md.name
}
```

#### 类型定义

```typescript
// 定义清晰的接口
interface SkillMetadata {
  name: string
  description: string
  author?: string
  version?: string
}

// 使用类型别名
type SkillValidationResult = {
  valid: boolean
  errors: string[]
}
```

### Python

#### 命名规范

| 类型 | 命名风格 | 示例 |
|------|----------|------|
| 文件名 | snake_case | `quick_validate.py` |
| 函数 | snake_case | `validate_skill` |
| 类 | PascalCase | `SkillValidator` |
| 常量 | UPPER_SNAKE_CASE | `MAX_NAME_LENGTH` |
| 私有成员 | _前缀 | `_parse_yaml` |

#### 代码风格

```python
#!/usr/bin/env python3
"""模块文档字符串。

详细说明模块功能。
"""

from pathlib import Path
from typing import Optional

# 常量定义
MAX_DESCRIPTION_LENGTH = 1024


def validate_skill(skill_path: Path) -> tuple[bool, str]:
    """验证技能格式。

    Args:
        skill_path: 技能目录路径

    Returns:
        元组：(是否有效, 错误消息)

    Example:
        >>> valid, msg = validate_skill(Path('skills/my-skill'))
        >>> print(valid, msg)
        True Skill is valid!
    """
    if not skill_path.exists():
        return False, f"Skill not found: {skill_path}"

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    return True, "Skill is valid!"
```

#### 类型注解

```python
from typing import Optional, Union, Any
from pathlib import Path

# 基础类型
def get_name(path: Path) -> str: ...

# 可选类型
def get_author(path: Path) -> Optional[str]: ...

# 联合类型
def get_value(key: str) -> Union[str, int, None]: ...

# Any 类型（谨慎使用）
def parse_data(data: Any) -> dict: ...
```

### Markdown

#### SKILL.md 格式

```markdown
---
name: skill-name
description: 简洁描述，说明何时触发和功能。
metadata:
  author: your-name
  version: "2026.01.01"
---

# 技能标题

简要说明技能功能。

## 使用方法

如何使用此技能...

## 示例

具体示例...

## 参考资料

| 主题 | 参考 |
|------|------|
| 详情 | [file.md](references/file.md) |
```

#### 标题层级

```
# 一级标题（仅用于标题）
## 二级标题（主要章节）
### 三级标题（子章节）
#### 四级标题（细节说明）
```

#### 代码块

````markdown
```python
# 指定语言以启用语法高亮
def example():
    pass
```

```bash
# Shell 命令
python script.py
```

```json
{
  "key": "value"
}
```
````

### ESLint 配置

```javascript
// eslint.config.mjs
import eslintConfig from '@eslint-sets/eslint-config'

export default eslintConfig({
  type: 'lib',
  ignores: ['skills/**', 'eval-viewer/**', '.venv/**'],
  markdown: false,
  python: true,
  react: false,
  rules: {
    'style/indent-binary-ops': 'off',
  },
  stylistic: {
    indent: 'tab',
  },
  typescript: true,
})
```

### Git Commit 规范

#### Commit 消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(skills): add vue skill` |
| `fix` | Bug 修复 | `fix(validate): handle empty description` |
| `docs` | 文档更新 | `docs(readme): update installation guide` |
| `style` | 代码格式 | `style: fix indentation` |
| `refactor` | 重构 | `refactor(scripts): extract common logic` |
| `test` | 测试 | `test(validate): add unit tests` |
| `chore` | 杂项 | `chore: update dependencies` |

#### 示例

```
feat(skills): add template skill for creating new skills

- Add SKILL.md with frontmatter examples
- Add references/example.md for structure guide
- Add validation for template skill

Closes #123
```

## 开发流程

### 创建新技能

#### 1. 从模板创建

```bash
# 复制模板
cp -r skills/template skills/my-skill

# 进入目录
cd skills/my-skill
```

#### 2. 编辑 SKILL.md

```yaml
---
name: my-skill
description: 详细描述技能的功能和触发条件。
metadata:
  author: your-name
  version: "2026.01.01"
---

# My Skill

技能详细说明...

## 使用方法

## 示例

## 参考资料
```

#### 3. 添加参考文档

```bash
mkdir -p references
touch references/guide.md
```

#### 4. 添加辅助脚本

```bash
mkdir -p scripts
touch scripts/helper.py
chmod +x scripts/helper.py
```

#### 5. 添加测试用例

```bash
mkdir -p evals/files

# 创建评估配置
cat > evals/evals.json << 'EOF'
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "测试提示",
      "expected_output": "预期输出",
      "expectations": [
        "输出包含 X",
        "使用了脚本 Y"
      ]
    }
  ]
}
EOF
```

#### 6. 验证和打包

```bash
# 激活虚拟环境
source .venv/bin/activate

# 验证格式
python scripts/quick_validate.py skills/my-skill

# 打包
python scripts/package_skill.py skills/my-skill
```

### 添加新工具脚本

#### 1. 创建脚本文件

```bash
touch scripts/my_tool.py
chmod +x scripts/my_tool.py
```

#### 2. 编写脚本

```python
#!/usr/bin/env python3
"""工具脚本说明。

用法:
    python scripts/my_tool.py <args>
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="工具说明")
    parser.add_argument("input", type=Path, help="输入路径")
    parser.add_argument("--output", "-o", type=Path, help="输出路径")
    args = parser.parse_args()

    # 实现逻辑
    print(f"Processing: {args.input}")


if __name__ == "__main__":
    main()
```

#### 3. 添加到 package.json

```json
{
  "scripts": {
    "my-tool": "python scripts/my_tool.py"
  }
}
```

#### 4. 更新文档

在 README.md 中添加使用说明。

### 修改现有技能

#### 1. 创建分支

```bash
git checkout -b update-skill-name
```

#### 2. 修改文件

```bash
# 编辑 SKILL.md
vim skills/my-skill/SKILL.md
```

#### 3. 验证修改

```bash
source .venv/bin/activate
python scripts/quick_validate.py skills/my-skill
```

#### 4. 提交修改

```bash
git add skills/my-skill/
git commit -m "feat(skills): update my-skill description"
```

#### 5. 运行测试

```bash
python scripts/run_eval.py \
  --skill-path skills/my-skill \
  --eval-set evals/evals.json
```

## 测试指南

### 单元测试

#### Vitest 配置

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: ['scripts/**/*.test.ts'],
    globals: true,
    coverage: {
      reporter: ['text', 'json', 'html'],
    },
  },
})
```

#### 测试示例

```typescript
// scripts/utils.test.ts
import { describe, it, expect } from 'vitest'
import { parseSkillMd } from './utils'
import { Path } from 'path'

describe('parseSkillMd', () => {
  it('should parse valid SKILL.md', () => {
    const skillPath = new Path('skills/template')
    const [name, description, content] = parseSkillMd(skillPath)

    expect(name).toBe('template')
    expect(description).toContain('template skill')
    expect(content).toContain('---')
  })

  it('should throw for missing SKILL.md', () => {
    const skillPath = new Path('skills/nonexistent')
    expect(() => parseSkillMd(skillPath)).toThrow()
  })
})
```

#### 运行测试

```bash
# 运行所有测试
pnpm test

# 监听模式
pnpm test --watch

# 覆盖率报告
pnpm test --coverage
```

### Python 测试

#### pytest 配置

```ini
# pytest.ini
[pytest]
testpaths = scripts
python_files = *_test.py
python_functions = test_*
```

#### 测试示例

```python
# scripts/quick_validate_test.py
import pytest
from pathlib import Path
from quick_validate import validate_skill


def test_validate_valid_skill():
    """测试验证有效技能"""
    skill_path = Path("skills/template")
    valid, message = validate_skill(skill_path)
    assert valid is True
    assert "valid" in message.lower()


def test_validate_missing_skill_md():
    """测试缺少 SKILL.md 的情况"""
    skill_path = Path("skills/nonexistent")
    valid, message = validate_skill(skill_path)
    assert valid is False
    assert "not found" in message.lower()


@pytest.mark.parametrize("name,expected", [
    ("valid-name", True),
    ("InvalidName", False),
    ("invalid_name", False),
    ("-invalid", False),
])
def test_name_validation(name, expected):
    """测试名称验证"""
    # 实现测试逻辑
    pass
```

#### 运行测试

```bash
# 安装 pytest
pip install pytest pytest-cov

# 运行测试
pytest

# 覆盖率报告
pytest --cov=scripts --cov-report=html
```

### 集成测试

#### 测试完整工作流

```bash
#!/bin/bash
# tests/integration/test_workflow.sh

set -e

# 创建测试技能
cp -r skills/template skills/test-skill

# 验证
python scripts/quick_validate.py skills/test-skill

# 打包
python scripts/package_skill.py skills/test-skill

# 检查输出
if [ -f "test-skill.skill" ]; then
    echo "✅ Integration test passed"
    rm -rf skills/test-skill test-skill.skill
else
    echo "❌ Integration test failed"
    exit 1
fi
```

### 测试覆盖率目标

| 组件 | 目标覆盖率 |
|------|-----------|
| Python 脚本 | ≥ 80% |
| TypeScript | ≥ 80% |
| 关键路径 | 100% |

## 调试技巧

### Python 调试

#### 使用 pdb

```python
import pdb

def complex_function():
    # 设置断点
    pdb.set_trace()

    # 或者使用 breakpoint()（Python 3.7+）
    breakpoint()
```

#### 使用 logging

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def validate_skill(path):
    logger.debug(f"Validating skill: {path}")
    # ...
    logger.info("Skill validated successfully")
```

#### 调试脚本

```bash
# 使用 verbose 输出
python scripts/run_eval.py --verbose ...

# 重定向输出
python scripts/run_eval.py 2>&1 | tee debug.log

# 使用 PYTHONPATH
PYTHONPATH=. python -m pdb scripts/run_eval.py
```

### Node.js 调试

#### 使用 console

```javascript
console.log('Debug info:', variable)
console.error('Error:', error)
```

#### 使用 VS Code 调试器

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Script",
      "program": "${workspaceFolder}/scripts/test.ts",
      "runtimeExecutable": "node"
    }
  ]
}
```

### 常见问题排查

#### 1. 技能验证失败

```bash
# 检查 YAML 格式
python -c "import yaml; yaml.safe_load(open('skills/my-skill/SKILL.md'))"

# 检查文件结构
ls -la skills/my-skill/

# 详细错误信息
python scripts/quick_validate.py skills/my-skill -v
```

#### 2. 打包失败

```bash
# 检查文件权限
ls -la skills/my-skill/

# 检查排除规则
python -c "
from scripts.package_skill import should_exclude
from pathlib import Path
print(should_exclude(Path('node_modules/package')))
"
```

#### 3. 评估运行失败

```bash
# 检查 claude CLI
which claude
claude --version

# 检查环境变量
env | grep CLAUDE

# 使用超时设置
python scripts/run_eval.py --timeout 60 ...
```

## 发布流程

### 版本管理

#### 语义化版本

```
MAJOR.MINOR.PATCH

MAJOR: 不兼容的 API 更改
MINOR: 向后兼容的新功能
PATCH: 向后兼容的 Bug 修复
```

#### 更新版本

```bash
# 更新 package.json 版本
npm version patch  # 1.0.0 → 1.0.1
npm version minor  # 1.0.0 → 1.1.0
npm version major  # 1.0.0 → 2.0.0
```

### 发布前检查

```bash
#!/bin/bash
# scripts/pre-release.sh

set -e

echo "🔍 Running pre-release checks..."

# 1. 代码检查
echo "1. Linting..."
pnpm lint

# 2. 运行测试
echo "2. Running tests..."
pnpm test
pytest

# 3. 验证所有技能
echo "3. Validating skills..."
source .venv/bin/activate
python scripts/quick_validate.py skills/

# 4. 打包所有技能
echo "4. Packaging skills..."
python scripts/package_all.py --output ./dist

# 5. 检查打包结果
echo "5. Checking packages..."
ls -la ./dist/*.skill

echo "✅ All checks passed!"
```

### 发布到 npm

#### 1. 构建

```bash
# 清理旧文件
rm -rf dist/

# 打包技能
source .venv/bin/activate
python scripts/package_all.py --output ./dist

# 运行 lint
pnpm lint --fix
```

#### 2. 测试发布

```bash
# 使用 dry run
pnpm publish --dry-run

# 检查将要发布的文件
pnpm pack
```

#### 3. 正式发布

```bash
# 登录 npm
pnpm login

# 发布
pnpm publish

# 或发布到指定 registry
pnpm publish --registry https://registry.npmjs.org/
```

### 发布到 GitHub

#### 1. 创建 Tag

```bash
# 创建带注释的 tag
git tag -a v1.0.0 -m "Release v1.0.0"

# 推送 tag
git push origin v1.0.0
```

#### 2. 创建 Release

在 GitHub 上创建 Release：
1. 进入仓库的 Releases 页面
2. 点击 "Draft a new release"
3. 选择 tag
4. 填写 Release notes
5. 上传 `.skill` 文件作为附件

#### 3. Release Notes 模板

```markdown
# Release v1.0.0

## 新增功能

- 添加 X 功能
- 添加 Y 技能

## 改进

- 优化 Z 性能

## Bug 修复

- 修复 A 问题

## 贡献者

感谢以下贡献者：
- @user1
- @user2
```

## 贡献指南

### 贡献流程

#### 1. Fork 仓库

在 GitHub 上 fork 项目。

#### 2. 克隆 Fork

```bash
git clone https://github.com/YOUR_USERNAME/skills.git
cd skills
git remote add upstream https://github.com/saqqdy/skills.git
```

#### 3. 创建分支

```bash
git checkout -b feature/my-feature
```

#### 4. 开发和测试

```bash
# 安装依赖
pnpm install
source .venv/bin/activate
pip install pyyaml

# 开发...

# 运行测试
pnpm test
pytest

# 运行 lint
pnpm lint --fix
```

#### 5. 提交更改

```bash
git add .
git commit -m "feat: add my feature"
```

#### 6. 推送分支

```bash
git push origin feature/my-feature
```

#### 7. 创建 Pull Request

在 GitHub 上创建 Pull Request。

### 代码审查标准

#### 必须检查项

- [ ] 代码通过 lint 检查
- [ ] 所有测试通过
- [ ] 有足够的测试覆盖
- [ ] 文档已更新
- [ ] Commit 消息符合规范
- [ ] 没有引入安全漏洞

#### 代码质量标准

- 代码清晰易读
- 有适当的注释
- 遵循项目代码风格
- 没有重复代码
- 错误处理完善

### 问题报告模板

```markdown
## Bug 报告

### 描述
简要描述问题。

### 复现步骤
1. 执行 '...'
2. 点击 '...'
3. 看到错误

### 预期行为
描述预期发生什么。

### 实际行为
描述实际发生了什么。

### 环境
- OS: [e.g. macOS 14]
- Node: [e.g. 18.0.0]
- Python: [e.g. 3.11.0]

### 日志/截图
```

### 功能请求模板

```markdown
## 功能请求

### 描述
简要描述你希望添加的功能。

### 问题
这个功能解决什么问题？

### 建议方案
描述你建议的解决方案。

### 替代方案
描述你考虑过的其他方案。

### 附加信息
任何其他相关信息。
```

## 常见问题

### 安装问题

#### Q: pnpm install 失败

```bash
# 清理缓存
pnpm store prune

# 删除 node_modules
rm -rf node_modules pnpm-lock.yaml

# 重新安装
pnpm install
```

#### Q: Python 虚拟环境激活失败

```bash
# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# 如果仍然失败，重新创建虚拟环境
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install pyyaml
```

### 技能开发问题

#### Q: 技能验证失败：Name should be kebab-case

技能名称必须是小写字母、数字和连字符：

```yaml
# ✅ 正确
name: my-skill
name: vue-3-skill
name: api-handler

# ❌ 错误
name: MySkill
name: my_skill
name: -my-skill
```

#### Q: 技能验证失败：Description is too long

描述必须在 1024 字符以内：

```yaml
# ✅ 正确
description: 简洁描述技能功能和触发条件。

# ❌ 错误（超过 1024 字符）
description: 非常长的描述...
```

#### Q: 打包后缺少文件

检查文件是否被排除：

```python
# 排除规则
EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_FILES = {".DS_Store"}
ROOT_EXCLUDE_DIRS = {"evals"}
```

### 评估问题

#### Q: run_eval.py 运行超时

增加超时时间：

```bash
python scripts/run_eval.py \
  --timeout 60 \
  --skill-path skills/my-skill \
  --eval-set evals.json
```

#### Q: 评估结果不准确

尝试增加运行次数：

```bash
python scripts/run_eval.py \
  --runs-per-query 5 \
  --trigger-threshold 0.6 \
  ...
```

#### Q: claude CLI 未找到

安装 Claude CLI：

```bash
# macOS/Linux
curl -fsSL https://claude.ai/install.sh | sh

# 验证安装
claude --version
```

### 发布问题

#### Q: npm publish 失败：需要登录

```bash
# 登录 npm
pnpm login

# 检查登录状态
pnpm whoami
```

#### Q: 发布版本已存在

```bash
# 检查当前版本
pnpm version

# 更新版本号
pnpm version patch
git push --tags
```

---

## 附录

### 有用的命令速查表

```bash
# 开发
pnpm install              # 安装依赖
pnpm lint --fix           # 代码检查
pnpm test                 # 运行测试

# Python
source .venv/bin/activate # 激活虚拟环境
pip install pyyaml        # 安装依赖
python scripts/quick_validate.py skills/  # 验证技能

# Git
git checkout -b feature/x # 创建分支
git add .                 # 暂存更改
git commit -m "feat: x"   # 提交
git push origin feature/x # 推送

# 发布
pnpm version patch        # 更新版本
pnpm publish              # 发布到 npm
git tag v1.0.0           # 创建 tag
```

### 相关资源

- [Claude Code 文档](https://claude.ai/code)
- [ESLint 配置](https://eslint.org/)
- [Vitest 文档](https://vitest.dev/)
- [pnpm 文档](https://pnpm.io/)
- [Python 虚拟环境](https://docs.python.org/3/library/venv.html)

---

**最后更新**: 2026-06-06

**维护者**: saqqdy