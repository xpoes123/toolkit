---
name: propose
description: Show an interactive review page on your own site instead of a wall of text whenever you need someone to weigh in — a design proposal, a set of decisions/options, or an architecture to sign off on. Builds a Tokyo-Night page where each decision is a card reacted to (👍 love / 🤔 tweak / 👎 nope + notes), with a "copy my feedback" button, then reply in chat with a SHORT blurb + the link. Two modes — "proposal" (quick, a few decisions) and "blueprint" (architecture sign-off, bigger, with an overall approve/rework gate). Trigger whenever you'd otherwise dump a design/spec/plan/options in chat for someone to approve. Great for people who find long prose review threads painful and much prefer reacting to visual, sectioned choices.
---

# Propose — interactive review docs

**Template** — this assumes you have (or are willing to stand up) a
git-backed personal site to publish pages to, in the same shape as the
`share-publish` template in this toolkit: write a file into a local clone,
optionally register it in a manifest, commit, push, pull on your VPS.

Instead of walls of text in chat when someone has to make a call: publish a
**visual, sectioned page** where each decision is a card with a tap-a-reaction
control, then send a **short blurb + the link** in chat. They react on the
page, hit **Copy my feedback**, and paste it back.

## Config — edit before use

`publish.py` reads these (env var, with a placeholder default if unset):
- `SITE_LOCAL_CLONE` — e.g. `~/code/your-site-repo` (default: `~/code/your-site-repo`)
- `SITE_VPS_HOST` — e.g. `user@your-vps-host` (default: `user@your-vps-host`)
- `SITE_VPS_PATH` — e.g. `/opt/your-site` (default: `/opt/your-site`)
- `SITE_DOMAIN` — e.g. `https://notes.yourdomain.com` (default: `https://notes.yourdomain.com`)

If your site has a `manifest.py`-style page registry (see `share-publish`),
`publish.py` will use it automatically when importable; otherwise it just
writes the HTML file and skips that step.

## When to use
- Presenting a **spec / design proposal** → mode `proposal`.
- Asking someone to choose between **options / approaches** → mode `proposal`.
- Getting **sign-off on an architecture / data model / big plan** → mode `blueprint`
  (bigger framing + an overall Approve / Approve-with-changes / Rework gate).

If you catch yourself about to write more than ~2 short paragraphs of
design/options in chat, stop and use this instead.

## How

1. **Compose the sections.** Each decision = one card: a short punchy
   proposal, a mockup/table where it helps, kept scannable. Lead with the
   single most important thing (the "why this matters"). Mark your own
   *suggested* additions with `"suggest": true` so they read as your idea,
   not a requirement.

2. **Write a spec JSON** to your scratchpad:
   ```json
   {
     "title": "Finance Hub — v1 Spec",
     "subtitle": "Your call on each piece — react to anything off.",
     "project": "finance",
     "mode": "proposal",
     "blurb": "17 decisions — tap reactions, copy feedback back to me",
     "sections": [
       {"tag": "The core", "title": "Per-category budgets",
        "html": "<p>You set a budget per category…</p><div class='mock'>…</div>",
        "suggest": false}
     ]
   }
   ```
   `html` is arbitrary HTML for the card body. Reusable mockup classes are
   baked into `template.html`:
   - `.mock` — a monospace mockup box. `.hero.over`/`.hero.under` — big signed number.
   - `.tabbar` + `<div class="on">` — a tab bar. `.bar`+`<i style="width:%">` — a progress bar.
   - `table.tradeoff` — an options/trade-off table (great for `blueprint` mode).
   - `.rev`/`.grn`/`.amb` — red/green/amber inline text. `.k` — blue keyword.
   - `.subline` — muted caption. `<ul><li>` — bullets.

3. **Publish:**
   ```bash
   python publish.py <your-spec>.json
   ```
   It renders `template.html`, writes the page into `$SITE_LOCAL_CLONE/<project>/`,
   registers it (unlisted — link-only, not on a public index — if a manifest
   system is present), commits, pushes, and pulls on the VPS. It prints the
   `URL:` and `BLURB:`. Add `--no-deploy` to render locally without pushing
   while iterating.

4. **Reply in chat, SHORT.** One or two lines of context + the link. Do NOT
   restate the whole design in chat — the page is the design. Example:
   > Here's the v1 spec — 17 decisions, tap 👍/🤔/👎 on each and hit **Copy my
   > feedback** to send it back: https://notes.yourdomain.com/finance/2026-…-spec.html

## Modes
- **proposal** (default): quick. A handful of decision cards. No sign-off gate.
- **blueprint**: architecture/big-design sign-off. Same card mechanic PLUS an
  **overall verdict** gate at the bottom (Approve / Approve-with-changes / Rework).
  Use richer cards — trade-off tables, phased plans, the data model. This is
  the one to "sign off" on before writing an implementation plan.

## After feedback comes back
Fold it in. For a `blueprint`, an "Approve" verdict is the green light to
move to an implementation plan. For a `proposal`, revise and either
re-publish (same script, new date-slug) or proceed.

## Notes
- Verify the page is live after publishing (`curl -s -o /dev/null -w "%{http_code}"`
  the URL → expect 200).
- Pages are unlisted by convention — gate/move them in your site's admin if it has one.
- Keep card copy tight — this whole skill exists to avoid walls of text.

## Install
Requires a site to publish to (see Config above) and `python3`. Copy this
directory to `~/.claude/skills/propose/`, fill in the env vars (or edit the
defaults in `publish.py`), and invoke via `/propose`.
