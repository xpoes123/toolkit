#!/usr/bin/env bash
# Guardrails (cf. Ryu's ESLint rules). Usage: check.sh <dir-or-files>
#  1. hex colors belong in themes/ only   2. radii come from --radius* tokens, not literal px/rem
rc=0
grep -rnE '#[0-9a-fA-F]{3,8}\b' --include='*.css' --include='*.html' "${@:-.}" | grep -v '/themes/' \
  && { echo "hardcoded hex above: use a var(--token)"; rc=1; }
grep -rnE 'border-radius\s*:\s*[^;"}]*[0-9.]+(px|rem|em)\b' --include='*.css' --include='*.html' "${@:-.}" \
  | grep -vE 'tokens\.css' \
  && { echo "literal radius above: use var(--radius-sm|--radius|--radius-lg|--radius-xl|--radius-pill)"; rc=1; }
[ $rc = 0 ] && echo ok; exit $rc
