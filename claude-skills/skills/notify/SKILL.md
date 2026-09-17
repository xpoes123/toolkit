---
name: notify
description: Message yourself (Discord/Slack/ntfy/etc.) when work finishes — a quick ping for small things, or a brief + link when there's real detail to read. Trigger proactively when a significant task completes (a feature shipped, a bug fixed, a deploy done, a long-running job finished) or whenever you're asked to be notified/messaged/pinged. Skip for small edits, mid-conversation answers, or read-only investigation — most turns should NOT trigger this.
---

# Notify

**Template** — this assumes you want Claude Code to reach you through some
out-of-band channel (Discord, Slack, ntfy, a webhook, your own bot) instead
of just ending the response silently. Pick one of two shapes based on how
much there is to say.

## Config — edit before use

This skill ships with `notify-example.sh`, a minimal Discord-webhook
implementation:
- Create a webhook in your Discord server (Channel Settings → Integrations →
  Webhooks) and set `DISCORD_WEBHOOK_URL` in your environment.
- Copy `notify-example.sh` somewhere on your `PATH` (e.g. `~/.local/bin/notify`) and `chmod +x` it.

If you use Slack/ntfy/your own bot API instead, swap the `curl` call in that
script for your provider — the interface (`notify TITLE [BODY] [LEVEL]`) is
the useful part, not the Discord specifics.

## Quick ping — nothing more to read

The message *is* the whole update: a one-line status, a deploy confirmation, "done,
nothing broke." No brief/link needed.

```bash
notify "TITLE" "one or two sentence summary" info
```

Args: TITLE, BODY, LEVEL. LEVEL is `info` for routine completions — reserve
`warn`/`crit` for things that actually need attention (a failure, something
broken), not normal "done."

## Full brief — there's real detail (multi-step session, decisions made, things that failed, a diff worth reviewing)

If you've set up the `share-publish` template from this toolkit, run it end
to end — its last step already posts the TL;DR + public URL via `notify`,
so don't call `notify` again yourself after running it (that would double-post).
Otherwise, just write the brief into `notify`'s BODY directly.

## When to trigger

Proactively, at the end of work you'd otherwise have to come back and check
on: a feature shipped, a bug fixed, a deploy or long-running build finished.
Also whenever explicitly asked to be notified/messaged/pinged.

Do NOT trigger for: small edits, mid-conversation answers, read-only
investigation, or anything still in progress. When unsure whether it's
"significant," default to not sending — false pings erode trust in the
channel faster than a missed one does.

## Install

1. Set up a webhook/bot for whatever channel you want pinged (Discord webhook is the easy default — see Config above).
2. Copy `notify-example.sh` to `~/.local/bin/notify` (or wherever's on your `PATH`), `chmod +x` it, and set `DISCORD_WEBHOOK_URL` (or adapt the script to your provider).
3. Copy `SKILL.md` to `~/.claude/skills/notify/SKILL.md`.
