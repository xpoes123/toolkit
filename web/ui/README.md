# web/ui

Tokens → primitives → components, mirroring Ryu's layering for plain-HTML tools.

- `tokens.css`: type/space/radius scales. `themes/*.css`: colors, selected with `<html data-theme="ink">` (default davidj).
- `primitives.css`: `ui-flex/stack/grid/pad`, headings. `components.css`: `ui-btn`, `ui-card`, `ui-stat`, `ui-pill`, tabs, table, modal, toast...
- Rules: no hex outside `themes/` (`./check.sh <dir>`); no restyling `ui-*` in feature CSS, fix the component here; add variants via modifiers (`ui-btn--danger`).
- Docs: open `preview.html` over http.
- Personal tools use this; public products (scibowl-org, davidJ, poverty-football) keep their own branding.

## Using it
- Link first in `<head>`: `/ui/ui.css` (same-origin; FastAPI apps add a route that concatenates the files from `/opt/toolkit/web/ui`, see finance/david-share `main.py`) or `https://share.djiang.xyz/ui/ui.css`. Sensitive apps (finance, anything with logins) should serve it same-origin.
- Migrate an existing repo: `./migrate.py [--apply] [--no-link] <dir>` (maps known palette hex to tokens, links the sheet, reports unmapped colors). Check for `--a: var(--b)` / `--b: var(--a)` cycles afterwards.

## Adding things
1. Missing color/token -> `themes/*.css` (all themes) or `tokens.css`. Missing component/variant -> `components.css` (`ui-` prefix, semantic tokens only).
2. `./check.sh <dir>`, view `preview.html` over http, commit + push.
3. Deploy: `ssh root@87.99.136.82 'git -C /opt/toolkit pull'`. No restarts; apps cache for 5 minutes.
