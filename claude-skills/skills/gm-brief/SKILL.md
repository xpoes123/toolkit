---
name: gm-brief
description: Deep-dive a project (or any domain you're the "GM" of) with fanned-out subagents to find high-leverage automation ideas, scope the best ones into build-ready specs, publish a shareable report, and notify you. Use when you want to reduce how often you have to personally stay on top of something — a fantasy team, a trading system, a side project, a monitoring setup — by finding what a genuinely obsessive manager would automate. Trigger phrases: "deep dive on X", "find ways to automate X", "be a sweaty GM for X", "what am I missing on X".
---

# GM Brief

Turns "I don't want to have to stay this on top of X" into a ranked, scoped
backlog of concrete automations — by fanning out research subagents instead
of brainstorming alone, then publishing the result somewhere you'll actually
read it.

Originated from a real run: turning a fantasy-football draft tool into a
"sweaty GM" system (waiver alerts, injury-trend monitoring, line-movement
signals) by deep-diving the existing codebase plus adjacent projects that
already had reusable alerting patterns. This skill generalizes that pattern
to any domain — it isn't fantasy-football-specific.

## When to use

- You have an existing system/project that requires you to pay attention
  manually, and want to find what could be automated instead.
- You want breadth (many independent research angles) before committing to
  what to build, not just your own first idea.
- The output should be something you read later (a report), not code
  written immediately — this skill scopes ideas, it doesn't implement them.

## Config

This skill composes with two other toolkit skills — fill these in, or skip
the steps that need them and just print the report inline instead:

- `NOTIFY_CMD` — how you get pinged when something finishes (see
  `../notify/` — e.g. a Discord webhook script, `notify-sage`, whatever you
  wired up). Leave unset to skip notification.
- `SHARE_PUBLISH` — how you publish a page you can read in a browser (see
  `../../commands/share-publish.md`). Leave unset to just print the full
  report in the response instead.

## Steps

### 1. Scope the domain

Nail down in one or two sentences: what's the system/domain, what already
exists (code, automation, feeds), and what's the pain point (what requires
manual attention today). If this isn't already clear from the request, ask
one clarifying question rather than guessing — the whole exercise is wasted
if it's aimed at the wrong problem.

### 2. Fan out research subagents (use your orchestration tool — Workflow if
available, otherwise parallel Task/Agent calls)

Run at least 3 independent research angles in parallel, each blind to the
others (that's what surfaces things a single pass misses):

- **Current state** — read the actual code/system in full. What runs
  automatically today, what's manual, what TODOs or known gaps exist in its
  own docs.
- **Reusable infra** — search sibling projects/repos for patterns that
  already solve a piece of this (an existing alerting pipe, a diff/snapshot
  pattern, a notification channel) so new ideas plug into what exists
  instead of reinventing it.
- **Broad brainstorm** — a wide, breadth-over-polish list of what a
  genuinely obsessive manager of this domain would do that a casual one
  skips because it's tedious. Every idea should note its data source and
  whether it's fully-automatable or needs a human yes/no.

Add more angles if the domain calls for it (e.g. a "what would break this"
risk-focused pass for anything money- or safety-adjacent).

### 3. Rank

One synthesis pass over all research memos: produce a ranked shortlist
(impact-per-effort, best first) of 6-10 ideas. For each: one-line pitch, why
it matters, rough effort, what existing code/infra it builds on. This step
needs the full research context, so it can't run until step 2 finishes.

### 4. Scope the top ideas

Expand the top 4-6 into build-ready specs: exact trigger/schedule, data
source (and how to get it), what the actual alert/output looks like
(concrete example, not a description), which file/module it extends vs.
needs new, and an honest MVP-vs-later split. Write this as a standalone
report — someone should be able to read just this and know what to build
first.

### 5. Publish and notify

If `SHARE_PUBLISH` is configured, publish the ranked list + top-N specs as
a page (see that skill for the exact mechanism). If `NOTIFY_CMD` is
configured, ping with a one-paragraph summary + the link. If neither is
configured, just give the full report in your response — don't skip the
report because publishing isn't wired up.

## Notes

- This is a **research-and-scope** skill, not a build skill — stop at the
  spec. If the person then asks you to implement item #1, that's a separate,
  normal implementation task using the spec as the plan.
- Keep the "also considered" tail (ideas that didn't make the top N) in the
  report — cut ideas are still useful context for later, and it shows the
  ranking wasn't arbitrary.
- Bias ideas toward what's already automatable with existing infra over
  what requires a new platform/service — the whole point is reducing effort,
  not adding a new thing to maintain.
