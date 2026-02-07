# deltable Agent Instructions

## Background
`deltable` is a Python library for comparing tables between one `.rtf` file and another `.rtf` file in clinical trial report workflows.

Current intended classification buckets:
1. `identical`: structure and data are equivalent.
2. `data_differences`: structure is equivalent and values differ.
3. `structure_differences`: structural changes are present (for example missing columns, different grouping, or incompatible layout).

## Output Contract
Comparison output should include:
- A category from the classification buckets above.
- A short, human-readable summary string that explains the primary difference.
- A returned dataclass instance for the comparison result.

## Comparison Assumptions
- Each `.rtf` contains exactly one table.
- Style-only differences are ignored for classification.
- When multiple differences apply, return the category representing the biggest difference.
  Example: if both style and data differ, return `data_differences`.

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
- Do not use or regenerate `uv.lock`.
- When dependencies are needed, use `uv pip install ".[dev]"`.

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
