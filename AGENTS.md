# deltable Agent Guide

## Project Summary
Goal: compute diffs/deltas between tables in .rtf files and classify differences into categories such as:
- Identical
- Different styles (e.g., bold headings in one)
- Different data (values slightly different within tolerance)
- Different data (values very different)
- Different structure (missing columns, etc.)
- Different structure entirely

The first planned milestone is to build a realistic test .rtf file containing a complex clinical study report-style table.

## Repository Structure
- `src/deltable/`: package source
- `tests/`: pytest-based unit tests
- `tests/data/`: test fixtures/data files
- `pyproject.toml`: project metadata and dependencies

## Dependencies (UV)
Dependencies are managed with `uv` per `pyproject.toml`.

Recommended setup (non-editable + dev deps):
```bash
uv venv --python 3.14
source .venv/bin/activate
uv pip install ".[dev]"
```

Notes:
- `pyproject.toml` requires Python `>=3.14`.
- `README.md` currently references `3.13` and installs the published package; prefer `pyproject.toml` for local dev.

## Tests (pytest)
Tests use `pytest` and live under `tests/`.

Run all tests:
```bash
uv run pytest
```

Optional with coverage:
```bash
uv run pytest --cov
```

## Test Data Conventions
- Place new fixtures under `tests/data/`.
- Keep sample RTFs alongside the tests that use them (e.g., `tests/data/rtf/...`).

## Near-Term Implementation Notes
- Build a complex clinical-report-like RTF table fixture that exercises:
  - multi-row headers
  - mixed alignment
  - merged cells
  - bold/italic styling
  - numeric precision/tolerance comparisons
  - missing/extra columns or rows
- Create tests that parse and compare two RTFs and assert classification buckets.

## Clarifying Questions
Always ask clarifying questions before starting new work. Do not proceed until the questions are answered.

## Development Workflow
Follow this sequence for new functionality:
1. Ask clarifying questions about the requested behavior.
2. Add a new unit test that captures the requested functionality.
3. Ask the user to review the new test and pause until they approve.
4. Implement the feature and iterate until the new test passes.
5. Run pre-commit hooks and fix any issues:
```bash
pre-commit run --all-files
```
