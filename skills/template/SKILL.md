---
name: template
description: A template skill demonstrating the standard structure. Use this as a reference when creating new skills. This skill triggers when users mention 'template', 'example skill', or ask how to create a new skill.
metadata:
  author: saqqdy
  version: "2026.01.01"
---

# Template Skill

This is a template skill that demonstrates the standard structure for Claude Code skills.

## Overview

Skills are specialized instructions for Claude Code that help with specific tasks. Each skill is a directory containing a `SKILL.md` file with instructions and optional supporting files.

## Usage

To create a new skill:

1. Copy this directory:
   ```bash
   cp -r skills/template skills/my-skill
   ```

2. Edit `SKILL.md` frontmatter:
   - `name`: Unique skill identifier (kebab-case)
   - `description`: When to trigger, what it does
   - `metadata`: author, version, etc.

3. Add your skill instructions in the body

4. Validate the skill:
   ```bash
   python scripts/quick_validate.py skills/my-skill
   ```

5. Package the skill:
   ```bash
   python scripts/package_skill.py skills/my-skill
   ```

## Structure

A skill can contain:

```
skill-name/
├── SKILL.md             # Required: Main skill definition
├── references/          # Optional: Additional documentation
├── scripts/             # Optional: Helper scripts
├── assets/              # Optional: Static assets
├── agents/              # Optional: Subagent definitions
└── evals/               # Optional: Test cases
    ├── evals.json
    └── files/
```

## References

| Topic | Reference |
|-------|-----------|
| Skill Structure | [example](references/example.md) |
| JSON Schemas | [schemas](../../references/schemas.md) |

## Best Practices

1. **Keep SKILL.md under 500 lines** - Use references for longer content
2. **Clear description** - Describe when to trigger and what it does
3. **Progressive disclosure** - Main instructions in SKILL.md, details in references
4. **Reusable scripts** - Put helper scripts in scripts/ directory
5. **Test your skill** - Add evals/ for validation
