#!/usr/bin/env bash
#
# Convenience wrapper for local development of sentera-wiki-builder.
#
# This script ensures dependencies are installed and then runs the builder.
#
# Usage:
#   ./scripts/run.sh
#   ./scripts/run.sh --verbose
#   ./scripts/run.sh --schema ../my-wiki/wiki_schema.yaml --output ../my-wiki

set -euo pipefail

# Resolve to the project root (one directory above scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "→ Syncing dependencies..."
uv sync

echo "→ Running builder..."
uv run build_wiki.py "$@"
