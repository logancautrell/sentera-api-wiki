---
name: wiki-agent-validation
description: Audit generated Sentera API wiki for fidelity against live source docs after any wiki_schema.yaml change or regeneration. Verifies structure, locations, and content accuracy.
---

# wiki-agent-validation

Verify that `sentera-api-wiki/` faithfully represents `wiki_schema.yaml` from https://admin.sentera.com/api/docs/.

## Process

1. Regenerate wiki after schema edits: `cd sentera-wiki-builder && ./scripts/run.sh`
2. Load `sentera-api-wiki/wiki/tree.json` first for machine index.
3. Run structural, fidelity, and hygiene checks below.
4. Fix issues or explicitly accept them before sign-off.

## Checks

**Structural / Location**
- `wiki_schema.yaml` at `sentera-api-wiki/` root
- `tree.json` at `wiki/tree.json` (no `_meta/`)
- All `.md` files under `wiki/`
- No stray folders at `sentera-api-wiki/` root

**Content Fidelity (per schema entry)**
- GraphQL pages: `url`, `kind`, `tags`, `children` match `tree.json`; field tables and deprecations match live source; nested args captured
- Prose pages: major sections and rules present; no fabricated content

**Quality / Hygiene**
- No example bloat on catalog pages
- Recent `last_fetched` timestamps
- `WIKI.md` present and correct
- No `_meta/` references remain

## Helpers
- Builder: `sentera-wiki-builder/scripts/run.sh`
- Automated report: `cd sentera-wiki-builder && uv run python ../.agents/skills/wiki-agent-validation/scripts/audit_report.py`

## Sign-off
Mark validated only when all listed pages exist, `tree.json` matches schema, no critical omissions or fabrications, and layout rules are followed. Document findings clearly.