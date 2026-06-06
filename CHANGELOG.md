# Changelog

## [1.0.0] - 2026-06-06

### Added

- **Project Foundation**
  - Initial project setup with pnpm workspace
  - TypeScript configuration with strict mode
  - ESLint configuration using `@eslint-sets/eslint-config`
  - Vitest test runner configuration
  - Git hooks with `simple-git-hooks` and `lint-staged`

- **Skill Development Tooling**
  - `scripts/package_skill.py` - Package skill into distributable `.skill` file
  - `scripts/quick_validate.py` - Validate SKILL.md format and frontmatter
  - `scripts/utils.py` - Shared utility functions
  - `scripts/run_eval.py` - Run skill trigger evaluations
  - `scripts/aggregate_benchmark.py` - Aggregate benchmark results
  - `scripts/improve_description.py` - Optimize skill descriptions
  - `scripts/run_loop.py` - Description optimization loop
  - `scripts/generate_report.py` - Generate HTML reports

- **Agent Definitions**
  - `agents/grader.md` - Grading test outputs
  - `agents/comparator.md` - Blind A/B comparison
  - `agents/analyzer.md` - Benchmark analysis

- **Assets and References**
  - `assets/eval_review.html` - Interactive evaluation review interface
  - `eval-viewer/generate_review.py` - Full evaluation viewer (471 lines)
  - `eval-viewer/viewer.html` - Standalone HTML viewer (43.9K)
  - `references/schemas.md` - JSON schemas documentation

- **Skill Template**
  - `skills/template/SKILL.md` - Template skill with frontmatter examples
  - `skills/template/references/example.md` - Skill structure guide

- **Skills**
  - `skills/frontend-design/` - Frontend design guidelines
  - `skills/template/` - Template skill for creating new skills

- **Documentation**
  - `README.md` - English documentation
  - `README_CN.md` - Chinese documentation (简体中文)
  - Comprehensive project structure description
  - Quick start guide with installation instructions
  - SKILL.md format reference
  - Tooling usage documentation
  - Best practices guide

- **License**
  - Apache License 2.0

### Project Structure

```
skills/
├── skills/              # Skill directories
│   ├── frontend-design/ # Frontend design guidelines
│   └── template/        # Template skill
├── scripts/             # Skill development tooling
├── agents/              # Subagent definitions
├── assets/              # Shared assets
├── references/          # Documentation schemas
├── eval-viewer/         # Evaluation viewer tool
├── package.json
├── pnpm-workspace.yaml
├── tsconfig.json
├── eslint.config.mjs
├── vitest.config.ts
├── LICENSE
├── README.md
├── README_CN.md
└── CHANGELOG.md
```

### Features Summary

| Feature | Description |
|---------|-------------|
| Skill Validation | `python scripts/quick_validate.py skills/` |
| Skill Packaging | `python scripts/package_skill.py skills/my-skill` |
| Evaluation Runner | `python scripts/run_eval.py --skill-path skills/my-skill` |
| Benchmark Aggregation | `python scripts/aggregate_benchmark.py results/` |
| Description Optimization | `python scripts/run_loop.py --skill-path skills/my-skill` |
| Eval Viewer | `python eval-viewer/generate_review.py workspace/` |
| Linting | `pnpm lint --fix` |
| Testing | `pnpm test` |