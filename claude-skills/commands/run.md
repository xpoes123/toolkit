Add a command to a rofi command menu at `~/.config/rofi/commands`.

File format is one entry per line: `Name|shell command`

The user will describe a task they want as a quick-access command (e.g. "kill all claude sessions", "restart waybar"). Translate it into a working shell one-liner, give it a clear short name, and append to the file. Confirm what was added.

## Install
Assumes rofi and a rofi script/mode that reads `~/.config/rofi/commands`, shows a menu, and runs the selected line's command (write one if you don't have it — same shape as the bookmark launcher: read the file, split on `|`, run the second half via `sh -c`). Copy this file to `~/.claude/commands/run.md`. Invoke with `/run <task description>`.
