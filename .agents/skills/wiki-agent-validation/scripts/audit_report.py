#!/usr/bin/env python3
"""
wiki-agent-validation / audit_report.py

Pre-flight automated analysis of the generated wiki.
Produces objective stats to guide the manual truth audit.

Run from repo root (ensures deps via builder env):
    cd sentera-wiki-builder && uv run python ../.agents/skills/wiki-agent-validation/scripts/audit_report.py

Or after a build:
    cd sentera-wiki-builder && ./scripts/dev.sh
    uv run python ../.agents/skills/wiki-agent-validation/scripts/audit_report.py
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Resolve paths relative to this script so it works regardless of cwd
# (e.g. run via `cd sentera-wiki-builder && uv run python ../.agents/...`)
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent
WIKI_ROOT = REPO_ROOT / "sentera-api-wiki" / "wiki"
META_TREE = WIKI_ROOT / "tree.json"

# Rough patterns for the current renderer output
INPUT_HEADING = re.compile(r"^## Input Fields", re.MULTILINE)
RETURN_HEADING = re.compile(r"^## Return Fields", re.MULTILINE)
EXAMPLES_HEADING = re.compile(r"^## Examples", re.MULTILINE)
DEPRECATED = re.compile(r"Deprecated", re.IGNORECASE)
FIELD_ROW = re.compile(r"^\|\s*`[^`]+`\s*\|", re.MULTILINE)


def parse_frontmatter(text: str) -> Dict[str, Any]:
    if not text.startswith("---"):
        return {}
    try:
        end = text.index("\n---\n", 3)
        fm = text[3:end]
        return yaml.safe_load(fm) or {}
    except Exception:
        return {}


def count_table_rows(text: str, after_heading: str) -> int:
    """Count field rows in the first table after a given heading."""
    match = re.search(rf"{re.escape(after_heading)}.*?(?=^## |\Z)", text, re.DOTALL | re.MULTILINE)
    if not match:
        return 0
    section = match.group(0)
    return len(FIELD_ROW.findall(section))


def count_lines_in_section(text: str, heading: str) -> int:
    match = re.search(rf"{re.escape(heading)}.*?(?=^## |\Z)", text, re.DOTALL | re.MULTILINE)
    if not match:
        return 0
    return len(match.group(0).splitlines())


def analyze_page(md_path: Path) -> Dict[str, Any]:
    text = md_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)

    analysis: Dict[str, Any] = {
        "path": str(md_path.relative_to(WIKI_ROOT)),
        "title": fm.get("title"),
        "kind": fm.get("kind"),
        "last_fetched": fm.get("last_fetched"),
        "tags": fm.get("tags", []),
        "input_fields": 0,
        "return_fields": 0,
        "has_deprecation": bool(DEPRECATED.search(text)),
        "example_lines": 0,
        "total_lines": len(text.splitlines()),
        "notes_section": bool(re.search(r"^## Notes", text, re.MULTILINE)),
        "size_kb": round(md_path.stat().st_size / 1024, 1),
    }

    if INPUT_HEADING.search(text):
        analysis["input_fields"] = count_table_rows(text, "## Input Fields")

    if RETURN_HEADING.search(text):
        analysis["return_fields"] = count_table_rows(text, "## Return Fields")

    if EXAMPLES_HEADING.search(text):
        analysis["example_lines"] = count_lines_in_section(text, "## Examples")

    # Heuristic bloat flag
    analysis["example_bloat"] = analysis["example_lines"] > 80

    return analysis


def main() -> None:
    if not WIKI_ROOT.exists():
        print(f"ERROR: {WIKI_ROOT} does not exist. Run the builder first.")
        sys.exit(1)

    pages = sorted(p for p in WIKI_ROOT.rglob("*.md") if p.name != "WIKI.md")

    print("=" * 70)
    print("WIKI AGENT VALIDATION — PRE-FLIGHT AUDIT REPORT")
    print(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    print(f"Wiki root: {WIKI_ROOT}")
    print("=" * 70)
    print()

    results: List[Dict[str, Any]] = []
    for p in pages:
        try:
            res = analyze_page(p)
            results.append(res)
        except Exception as e:
            print(f"Failed to analyze {p}: {e}")

    # Summary table
    print(f"{'Page':<35} {'Kind':<8} {'In':>4} {'Ret':>4} {'ExLines':>7} {'Bloat':<6} {'Size':>7}")
    print("-" * 70)
    for r in results:
        bloat = "⚠️ YES" if r["example_bloat"] else "no"
        print(
            f"{r['path']:<35} "
            f"{r['kind']:<8} "
            f"{r['input_fields']:>4} "
            f"{r['return_fields']:>4} "
            f"{r['example_lines']:>7} "
            f"{bloat:<6} "
            f"{r['size_kb']:>6}k"
        )

    print()
    print("--- Detailed Findings ---")
    for r in results:
        flags = []
        if r["example_bloat"]:
            flags.append("EXAMPLE BLOAT (high noise risk)")
        if not r["has_deprecation"] and r["kind"] in ("mutation", "query"):
            # Deprecations are optional; do not flag absence.
            pass
        if r["total_lines"] > 400:
            flags.append("Very large file")

        print(f"\n{r['path']}")
        print(f"  Title: {r['title']}")
        print(f"  last_fetched: {r['last_fetched']}")
        print(f"  Fields: {r['input_fields']} input / {r['return_fields']} return")
        print(f"  Examples section: {r['example_lines']} lines")
        print(f"  File size: {r['size_kb']} KB, total lines: {r['total_lines']}")
        if flags:
            print(f"  Flags: {', '.join(flags)}")

    # Tree sanity
    if META_TREE.exists():
        try:
            tree = json.loads(META_TREE.read_text()) or {}
            print(f"\ntree.json sanity:")
            print(f"  Total nodes: {len(tree.get('nodes', []))}")
            print(f"  Generated at: {tree.get('generated_at')}")
            print(f"  Stats: {tree.get('stats')}")
        except Exception as e:
            print(f"Failed to read tree.json: {e}")

    print("\n" + "=" * 70)
    print("NEXT STEPS FOR MANUAL AUDIT:")
    print("  1. Review any pages flagged with EXAMPLE BLOAT or large size first.")
    print("  2. For each page, open the live docs URL + the .md side-by-side.")
    print("  3. Use the checklist in .agents/skills/wiki-agent-validation/SKILL.md")
    print("  4. Record findings using the structured template in the skill.")
    print("=" * 70)


if __name__ == "__main__":
    main()
