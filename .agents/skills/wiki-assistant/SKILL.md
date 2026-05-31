---
name: wiki-assistant
description: Convert vague NLP or implementation requests into minimal high-signal wiki coverage and precise GraphQL structured data from Sentera admin docs. Triggers on loose prompts about tasks, mutations, types, or app needs. Synthesizes intent, curates schema, runs builder, delivers extracts or pages.
---

# wiki-assistant

Expert at turning vague or implementation-oriented requests into high-signal wiki pages and structured GraphQL data from https://admin.sentera.com/api/docs/.

## Mandatory Process

1. **Synthesize Intent**  
   Articulate the user's real goal in one sentence (reference docs vs precise shapes for code). Decide deliverable: wiki, rich extracts via helpers, or hybrid. For loose NLP prompts, run `--synthesize-intent "prompt"` first (or call `synthesize_intent()` from build_wiki).

2. **Research**  
   Use builder helpers (invoke via `cd sentera-wiki-builder && ./scripts/run.sh --flag` or direct import in uv env):  
   - `--inspect-docs` or `--inspect-docs --json` for site map  
   - `--get-type-details TypeName --json` for fields/enums  
   - `--get-mutation-signature mut1 mut2 --json` for input/return shapes  
   - `--get-query-signature query --json`  
   - `--extract-page-links URL --json` and `--find-related keyword --json` for discovery  
   - `--extract-main-content URL --json` for prose guides  
   Reuse `parse_page` and `extract_fields` from build_wiki.py.

3. **Curate**  
   Edit `sentera-api-wiki/wiki_schema.yaml` with minimal, tagged entries. Pages listed under `children` of an entry are generated with hierarchy links (parent set in frontmatter + tree); promote to direct top-level entries when you need custom tags or explicit top-level placement in the index.

4. **Generate**  
   Run `cd sentera-wiki-builder && ./scripts/run.sh [--verbose]` to rebuild wiki from schema.

5. **Deliver & Validate**  
   Return the exact data the user needs (signatures, field tables, enums) plus any wiki changes. Run `wiki-agent-validation` skill. Confirm against original intent model.

## Principles

- High signal only. Prune aggressively — relatedness alone does not justify inclusion.
- Implementation requests favor helper extracts over generated prose pages.
- Explicit intent modeling is required for every vague prompt; surface the model to the user for correction.
- Parser and normalization logic is authoritative in build_wiki.py — do not duplicate.
- Schema edits must be purposeful; run generator only after changes.
- Maintain ≥85% test coverage in builder after modifications.

All non-obvious workflow, helper dispatch, and curation rules live here. Everything else is standard agent capability.