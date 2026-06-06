# @saqqdy/skills

A collection of Claude Code skills for building AI-powered development tools.

[简体中文](README_CN.md)

## What are Skills?

Skills are specialized instruction sets for Claude Code that enhance its capabilities for specific tasks. Each skill is a self-contained directory with a `SKILL.md` file containing structured instructions, plus optional supporting resources like scripts, documentation, and test cases.

### Why Use Skills?

- **Reusability**: Write once, use across multiple projects
- **Consistency**: Standardized patterns for common tasks
- **Progressive Disclosure**: Simple descriptions trigger detailed instructions
- **Distributable**: Package and share skills as `.skill` files

## Project Structure

```
skills/
├── skills/              # Skill directories
│   ├── frontend-design/ # Frontend design guidelines
│   └── template/        # Template skill for reference
├── scripts/             # Skill development tooling (Python)
│   ├── package_skill.py       # Package skill into .skill file
│   ├── package_all.py         # Batch package all skills
│   ├── quick_validate.py      # Validate SKILL.md format
│   ├── run_eval.py            # Run trigger evaluations
│   ├── aggregate_benchmark.py # Aggregate benchmark results
│   ├── improve_description.py # Optimize skill descriptions
│   ├── run_loop.py            # Description optimization loop
│   ├── generate_report.py     # Generate HTML reports
│   └── utils.py               # Shared utility functions
├── agents/              # Subagent definitions for testing
│   ├── grader.md              # Grade test outputs
│   ├── comparator.md          # Compare two outputs
│   └── analyzer.md            # Analyze benchmark results
├── assets/              # Shared assets
│   └── eval_review.html       # Evaluation review template
├── references/          # Shared documentation
│   └── schemas.md             # JSON schemas
├── eval-viewer/         # Evaluation viewer tool
│   ├── generate_review.py     # Full evaluation viewer (471 lines)
│   └── viewer.html            # Standalone HTML viewer (43.9K)
├── package.json
├── pnpm-workspace.yaml
├── tsconfig.json
├── eslint.config.mjs
└── vitest.config.ts
```

## Documentation

- [DEVELOPMENT.md](DEVELOPMENT.md) - Detailed development guide (Chinese)
- [CHANGELOG.md](CHANGELOG.md) - Version history

## Quick Start

### Prerequisites

- Node.js 18+
- pnpm 9+
- Python 3.11+ (for tooling scripts)

### Installation

```bash
# Clone the repository
git clone https://github.com/saqqdy/skills.git
cd skills

# Install dependencies
pnpm install

# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install pyyaml
```

### Create a New Skill

1. **Copy the template**:
   ```bash
   cp -r skills/template skills/my-skill
   ```

2. **Edit SKILL.md** with your skill's configuration:
   ```yaml
   ---
   name: my-skill
   description: When to trigger this skill and what it does.
   metadata:
     author: your-name
     version: "2026.01.01"
   ---
   ```

3. **Add instructions** in the body of SKILL.md

4. **Validate** the skill:
   ```bash
   source .venv/bin/activate
   python scripts/quick_validate.py skills/my-skill
   ```

5. **Package** the skill:
   ```bash
   python scripts/package_skill.py skills/my-skill
   ```

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md             # Required: Main skill definition
│   ├── YAML frontmatter (name, description, metadata)
│   └── Markdown instructions
├── references/          # Optional: Additional documentation
│   └── *.md
├── scripts/             # Optional: Helper scripts
│   ├── *.py
│   ├── *.sh
│   └── *.js
├── assets/              # Optional: Static assets
│   └── templates, icons, fonts, etc.
├── agents/              # Optional: Subagent definitions
│   └── *.md
├── evals/               # Optional: Test cases
│   ├── evals.json
│   └── files/
└── LICENSE.md           # Optional: Skill-specific license
```

### SKILL.md Format

```markdown
---
name: skill-name
description: When to trigger this skill and what it does. Keep under 1024 characters.
metadata:
  author: your-name
  version: "2026.01.01"
  compatibility: Optional compatibility notes
---

# Skill Title

Brief overview of what this skill does.

## Usage

How to use this skill...

## References

| Topic | Reference |
|-------|-----------|
| Details | [file.md](references/file.md) |
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique skill identifier (kebab-case, max 64 chars) |
| `description` | Yes | When to trigger, what it does (max 1024 chars) |
| `metadata.author` | No | Skill author |
| `metadata.version` | No | Skill version |
| `metadata.compatibility` | No | Compatibility notes |

### Writing Good Descriptions

The description is critical for triggering. Follow these guidelines:

1. **State when to use**: "Use this skill when..."
2. **Focus on user intent**: What the user wants to achieve
3. **Be distinctive**: Make it stand out from other skills
4. **Stay under 1024 characters**

Example descriptions:

```
Use for PDF form filling and data extraction. Handles fillable PDFs, extracts field data, supports multi-page documents. Triggers when users mention PDFs, forms, or form fields.

Extract data from spreadsheets and CSV files. Supports Excel, Google Sheets, CSV format. Use when users mention spreadsheets, Excel, CSV, or tabular data.
```

## Python Tooling Scripts Reference

### 1. quick_validate.py - Validate Skill Format

Validates SKILL.md file format and structure.

**Usage**:
```bash
# Validate single skill
python scripts/quick_validate.py skills/my-skill

# Validate all skills
python scripts/quick_validate.py skills/
```

**Checks**:
- SKILL.md file exists
- Valid YAML frontmatter
- Required fields present
- Name follows kebab-case
- Description under 1024 characters

### 2. package_skill.py - Package Skill

Packages skill directory into distributable `.skill` file (zip format).

**Usage**:
```bash
python scripts/package_skill.py skills/my-skill
python scripts/package_skill.py skills/my-skill ./dist
```

### 3. package_all.py - Batch Package Skills

Packages all skills in the skills/ directory.

**Usage**:
```bash
python scripts/package_all.py
python scripts/package_all.py --output ./release
```

### 4. run_eval.py - Run Trigger Evaluation

Tests whether skill description triggers correctly for given queries.

**Usage**:
```bash
python scripts/run_eval.py \
  --eval-set evals/trigger_eval.json \
  --skill-path skills/my-skill
```

**Parameters**:
| Parameter | Description |
|-----------|-------------|
| `--eval-set` | Evaluation JSON file path |
| `--skill-path` | Skill directory path |
| `--num-workers` | Parallel workers (default: 10) |
| `--timeout` | Query timeout in seconds (default: 30) |
| `--runs-per-query` | Runs per query (default: 3) |

### 5. aggregate_benchmark.py - Aggregate Benchmark Results

Aggregates benchmark results from multiple run directories.

**Usage**:
```bash
python scripts/aggregate_benchmark.py ./workspace/iteration-1 \
  --skill-name my-skill
```

Generates `benchmark.json` and `benchmark.md`.

### 6. improve_description.py - Optimize Skill Description

Automatically improves skill description based on evaluation results.

**Usage**:
```bash
python scripts/improve_description.py \
  --eval-results results.json \
  --skill-path skills/my-skill \
  --model claude-sonnet-4-20250514
```

### 7. run_loop.py - Description Optimization Loop

Automatically runs multiple rounds of evaluation and optimization.

**Usage**:
```bash
python scripts/run_loop.py \
  --eval-set evals/trigger_eval.json \
  --skill-path skills/my-skill \
  --model claude-sonnet-4-20250514 \
  --max-iterations 5
```

### 8. generate_report.py - Generate HTML Report

Generates HTML visualization report of optimization process.

**Usage**:
```bash
python scripts/generate_report.py \
  --eval-set evals/trigger_eval.json \
  --skill-path skills/my-skill
```

### 9. utils.py - Shared Utility Functions

Shared functions used by other scripts.

```python
from scripts.utils import parse_skill_md, get_skill_metadata, find_skill_dirs

# Parse SKILL.md file
name, description, content = parse_skill_md(skill_path)

# Get skill metadata
metadata = get_skill_metadata(skill_path)

# Find all skill directories
skill_dirs = find_skill_dirs(base_path)
```

## eval-viewer Evaluation Viewer

### generate_review.py - Full Evaluation Viewer

Starts interactive web server to view evaluation results.

**Usage**:
```bash
# Start server and open browser
python eval-viewer/generate_review.py ./workspace/iteration-1 \
  --skill-name my-skill

# Generate static HTML file
python eval-viewer/generate_review.py ./workspace/iteration-1 \
  --skill-name my-skill \
  --static ./report.html
```

### viewer.html - Standalone HTML Viewer

A complete single-file HTML viewer that works without a server.

## Agents Subagents

### grader.md - Grading Agent

Evaluates test outputs against expectations.

**Input**:
- `expectations`: Expected results list
- `transcript_path`: Execution log path
- `outputs_dir`: Output files directory

### comparator.md - Comparison Agent

Blind comparison of two outputs to determine which is better.

**Input**:
- `output_a_path`: Output A path
- `output_b_path`: Output B path
- `eval_prompt`: Original task

### analyzer.md - Analysis Agent

Analyzes benchmark results to find patterns and issues.

**Output**:
- Winner strengths
- Loser weaknesses
- Improvement suggestions

## JSON Data Formats

See [references/schemas.md](references/schemas.md) for complete schemas.

### evals.json - Evaluation Definition

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's test prompt",
      "expected_output": "Expected result",
      "expectations": ["Output includes X"]
    }
  ]
}
```

### grading.json - Grading Results

```json
{
  "expectations": [
    {"text": "Expectation", "passed": true, "evidence": "..."}
  ],
  "summary": {"passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67}
}
```

### benchmark.json - Benchmark Summary

```json
{
  "run_summary": {
    "with_skill": {"pass_rate": {"mean": 0.85}},
    "without_skill": {"pass_rate": {"mean": 0.35}},
    "delta": {"pass_rate": "+0.50"}
  }
}
```

## Development

### Code Style

```bash
pnpm lint --fix
```

Uses `@eslint-sets/eslint-config` with TypeScript and Python support.

### Testing

```bash
pnpm test
```

Run tests with Vitest.

### Git Hooks

Pre-commit hooks automatically run linting via `simple-git-hooks` and `lint-staged`.

## Publishing

### As npm Package

```bash
pnpm package
pnpm publish
```

### As .skill File

```bash
python scripts/package_skill.py skills/my-skill ./dist
```

## Best Practices

### Keep SKILL.md Under 500 Lines

Move detailed content to `references/` directory.

### Use Progressive Disclosure

1. **Metadata** - Always visible
2. **SKILL.md body** - Loaded when triggered
3. **References** - Loaded on demand

### Add Test Cases

Create `evals/evals.json`:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Test prompt",
      "expectations": ["Output contains X"]
    }
  ]
}
```

## License

Apache License 2.0 © 2026 saqqdy