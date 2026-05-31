# Sentera Wiki Builder

A reusable Python toolkit that generates clean, structured Markdown documentation from `wiki_schema.yaml` definitions.

## Components

- **`sentera-wiki-builder/`** — The core tool. It reads page definitions from a YAML schema and produces navigable Markdown output (including `tree.json` for programmatic use).
- **`sentera-api-wiki/`** — A complete, living example wiki for the Sentera admin GraphQL API. Serves as both reference documentation and a test case for the builder.
- **`.agents/`** — Two specialized skills: `wiki-agent-validation` (audits generated wikis for fidelity against live source documentation) and `wiki-assistant` (turns natural-language requests into precise wiki coverage and structured GraphQL data).
- **`examples/`** — A minimal example schema and a generated snapshot (May 31, 2026) for reference.

## Quick Start

```bash
cd sentera-wiki-builder
./scripts/run.sh
```

The `run.sh` script handles dependency installation and passes arguments to `build_wiki.py`.

Common options: `--verbose`, `--dry-run`.

See `sentera-wiki-builder/README.md` for detailed usage and `sentera-wiki-builder/AGENTS.md` for development guidelines.

## Project Structure

```
.
├── sentera-wiki-builder/     # The reusable generation tool
├── sentera-api-wiki/         # Example wiki output and schema
├── examples/                 # Example schema and snapshot
└── .agents/                  # Specialized skills (validation + research)
```

## Workflow

1. Define or edit `wiki_schema.yaml`.
2. Run the builder.
3. (Optional) Use the validation skill to audit output quality.

Full instructions and agent tooling live in the `sentera-wiki-builder/` directory.

---

Built with Grok • May 2026