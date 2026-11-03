# web/ui

Tokens → primitives → components, mirroring Ryu's layering for plain-HTML tools.

- `tokens.css`: type/space/radius scales. `themes/*.css`: colors, selected with `<html data-theme="ink">` (default davidj).
- `primitives.css`: `ui-flex/stack/grid/pad`, headings. `components.css`: `ui-btn`, `ui-card`, `ui-stat`, `ui-pill`, tabs, table, modal, toast...
- Rules: no hex outside `themes/` (`./check.sh <dir>`); no restyling `ui-*` in feature CSS, fix the component here; add variants via modifiers (`ui-btn--danger`).
- `fonts/`: self-hosted Space Grotesk, JetBrains Mono, Newsreader (woff2, latin, variable, OFL). `@font-face` lives in `tokens.css` with URLs relative to the sheet, so serve `/ui/fonts/*` wherever you serve `/ui/ui.css` (add `Access-Control-Allow-Origin: *` if other origins link it).
- `ui.js` (optional, serve at `/ui/ui.js`): `ui.spark(values, {label, ref, refLine, area})` returns a sparkline SVG; `ui.cat(i)` / `ui.catFor(name)` map a category to `var(--cat-1..8)`.
- Docs: open `preview.html` over http.
- Personal tools use this; public products (scibowl-org, davidJ, poverty-football) keep their own branding.

## Using it
- Link first in `<head>`: `/ui/ui.css` (same-origin; FastAPI apps add a route that concatenates the files from `/opt/toolkit/web/ui`, see finance/david-share `main.py`) or `https://share.djiang.xyz/ui/ui.css`. Sensitive apps (finance, anything with logins) should serve it same-origin.
- Migrate an existing repo: `./migrate.py [--apply] [--no-link] <dir>` (maps known palette hex to tokens, links the sheet, reports unmapped colors). Check for `--a: var(--b)` / `--b: var(--a)` cycles afterwards.

## v2 base (additive, use for new work)
- Shell: `<body class="ui-app ui-controls">` (bg, sans 15px, tabular lining numerals, themed native inputs/select/checkbox via `accent-color`).
- Type scale: `--fs-meta 11 / --fs-small 13 / --fs-body 15 / --fs-lead 17 / --fs-title 24 / --fs-display`. Money in the sans with `.ui-num` (tabular); mono only for small metadata (`.ui-eyebrow`, `.ui-meta`).
- One focal number per screen: `.ui-display` + `.ui-display__unit`. Serif aside: `.ui-note`. Empty state: `.ui-empty`.
- Flat lists, not cards: `.ui-list > .ui-row` (`__main/__title/__meta/__amt/__flag`, `--kv` for label/value). Section header with right total: `.ui-sechead`. At most one `.ui-raised` per screen.
- Controls: `.ui-seg` (segmented, `aria-pressed`), `.ui-btn--lg` (44px), `--quiet`, `--solid`, `.ui-check`, `.ui-select`.
- Data: `.ui-bar` (`--v` fill, `--m` marker), `.ui-stackbar`, `.ui-spark`, `.ui-heat` (calendar heatmap), `.ui-dtable` + `.ui-depth`, `.ui-scroll` (tables scroll inside, never the page). Layout: `.ui-cols` / `__main` / `__side`.
- Colors: gold `--accent` marks only the primary action or current focus; `--ok`/`--bad` (`.ui-pos`/`.ui-neg`) only for deltas and over/under; balances stay `--text`. Categories use `--cat-1..8`; `--div-*` is a diverging ramp; `--pink` is for streaks/celebration; `--surface-3` is the raised surface.
- Radii: only `--radius-sm|--radius|--radius-lg|--radius-xl|--radius-pill` (check.sh enforces).
- Densities on `<html data-density>`: `terminal` (mono, square, tight; `.ui-ticker`, `.ui-panels`, `.ui-alert`) and `simple` (rounded, big; `.ui-hero`, `.ui-tile`, `.ui-deck`, `.ui-callout`). Phones stay 44px-tappable in both.

## Adding things
1. Missing color/token -> `themes/*.css` (all themes) or `tokens.css`. Missing component/variant -> `components.css` (`ui-` prefix, semantic tokens only).
2. `./check.sh <dir>`, view `preview.html` over http, commit + push.
3. Deploy: `ssh root@87.99.136.82 'git -C /opt/toolkit pull'`. No restarts; apps cache for 5 minutes.
