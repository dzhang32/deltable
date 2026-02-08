# deltable Agent Instructions

## Background
`deltable` is a Python library for clinical-report table comparison workflows. The current implementation is a two-step flow:
1. Convert `.rtf` to `.html` using LibreOffice (`soffice`) via `convert_rtf_to_html`.
2. Compare table structure across two HTML files via `compare_html_tables`.

Current implemented comparison outcomes:
1. `structure_match=True`: table structures are equivalent under current rules.
2. `structure_match=False`: a structural mismatch was detected, with a reason in `summary`.

## Output Contract
Comparison output should include:
- A returned `ComparisonResult` dataclass instance.
- A `structure_match: bool` field.
- A short, human-readable `summary: str` that explains the primary outcome.

## Comparison Assumptions
- Structural comparison currently runs on `.html` files.
- Each file can contain one or more tables; table-count mismatches are failures.
- Style-only differences are ignored by table parsing/comparison.
- Numeric value differences are intentionally ignored for structural matching.
- String comparisons normalize whitespace and case.
- Row order matters for string columns.

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
- Never add exports to `src/deltable/__init__.py` unless explicitly requested.

## Environment And Tooling
Use `uv` for dependency and command management.
- Never create or regenerate `uv.lock`.
- When dependencies are needed, use `uv pip install ".[dev]"`.

Setup:
```bash
uv venv --python 3.13
source .venv/bin/activate
uv pip install ".[dev]"
```

Run tests:
```bash
pytest
```

Optional coverage:
```bash
pytest --cov
```

Run pre-commit hooks:
```bash
pre-commit run --all-files
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
