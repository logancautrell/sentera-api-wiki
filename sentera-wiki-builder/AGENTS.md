# AGENTS.md

**AI agents only.** Read this file completely before exploring, planning, or editing anything in this project. It is the single source of truth for how to work here.

## Project Structure and File Layout

This is a Python tool that generates agent-ready Markdown wikis from source documentation sites.

- Root contains: `AGENTS.md`, `README.md`, `pyproject.toml`, `build_wiki.py`, `scripts/`, and `tests/`.
- Key directories:
  - `scripts/` — Convenience scripts (e.g. `run.sh`).
  - `tests/` — Unit tests (pytest). Target ≥85% coverage (enforced by pyproject.toml).
  - No `src/` layout — the main logic lives in the single `build_wiki.py` file for simplicity.

**Discovery rule**: Prefer reading `README.md`, `pyproject.toml`, and this `AGENTS.md` first. Use `read_file` on `build_wiki.py` only when you need specific implementation details.

## Build & Run System

This project uses `uv` (not pip or poetry).

Common commands:
- `uv sync` — Install dependencies (including dev tools).
- `./scripts/run.sh` (preferred) or `uv run build_wiki.py` — Run the builder.
- `uv run pytest` — Run the test suite.
- `uv run pytest --cov=build_wiki --cov-report=term-missing` — Run tests with coverage.

For daily work, prefer the convenience script:

```bash
./scripts/run.sh --schema ../path/to/wiki_schema.yaml --output ../output-dir
```

It handles `uv sync` + `uv run` for you. You can pass any arguments to `build_wiki.py` through it.

## Formatting, Linting & Quality

Configured in `pyproject.toml`:
- Tests use `pytest` with `fail_under = 85` (in pyproject.toml) for coverage.
- Run `uv run pytest --cov=build_wiki --cov-report=term-missing` before committing significant changes.

**Mandatory before changes that affect behavior:**
1. Run the full test suite with coverage.
2. Ensure coverage does not drop below 85%.
3. Fix any new violations.

## How to Use Available Tools Correctly

- **File ops**: Use `read_file` (with offset/limit for large files like `build_wiki.py`), `edit_file`, `write_file`.
- **Running code**: Always go through `uv run` (never raw `python build_wiki.py` unless testing the shebang).
- **Validation**: After edits, run `uv run pytest --cov=build_wiki --cov-report=term-missing` and confirm the threshold is met.

## Coding Standards and Patterns

**Core principles**:
- Keep it lightweight. Avoid heavy dependencies for the core extraction path.
- The main logic lives in one file (`build_wiki.py`) by design.
- Use structured BeautifulSoup extraction against stable site classes rather than regex or LLMs for parsing.
- All public functions have clear type hints and docstrings.
- Logging is used for CLI output (see `_setup_logging`).

**Good example — main public API**:
```python
def build_wiki(
    schema_path: Path, 
    output_dir: Path, 
    dry_run: bool = False, 
    verbose: bool = False
) -> None:
    ...
```

**Good example — validation**:
```python
def _validate_wiki_schema(schema: list) -> None:
    """Raises clear ValueError on structural problems. Warns on extra fields."""
    ...
```

**CLI entrypoint pattern** (in `if __name__ == "__main__"`):
- Uses `argparse`
- Calls `_setup_logging(verbose=...)` early
- Passes `--schema`, `--output`, `--dry-run`, `-v/--verbose`
- Folded helpers (e.g. --get-query-signature as the load/"details" counterpart to --get-mutation-signature) follow identical dispatch, --json, runpy coverage, and direct import patterns.

## Workflow for Any Change

1. Read this `AGENTS.md` and the current `README.md`.
2. Explore `build_wiki.py` (and tests) only as needed using `read_file`.
3. Make the minimal correct change.
4. Run `uv run pytest --cov=build_wiki --cov-report=term-missing`.
5. Confirm coverage ≥ 85% and all tests pass.
6. If you changed public behavior or added new CLI flags, update this `AGENTS.md`.
7. Commit only when clean.

**Maintainer note**: This file governs work inside the `sentera-wiki-builder/` directory. For the generated wiki itself, see the sibling `sentera-api-wiki/AGENTS.md`.