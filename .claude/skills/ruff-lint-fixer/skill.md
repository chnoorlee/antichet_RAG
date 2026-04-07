---
name: ruff-lint-fixer
description: >
  Use this skill when the user says "run lint", "fix lint errors", "ruff check",
  "lint my code", or when ruff violations appear in build output.
  Triggers include: "make lint", "ruff check", "linting errors", "format code".
  When in doubt, use this skill rather than skipping it.
license: MIT
metadata:
  version: "1.0.0"
  author: "Repository Analyst"
  priority: "high"
  category: "code-quality"
---

# Ruff Lint Fixer

## Role

You are an expert in Python code quality using ruff linter. Your job is to run ruff check, analyze violations, and apply targeted fixes following the project's linting conventions.

---

## Workflow

1. **Run Lint** — Execute `make lint` to identify all ruff violations.
2. **Analyze Output** — Parse the violations to understand which rules are failing.
3. **Auto-Fix** — Run `make fmt` to apply auto-fixes for fixable issues (unused imports, formatting, etc.).
4. **Manual Review** — For non-fixable violations (E, F errors), read the affected files and apply targeted edits.
5. **Re-run** — Execute `make lint` again to confirm all issues are resolved.
6. **Report** — Summarize what was fixed and any remaining manual changes needed.

---

## Project Conventions

- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Target Python**: 3.10+
- **Ruff rules**: E, F, I, W enabled; E501 (line too long) ignored
- **Lint command**: `ruff check .`
- **Format command**: `ruff format . && ruff check --fix .`

---

## Constraints

- NEVER modify files outside the `app/` or `tests/` directories without explicit confirmation.
- DO NOT apply `--fix` blindly — verify each change makes sense in context.
- Anti-Loop: If `make lint` fails 3 times consecutively after fixes, STOP and report the specific errors.
- Always run `make lint` after `make fmt` to ensure no regressions.

---

## Examples

**User:** "Run lint and fix any issues"

**Assistant:**

Thinking:
1. Run `make lint` to see all violations.
2. Run `make fmt` to auto-fix formatting and fixable issues.
3. Re-run `make lint` to check remaining errors.
4. Manually fix any non-fixable violations.

Uses the `bash` tool with command `make lint`
Uses the `bash` tool with command `make fmt`
