# Template Skill

## 简介

`template` 是一个创建新 Skill 的模板，包含标准结构和示例。

## 使用方法

复制 `skills/template/` 目录作为新 Skill 的起点：

```bash
cp -r skills/template skills/my-new-skill
cd skills/my-new-skill
# 编辑 SKILL.md
```

## 文件结构

```
template/
├── SKILL.md
├── README.md
└── references/
    └── example.md
```

## SKILL.md 格式

```yaml
---
name: skill-name
description: 简洁描述，说明何时触发和功能。
metadata:
  author: your-name
  version: "2026.01.01"
---

# Skill 内容

详细说明...
```
