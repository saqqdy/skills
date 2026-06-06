# Skill Structure Guide

This document describes the standard structure for Claude Code skills.

## Directory Structure

```
skill-name/
├── SKILL.md             # Required: Main skill definition
├── references/          # Optional: Additional documentation
│   └── *.md
├── scripts/             # Optional: Helper scripts
│   ├── *.py
│   ├── *.sh
│   └── *.js
├── assets/              # Optional: Static assets
│   └── templates, icons, etc.
├── agents/              # Optional: Subagent definitions
│   └── *.md
├── evals/               # Optional: Test cases
│   ├── evals.json
│   └── files/
└── LICENSE.md           # Optional: If different from project
```

## SKILL.md Format

```markdown
---
name: skill-name
description: When to trigger this skill and what it does.
metadata:
  author: your-name
  version: "2026.01.01"
---

# Skill Title

Instructions for the skill...

## Usage

How to use this skill...

## References

| Topic | Reference |
|-------|-----------|
| Topic | [file.md](references/file.md) |
```

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique skill identifier (kebab-case) |
| `description` | Yes | When to trigger, what it does (max 1024 chars) |
| `metadata.author` | No | Skill author |
| `metadata.version` | No | Skill version |

## Description Guidelines

The description is critical for triggering:

1. **State when to use** - "Use this skill when..."
2. **Focus on user intent** - What the user wants to achieve
3. **Be distinctive** - Make it stand out from other skills
4. **Stay under 1024 characters**

Example descriptions:

```
Use this skill for PDF form filling and data extraction. Handles fillable PDFs, extracts field data, and supports multi-page documents. Triggers when users mention PDFs, forms, or form fields.

Extract data from spreadsheets and CSV files. Supports Excel, Google Sheets, and CSV. Use when users mention spreadsheets, Excel, CSV, or tabular data.

Vue.js component development and best practices. Use when creating Vue components, setting up Vue projects, or discussing Vue patterns.
```

## Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) - Always in context
2. **SKILL.md body** - In context when skill triggers
3. **Bundled resources** - As needed

Keep SKILL.md under 500 lines. Move detailed content to references.

## Adding Helper Scripts

Put executable scripts in `scripts/`:

```python
# scripts/helper.py
#!/usr/bin/env python3
"""Helper script for this skill."""

def main():
    print("Helper script running...")

if __name__ == "__main__":
    main()
```

Reference from SKILL.md:

```markdown
To use the helper script:

```bash
python scripts/helper.py
```
```

## Adding Tests

Put tests in `evals/`:

```json
// evals/evals.json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's test prompt",
      "expected_output": "Expected result",
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

## Packaging

Package a skill into a distributable `.skill` file:

```bash
python scripts/package_skill.py skills/my-skill
```

This creates `my-skill.skill` (zip format) containing all skill files.
