#!/usr/bin/env bash
# Vendor the shared UI css into a repo: sync.sh <dest-dir>  -> <dest>/ui.css (one file, default theme + all others)
set -e; d="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$1"
cat "$d/tokens.css" "$d/primitives.css" "$d"/themes/*.css "$d/components.css" > "$1/ui.css"
echo "wrote $1/ui.css"
