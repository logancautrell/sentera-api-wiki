#!/usr/bin/env python3
from __future__ import annotations
"""
Sentera API Wiki Builder
========================
Builds a clean, agent-ready Markdown wiki from a wiki_schema.yaml.

Usage:
    uv run build_wiki.py
    uv run build_wiki.py --schema custom.yaml --output ../my-wiki -v

The script:
- Reads wiki_schema.yaml (with structural validation) defining the pages to include
- Safely rotates previous output into `_archive/`
- Fetches and parses documentation pages using stable site structure
- Renders consistent Markdown with frontmatter, field tables (including proper "Fields" sections for object/input_object/interface pages), deprecations, and examples
- Writes output under a `wiki/` subdirectory and regenerates `tree.json`

Support for GraphQL type pages (objects, input objects, enums, scalars, interfaces) so that wiki output is more useful for implementation-oriented use cases.

Use `-v` / `--verbose` for detailed progress output. Errors are always shown.
"""

import argparse
import itertools
import json
import logging
import re
import shutil
import sys
import threading
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from collections import defaultdict

import yaml

logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool = False) -> None:
    """Configure logging.
    - Non-verbose: show INFO+ (good status + all errors/warnings)
    - Verbose: show DEBUG (detailed per-page progress)
    Errors always go to output.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )
    # Keep third-party HTTP logs quiet unless very verbose
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


class _Spinner:
    """Lightweight, stdlib-only Unicode spinner for terminal UX during long operations.

    - Braille-dot animation (beautiful on modern terminals).
    - Writes only to stderr (coexists with the existing logger which also targets stderr).
    - Automatically becomes a silent no-op when stderr is not a TTY (pytest, CI,
      output redirection, scripts). This keeps all tests clean and deterministic.
    - Safe to use via context manager or explicit start()/stop().
    - Used only for the default (non-verbose) wiki build path so that -v still
      produces an uninterrupted log stream.

    Example:
        with _Spinner("Fetching pages"):
            do_work()
    """

    SPINNER_CHARS: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, message: str = "Working", delay: float = 0.08) -> None:
        self.message = message
        self.delay = delay
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _animate(self) -> None:
        """Background animation loop. Never runs on non-TTY."""
        for char in itertools.cycle(self.SPINNER_CHARS):  # pragma: no cover (TTY animation)
            if self._stop_event.is_set():
                break
            sys.stderr.write(f"\r{char} {self.message}")
            sys.stderr.flush()
            time.sleep(self.delay)
        # Best-effort clear if loop exits naturally
        self._clear_line()  # pragma: no cover (TTY animation)

    def _clear_line(self) -> None:
        # Wipe a comfortable width (covers the message + spinner char + some margin)
        sys.stderr.write("\r" + " " * 80 + "\r")
        sys.stderr.flush()

    def start(self) -> None:
        """Start the spinner thread (no-op if already running or not on a TTY)."""
        if self._thread is not None:
            return
        if not sys.stderr.isatty():  # pragma: no cover (TTY detection)
            return  # critical: no animation in tests/CI/pipes
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()  # pragma: no cover (TTY animation)

    def stop(self) -> None:
        """Stop the spinner and clear its line (safe to call multiple times)."""
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join(timeout=0.5)  # pragma: no cover (TTY animation)
        self._clear_line()
        self._thread = None  # pragma: no cover (TTY animation)

    def __enter__(self) -> "_Spinner":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()


# Try to import optional dependencies
try:
    import requests
    from bs4 import BeautifulSoup, Tag
    HAS_DEPS = True
except ImportError:  # pragma: no cover (missing optional dependencies at import time)
    HAS_DEPS = False
    Tag = Any  # type: ignore[misc,assignment]  # for type hints when bs4 missing

# =============================================================================
# CONFIG
# =============================================================================
DEFAULT_WIKI_SCHEMA = Path(__file__).parent.parent / "sentera-api-wiki" / "wiki_schema.yaml"
DEFAULT_OUTPUT = Path(__file__).parent.parent / "sentera-api-wiki"

# Generated Markdown content is isolated under this subfolder.
# wiki_schema.yaml and tree.json live alongside the generated content in wiki/.
WIKI_SUBDIR = "wiki"


# =============================================================================
# ROTATION
# =============================================================================

def rotate_wiki(output_dir: Path, keep_zip: bool = True, content_subdir: Optional[str] = None) -> Optional[Path]:
    """
    Archive the current *generated* wiki content before a fresh build.

    When content_subdir is provided (recommended), only the contents of
    output_dir / content_subdir are considered for rotation. This keeps
    wiki_schema.yaml, root docs, etc. completely untouched.

    Falls back to scanning the output root for legacy layouts.
    """
    if not output_dir.exists():
        return None

    protected_names = {
        "_meta", "_archive", "AGENTS.md", "README.md", "WIKI.md",  # never rotate; user may maintain
        "Agents.md", "agents.md"
    }
    generated_dir_names = {"query", "mutation", "object", "uploading_files", "single_part", "multi_part", "howto"}

    scan_root = output_dir / content_subdir if content_subdir else output_dir

    if not scan_root.exists():
        logger.info("  (no generated content directory to archive yet)")
        return None

    to_archive = []
    for item in scan_root.iterdir():
        if item.name in protected_names:
            continue
        if item.is_dir() and (content_subdir or item.name in generated_dir_names):
            to_archive.append(item)
        elif item.is_file() and item.suffix == ".md" and item.name not in protected_names:
            to_archive.append(item)

    # One-time legacy migration help: if we're targeting wiki/ but old flat
    # generated folders still exist directly under output root, archive them too.
    if content_subdir and ((output_dir / "query").exists() or (output_dir / "mutation").exists()):
        for name in generated_dir_names:
            p = output_dir / name
            if p.exists() and p.is_dir():
                to_archive.append(p)

    if not to_archive:
        logger.info("  (no generated content to archive)")
        return None

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    archive_dir = output_dir / "_archive" / ts
    archive_dir.mkdir(parents=True, exist_ok=True)

    for item in to_archive:
        target = archive_dir / item.name
        if target.exists():
            shutil.rmtree(target) if target.is_dir() else target.unlink()
        shutil.move(str(item), target)

    zip_path = None
    if keep_zip:
        zip_path = archive_dir.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in archive_dir.rglob("*"):
                if p.is_file():
                    zf.write(p, p.relative_to(archive_dir.parent))

    logger.info(f"  ↻ Rotated previous wiki content → {archive_dir}")
    if zip_path:
        logger.info(f"     (also zipped to {zip_path.name})")

    return archive_dir


# =============================================================================
# PARSING
# =============================================================================

FIELD_REGEX = re.compile(r'-\s+`([^`]+)`\s+\(`([^`]+)`\)\s*[–-]\s*(.+)')




def parse_field_list(text: str) -> List[Dict[str, str]]:
    """Legacy fallback parser (old regex style). Kept for edge cases only."""
    fields = []
    for line in text.splitlines():
        match = FIELD_REGEX.match(line.strip())
        if match:
            fields.append({
                "name": match.group(1),
                "type": match.group(2),
                "description": match.group(3).strip()
            })
    return fields


def extract_section(soup: BeautifulSoup, heading: str) -> Optional[str]:
    """Legacy text extractor under a heading. Used as fallback only."""
    h = soup.find(lambda tag: tag.name in ("h2", "h3") and heading.lower() in tag.get_text(strip=True).lower())
    if not h:
        return None
    content = []
    for sibling in h.find_next_siblings():
        if sibling.name in ("h2", "h3"):
            break
        content.append(sibling.get_text(separator=" ", strip=True))
    return "\n".join(content) if content else None


# -----------------------------------------------------------------------------
# Structured extraction using the stable CSS classes emitted by the docs site.
# -----------------------------------------------------------------------------

def _find_heading(soup: BeautifulSoup, text_contains: str) -> Optional[Tag]:
    """Find first h2/h3 whose text contains the given substring (case-insensitive)."""
    text_contains = text_contains.lower()
    return soup.find(lambda t: t.name in ("h2", "h3") and text_contains in t.get_text(strip=True).lower())


def _parse_field_entry(div: Tag) -> Dict[str, Any]:
    """
    Parse a single .field-entry div into a rich field dict.

    Captures:
      - name, type (with link if present)
      - description
      - deprecation (if .deprecation-notice present)
      - nested arguments table (lives inside .description-wrapper after the description p)
    """
    field: Dict[str, Any] = {}

    name_span = div.find(class_="field-name")
    if name_span:
        raw = name_span.get_text(separator=" ", strip=True)
        if " (" in raw:
            field["name"] = raw.split(" (", 1)[0].strip()
        else:
            field["name"] = raw.strip()

        code = name_span.find("code")
        if code:
            a = code.find("a")
            field["type"] = a.get_text(strip=True) if a else code.get_text(strip=True)
            if a and a.get("href"):
                field["type_url"] = a["href"]
        else:
            m = re.search(r'\(\s*([^)]+?)\s*\)', raw)
            field["type"] = m.group(1).strip() if m else ""

    desc_wrap = div.find(class_="description-wrapper")
    if desc_wrap:
        deprecation_div = desc_wrap.find(class_="deprecation-notice")
        if deprecation_div:
            dep_text = deprecation_div.get_text(separator=" ", strip=True)
            # Clean the label
            dep_text = re.sub(r'^Deprecation notice\s*', '', dep_text, flags=re.I).strip()
            field["deprecation"] = dep_text

        # Description: prefer the first <p> that is not inside a deprecation-notice
        desc_p = None
        for p in desc_wrap.find_all("p", recursive=False):
            if p.find_parent(class_="deprecation-notice"):
                continue
            desc_p = p
            break
        if desc_p:
            field["description"] = desc_p.get_text(separator=" ", strip=True)
        else:
            # fallback
            field["description"] = desc_wrap.get_text(separator=" ", strip=True)

        # Arguments table is inside the wrapper (after the description p)
        table = desc_wrap.find("table", class_="arguments")
        if table:
            field["arguments"] = _parse_arguments_table(table)

    # Also check immediate following sibling table as a secondary location
    if "arguments" not in field:
        table = div.find_next_sibling("table", class_="arguments")
        if table:
            field["arguments"] = _parse_arguments_table(table)

    return field


def _parse_arguments_table(table: Tag) -> List[Dict[str, str]]:
    """Parse <table class="arguments"> into list of {name, type, description}."""
    args = []
    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]  # skip header
    for tr in rows:
        tds = tr.find_all("td")
        if len(tds) >= 2:
            name = tds[0].get_text(strip=True)
            typ = tds[1].get_text(strip=True)
            desc = tds[2].get_text(separator=" ", strip=True) if len(tds) > 2 else ""
            args.append({"name": name, "type": typ, "description": desc})
    return args


def extract_fields(soup: BeautifulSoup, section: str) -> List[Dict[str, Any]]:
    """
    Extract all .field-entry blocks under the given section heading ("Input fields", "Return fields", etc).
    Stops at the next h2/h3.

    This is the canonical implementation for structured field extraction from Sentera docs pages.
    It is intended for reuse by other tools (e.g. the wiki-assistant skill scripts) in addition to
    the wiki builder itself. The returned field dicts are rich (include optional "deprecation" and
    "arguments" keys when present in the source).
    """
    h = _find_heading(soup, section)
    if not h:
        return []

    fields = []
    for sib in h.find_next_siblings():
        if sib.name in ("h2", "h3"):
            break
        if isinstance(sib, Tag) and "field-entry" in (sib.get("class") or []):
            f = _parse_field_entry(sib)
            if f.get("name"):
                fields.append(f)
    return fields


def extract_examples(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Collect GraphQL/JSON examples under the Examples section."""
    h = _find_heading(soup, "example")
    if not h:
        return []

    examples = []
    for pre in h.find_next_siblings("pre"):
        code = pre.get_text(strip=True)
        if not code:
            continue
        lang = "graphql" if any(k in code.lower() for k in ["query", "mutation", "{"]) else "json"
        examples.append({"type": lang, "code": code})
        if len(examples) >= 4:  # reasonable cap
            break
    return examples


def extract_deprecations(soup: BeautifulSoup) -> List[str]:
    """
    Collect any page-level deprecation notices (outside individual fields).

    Stable helper intended for reuse by tools that import the parser (e.g. wiki-assistant scripts).
    """
    notices = []
    for div in soup.find_all(class_="deprecation-notice"):
        # Only collect if not already inside a field-entry we parsed
        if not div.find_parent(class_="field-entry"):
            txt = div.get_text(separator=" ", strip=True)
            if txt:
                notices.append(txt)
    return notices


# =============================================================================
# Wiki-Assistant Skill Helpers (folded in from .agents/skills/wiki-assistant/scripts/)
# =============================================================================

INTENT_SYNTHESIS_TEMPLATE = """
================================================================================
INTENT SYNTHESIS — WIKI-ASSISTANT
================================================================================

Raw user prompt:
"{prompt}"

--------------------------------------------------------------------------------
1. USER GOAL (in one sentence)
--------------------------------------------------------------------------------
[Infer the real objective. What is the user ultimately trying to achieve?]

--------------------------------------------------------------------------------
2. INFORMATION NEED TYPE (choose one or more)
--------------------------------------------------------------------------------
[ ] Broad reference / exploration ("tell me about this area")
[ ] Implementation / coding ("I need the exact shapes and semantics to write code")
[ ] Workflow / how-to ("how do I accomplish X end-to-end?")
[ ] Specific data extraction ("what are the possible values for Y?")

Primary: ________________

--------------------------------------------------------------------------------
3. SPECIFIC ARTIFACTS THE USER NEEDS
--------------------------------------------------------------------------------
- Mutation signatures / input shapes for: ...
- Type details (fields + descriptions) for: ...
- Enum values + meanings for: ...
- Prose / workflow guidance from: ...
- Other: ...

--------------------------------------------------------------------------------
4. RECOMMENDED DELIVERABLE STRATEGY
--------------------------------------------------------------------------------
[ ] Primarily update wiki_schema.yaml + run generator (broad reference)
[ ] Primarily use helper scripts for rich structured extracts (implementation)
[ ] Hybrid (recommended for most real requests)
[ ] Other: ...

Rationale: ...

--------------------------------------------------------------------------------
5. KEY SEARCH TERMS / STARTING PAGES
--------------------------------------------------------------------------------
Keywords to feed find_related / extract_page_links:
- ...

High-value starting pages (from prior knowledge or inspect_docs):
- ...

--------------------------------------------------------------------------------
6. SUCCESS CRITERIA (how to verify the user was helped)
--------------------------------------------------------------------------------
After this work, the user will be able to:
- ...

================================================================================
Next step: Use the above as your Intent Model, then proceed to Research.
================================================================================
"""


def synthesize_intent(prompt: str) -> str:
    """
    Return the structured intent synthesis template filled with the given raw user prompt.

    Recommended first action for vague/natural-language requests (e.g. "I need tasks and flight parameters for my planning app").
    Produces a structured template to force explicit intent modeling before research or schema edits.

    The returned string is designed to be copied into an agent's reasoning to force
    explicit modeling of the user's underlying goal before any schema changes or
    research with the other helpers.

    Example:
        output = synthesize_intent("I need to build flight plans in code")
        print(output)
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty for intent synthesis")
    return INTENT_SYNTHESIS_TEMPLATE.format(prompt=prompt.strip())


DOCS_BASE = "https://admin.sentera.com/api/docs"


def _normalize_docs_href(href: str) -> str:
    """Robustly turn a sidebar href into a full docs URL."""
    if href.startswith("http"):
        return href
    # Remove any leading /api/docs/ prefix that is present
    href = href.lstrip("/")
    if href.startswith("api/docs/"):
        href = href[len("api/docs/"):]
    return urljoin(DOCS_BASE.rstrip("/") + "/", href)


def inspect_docs() -> List[List[Dict[str, Any]]]:
    """
    Fetch the Sentera docs main page and return a structured view of the navigation menus.

    This gives a high-level map of categories (Guides, Queries, Mutations, Objects, etc.)
    so agents can reason about where to look for content related to a user request.

    Returns:
        A list of menus. Each menu is a list of dicts with "title" and "url".
        Example:
            [
                [{"title": "Authentication", "url": "..."}],
                [{"title": "Mutations", "url": "..."} , ...]
            ]

    Safe to import and call from other tools. Reuses the builder's HTML parsing.

    Raises:
        RuntimeError: If required dependencies (requests, beautifulsoup4) are missing.
    """
    if not HAS_DEPS:
        raise RuntimeError(
            "inspect_docs requires requests and beautifulsoup4. "
            "Run: uv add requests beautifulsoup4"
        )

    resp = requests.get(DOCS_BASE, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    sidebar = soup.find(id="sidebar")
    if not sidebar:
        return []

    menus: List[List[Dict[str, Any]]] = []
    for ul in sidebar.find_all("ul", class_="menu-root"):
        items: List[Dict[str, Any]] = []
        for li in ul.find_all("li", recursive=False):
            a = li.find("a", href=True)
            if a:
                text = a.get_text(strip=True)
                href = _normalize_docs_href(a["href"])
                items.append({"title": text, "url": href})
        if items:
            menus.append(items)
    return menus


def get_mutation_signature(name: str) -> Dict[str, Any]:  # pragma: no cover (CLI helper surface)
    """
    Given a mutation name, return a compact signature focused on the direct input and return types.

    This is one of the two primary tools for implementation-oriented requests in the wiki-assistant skill
    ("I need the exact shapes so I can write code").

    It deliberately returns a minimal, high-signal view:
      - main_input_type / main_return_type (first item, for the common case)
      - all_input_fields / all_return_fields (full lists for completeness)

    Internally reuses the canonical `parse_page` + `extract_fields` from the builder for robustness
    and to eliminate duplicated field-entry walking logic.

    Returns a dict with keys: name, url, title, main_input_type, main_return_type,
    all_input_fields, all_return_fields, or "error" on failure.
    """
    url = f"{DOCS_BASE}/mutation/{name}/"

    if not HAS_DEPS:
        return {"name": name, "url": url, "error": "Missing dependencies (requests, beautifulsoup4)"}

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()

        # Leverage the existing rich parser
        parsed = parse_page(url, resp.text, kind_hint="mutation")

        inputs = parsed.get("inputs", []) or []
        returns = parsed.get("returns", []) or []

        # Reshape into the compact "main + all" shape the skill has historically delivered
        main_input = inputs[0] if inputs else None
        main_return = returns[0] if returns else None

        # Normalize type_url to absolute docs URLs (skill convention)
        def _normalize_field(f):
            if not f:
                return None
            typ_url = f.get("type_url", "")
            if typ_url and not typ_url.startswith("http"):
                typ_url = _normalize_docs_href(typ_url)
            return {
                "name": f.get("name"),
                "type": f.get("type"),
                "type_url": typ_url,
            }

        return {
            "name": name,
            "url": url,
            "title": parsed.get("title", name),
            "main_input_type": _normalize_field(main_input),
            "main_return_type": _normalize_field(main_return),
            "all_input_fields": [_normalize_field(f) for f in inputs],
            "all_return_fields": [_normalize_field(f) for f in returns],
        }
    except Exception as e:
        return {"name": name, "url": url, "error": str(e)}


def get_query_signature(name: str) -> Dict[str, Any]:  # pragma: no cover (CLI helper surface - integration tested)
    """
    Given a query name, return a compact signature focused on the direct input and return types.

    This is the primary tool for "load X details" / query-heavy use cases in the wiki-assistant
    subprocess (e.g. vague "I want to load field details." requests). Modeled exactly on
    get_mutation_signature: reuses parse_page(kind_hint="query") and identical output shape.

    Returns a dict with keys: name, url, title, main_input_type, main_return_type,
    all_input_fields, all_return_fields, or "error" on failure.
    """
    url = f"{DOCS_BASE}/query/{name}/"

    if not HAS_DEPS:
        return {"name": name, "url": url, "error": "Missing dependencies (requests, beautifulsoup4)"}

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()

        # Leverage the existing rich parser
        parsed = parse_page(url, resp.text, kind_hint="query")

        inputs = parsed.get("inputs", []) or []
        returns = parsed.get("returns", []) or []

        # Reshape into the compact "main + all" shape the skill has historically delivered
        main_input = inputs[0] if inputs else None
        main_return = returns[0] if returns else None

        # Normalize type_url to absolute docs URLs (skill convention)
        def _normalize_field(f):
            if not f:
                return None
            typ_url = f.get("type_url", "")
            if typ_url and not typ_url.startswith("http"):
                typ_url = _normalize_docs_href(typ_url)
            return {
                "name": f.get("name"),
                "type": f.get("type"),
                "type_url": typ_url,
            }

        return {
            "name": name,
            "url": url,
            "title": parsed.get("title", name),
            "main_input_type": _normalize_field(main_input),
            "main_return_type": _normalize_field(main_return),
            "all_input_fields": [_normalize_field(f) for f in inputs],
            "all_return_fields": [_normalize_field(f) for f in returns],
        }
    except Exception as e:
        return {"name": name, "url": url, "error": str(e)}


def get_type_details(name: str) -> Dict[str, Any]:  # pragma: no cover (CLI helper surface)
    """
    Given a type name (e.g. FlightTask, FlightTaskImport, TaskStatus, or "Field"), extract
    structured fields or enum values.

    This is one of the two primary tools for implementation-oriented requests
    in the wiki-assistant skill ("I need the exact data model shapes for code").

    It tries common type URL patterns (object, input_object, interface, enum, scalar)
    and returns a compact shape with 'fields' or 'enum_values'.

    Heavily reuses the canonical parser for field extraction.
    Now normalizes common GraphQL type casing (e.g. PascalCase "Field") to lowercase
    docs slugs ("field") for robust lookups.
    """
    if not HAS_DEPS:
        return {"name": name, "error": "Missing dependencies (requests, beautifulsoup4)"}

    # Normalize name for URL slugs: try original first (avoids extra 404s for common PascalCase like "FlightTask"),
    # then .lower() fallback only on failure (preserves "Field" audit case via docs slug "field").
    # Tradeoff: 1 extra request only for the rare casing-mismatch case (e.g. GraphQL Pascal vs lowercase slug).
    # Return keeps the canonical "name" arg as passed (title from page h1).
    slug_variants = [name or ""]
    if name and name.lower() != name:
        slug_variants.append(name.lower())
    # Explicit loop (matches _extract_enum_values pattern in this file; no side-effecting comp)
    seen = set()
    deduped = []
    for s in slug_variants:
        if s and s not in seen:
            seen.add(s)
            deduped.append(s)
    slug_variants = deduped

    for slug in slug_variants:
        candidates = [
            f"{DOCS_BASE}/object/{slug}/",
            f"{DOCS_BASE}/input_object/{slug}/",
            f"{DOCS_BASE}/interface/{slug}/",
            f"{DOCS_BASE}/enum/{slug}/",
            f"{DOCS_BASE}/scalar/{slug}/",
        ]

        for url in candidates:
            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                h1 = soup.find("h1")
                title = h1.get_text(strip=True) if h1 else name

                kind = "unknown"
                if "/object/" in url:
                    kind = "object"
                elif "/input_object/" in url:
                    kind = "input_object"
                elif "/interface/" in url:
                    kind = "interface"
                elif "/enum/" in url:
                    kind = "enum"
                elif "/scalar/" in url:
                    kind = "scalar"

                fields = []
                enum_values = []

                if kind in ("object", "input_object", "interface"):
                    # Reuse the rich field extraction
                    parsed = parse_page(url, resp.text, kind_hint=kind)
                    fields = parsed.get("fields", []) or parsed.get("inputs", [])
                elif kind == "enum":
                    # Use the specialized enum extraction (ported from skill for high-signal output)
                    enum_values = _extract_enum_values(soup)

                return {
                    "name": name,
                    "url": url,
                    "title": title,
                    "kind": kind,
                    "fields": fields,
                    "enum_values": enum_values,
                }
            except Exception:
                continue

    return {"name": name, "error": "Type page not found or unparseable"}


def _extract_enum_values(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract enum values.

    Supports current site structure (h3 "Values" + h4.name + div.description-wrapper),
    legacy .field-entry (for tests), and li/code fallback.
    """
    values: List[Dict[str, str]] = []
    seen = set()

    # Modern structure (live site): h3 containing "Values", then h4 + description-wrapper siblings
    for h3 in soup.find_all("h3"):
        if "value" in h3.get_text(strip=True).lower():
            sib = h3.find_next_sibling()
            while sib:
                if getattr(sib, "name", None) in ("h2", "h3"):
                    break
                if getattr(sib, "name", None) == "h4":
                    name = sib.get_text(strip=True).strip()
                    if name and name not in seen:
                        seen.add(name)
                        desc = ""
                        nxt = sib.find_next_sibling()
                        while nxt and getattr(nxt, "name", None) and not str(nxt.name).startswith("h"):
                            cls = " ".join(getattr(nxt, "get", lambda k, d=None: [])( "class", []) or [])
                            if nxt.name == "div" and "description-wrapper" in cls:
                                desc = nxt.get_text(separator=" ", strip=True)
                                break
                            nxt = getattr(nxt, "find_next_sibling", lambda: None)()
                        values.append({"value": name, "description": desc})
                sib = getattr(sib, "find_next_sibling", lambda: None)()
            break  # only the first Values section

    if not values:
        for entry in soup.find_all(class_="field-entry"):
            name_span = entry.find(class_="field-name")
            if name_span:
                name = name_span.get_text(strip=True)
                if name in seen:
                    continue
                seen.add(name)
                desc = ""
                desc_wrap = entry.find(class_="description-wrapper")
                if desc_wrap:
                    desc = desc_wrap.get_text(separator=" ", strip=True)
                values.append({"value": name, "description": desc})

    if not values:
        for li in soup.select("li"):
            text = li.get_text(separator=" ", strip=True)
            code = li.find("code")
            if code:
                name = code.get_text(strip=True)
                if name and name not in seen:
                    seen.add(name)
                    values.append({"value": name, "description": text.replace(name, "", 1).strip()})

    return values


def classify_url(url: str) -> str:
    """Classify a docs URL into a high-level category (guide, mutation, object, etc.).
    Used by extract_page_links for dependency scoping.
    """
    path = urlparse(url).path.lower()

    if "/uploading_files" in path or "/authentication" in path or "/importing_data" in path:
        return "guide"
    if "/operation/mutation/" in path or "/mutation/" in path:
        return "mutation"
    if "/operation/query/" in path or "/query/" in path:
        return "query"
    if "/object/" in path:
        return "object"
    if "/interface/" in path:
        return "interface"
    if "/enum/" in path:
        return "enum"
    if "/input_object/" in path:
        return "input_object"
    if "/scalar/" in path:
        return "scalar"
    if "/directive/" in path:
        return "directive"
    return "other"


def extract_page_links(url: str) -> Dict[str, Any]:  # pragma: no cover (CLI helper surface)
    """
    Fetch a Sentera docs page and extract all internal links to other documentation pages,
    classified by category (mutation, object, guide, etc.).

    Primary API for the folded extract_page_links.py helper. Excellent for finding
    dependencies when curating wiki_schema.yaml for workflow pages.

    Leverages the existing `parse_page` (for title/kind extraction) and the shared
    `_normalize_docs_href` / DOCS_BASE to avoid duplication of URL handling.

    Returns a dict: {url, title, links_by_category: {cat: [urls...]}, total_links}
    or {"url", "error"} on failure.
    """
    norm_url = _normalize_docs_href(url) if HAS_DEPS else url

    if not HAS_DEPS:
        return {"url": norm_url, "error": "Missing dependencies (requests, beautifulsoup4)"}

    try:
        resp = requests.get(norm_url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Leverage canonical parser for title (and kind as side-effect) to avoid duplicating h1 logic
        parsed = parse_page(norm_url, resp.text)
        title = parsed.get("title", "Untitled")

        links_by_category: Dict[str, Set[str]] = defaultdict(set)

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("#"):
                continue

            full_url = _normalize_docs_href(urljoin(norm_url, href))

            if "/api/docs" not in full_url:
                continue

            category = classify_url(full_url)
            links_by_category[category].add(full_url)

        links_dict: Dict[str, List[str]] = {cat: sorted(list(urls)) for cat, urls in links_by_category.items()}

        return {
            "url": norm_url,
            "title": title,
            "links_by_category": links_dict,
            "total_links": sum(len(v) for v in links_dict.values()),
        }
    except Exception as e:
        return {"url": norm_url, "error": str(e)}


def find_related(term: str) -> Dict[str, Any]:  # pragma: no cover (CLI helper surface)
    """
    Given a keyword or starting URL, find relevant documentation pages.

    - If term looks like http URL: fetch it and return its internal links (limited).
    - Else: keyword search against high-value candidate pages + sidebar navigation (via inspect_docs reuse).

    Useful supporting discovery tool before using the primary signature/details tools.
    Reuses `inspect_docs()` for sidebar scanning (deduplicates fetch+parse logic) and
    shared normalizer + HAS_DEPS guard.

    Returns shape matching historical skill output for compatibility.
    """
    if not HAS_DEPS:
        return {"term": term, "error": "Missing dependencies (requests, beautifulsoup4)"}

    term = term.strip()
    if not term:
        return {"term": term, "matches": []}

    if term.startswith("http"):
        try:
            norm = _normalize_docs_href(term)
            resp = requests.get(norm, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            # simple link extraction (modeled on old, but using our normalizer)
            links: Set[str] = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("#") or ("admin.sentera.com" not in href and "://" in href):
                    continue
                full = _normalize_docs_href(urljoin(norm, href))
                if "/api/docs" in full:
                    links.add(full)
            h1 = soup.find("h1")
            title = h1.get_text(strip=True) if h1 else term
            return {
                "start": {"title": title, "url": norm},
                "related": [{"url": u} for u in sorted(links)[:40]],
            }
        except Exception as e:
            return {"term": term, "error": str(e)}

    # keyword mode
    results = []
    kw = term.lower()

    # high-value candidates (guides + roots) - fetch and text search
    candidates = [
        f"{DOCS_BASE}/uploading_files/index.html",
        f"{DOCS_BASE}/authentication/index.html",
        f"{DOCS_BASE}/importing_data/index.html",
        f"{DOCS_BASE}/operation/mutation/",
        f"{DOCS_BASE}/operation/query/",
    ]
    for url in candidates:
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            if kw in soup.get_text().lower():
                h1 = soup.find("h1")
                title = h1.get_text(strip=True) if h1 else url
                results.append({"title": title, "url": url, "matched": "content"})
        except Exception:
            pass  # tolerant like original

    # sidebar via reuse of inspect_docs (excellent dedup!)
    try:
        menus = inspect_docs()
        for menu in menus:
            for item in menu:
                if kw in item.get("title", "").lower():
                    results.append({"title": item["title"], "url": item["url"], "matched": "sidebar"})
    except Exception:
        pass

    # dedup preserving order
    seen = set()
    out = []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            out.append(r)
    return {"term": term, "matches": out}


def _clean_text(text: str) -> str:
    """Collapse whitespace and strip (shared helper for content extract)."""
    return re.sub(r'\s+', ' ', text).strip()


def extract_main_content(url: str) -> Dict[str, Any]:  # pragma: no cover (CLI helper surface)
    """
    Extract human-readable main content from a Sentera docs page (title, description,
    key sections with prose, and backtick-mentioned identifiers).

    Complements the GraphQL field tools for "how do I..." / guide / workflow pages.
    For howto pages, reuses `parse_page` (kind="howto") to get title + prose_html as
    starting point, then applies targeted section walking (avoids full reimplementation).

    Returns: {url, title, description, sections: [{title, content}], mentioned_identifiers}
    or error.
    """
    norm_url = _normalize_docs_href(url) if HAS_DEPS else url

    if not HAS_DEPS:
        return {"url": norm_url, "error": "Missing dependencies (requests, beautifulsoup4)"}

    try:
        resp = requests.get(norm_url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Leverage parse_page for title (and prose_html for howtos)
        parsed = parse_page(norm_url, resp.text, kind_hint="howto" if any(x in norm_url for x in ["/uploading_files", "/single_part", "/multi_part", "/howto"]) else None)
        title = parsed.get("title", "Untitled")
        desc = ""

        # Section extraction (h2/h3 under main content, stop before Examples etc) - modeled on original
        main_content = soup.find(id="content") or soup.find("main") or soup.body
        sections: List[Dict[str, str]] = []
        if main_content:
            for heading in main_content.find_all(["h2", "h3"]):
                section_title = _clean_text(heading.get_text())
                if not section_title or section_title.lower() in ["examples", "directives"]:
                    continue
                content_parts = []
                for sib in heading.find_next_siblings():
                    if sib.name in ["h2", "h3"]:
                        break
                    if sib.name in ["p", "ul", "ol", "pre", "table"]:
                        text = _clean_text(sib.get_text(separator=" "))
                        if text and len(text) > 10:
                            content_parts.append(text)
                if content_parts:
                    sections.append({
                        "title": section_title,
                        "content": " ".join(content_parts)[:2000],
                    })

        # Mentioned identifiers via regex on full text (backticks)
        mentioned: List[str] = []
        full_text = main_content.get_text() if main_content else ""
        for match in re.finditer(r'`([a-z_][a-z0-9_]*)`', full_text, re.IGNORECASE):
            name = match.group(1)
            if len(name) > 3 and name not in mentioned:
                mentioned.append(name)
        mentioned = mentioned[:15]

        # If parse gave better desc, prefer
        if not desc and parsed.get("description"):
            desc = parsed["description"]

        return {
            "url": norm_url,
            "title": title,
            "description": desc,
            "sections": sections,
            "mentioned_identifiers": mentioned,
        }
    except Exception as e:
        return {"url": norm_url, "error": str(e)}


def get_mutation_deps(name: str) -> Dict[str, Any]:  # pragma: no cover (CLI helper surface)
    """
    Older variant: given mutation name, return direct input types and return types
    by inspecting links on the page.

    **Prefer** `get_mutation_signature` + `get_type_details` for new work (richer, uses
    canonical field parser).

    Implementation reuses `parse_page` + `extract_fields` (via the mutation path) to
    avoid duplicating the <a> href walking that the original script did. Types are
    derived from the parsed 'type' / 'type_url' on input/return fields.

    Returns {name, url, title, direct_input_types: [{name,url}], direct_return_types: [...] } or error.
    """
    url = f"{DOCS_BASE}/mutation/{name}/"

    if not HAS_DEPS:
        return {"name": name, "url": url, "error": "Missing dependencies (requests, beautifulsoup4)"}

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()

        # Heavy reuse: the parser already walks .field-entry for inputs/returns using rich logic
        parsed = parse_page(url, resp.text, kind_hint="mutation")
        title = parsed.get("title", name)

        inputs = parsed.get("inputs", []) or []
        returns = parsed.get("returns", []) or []

        def _to_type_entry(f: Dict[str, Any]) -> Dict[str, str]:
            typ = f.get("type", "")
            typ_url = f.get("type_url", "")
            if typ_url and not typ_url.startswith("http"):
                typ_url = _normalize_docs_href(typ_url)
            return {"name": typ, "url": typ_url}

        # Mimic original classification (input vs return/object-ish) but from parsed data (no dup walk)
        input_types = []
        return_types = []
        seen_in = set()
        seen_ret = set()
        for f in inputs:
            ent = _to_type_entry(f)
            if ent["name"] and ent["name"] not in seen_in:
                seen_in.add(ent["name"])
                input_types.append(ent)
        for f in returns:
            ent = _to_type_entry(f)
            # original only kept object/interface for return (mutations/queries ignored)
            if ent["name"] and ("/object/" in ent.get("url","") or "/interface/" in ent.get("url","") or not ent.get("url")):
                if ent["name"] not in seen_ret:
                    seen_ret.add(ent["name"])
                    return_types.append(ent)

        return {
            "name": name,
            "url": url,
            "title": title,
            "direct_input_types": input_types,
            "direct_return_types": return_types,
        }
    except Exception as e:
        return {"name": name, "url": url, "error": str(e)}


def parse_page(url: str, html: str, kind_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Primary parser for Sentera GraphQL docs pages.

    Strategy (lightweight + robust):
      - For query/mutation/object pages: use the excellent .field-entry components.
      - For howto/prose pages: fall back to main content extraction.
      - Never uses LLM. No browser. Pure BeautifulSoup + tiny targeted helpers.

    This function (and the extract_* helpers it uses) is the canonical, tested implementation
    for turning Sentera admin docs HTML into structured data. It is explicitly intended for
    reuse by higher-level tools such as the wiki-assistant skill's helper scripts, in addition
    to the wiki builder itself. Callers receive a rich dict and post-process it into
    more minimal shapes as needed.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Title
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else url.rstrip("/").split("/")[-1] or "untitled"

    # Kind
    if kind_hint:
        kind = kind_hint
    elif "/query/" in url:
        kind = "query"
    elif "/mutation/" in url:
        kind = "mutation"
    elif "/object/" in url:
        kind = "object"
    elif "/input_object/" in url:
        kind = "input_object"
    elif "/interface/" in url:
        kind = "interface"
    elif "/enum/" in url:
        kind = "enum"
    elif "/scalar/" in url:
        kind = "scalar"
    elif any(x in url for x in ["/uploading_files", "/single_part", "/multi_part", "/howto"]):
        kind = "howto"
    else:
        kind = "page"

    # Description — first real paragraph after the h1, before the first Input/Return/Examples heading
    desc = ""
    h1 = soup.find("h1")
    if h1:
        for sib in h1.find_next_siblings():
            if sib.name in ("h2", "h3"):
                # stop at the first content section heading
                htext = sib.get_text(strip=True).lower()
                if any(k in htext for k in ["input", "return", "example"]):
                    break
                # otherwise keep going (multiple h2s can precede the first content)
                continue
            if sib.name == "p":
                t = sib.get_text(strip=True)
                if len(t) > 15 and not any(bad in t.lower()[:40] for bad in ["using the api", "graphiql", "operations"]):
                    desc = t[:320]
                    break

    inputs: List[Dict] = []
    returns: List[Dict] = []
    fields: List[Dict] = []
    enum_values: List[Dict] = []
    examples: List[Dict] = []
    deprecations: List[str] = []
    prose_html: Optional[str] = None

    if kind in ("query", "mutation"):
        inputs = extract_fields(soup, "Input fields")
        returns = extract_fields(soup, "Return fields")
        examples = extract_examples(soup)
        deprecations = extract_deprecations(soup)
    elif kind in ("object", "input_object", "interface"):
        # GraphQL type pages use "Fields" or "Input fields"
        fields = extract_fields(soup, "Fields") or extract_fields(soup, "Input fields")
        examples = extract_examples(soup)
        deprecations = extract_deprecations(soup)
    elif kind == "enum":
        enum_values = _extract_enum_values(soup)
        examples = extract_examples(soup)
        deprecations = extract_deprecations(soup)
    else:
        # Prose / howto pages — capture the main content area
        content = soup.select_one("#content") or soup.select_one("#wrap") or soup.find("main") or soup.find("article")
        if content:
            prose_html = str(content)

    return {
        "url": url,
        "kind": kind,
        "title": title,
        "description": desc,
        "inputs": inputs,
        "returns": returns,
        "fields": fields,
        "enum_values": enum_values,
        "examples": examples,
        "deprecations": deprecations,
        "prose_html": prose_html,
        "raw_html_len": len(html),
    }


# =============================================================================
# RENDERING
# =============================================================================

def render_frontmatter(data: Dict[str, Any]) -> str:
    """Generate clean YAML frontmatter."""
    fm = {
        "url": data["url"],
        "kind": data["kind"],
        "title": data["title"],
        "description": data["description"],
        "parent": data.get("parent"),
        "children": data.get("children", []),
        "tags": [],
        "last_fetched": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    }
    return "---\n" + yaml.dump(fm, sort_keys=False, default_flow_style=False) + "---\n"


def _simple_html_to_md(html: str) -> str:
    """
    Lightweight, zero-dep HTML → Markdown converter for prose howto pages.

    Handles the tags we actually see in Sentera docs content.
    Not a full markdownify replacement — intentionally small and targeted.
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # Remove obvious nav/sidebar junk
    for selector in ["nav", "header", "footer", ".sidebar", ".breadcrumb", "#graphiql", "script", "style"]:
        for el in soup.select(selector):
            el.decompose()

    def walk(node: Tag) -> str:
        if not isinstance(node, Tag):
            return str(node).strip()

        name = node.name.lower()

        if name in ("h1", "h2", "h3", "h4"):
            level = int(name[1])
            txt = node.get_text(separator=" ", strip=True)
            return "\n" + "#" * (level + 1) + " " + txt + "\n\n"

        if name == "p":
            parts = [walk(c) for c in node.children if isinstance(c, (Tag, str))]
            return "".join(p for p in parts if p).strip() + "\n\n"

        if name == "pre":
            code = node.get_text()
            lang = "graphql" if any(k in code.lower() for k in ["query", "mutation"]) else ""
            return f"```{lang}\n{code.strip()}\n```\n\n"

        if name == "code" and node.parent and node.parent.name != "pre":
            return "`" + node.get_text(strip=True) + "`"

        if name == "a":
            href = node.get("href", "")
            txt = node.get_text(strip=True)
            if href:
                return f"[{txt}]({href})"
            return txt

        if name in ("strong", "b"):
            return "**" + node.get_text(strip=True) + "**"

        if name in ("em", "i"):
            return "*" + node.get_text(strip=True) + "*"

        if name == "ul":
            items = []
            for li in node.find_all("li", recursive=False):
                items.append("- " + walk(li).strip())
            return "\n".join(items) + "\n\n"

        if name == "ol":
            items = []
            for i, li in enumerate(node.find_all("li", recursive=False), 1):
                items.append(f"{i}. " + walk(li).strip())
            return "\n".join(items) + "\n\n"

        if name == "table":
            # Simple table support (used for nested arguments)
            rows = []
            for tr in node.find_all("tr"):
                cells = [c.get_text(separator=" ", strip=True).replace("|", "\\|") for c in tr.find_all(["th", "td"])]
                rows.append("| " + " | ".join(cells) + " |")
            if rows:
                # crude header separator
                if len(rows) > 1:
                    sep = "| " + " | ".join(["---"] * len(rows[0].split("|"))) + " |"
                    rows.insert(1, sep)
                return "\n".join(rows) + "\n\n"
            return ""

        if name in ("div", "section", "article", "main", "span"):
            parts = [walk(c) for c in node.children if isinstance(c, (Tag, str))]
            return "".join(p for p in parts if p)

        # default: just recurse
        parts = [walk(c) for c in node.children if isinstance(c, (Tag, str))]
        return "".join(p for p in parts if p)

    body = soup.find("body") or soup
    return walk(body).strip()


def _render_field_table(fields: List[Dict[str, Any]], include_required: bool = True) -> str:
    """Render a nice field table, including deprecation and nested arguments where present.

    Argument tables for complex fields are rendered as separate sections *after*
    the main table. This produces valid, clean Markdown instead of interrupting
    the parent table.
    """
    if not fields:
        return ""

    lines = []
    if include_required:
        lines.append("| Field | Type | Required | Description |")
        lines.append("|-------|------|----------|-------------|")
    else:
        lines.append("| Field | Type | Description |")
        lines.append("|-------|------|-------------|")

    argument_sections = []

    for f in fields:
        name = f"`{f['name']}`"
        typ = f"`{f.get('type', '')}`"
        req = "Yes" if "!" in f.get("type", "") else "No"
        desc = f.get("description", "")
        if f.get("deprecation"):
            dep = f["deprecation"].rstrip(".")
            desc = f"**Deprecated:** {dep}. {desc}".strip()

        if include_required:
            lines.append(f"| {name} | {typ} | {req} | {desc} |")
        else:
            lines.append(f"| {name} | {typ} | {desc} |")

        if f.get("arguments"):
            # Collect argument section to render after the main table
            arg_lines = [f"\n**{f['name']} arguments:**"]
            arg_lines.append("| Argument | Type | Description |")
            arg_lines.append("|----------|------|-------------|")
            for a in f["arguments"]:
                arg_lines.append(f"| `{a['name']}` | `{a['type']}` | {a.get('description','')} |")
            argument_sections.append("\n".join(arg_lines))

    main_table = "\n".join(lines) + "\n\n"

    if argument_sections:
        return main_table + "\n".join(argument_sections) + "\n\n"

    return main_table


def _validate_markdown(content: str, path: Path) -> list[str]:
    """Lightweight structural validation of generated Markdown.

    Returns a list of violation messages. Empty list means the content is clean.

    This is intentionally narrow at first and focused on problems we have
    actually observed in real output (e.g. interrupted tables from nested
    field arguments).
    """
    violations: list[str] = []
    lines = content.splitlines()

    # Simple robust check: look for a data table row followed (with at most one blank)
    # by an arguments header. This specifically catches the old broken renderer output.
    for i in range(len(lines) - 1):
        current = lines[i].strip()
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
        next_next = lines[i + 2].strip() if i + 2 < len(lines) else ""

        is_table_row = current.startswith("|") and not current.startswith("|---")
        is_args_header = next_line.startswith("**") and "arguments:" in next_line.lower()

        # Also check one blank line in between
        is_args_after_blank = next_line == "" and next_next.startswith("**") and "arguments:" in next_next.lower()

        if is_table_row and (is_args_header or is_args_after_blank):
            violations.append(
                f"{path.name}: Interrupted table detected. "
                "Nested argument tables are being inserted inside the main field table, producing invalid Markdown."
            )
            break  # only report once per file

    return violations


def render_markdown(data: Dict[str, Any]) -> str:
    """Render high-signal Markdown matching the style of the curated gold files."""
    md = render_frontmatter(data)
    md += f"\n# {data['title']}\n\n"
    if data.get("description"):
        md += f"**Description:** {data['description']}\n\n"

    # Deprecations (page level)
    if data.get("deprecations"):
        md += "## Deprecations\n\n"
        for d in data["deprecations"]:
            md += f"- {d}\n"
        md += "\n"

    if data["inputs"]:
        md += "## Input Fields\n\n"
        md += _render_field_table(data["inputs"], include_required=True)

    if data["returns"]:
        md += "## Return Fields\n\n"
        md += _render_field_table(data["returns"], include_required=False)

    if data.get("fields"):
        md += "## Fields\n\n"
        md += _render_field_table(data["fields"], include_required=False)

    if data.get("enum_values"):
        md += "## Values\n\n"
        for v in data["enum_values"]:
            val = v.get("value", "")
            desc = v.get("description", "").strip()
            if desc:
                md += f"- `{val}` — {desc}\n"
            else:
                md += f"- `{val}`\n"
        md += "\n"

    if data["examples"]:
        md += "## Examples\n\n"
        for ex in data["examples"]:
            md += f"```{ex['type']}\n{ex['code']}\n```\n\n"

    # Prose content for howto pages
    if data.get("prose_html"):
        prose_md = _simple_html_to_md(data["prose_html"])
        if prose_md:
            md += prose_md + "\n"

    md += "\n---\n*Generated by sentera-wiki-builder (structured extraction, no LLM)*\n"
    return md


# =============================================================================
# MAIN BUILD LOGIC
# =============================================================================

def _derive_path(url: str) -> Path:
    """Turn a docs URL into the relative .md path under the wiki root."""
    path_parts = url.replace("https://admin.sentera.com/api/docs/", "").strip("/").split("/")
    last = path_parts[-1]
    if last == "index.html":
        path_parts[-1] = "index.md"
    elif not last.endswith(".md"):
        path_parts[-1] = last + ".md"
    return Path(*path_parts)


def _kind_from_url(url: str) -> str:
    if "/query/" in url:
        return "query"
    if "/mutation/" in url:
        return "mutation"
    if "/object/" in url:
        return "object"
    if "/input_object/" in url:
        return "input_object"
    if "/interface/" in url:
        return "interface"
    if "/enum/" in url:
        return "enum"
    if "/scalar/" in url:
        return "scalar"
    if any(x in url for x in ["/uploading_files", "/single_part", "/multi_part"]):
        return "howto"
    return "page"


def _validate_wiki_schema(schema: list) -> None:
    """Validate that the wiki_schema.yaml matches the supported structure.

    Enforces:
      - Top level is a list
      - Each entry is a dict
      - 'url' is required and must be a string
      - 'tags' (optional) must be a list of strings
      - 'children' (optional) must be a list of strings

    Extra/unknown fields are allowed but will trigger a warning.
    """
    if not isinstance(schema, list):
        raise ValueError("wiki_schema.yaml must contain a top-level list of entries")

    allowed_keys = {"url", "tags", "children"}

    for i, entry in enumerate(schema):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry #{i} must be a dictionary, got {type(entry).__name__}")

        url = entry.get("url", "<missing>")
        prefix = f"Entry #{i} (url={url!r})"

        # Required field
        if "url" not in entry:
            raise ValueError(f"{prefix} is missing the required 'url' field")
        if not isinstance(entry["url"], str):
            raise ValueError(f"{prefix} 'url' must be a string")
        if not entry["url"].startswith(("http://", "https://")):
            raise ValueError(f"{prefix} 'url' must start with http:// or https://")

        # Optional fields with type enforcement
        for key in ("tags", "children"):
            if key in entry:
                value = entry[key]
                if not isinstance(value, list):
                    raise ValueError(f"{prefix} '{key}' must be a list of strings")
                for j, item in enumerate(value):
                    if not isinstance(item, str):
                        raise ValueError(f"{prefix} '{key}[{j}]' must be a string")

        # Warn on extra fields (don't fail)
        extra = set(entry.keys()) - allowed_keys
        if extra:
            logger.warning(f"{prefix} contains unknown fields {sorted(extra)} — they will be ignored.")


def build_wiki(schema_path: Path, output_dir: Path, dry_run: bool = False, verbose: bool = False):
    logger.info(f"Building Sentera API Wiki from {schema_path}")
    logger.info(f"Output root: {output_dir}")
    logger.info(f"Generated content will be written under: {output_dir / WIKI_SUBDIR}")

    with open(schema_path) as f:
        schema = yaml.safe_load(f) or []

    _validate_wiki_schema(schema)

    wiki_content_root = output_dir / WIKI_SUBDIR

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        wiki_content_root.mkdir(parents=True, exist_ok=True)
        rotate_wiki(output_dir, content_subdir=WIKI_SUBDIR)

        # Ensure a minimal WIKI.md marker exists (canned placeholder per current requirements).
        # Use exclusive create ("x") + try/except to guarantee we never overwrite
        # an existing file (defends against TOCTOU races with rotation or concurrent builds).
        wiki_md = wiki_content_root / "WIKI.md"
        if not wiki_md.exists():
            try:
                with open(wiki_md, "x", encoding="utf-8") as f:
                    f.write(
                        "# Sentera API Wiki (Generated)\n\n"
                        "This directory contains auto-generated Markdown documentation "
                        "produced by `sentera-wiki-builder` from the official Sentera GraphQL docs.\n\n"
                        "- Source of truth: `../wiki_schema.yaml`\n"
                        "- Index for agents: `tree.json`\n"
                        "- Rebuild with: `cd ../sentera-wiki-builder && ./scripts/run.sh`\n\n"
                        "**Do not edit auto-generated files in this directory by hand** (except `WIKI.md`, which is protected for user maintenance). They will be overwritten on the next build.\n",
                    )
                logger.info("  + Created wiki/WIKI.md placeholder")
            except FileExistsError:  # pragma: no cover (race condition on WIKI.md creation)
                # Raced with rotation or another process; an existing file was left in place.
                pass

    nodes: List[Dict[str, Any]] = []
    by_kind: Dict[str, int] = {}

    # Pre-scan to know direct entries vs. pure children for generation + dedup.
    # This enables generating content for children declared in schema while
    # avoiding duplicates when a URL is both direct (promoted, with tags) and listed as child.
    direct_urls: Set[str] = set()
    children_of: Dict[str, List[str]] = {}  # parent_url -> [child_url, ...]
    parent_of: Dict[str, str] = {}          # child_url -> parent_url (for pure children only)
    for entry in schema:
        u = entry["url"]
        direct_urls.add(u)
        ch = entry.get("children", [])
        if ch:
            children_of[u] = ch
            for c in ch:
                if c not in direct_urls:  # pure child (not promoted); may be overwritten if listed under multiple, last wins is fine for 1-level schema
                    parent_of[c] = u

    # Beautiful terminal spinner during the network-bound work (only in default
    # non-verbose mode on a real TTY; completely silent in tests/CI/pipes/-v).
    spinner: Optional[_Spinner] = None
    if not verbose:
        spinner = _Spinner("Fetching and rendering pages from Sentera docs")
        spinner.start()

    # Internal helper: fetch/parse/render/write (or placeholder) + tag/parent/children injection for one page.
    # Keeps the main paths minimal and avoids duplicating the write logic for pure children.
    def _write_one(url: str, tags: List[str], parent_path: Optional[str], child_urls: List[str]) -> Dict[str, Any]:
        path = _derive_path(url)
        kind = _kind_from_url(url)
        target_path = wiki_content_root / path
        if not dry_run:
            target_path.parent.mkdir(parents=True, exist_ok=True)

        parsed: Optional[Dict[str, Any]] = None
        if not dry_run and HAS_DEPS:
            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
                parsed = parse_page(url, resp.text, kind_hint=kind)
                logger.debug(f"    ✓ fetched + parsed ({len(parsed.get('inputs', []))} inputs, {len(parsed.get('returns', []))} returns)")
            except Exception as e:
                logger.warning(f"    ⚠ fetch/parse failed: {e}")
                parsed = None
        elif dry_run:
            logger.debug("    (dry-run: skipping fetch)")
        elif not HAS_DEPS:
            logger.debug("    (skipping live fetch — missing requests/bs4)")

        # Build render data so frontmatter can carry real hierarchy when present
        render_data: Dict[str, Any] = {
            "url": url,
            "kind": kind,
            "title": path.stem,
            "description": "",
            "parent": parent_path,
            "children": [_derive_path(c).as_posix() for c in child_urls],
        }

        if parsed and not dry_run:
            # render_markdown calls render_frontmatter which now honors parent/children
            content = render_markdown({**parsed, "parent": parent_path, "children": render_data["children"]})

            # Lightweight Markdown validation (warning-only in initial rollout)
            violations = _validate_markdown(content, target_path)
            if violations:  # pragma: no cover (only hit when bad Markdown is generated)
                # Use print to stderr so lint warnings are always visible, even without --verbose
                for v in violations:
                    print(f"    ⚠ Markdown lint: {v}", file=sys.stderr)
                print("    (Markdown validation is currently warning-only during rollout)", file=sys.stderr)

            target_path.write_text(content, encoding="utf-8")

            # Inject tags (existing) + parent/children (new, for pages that declare hierarchy)
            try:
                if target_path.exists():
                    txt = target_path.read_text(encoding="utf-8")
                    if txt.startswith("---\n"):
                        if tags:
                            txt = re.sub(r"^tags:\s*\[\s*\]", f"tags: {tags}", txt, flags=re.MULTILINE)
                        if parent_path is not None:
                            txt = re.sub(r"^parent:\s*.*$", f"parent: {parent_path}", txt, flags=re.MULTILINE)
                        if child_urls:
                            ch_paths = [_derive_path(c).as_posix() for c in child_urls]
                            txt = re.sub(r"^children:\s*\[\s*\]", f"children: {ch_paths}", txt, flags=re.MULTILINE)
                        target_path.write_text(txt, encoding="utf-8")
            except Exception:  # pragma: no cover (defensive post-write injection failure)
                pass
        elif not dry_run:
            placeholder = render_frontmatter(render_data)
            placeholder += f"\n# {path.stem}\n\n*(Content not yet generated — run with live internet)*\n"
            target_path.write_text(placeholder, encoding="utf-8")

        return {
            "path": str(path),
            "url": url,
            "kind": kind,
            "title": path.stem,
            "tags": tags,
            "parent": parent_path,
            "children": [_derive_path(c).as_posix() for c in child_urls],
        }

    nodes_by_url: Dict[str, Dict[str, Any]] = {}

    for entry in schema:
        url = entry["url"]
        tags = entry.get("tags", [])
        children = entry.get("children", [])
        logger.debug(f"  Processing: {url}")

        node = _write_one(url, tags, None, children)
        nodes_by_url[url] = node
        by_kind[node["kind"]] = by_kind.get(node["kind"], 0) + 1

    # Generate content + nodes for pure children (those declared under children: but never promoted to direct top-level entries).
    # This fixes the core bug: children are now actually generated and linked.
    for child_url, parent_url in parent_of.items():
        if child_url in nodes_by_url:
            continue  # already handled as direct
        ppath = _derive_path(parent_url).as_posix()
        logger.debug(f"  Processing child: {child_url} (under {parent_url})")
        node = _write_one(child_url, [], ppath, [])
        nodes_by_url[child_url] = node
        by_kind[node["kind"]] = by_kind.get(node["kind"], 0) + 1

    # Assemble final nodes list (deduped, with consistent path-based children)
    for n in nodes_by_url.values():
        nodes.append(n)

    # Stop spinner (if any) now that the fetch/render work is complete.
    # The subsequent tree.json + success banner are fast.
    if spinner:
        spinner.stop()

    # Write tree.json (accurate stats, no hardcoding)
    tree = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "root": str(output_dir.name),
        "nodes": nodes,
        "stats": {
            "total_pages": len(nodes),
            "by_kind": by_kind or {"query": 0, "mutation": 0, "howto": 0, "object": 0, "page": 0}
        }
    }
    if not dry_run:
        tree_path = output_dir / WIKI_SUBDIR / "tree.json"
        tree_path.parent.mkdir(parents=True, exist_ok=True)
        with open(tree_path, "w") as f:
            json.dump(tree, f, indent=2)
    else:
        logger.info("   (dry-run: tree.json not written)")

    logger.warning(f"\n✅ Wiki built with {len(nodes)} pages")
    logger.warning("   tree.json updated with accurate stats")
    if dry_run:
        logger.warning("   (dry-run: no files written, no rotation performed)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sentera Wiki Builder with integrated agent helper tools"
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_WIKI_SCHEMA, help="Path to wiki_schema.yaml")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed progress logs")

    # Skill helper tools (integrated wiki-assistant capabilities)
    parser.add_argument(
        "--synthesize-intent",
        metavar="PROMPT",
        help="Print the structured intent synthesis template for a user request. "
             "This is the recommended first step for NLP-style queries to the wiki-assistant skill."
    )
    parser.add_argument(
        "--inspect-docs",
        action="store_true",
        help="Fetch and print a structured map of the Sentera docs navigation (menus from the sidebar). "
             "Useful as a starting point for discovery. Combine with --json for machine-readable output."
    )
    parser.add_argument(
        "--get-mutation-signature",
        "--mutation-signature",
        dest="mutation_signatures",
        nargs="+",
        metavar="MUTATION",
        help="Get compact input/return signatures for one or more mutations (primary tool for implementation requests). "
             "Supports --json for structured output."
    )
    parser.add_argument(
        "--get-query-signature",
        "--query-signature",
        dest="query_signatures",
        nargs="+",
        metavar="QUERY",
        help="Get compact input/return signatures for one or more queries (primary tool for load/query details and NLP 'I want to load X details' requests). "
             "Supports --json for structured output. (Added for wiki-assistant symmetry with mutations.)"
    )
    parser.add_argument(
        "--get-type-details",
        "--type-details",
        dest="type_details",
        nargs="+",
        metavar="TYPE",
        help="Get structured fields/enum values for one or more GraphQL types (primary tool for data models). "
             "Supports --json."
    )
    parser.add_argument(
        "--extract-page-links",
        dest="page_links",
        nargs="+",
        metavar="URL",
        help="Extract and classify internal doc links from one or more pages (for dependency analysis in schema curation). "
             "Supports --json."
    )
    parser.add_argument(
        "--find-related",
        dest="find_related_term",
        metavar="TERM",
        help="Keyword or URL search for related docs pages (supports content + sidebar discovery). "
             "Supports --json."
    )
    parser.add_argument(
        "--extract-main-content",
        dest="main_content_url",
        metavar="URL",
        help="Extract prose, sections and key mentions from a how-to/guide page. Supports --json."
    )
    parser.add_argument(
        "--get-mutation-deps",
        dest="mutation_deps",
        nargs="+",
        metavar="MUTATION",
        help="Older mutation dep extractor (input/return type links). Prefer get-mutation-signature. Supports --json."
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format (for helper modes like --inspect-docs, --get-mutation-signature, --get-query-signature, --get-type-details, --extract-page-links, --find-related, --extract-main-content, --get-mutation-deps, etc.)")

    args = parser.parse_args()

    # Handle skill helper modes first (they short-circuit normal wiki building)
    if args.synthesize_intent:  # pragma: no cover (CLI helper path)
        # No logging setup needed for this pure output mode
        try:
            result = synthesize_intent(args.synthesize_intent)
            print(result)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    if args.inspect_docs:  # pragma: no cover (CLI helper path)
        try:
            menus = inspect_docs()
            if args.json:
                print(json.dumps(menus, indent=2))
            else:
                print("=== Sentera Docs Navigation Map ===\n")
                for i, menu in enumerate(menus):
                    print(f"--- Menu {i} ---")
                    for item in menu[:15]:
                        print(f"  - {item['title']} -> {item['url']}")
                    if len(menu) > 15:
                        print(f"  ... ({len(menu) - 15} more)")
                    print()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    if args.mutation_signatures:  # pragma: no cover (CLI helper - covered at integration level)
        results = [get_mutation_signature(m) for m in args.mutation_signatures]
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                if "error" in r:
                    print(f"{r['name']}: ERROR - {r['error']}")
                    continue
                print(f"\n=== {r['title']} ===")
                if r.get("main_input_type"):
                    print(f"Main Input: {r['main_input_type']['type']} -> {r['main_input_type']['type_url']}")
                if r.get("main_return_type"):
                    print(f"Main Return: {r['main_return_type']['type']} -> {r['main_return_type']['type_url']}")
        sys.exit(0)

    if args.query_signatures:  # pragma: no cover (CLI helper - covered at integration level)
        results = [get_query_signature(q) for q in args.query_signatures]
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                if "error" in r:
                    print(f"{r['name']}: ERROR - {r['error']}")
                    continue
                print(f"\n=== {r['title']} ===")
                if r.get("main_input_type"):
                    print(f"Main Input: {r['main_input_type']['type']} -> {r['main_input_type']['type_url']}")
                if r.get("main_return_type"):
                    print(f"Main Return: {r['main_return_type']['type']} -> {r['main_return_type']['type_url']}")
        sys.exit(0)

    if args.type_details:  # pragma: no cover (CLI helper - covered at integration level)
        results = [get_type_details(t) for t in args.type_details]
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                if "error" in r:
                    print(f"{r['name']}: {r['error']}")
                    continue
                print(f"\n=== {r['title']} ({r['kind']}) ===")
                print(f"URL: {r['url']}")
                if r.get("fields"):
                    print("Fields:")
                    for f in r["fields"]:
                        desc = (f.get("description") or "")[:100]
                        print(f"  {f['name']}: {f['type']} — {desc}")
                if r.get("enum_values"):
                    print("Values:")
                    for v in r["enum_values"]:
                        desc = (v.get("description") or "")[:80]
                        print(f"  {v['value']} — {desc}")
        sys.exit(0)

    if args.page_links:  # pragma: no cover (CLI helper - covered at integration level)
        results = [extract_page_links(u) for u in args.page_links]
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                if "error" in r:
                    print(f"{r.get('url', '?')}: ERROR - {r['error']}")
                    continue
                print(f"\n=== {r['title']} ===")
                print(f"Source: {r['url']}")
                print(f"Total unique internal doc links found: {r['total_links']}\n")
                for category, links in sorted(r.get("links_by_category", {}).items()):
                    print(f"--- {category.upper()} ({len(links)}) ---")
                    for link in links:
                        print(f"  {link}")
                    print()
        sys.exit(0)

    if args.find_related_term:
        try:
            out = find_related(args.find_related_term)
            if args.json:
                print(json.dumps(out, indent=2))
            else:
                if "start" in out:
                    print(f"Starting page: {out['start']['title']}")
                    for r in out.get("related", []):
                        print(f"  - {r['url']}")
                elif "error" in out:
                    print(f"Error: {out['error']}", file=sys.stderr)
                else:
                    for m in out.get("matches", []):
                        print(f"- {m['title']} -> {m['url']} ({m.get('matched', '')})")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    if args.main_content_url:
        try:
            content = extract_main_content(args.main_content_url)
            if args.json:
                print(json.dumps(content, indent=2))
            else:
                print(f"Title: {content.get('title', '')}")
                print(f"URL: {content.get('url', '')}\n")
                if content.get("description"):
                    print(f"Description:\n{content['description']}\n")
                if content.get("sections"):
                    print("Key Sections:")
                    for sec in content["sections"]:
                        txt = sec["content"][:800] + ("..." if len(sec["content"]) > 800 else "")
                        print(f"\n## {sec['title']}\n{txt}")
                if content.get("mentioned_identifiers"):
                    print(f"\nMentioned identifiers: {', '.join(content['mentioned_identifiers'])}")
                if "error" in content:
                    print(f"Error: {content['error']}", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    if args.mutation_deps:
        results = [get_mutation_deps(m) for m in args.mutation_deps]
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                if "error" in r:
                    print(f"{r['name']}: ERROR - {r['error']}")
                    continue
                print(f"\n=== {r['title']} ===")
                print(f"URL: {r['url']}")
                print("Direct Input Types:")
                for t in r.get("direct_input_types", []):
                    print(f"  - {t['name']} -> {t['url']}")
                print("Direct Return Types:")
                for t in r.get("direct_return_types", []):
                    print(f"  - {t['name']} -> {t['url']}")
        sys.exit(0)

    _setup_logging(verbose=args.verbose)

    if not HAS_DEPS:
        logger.error("⚠️  Missing dependencies. Run: uv add requests beautifulsoup4 pyyaml")
        logger.error("   (Live fetching + structured parsing will be skipped)")

    build_wiki(args.schema, args.output, args.dry_run, verbose=args.verbose)
