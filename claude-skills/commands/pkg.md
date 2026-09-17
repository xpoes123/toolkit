Install, remove, or search for packages on an Arch-based Linux system (Arch, CachyOS, Manjaro, EndeavourOS, etc.).

Package managers:
- `pacman` — official Arch repos (use `sudo pacman -S <pkg>`)
- `yay` or `paru` — AUR (Arch User Repository) for community packages not in official repos

## If the user provides arguments: $ARGUMENTS

Treat as a package name or description. Do the following:
1. Search official repos first: `pacman -Ss "$ARGUMENTS"`
2. If not found or user wants AUR: `yay -Ss "$ARGUMENTS"` (if yay is installed)
3. Recommend the best match and confirm before installing

## Common operations

**Install:** `sudo pacman -S <package>`
**Remove (and unused deps):** `sudo pacman -Rs <package>`
**Search:** `pacman -Ss <term>`
**Update everything:** `sudo pacman -Syu`
**What package owns a file:** `pacman -Qo <filepath>`
**List explicitly installed packages:** `pacman -Qe`

## AUR packages
Some packages (Discord, Spotify, Brave, etc.) live in the AUR. Check if `yay` or `paru` is installed first:
```
which yay paru 2>/dev/null
```
If neither is installed, explain that the user needs an AUR helper and offer to install `paru`.

## Notes
- Always use `pacman -Rs` not `pacman -R` when removing — the `-s` cleans up orphaned dependencies.
- Arch-based rolling releases update everything at once via `sudo pacman -Syu` — don't partially upgrade.
- Explain what a package does before installing, especially system-level ones.

## Install
No dependencies beyond pacman itself (and optionally an AUR helper). Copy this file to `~/.claude/commands/pkg.md`. Invoke with `/pkg` or `/pkg <package name>`.
