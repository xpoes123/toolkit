---
name: project-deep-dive
description: Deeply analyze a project with fanned-out subagents — current state, gaps, adjacent reusable patterns — then merge that with your existing TODOs/backlog into one reprioritized, scoped roadmap. Use when you want a real answer to "what should I build next on this" instead of picking off the top of a stale TODO list. Trigger phrases: "deep dive on this project", "what should I build next", "reprioritize my todos", "analyze this and tell me what to do".
---

# Project Deep Dive

Turns "I haven't looked at this project in a while, what should I actually
do with it" into a single reprioritized, scoped roadmap — by fanning out
research subagents instead of skimming the README yourself, and merging the
result with whatever backlog/TODOs already exist instead of ignoring them.

Two things make this different from just asking Claude "what should I build
next": (1) it reads the actual code and adjacent projects in parallel via
independent subagents, so it finds things a single linear pass misses, and
(2) it doesn't just generate fresh ideas — it explicitly pulls in your
existing TODOs/backlog/open-questions docs and re-ranks everything together,
so old half-remembered plans don't get silently ignored in favor of shiny
new ones.

## When to use

- You want a real prioritized answer, not a brainstorm — this ends in a
  ranked, scoped list, not just ideas.
- The project has existing TODOs, a backlog, open-questions docs, or a
  HANDOFF-style doc that should factor into the ranking, not be replaced by it.
- You want breadth (multiple independent research angles) before committing,
  not just your own first read of the code.

## Config

Composes with two other toolkit skills — fill in, or skip and just print
the report inline:

- `NOTIFY_CMD` — how you get pinged when it's done (see `../notify/`).
  Leave unset to skip.
- `SHARE_PUBLISH` — how you publish something readable in a browser (see
  `../../commands/share-publish.md`). Leave unset to print the full report
  in the response instead.

## Steps

### 1. Scope the project

Confirm which project/repo, and locate anything that already tracks
intent: TODO comments, a backlog doc, `HANDOFF.md`, `docs/open_questions.md`,
GitHub issues, a roadmap section in the README. If it's genuinely untracked
(nothing exists), that's fine — note it and move on to research.

### 2. Fan out research subagents (Workflow if available, else parallel
Task/Agent calls) — at least 3 independent, blind-to-each-other angles:

- **Current state** — read the actual code in full: what's built and
  working, what's half-finished, what's explicitly marked TODO/FIXME/"not
  built yet" in the code or docs.
- **Existing intent** — read every backlog/TODO/open-questions/HANDOFF
  source found in step 1 and extract every discrete planned item, with
  whatever context explains *why* it was planned (a decision, a constraint,
  a deferred tradeoff).
- **Adjacent + fresh ideas** — look at sibling projects for reusable
  patterns, and independently brainstorm what's missing or worth building,
  breadth over polish. Don't read the "existing intent" memo first — this
  angle should be blind, so it doesn't just rubber-stamp the old list.

Add more angles when the project calls for it (a risk/safety pass for
anything money- or user-data-adjacent, a "what's actually being used"
usage-analysis pass if that's answerable).

### 3. Merge and rank

One synthesis pass over ALL memos together — old backlog items and new
ideas in the same list, not two separate sections. Rank by impact-per-effort,
best first. For each item: one-line pitch, why it matters now, rough effort,
whether it's a pre-existing TODO or a fresh find, what it builds on. This
step needs all of step 2's output, so it can't start until that phase
finishes. Explicitly call out anything from the old backlog that no longer
seems worth doing (stale/superseded) rather than silently keeping it ranked.

### 4. Scope the top items

Expand the top 4-6 into build-ready specs: what exactly changes, which
file/module, a concrete example of the end result (not just a description),
and an MVP-vs-later cut. Standalone enough that someone could hand just this
section to an implementer.

### 5. Publish and notify

If `SHARE_PUBLISH` is configured, publish the merged ranked list + top-N
specs as a page. If `NOTIFY_CMD` is configured, ping with a short summary +
link. If neither is configured, give the full report inline — don't skip
the report just because publishing isn't wired up.

## Notes

- This is research-and-scope, not build — stop at the spec. Implementing
  item #1 afterward is a normal separate task using the spec as the plan.
- Keep a visible "also considered" tail (items that didn't make the top N,
  including deprioritized old TODOs) — shows the ranking wasn't arbitrary
  and preserves context for later instead of silently dropping it.
- If the project has real stakes (money, live users, safety-critical paths),
  say so explicitly in the report rather than treating every idea as equally
  low-risk to just go build.
