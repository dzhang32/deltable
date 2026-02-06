# deltable Agent Instructions

## Background
`deltable` is a Python library for comparing tables between one `.rtf` file and another `.rtf` file in clinical trial report workflows.

Current intended classification buckets:
1. `identical`: structure, style, and data are equivalent.
2. `style_diff`: data and structure are equivalent, but styling differs (for example bold headers in one file only).
3. `data_diff_within_tolerance`: structure is equivalent and values differ only within configured tolerance.
4. `data_diff_beyond_tolerance`: structure is equivalent and values differ beyond configured tolerance.
5. `structure_diff`: larger structural changes (for example missing columns or different grouping) while still being recognizably related tables.
6. `structure_diff_entirely`: structures are fundamentally different.

## Output Contract
Comparison output should include:
- A category from the classification buckets above.
- A short, human-readable summary string that explains the primary difference.
- A returned dataclass instance for the comparison result.

## Configuration
- Numeric tolerance and category thresholds must be adjustable.
- Do not hardcode comparison thresholds in a way that callers cannot override.

## Comparison Assumptions
- Each `.rtf` contains exactly one table.
- When multiple differences apply, return the category representing the biggest difference.
  Example: if both style and data differ, return the data difference category.

## Repository Context
- Source code: `src/deltable/`
- Tests: `tests/`
- Test fixtures: `tests/data/`
- Project config and dependencies: `pyproject.toml`
- Realistic clinical report table fixtures will be created incrementally as requirements are clarified.

## Agent Role
Be a practical engineering collaborator for this repository:
- Keep guidance at the right altitude: concrete and actionable, but not brittle.
- Preserve momentum by implementing requested changes after requirements are clear.
- Prefer small, testable increments over large speculative rewrites.

## Persistent Instructions
- Ask clarifying questions before starting new work.
- Keep persistent behavior rules in this file; keep task-specific details in user requests.
- Do not assume missing project context. Ask when requirements are ambiguous.
- Prefer minimal context loading and reference only files needed for the task.

## Environment And Tooling
Use `uv` for dependency and command management.

Setup:
```bash
uv venv --python 3.14
source .venv/bin/activate
uv pip install ".[dev]"
```

Run tests:
```bash
uv run pytest
```

Optional coverage:
```bash
uv run pytest --cov
```

Run pre-commit hooks:
```bash
uv run pre-commit run --all-files
```

## Development Workflow
For each new feature or behavioral change, follow this exact sequence:
1. Ask clarifying questions about expected behavior and acceptance criteria.
2. Add or update unit tests that capture the requested behavior.
3. Ask the user to review the test changes and pause until approval.
4. Implement the feature.
5. Iterate until tests pass.
6. Run pre-commit hooks and fix any reported issues.

## Definition Of Done
A change is done when all of the following are true:
- Requirements are clarified and reflected in tests.
- Relevant tests pass locally.
- Pre-commit hooks pass.
- The final summary explains what changed and any remaining risks or assumptions.
