#!/usr/bin/env bash
# Standard VPS-side half of David's git-pull-deploy flow (commit -> push ->
# this). Generalized from david-share/app/git_ops.py's commit_push(), which
# already handles the admin-mutation side with pull/push race-retry — this
# script is the missing VPS-side piece other repos (e.g. finance) don't have.
#
# Usage: git-pull-deploy.sh <repo-dir> [systemd-unit ...]
# Exits non-zero (and does NOT restart anything) if the pull isn't a clean
# fast-forward — never force-overwrites local state on the box.
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "usage: git-pull-deploy.sh <repo-dir> [systemd-unit ...]" >&2
  exit 1
fi

repo_dir="$1"; shift
units=("$@")

cd "$repo_dir"
git pull --ff-only

for unit in "${units[@]:-}"; do
  [ -n "$unit" ] && systemctl restart "$unit"
done

echo "deployed $repo_dir$( [ ${#units[@]} -gt 0 ] && printf ' -> %s' "${units[@]}" )"
