# AGENTS.md

## Project Overview

Drum Book Tracker is a Django 6 application for organizing drum method books and tracking practice history over time. The app uses HTMX-enhanced server-rendered templates, with domain logic centered in `src/book_tracker`.

Core stack:
- Python 3.14
- Django 6
- HTMX via `django-htmx`
- `uv` for environment and command execution
- `pytest` + `pytest-django`
- `ruff` for linting/formatting
- `djlint` for Django template linting

## Repository Layout

- `src/book_tracker/`: app models, forms, views, templates, migrations
- `src/core/`: settings and project URLs
- `src/tests/`: pytest suite (apps/forms/models/views)
- `pyproject.toml`: dependencies and tool configuration
- `.pre-commit-config.yaml`: commit-time quality gates

## Setup Commands

### Local (default workflow)

1. Install and sync dependencies:
   - `uv sync --all-groups`
2. Apply database migrations:
   - `uv run python src/manage.py migrate`
3. Start dev server:
   - `uv run python src/manage.py runserver`

Notes:
- Tests use `core.settings_local_test` and SQLite test DB (`src/db_test.sqlite3`) by default.
- Local uv/pytest is the default execution path for daily development.

## Execution Policy (Critical)

- Do not run Docker or `docker compose` commands unless the user explicitly asks for it in the current chat.
- Use local `uv` commands for testing, linting, formatting, and template validation.
- If Docker parity is needed, wait for an explicit instruction before running any container workflow.

## Development Workflow (Mandatory)

### Hard Policy: Test-First (TDD)

No production code changes for features/bugfixes without a failing test first.

Required RED/GREEN loop:
1. RED: Add or update a targeted test that describes the desired behavior.
2. Verify RED: Run only that test and confirm it fails for the expected reason.
3. GREEN: Implement the minimal code needed to pass.
4. Verify GREEN: Re-run targeted tests, then run the full affected test scope.
5. REFACTOR: Clean up only while keeping tests green.
6. LINT (Critical): Run `uv run ruff check . --output-format json` and resolve all Ruff findings introduced or touched by the change before handoff.
7. TYPECHECK (Critical): Run `uvx pyrefly check --config pyproject.toml --output-format json` from the repository root and resolve type errors introduced or touched by the change before handoff.

If code is written before a failing test, delete/rework it and re-enter the cycle from RED.

## Testing Commands

Use uv locally by default.

- Run all tests:
  - `uv run pytest`
- Run a single test file:
  - `uv run pytest src/tests/apps/book_tracker/views/test_exercise_crud_views.py`
- Run a single test:
  - `uv run pytest src/tests/apps/book_tracker/views/test_exercise_crud_views.py::test_create_exercise`
- Run by pattern:
  - `uv run pytest -k "exercise and filter"`
- Stop on first failure:
  - `uv run pytest -x`
- Re-run last failures:
  - `uv run pytest --lf`
- Coverage report:
  - `uv run pytest --cov --cov-report=term-missing`

Minimum completion bar for a change:
- Targeted test(s) for changed behavior
- Full affected module/package suite
- Ruff checks run and any relevant lint issues resolved
- Pyrefly type checks run and any relevant type issues resolved
- No known failing tests caused by the change

## pytest-django Conventions

- Any DB-touching test must use `@pytest.mark.django_db` (or module-level `pytestmark`).
- Keep tests under `src/tests/` and mirror app structure when adding new tests.
- Prefer factories and fixtures over ad hoc inline object construction.
- Test behavior/outcomes, not framework internals.

## Code Style and Validation

### Python

- Lint:
  - `uv run ruff check . --output-format json`
- Auto-fix lint issues when safe:
  - `uv run ruff check . --fix --output-format json`
- Format:
  - `uv run ruff format .`

### Type Checking

- Run project type checks with explicit repo config:
  - `uvx pyrefly check --config pyproject.toml --output-format json`

Why this command:
- Passing no files keeps Pyrefly in project mode, so it uses configured project include/exclude behavior.
- `--config pyproject.toml` ensures deterministic config resolution regardless of current subdirectory.

Ruff rules are strict (`select = ["ALL"]`); respect existing per-file ignores.

### Django Templates

If any file under `src/book_tracker/templates/` changes, run djlint before handoff.

- Lint templates locally:
  - `uv run djlint src/book_tracker/templates`
- Optional auto-reformat:
  - `uv run djlint src/book_tracker/templates --reformat`

## Pre-commit

Before finalizing work (and always before committing), run:
- `uv run pre-commit run --all-files`

Expect hooks including Ruff, djlint, bandit, detect-secrets, YAML/JSON/schema checks, and other hygiene checks.

## Agent Guardrails and Safety Rules

- Make the smallest safe change set that satisfies requirements.
- Do not revert or overwrite unrelated existing workspace changes.
- Do not use destructive git commands unless explicitly requested.
- Do not run Docker or `docker compose` unless explicitly requested in this chat.
- Prefer deterministic, non-interactive commands.
- Keep behavior changes covered by tests.
- When changing templates, include template lint validation.
- When uncertain, verify with targeted tests rather than assumptions.

## PR / Handoff Checklist

Before handing off a change:
1. TDD evidence exists: failing test first, then passing implementation.
2. Targeted tests pass for changed behavior.
3. Full affected test scope passes.
4. Ruff check/format completed and relevant lint findings resolved.
5. Pyrefly type checks completed and relevant type findings resolved.
6. djlint run if templates changed.
7. `pre-commit run --all-files` is clean (or remaining issues are documented with rationale).
8. Any limitations, assumptions, or follow-up work are explicitly documented in the handoff notes.

## Command Quick Reference

- Setup: `uv sync --all-groups`
- Migrate: `uv run python src/manage.py migrate`
- Dev server: `uv run python src/manage.py runserver`
- Tests: `uv run pytest`
- Lint: `uv run ruff check . --output-format json`
- Format: `uv run ruff format .`
- Typecheck: `uvx pyrefly check --config pyproject.toml --output-format json`
- Templates: `uv run djlint src/book_tracker/templates`
- Pre-commit: `uv run pre-commit run --all-files`
