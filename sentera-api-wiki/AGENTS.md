# AGENTS.md

**AI agents only.** Read this file completely before exploring or using the documentation in this directory. It is the single source of truth for working with the Sentera API Wiki.

## Project Structure and File Layout

This directory contains the generated agent-ready documentation for the Sentera admin GraphQL API.

- `wiki/` — The main documentation content (organized by `query/`, `mutation/`, `uploading_files/`, etc.)
- `wiki/tree.json` — Primary index. Always load this first.
- `wiki_schema.yaml` — Defines the source pages included in the wiki (at the root of this directory).
- `wiki/WIKI.md` — High-level overview and navigation for the generated content.
- `README.md` — Human-oriented introduction (read this for context, not for agent workflows).

**Discovery rule**: Start by reading `wiki/tree.json` and `wiki_schema.yaml`. Use `read_file` on individual `.md` files only after consulting the index.

## Primary Entry Point

**Always load `wiki/tree.json` first.** It contains the complete hierarchy, kinds, tags, paths, and stats for every page in the wiki.

## Key Files and Their Purpose

- `wiki/tree.json`: The canonical machine-readable index. Use it for discovery, filtering, and navigation.
- `wiki_schema.yaml`: The source of truth for which pages are included. Edit this (then regenerate) when the set of documented endpoints changes.
- Individual pages under `wiki/`: Self-contained reference material with frontmatter, field tables, and examples.

## How to Query This Documentation

1. Load `wiki/tree.json`.
2. Filter nodes using `kind` (query/mutation/howto) and `tags`.
3. Open specific files under `wiki/` as needed.
4. Use the YAML frontmatter and tables for structured data extraction.
5. Follow `children` references and relative links for related pages.

## Regeneration Workflow (for Any Change)

When the underlying API documentation changes or you need to add/remove pages:

1. Edit `wiki_schema.yaml` to update the list of source URLs and tags.
2. Run the builder (recommended):
   ```bash
   cd ../sentera-wiki-builder
   ./scripts/run.sh
   ```
3. The output will be written under `wiki/`, and `wiki/tree.json` will be regenerated.
4. Review the changes (especially new or modified pages) before committing.

## Important Notes

- Some pages contain additional hand-curated content (Notes sections, constraints, cross-references) beyond what is automatically extracted. These improve signal for agents.
- Prefer `wiki/tree.json` + targeted file reads over broad searches when possible.
- The documentation is regenerated from https://admin.sentera.com/api/docs/. Do not edit generated files directly.

**Scope**: This AGENTS.md applies to the `sentera-api-wiki/` directory and its contents.