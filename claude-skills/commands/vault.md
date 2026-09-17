Search, retrieve, add, or edit Bitwarden vault entries using rbw.

The user's vault is managed with `rbw`. First check if it's unlocked with `rbw unlocked`. If not, tell the user to run `rbw unlock` before proceeding (you cannot enter the master password for them).

## If the user provides arguments: $ARGUMENTS

Treat the argument as a search term and run `rbw get "$ARGUMENTS"` to retrieve the password. If that fails, try `rbw search "$ARGUMENTS"` to show matching entries, then ask which one they want.

Also show the full entry with `rbw get "$ARGUMENTS" --full` so the user can see username, URL, and notes too.

## If no arguments

Ask the user what they want to do:
1. **Get a password** — `rbw get <name>`
2. **See full entry** — `rbw get <name> --full`
3. **Search** — `rbw search <term>`
4. **Add new entry** — walk them through `rbw add` (name, username, password or generate one)
5. **Edit existing** — `rbw edit <name>`
6. **Get a 2FA code** — `rbw code <name>`
7. **Sync vault** — `rbw sync`

## Notes
- `rbw get` prints the password to stdout. Remind the user it'll be visible in terminal history.
- For sensitive entries, suggest piping to clipboard: `rbw get <name> | wl-copy` (swap `wl-copy` for `pbcopy`/`xclip` off Wayland).
- After adding/editing, Bitwarden cloud is updated automatically. Changes from phone/web need `rbw sync` to appear locally.

## Install
Requires [`rbw`](https://github.com/doy/rbw) (`pacman -S rbw` / `brew install rbw`) already configured against your Bitwarden account (`rbw config set email you@example.com && rbw login`).
Copy this file to `~/.claude/commands/vault.md`. Invoke with `/vault` or `/vault <search term>`.
