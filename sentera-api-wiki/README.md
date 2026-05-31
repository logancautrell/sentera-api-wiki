# Sentera API Wiki

Structured Markdown documentation for the Sentera admin GraphQL API.

This collection provides clear, consistent reference material for the Sentera admin API, generated directly from the official documentation.

**Source**: https://admin.sentera.com/api/docs/

## What's Inside

The documentation lives in the `wiki/` folder and includes:

- **query/catalog.md** — Product catalog query
- **mutation/update_shape.md** — Update field shapes
- **uploading_files/index.md** — File upload overview (including single-part and multi-part flows)

Each page includes:

- A short description
- Input and return field tables with types and descriptions
- Examples where relevant
- YAML frontmatter with metadata for easier navigation

## Getting Started

- Browse the folders under `wiki/` by category (queries, mutations, how-tos).
- For a complete overview of all pages and their relationships, see `wiki/tree.json`.

## Keeping It Up to Date

This wiki is generated automatically. To include new pages or update existing ones:

1. Edit `wiki_schema.yaml` (at the root of this directory) to add or change source URLs.
2. Run the builder from the `sentera-wiki-builder` directory.

See the builder's documentation for details on the generation process.

## Notes

Some pages include additional hand-written context (such as usage notes or cross-references) on top of the automatically extracted information. These are maintained separately for higher signal.
