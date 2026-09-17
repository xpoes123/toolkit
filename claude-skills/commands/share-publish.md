Publish a Claude session brief to your own personal site so you can read it in a browser.

**Template — this assumes an architecture: a small git-backed app or static
site, driven by a manifest/index file, deployed by pull-to-deploy over SSH.
Adapt Steps 3-5 to however your own site actually works if it's different —
the parts that matter are: write the page, register it wherever your site's
index comes from, commit, push, deploy.**

## Config — edit before use

- `SITE_REPO` — e.g. `yourname/your-site-repo` (the git repo backing your site)
- `SITE_LOCAL_CLONE` — e.g. `~/code/your-site-repo`
- `SITE_VPS_HOST` — e.g. `user@your-vps-host` (or an `~/.ssh/config` alias)
- `SITE_VPS_PATH` — e.g. `/opt/your-site`
- `SITE_DOMAIN` — e.g. `https://notes.yourdomain.com`

## How this kind of site works (app + manifest, pull-to-deploy)

The reference implementation this is modeled on is a small FastAPI app on a
VPS, behind Caddy, that serves pages at `/{project}/{slug}.html` with access
control (public/unlisted/password). A single `manifest.json` in the repo is
the source of truth — each page gets an entry (project, date, title, tag,
visibility) and the app renders all indexes from it, so pages never need
hand-built index HTML.

You publish by writing the page HTML + a manifest entry, committing, pushing,
and pulling on the VPS. Never scp loose files — git is the source of truth.

```
write $SITE_LOCAL_CLONE/{project}/{slug}.html + upsert manifest.json
  → git add/commit/push → ssh $SITE_VPS_HOST "cd $SITE_VPS_PATH && git pull --ff-only"
```

If your own site is just static HTML with no manifest/app, skip the manifest
step entirely and just write + commit + push + pull the HTML file.

## When to use

At the end of a big working session — overnight work, anything you'll want
to read later. Also mid-session for checkpoints.

## Arguments

`$ARGUMENTS` can be:
- Empty — auto-detect project from current directory, auto-generate title from date
- A title: `"Wake-up brief — May 29"`
- A project override: `myproject: Wake-up brief`

## Step 0 — Sync the local clone

```bash
git -C $SITE_LOCAL_CLONE pull --ff-only
```

## Step 1 — Gather session context

```bash
git log --oneline --since="24 hours ago" 2>/dev/null || git log --oneline -20
git diff HEAD~5..HEAD --stat 2>/dev/null | head -40
git status --short
git branch --show-current
```

Also read any files changed during the session (design docs, test output) that would help the brief.

## Step 2 — Write the brief

Write a thorough markdown brief. Be honest and specific — this is a diagnostic, not a PR description.

```
# [Title] — [Date]

## TL;DR
2-4 sentences. State of the project now vs when the session started? The single
most important thing to know?

## What was attempted
Narrative timeline: what was tried, what happened, why it failed (root cause, not symptoms).

## What succeeded / what failed or is incomplete
Concrete lists — commits/PRs that landed, dead ends and why, things left unfinished.

## Current state
What's merged? On a branch? Undeployed? Broken?

## Recommendations
What to do first, in priority order.
```

## Step 3 — Generate the HTML into the local clone

Enforce a naming convention, e.g. `{project}/YYYY-MM-DD-<kebab-slug>.html`.

```python
#!/usr/bin/env python3
import os, re
from datetime import date

SHARE = os.path.expanduser(os.environ.get("SITE_LOCAL_CLONE", "~/code/your-site-repo"))
PROJECT = os.path.basename(os.getcwd())   # or an explicit override
TITLE = "Wake-up brief — May 29"          # replace with actual title
TAG = "brief"                             # brief|report|research|hub|blog
TODAY = date.today().strftime("%Y-%m-%d")

def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s.lower().strip())
    return re.sub(r"[\s_-]+", "-", s)[:60].strip("-")

SLUG = f"{TODAY}-{slugify(TITLE)}"
REL = f"{PROJECT}/{SLUG}.html"
OUT = os.path.join(SHARE, REL)
DOMAIN = os.environ.get("SITE_DOMAIN", "https://notes.yourdomain.com")
PUBLIC_URL = f"{DOMAIN}/{REL}"

BRIEF_MD = """
[PASTE THE FULL BRIEF MARKDOWN HERE]
""".strip()

def md_to_html(md):
    lines, in_pre = [], False
    for line in md.splitlines():
        if line.startswith("```"):
            if in_pre:
                lines.append("</code></pre>"); in_pre = False
            else:
                lines.append(f'<pre><code class="language-{line[3:].strip()}">'); in_pre = True
            continue
        if in_pre:
            lines.append(line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")); continue
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            n = len(m.group(1)); lines.append(f"<h{n}>{m.group(2)}</h{n}>"); continue
        if line.startswith("---"):
            lines.append("<hr>"); continue
        if line.startswith("- ") or line.startswith("* "):
            c = re.sub(r"`([^`]+)`", r"<code>\1</code>", re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line[2:]))
            lines.append(f"<li>{c}</li>"); continue
        if line.strip() == "":
            lines.append(""); continue
        c = re.sub(r"`([^`]+)`", r"<code>\1</code>", re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line))
        lines.append(f"<p>{c}</p>")
    return "\n".join(lines)

# Swap this for your own CSS, or reuse toolkit/web/tokyo-night.css if you like the look.
CSS = """
:root{--bg:#0c0f14;--fg:#e6e9ef;--fg-dim:#9aa3b2;--accent:#7aa2f7;--rule:#232936;--code-bg:#0a0d12;--code-border:#1d2330;--mono:ui-monospace,"JetBrains Mono","Fira Code",monospace;--sans:-apple-system,BlinkMacSystemFont,"Inter",system-ui,sans-serif}
*{box-sizing:border-box}html,body{margin:0;padding:0;background:var(--bg);color:var(--fg);font-family:var(--sans)}
body{font-size:16.5px;line-height:1.6}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
main{max-width:760px;margin:0 auto;padding:36px 22px 80px}
h1{font-size:28px;margin:0 0 28px;font-weight:700;border-bottom:1px solid var(--rule);padding-bottom:18px}
h2{font-size:20px;margin:38px 0 12px;font-weight:650}h3{font-size:16.5px;margin:26px 0 10px;color:var(--fg-dim)}
p,ul,ol{margin:0 0 14px}ul,ol{padding-left:24px}li{margin-bottom:6px}strong{color:#fff}hr{border:none;border-top:1px solid var(--rule);margin:36px 0}
code{font-family:var(--mono);font-size:.88em;background:var(--code-bg);border:1px solid var(--code-border);border-radius:4px;padding:1px 5px}
pre{background:var(--code-bg);border:1px solid var(--code-border);border-radius:6px;padding:14px 16px;overflow-x:auto;font-size:.88em}pre code{background:none;border:none;padding:0}
.meta{color:var(--fg-dim);font-size:.9em;margin-bottom:28px}
"""

html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE} — {PROJECT}</title><style>{CSS}</style>
</head><body><main>
<h1>{TITLE}</h1>
<p class="meta">{PROJECT} &bull; {TODAY}</p>
{md_to_html(BRIEF_MD)}
</main></body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write(html)

# --- Optional: upsert a manifest entry if your site has one (see "How this kind
# of site works" above). Skip this block entirely for a plain static site. ---
try:
    import sys
    sys.path.insert(0, SHARE)
    from app import manifest
    data = manifest.load()
    data["projects"].setdefault(PROJECT, {"label": PROJECT, "section": "Misc", "default_visibility": "public"})
    manifest.upsert_page(data, {
        "file": REL, "project": PROJECT, "date": TODAY, "title": TITLE,
        "tag": TAG, "visibility": None, "password": None, "redirect_from": [],
    })
    manifest.save(data)
except ImportError:
    pass  # no manifest system — plain static file is enough

print(f"Wrote {OUT}\nWill be live at {PUBLIC_URL}")
```

## Step 4 — Deploy (commit → push → pull)

```bash
cd $SITE_LOCAL_CLONE && git add -A && \
  git commit -m "share: $PROJECT — $TITLE" && \
  git push && \
  ssh $SITE_VPS_HOST "cd $SITE_VPS_PATH && git pull --ff-only"
```

If your site's app re-reads its manifest per request, no service restart is
needed — the page is live once the pull completes. If it's a static site,
Caddy/nginx will just serve the new file.

## Step 5 — Notify yourself (optional)

If you've set up the `notify` skill/template from this toolkit, ping it with
the TL;DR + public URL so the brief shows up somewhere other than this chat:

```bash
notify "$TITLE" "$(printf '%s\n\n%s' "$TLDR" "$PUBLIC_URL")" info
```

Skip if you'd rather just read it here.

## Step 6 — Report to the user

- The URL (clickable)
- TL;DR in 2-3 sentences
- The single most important action item
- If the page should be gated/unlisted, remind where that's controlled on your site

## Install
Assumes you already have (or are willing to stand up) a git-backed personal
site on a VPS — see the "How this kind of site works" section above for the
reference shape. Copy this file to `~/.claude/commands/share-publish.md`, fill
in the Config section, and invoke with `/share-publish` or `/share-publish "Title"`.
