# Claude Code skills

Personally-authored Claude Code commands and skills, pulled out of David's
`~/.claude/` and generalized so anyone can use them. Same spirit as the rest
of this toolkit: real tools that were actually used daily, with the
personal-infrastructure specifics (IPs, domains, bot names, service lists)
swapped for placeholder config.

Two kinds of files, matching Claude Code's own conventions:
- **Commands** (`commands/*.md`) — single-file slash commands. Copy to `~/.claude/commands/<name>.md`. Invoke as `/<name> [args]`.
- **Skills** (`skills/<name>/SKILL.md` + assets) — folder-based, with frontmatter (`name`, `description`) that Claude uses to decide when to trigger. Copy the whole folder to `~/.claude/skills/<name>/`.

## Commands

| File | What it does | Status |
|---|---|---|
| `commands/vault.md` | Search/retrieve/add/edit Bitwarden entries via `rbw` | As-is, generic |
| `commands/pkg.md` | Install/remove/search packages on Arch-based Linux | As-is, generic |
| `commands/hypr.md` | Configure/troubleshoot Hyprland window manager | Lightly genericized (dropped personal hardware/name refs) |
| `commands/bookmark.md` | Append a bookmark to a rofi bookmarks file | As-is, generic |
| `commands/run.md` | Append a command to a rofi command-menu file | As-is, generic |
| `commands/transcript.md` | Pull + clean a YouTube transcript via `yt-dlp` | As-is, generic |
| `commands/vps-ops.md` | SSH/deploy/logs/status pattern for a Caddy+systemd VPS | **Template** — IP/domain/service-table stripped to placeholders |
| `commands/share-publish.md` | Publish a session brief to a git-backed personal site | **Template** — repo/VPS/domain stripped to env-var config |

## Skills

| Folder | What it does | Status |
|---|---|---|
| `skills/notify/` | Ping yourself (Discord/Slack/etc.) when work finishes | **Template** — swapped a private bot API for a generic Discord-webhook example script |
| `skills/propose/` | Publish an interactive Tokyo-Night review page (react to design decisions, copy feedback back) instead of a wall of chat text | **Template** — site/VPS coordinates are env-configurable, manifest-registry step optional |
| `skills/memory-refresh/` | Weekly sweep of Claude Code transcripts for memory-worthy facts your session missed | Lightly genericized — assumes you run a `MEMORY.md`-style memory index |
| `skills/gm-brief/` | Fan out subagents to deep-dive a project/domain, rank automation ideas, scope the top ones, publish + notify | Generic from the start — composes with `notify/` and `share-publish.md` |

## Config conventions

Templates use env vars or an explicit "Config" block at the top of the file
— fill those in (or just tell Claude the values once at the start of a
session; it'll use them for that conversation). Nothing in this directory
contains real IPs, domains, tokens, or service names — those were either
generalized into placeholders or, where they couldn't be cleanly separated
from personal infrastructure, left out of the toolkit entirely.

## Deliberately excluded

- **`weekly-audit`** — a multi-agent weekly recap skill (desktop+VPS health,
  project roundup, Claude Code usage coaching). Too entangled with a
  specific personal directory layout, a private nightly-extraction tool not
  included here, and specific project/service names to cleanly genericize
  without gutting most of its content. The underlying pattern (a lead agent
  fanning out read-only subagents, then synthesizing a recap) is worth
  reproducing fresh if you want it — see `skills/propose` and `skills/notify`
  for the same fan-out-and-report shape applied to smaller jobs.
- Two licensed/third-party skills (video generation, "hyperframes") are not
  David's own work and were never candidates for this repo.
