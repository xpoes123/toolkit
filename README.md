# djtoolkit

Utilities pulled out of David's `~/code` repos after a cross-repo audit found
the same code (or the same trick) reimplemented 2-3 times independently.
Each module below names its origin repo — read that file first if you want
the full context/history, this is the stripped-down, dependency-minimal
version.

**Status: v1, not yet wired into any live repo.** sage, stavid, SharpLab,
nba-modeling, and nsba-markets all currently have their own local copies of
this logic and keep running exactly as before. Migrating each one over is a
separate, deliberate follow-up — several of these repos are live production
systems (real Discord users, real trades), so swapping their internals for a
shared dependency happens one repo at a time, on request, not in bulk.

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

### `web/tokyo-night.css`
Shared CSS custom properties, extracted from `finance/index.html` and
`david-share/app/static/share.css` — both had the exact same hex values
copy-pasted under different variable names.

## Design system

Two deliberately different visual languages across the fleet, not
inconsistency:

- **Personal single-user tools** (finance, david-share, future ones in the
  same category) — Tokyo Night dark, matching the desktop. Use
  `web/tokyo-night.css`. These are tools David uses himself; they should
  look like the rest of his machine.
- **Public-facing products** (scibowl-org — students/coaches; davidJ — a
  public portfolio) — their own branding, not Tokyo Night. scibowl-org is
  light-themed and Tailwind-based on purpose (a product for a general
  audience); davidJ uses a warm gold accent + different type system on
  purpose (personal-brand identity, distinct from "David's internal tool"
  aesthetic). Don't retrofit Tokyo Night onto either.

Rule of thumb: if the only users are David (and maybe Steph), it's Tokyo
Night. If it's a product other people log into, it gets its own identity.

## Self-checks

Every module with non-trivial logic (branches, a parser, a PRNG, money math)
has an assert-based `_demo()` runnable directly — no test framework, no
fixtures:

```
python3 djtoolkit/discord_kit.py
python3 djtoolkit/oddsmath.py
python3 djtoolkit/avatar.py
```
