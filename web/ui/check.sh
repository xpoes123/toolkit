#!/usr/bin/env bash
# Guardrail (cf. Ryu's ESLint rules): hex colors belong in themes/ only. Usage: check.sh <dir-or-files>
grep -rnE '#[0-9a-fA-F]{3,8}\b' --include='*.css' --include='*.html' "${@:-.}" | grep -v '/themes/' \
  && { echo "hardcoded hex above: use a var(--token)"; exit 1; } || echo ok
