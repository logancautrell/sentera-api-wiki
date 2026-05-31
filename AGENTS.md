# AGENTS.md

**AI agents only.** Read this completely before working in the repository.

## Project Overview

This repository contains:
- `sentera-wiki-builder/` — A Python tool that generates agent-ready Markdown documentation from pages defined in a `wiki_schema.yaml` file.
- `sentera-api-wiki/` — Example output for the Sentera admin GraphQL API (used both as living documentation and as a test case for the builder).

The builder is designed to be reusable for similar documentation sites.

## Key Directories

- `sentera-wiki-builder/` — The main tool (Python package with `pyproject.toml`, tests, and `build_wiki.py`).
- `sentera-api-wiki/` — Generated wiki content under `wiki/`, with `wiki_schema.yaml` and `wiki/tree.json` at the top level of the wiki.
- `.agents/` — Agent instructions and skills (including the validation process).

## Running the Builder

The recommended way to run the builder is:

```bash
cd sentera-wiki-builder
./scripts/run.sh
```

This handles dependency syncing and execution. Pass any arguments you give to `build_wiki.py`:

```bash
./scripts/run.sh --verbose
./scripts/run.sh --dry-run
```

See `sentera-wiki-builder/AGENTS.md` and `sentera-wiki-builder/README.md` for details.

## Testing & Quality

- Tests live in `sentera-wiki-builder/tests/`.
- The test suite targets high coverage on the core builder logic.
- Run with coverage: `uv run pytest --cov=build_wiki --cov-report=term-missing`

## Workflow for Changes

1. Read the relevant `AGENTS.md` (root + subdirectory).
2. Make the minimal correct change.
3. Run tests + any linting in the affected package.
4. Update documentation and agent instructions if conventions change.
5. Commit only when clean.

## Open Source Notes

This project is intended for public release. Keep documentation timeless. Remove dated internal history, debug comments, and tool-specific artifacts when they no longer serve external contributors.


