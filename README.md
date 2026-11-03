# djtoolkit

Utilities pulled out of David's `~/code` repos after a cross-repo audit found
the same code (or the same trick) reimplemented 2-3 times independently.
Each module below names its origin repo — read that file first if you want
the full context/history, this is the stripped-down, dependency-minimal
version.

**Status:** `oddsmath` and `kalshi` are imported by live repos (SharpLab,
live-trader, finance, vigil). The rest is v1 — sage, stavid, nba-modeling,
and nsba-markets still have their own local copies of that logic. Migrating each one over is a
separate, deliberate follow-up — several of these repos are live production
systems (real Discord users, real trades), so swapping their internals for a
shared dependency happens one repo at a time, on request, not in bulk.
For `discord_kit.py`, the named starting points are `sage/cogs/chat.py` (28
bare try/except) + `sage/cogs/gcal.py` (8), and `stavid/src/cogs/reminders.py`
+ `budget.py` (no centralized error handling at all) — start there, not with
a generic sweep.

## Modules

### `djtoolkit/discord_kit.py`
Ported from sage's `cogs/__init__.py` + `services/error_reporting.py`,
stripped of sage's DB/Sentinel coupling.
- `sanitize_error(exc)` / `command_error_handler` — turn an exception into a
  safe user-facing message instead of leaking a raw traceback to Discord.
- `load_all_cogs(bot, package_name)` — glob-load every cog, log-not-crash on
  a bad one.
- `ErrorDeduper` — fingerprint exceptions by `(type, file, function)` so
  repeats bump a counter instead of re-alerting. In-memory; wire it into your
  own DB table if you want persistence across restarts.

Install: `pip install "djtoolkit[discord] @ git+https://github.com/xpoes123/toolkit.git"`

### `djtoolkit/oddsmath.py`
Ported from `SharpLab/shared/odds_utils.py` (the most complete of three
independent copies — nba-modeling had two, sharp-nba a third). Pure math, no
I/O: American/decimal/prob conversion, de-vig, CLV, a format-agnostic
`parse_odds_input`, and a `kelly_fraction` helper. Vendor-specific fetchers
(Kalshi/Polymarket network calls) were deliberately left out — those stay in
the app that needs them.

### `djtoolkit/kalshi.py`
Kalshi trade-API transport, consolidated from live-trader's `kalshi.py` (the
original), SharpLab's `shared/kalshi.py` + `shared/kalshi_account.py`,
finance's `app/kalshi.py`, and vigil's `live/pnl.py`. Only the shared part:
- `load_key(pem)` / `load_key_file(path)` — PEM parse, with SharpLab's repair
  for pastes that lost their newlines.
- `sign_headers(key_id, key, method, path, ts_ms=None)` — RSA-PSS over
  `ts + METHOD + path` (path incl. `/trade-api/v2`, query stripped).
- `KalshiClient` (sync) / `AsyncKalshiClient` — signed `request`/`get`,
  cursor `paginate(path, field)`, `balance()`. 401/403 raise
  `KalshiAuthError` (an `httpx.HTTPStatusError` subclass).
- `balance_dollars` / `portfolio_value_dollars` / `account_value_cents` —
  handle both the cents-int and `*_dollars` response shapes.

App logic stays in the apps: SharpLab's PnL/slates/boards, live-trader's
order placement + orderbook parsing.

Install: `pip install "djtoolkit[kalshi] @ git+https://github.com/xpoes123/toolkit.git@v0.2.0"`

### `djtoolkit/avatar.py` + `web/avatar.ts`
The mechanism behind nsba-cardai's `CuteAvatar.tsx` — deterministic,
zero-cost per-identity art. `hash32(name)` (FNV-1a) seeds an xorshift32 PRNG;
draw trait indices from it with `.pick(n)`/`.chance(p)`. No image files, no
AI image API, no server round-trip. The Python and TS versions use the exact
same algorithm so a backend and frontend derive identical traits from the
same name. **The trait art itself (palettes, shapes, faces) is not
included** — that's per-app, define your own tables and call `.pick()`/
`.chance()` to select from them. See each file's `_demo()` for a minimal
worked example.

### `deploy/git-pull-deploy.sh`
The VPS-side half of the deploy flow documented in `~/.claude/CLAUDE.md`
(commit -> push -> VPS `git pull` -> restart). Generalized from
`david-share/app/git_ops.py`'s `commit_push()` (which handles the
admin-mutation/push side already). Fails loud instead of force-overwriting
local state if the pull isn't a clean fast-forward.

```
git-pull-deploy.sh /opt/finance finance-app
```

### `web/ui/`
The shared design system: tokens, themes (`davidj` default, `ink`, `paper`,
`tokyo-night`), layout primitives and `ui-*` components. See `web/ui/README.md`.
`web/tokyo-night.css` is the legacy variables-only file, superseded.

## Consuming it

The repo is public, so consumers pin a tag over HTTPS in their deps (no deploy
key needed on the VPS):

```
djtoolkit[kalshi] @ git+https://github.com/xpoes123/toolkit.git@v0.2.0
```

Bump the tag (and `version` in `pyproject.toml`) for each release; on deploy,
`pip install -r requirements.txt` / `pip install -e .` picks up the new pin.

Tests: `pytest tests/`.

## Claude Code skills

`claude-skills/` — personally-authored Claude Code commands and skills
(Bitwarden vault search, Arch/CachyOS package help, Hyprland config help,
rofi bookmarks/commands, YouTube transcripts, plus reusable VPS-ops,
site-publishing, notify, and interactive-review-page templates). See
`claude-skills/README.md` for the full list, what's genericized vs.
template-with-config, and what was deliberately left out as too entangled
with personal infrastructure to publish responsibly.

## Design system

Personal single-user tools all use `web/ui/` (default theme `davidj`, matching
the personal site) via one stylesheet, so redesigning is one edit here. New
colors/components/assets go in `web/ui/`, never into a consuming repo.
Public-facing products (scibowl-org, davidJ, poverty-football, redherring,
tv, games) keep their own branding on purpose. Rule of thumb: if the only
users are David (and maybe Steph), use `web/ui/`; if other people log in, it
gets its own identity.

## Self-checks

Every module with non-trivial logic (branches, a parser, a PRNG, money math)
has an assert-based `_demo()` runnable directly — no test framework, no
fixtures:

```
python3 djtoolkit/discord_kit.py
python3 djtoolkit/oddsmath.py
python3 djtoolkit/avatar.py
```
