# web/ui

Tokens → primitives → components, mirroring Ryu's layering for plain-HTML tools.

- `tokens.css`: type/space/radius scales. `themes/*.css`: colors, selected with `<html data-theme="ink">` (default tokyo-night).
- `primitives.css`: `ui-flex/stack/grid/pad`, headings. `components.css`: `ui-btn`, `ui-card`, `ui-stat`, `ui-pill`, tabs, table, modal, toast...
- Rules: no hex outside `themes/` (`./check.sh <dir>`); no restyling `ui-*` in feature CSS, fix the component here; add variants via modifiers (`ui-btn--danger`).
- Docs: open `preview.html` over http.
- Personal tools use this; public products (scibowl-org, davidJ, poverty-football) keep their own branding.
