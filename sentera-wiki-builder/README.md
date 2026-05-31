# Sentera API Wiki Builder

Builds a clean, hierarchical Markdown wiki from the Sentera admin API documentation.

## Quick Start

All commands below assume you are in the root of the repository.

See [AGENTS.md](AGENTS.md) for maintenance and build instructions.

The easiest way to get started (from the repository root):

```bash
cd sentera-wiki-builder
./scripts/run.sh
```

This will run `uv sync` followed by `uv run build_wiki.py`.

You can also pass arguments through:

```bash
./scripts/run.sh --verbose
./scripts/run.sh --dry-run
```

## How It Works

1. Reads `wiki_schema.yaml` (your single source of truth) and validates its structure
2. Before writing anything, rotates any previous generated content into `_archive/<timestamp>/` (+ zip) for safety
3. For each URL:
   - Fetches the live page
   - Parses using **targeted BeautifulSoup against the site's stable component classes** (`.field-entry` etc.) — deliberately chosen middle ground between fragile regex and heavy LLM/browser tools
   - Renders rich Markdown (fields, deprecations, nested argument tables, examples, prose for howtos)
   - Writes to the URL-derived folder tree
4. Generates accurate `wiki/tree.json` (canonical index for agents)

## Frontmatter Schema (per file)

```yaml
---
url: "..."
kind: "query" | "mutation" | "howto" | "object" | ...
title: "..."
description: "..."
parent: null | "path/to/parent.md"
children: ["path/to/child1.md", ...]
tags: []
last_fetched: "..."
---
```

When entries in `wiki_schema.yaml` use the `children:` key, the parent page and pure-child pages receive populated `parent` / `children` values (paths) for navigation.

## Adding New Pages

Just add the URL to `wiki_schema.yaml`. The file is validated on load (required fields + correct types are enforced; extra fields only warn).

```yaml
- url: "https://admin.sentera.com/api/docs/mutation/create_file_upload/"
  tags: ["file-upload", "core"]
```

Then re-run the builder.

## Live Mode vs Sandbox

- Without network (or missing deps): The builder still validates the schema, derives paths, and produces a `tree.json` with placeholders.
- With network: It fetches live pages from the source docs and generates full Markdown (including field tables and examples) for every entry in `wiki_schema.yaml`.

## Output Structure

Generated Markdown lives under the `wiki/` subfolder.
`wiki_schema.yaml` lives at the root of `sentera-api-wiki/`.
`tree.json` lives inside `wiki/` (alongside the generated content).

```
sentera-api-wiki/
├── wiki_schema.yaml
├── wiki/
│   ├── tree.json
│   ├── WIKI.md
│   ├── query/
│   │   └── catalog.md
│   ├── mutation/
│   │   └── update_shape.md
│   └── uploading_files/
│       └── index.md
└── ...
```

## Notes

This tool is intentionally lightweight. It uses BeautifulSoup for structured extraction rather than heavy scraping frameworks or LLMs for the core parsing. High-signal curation (rich notes, constraints, cross-references) is still expected after generation.

