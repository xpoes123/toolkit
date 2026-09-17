Add a bookmark to a rofi bookmarks launcher at `~/.config/rofi/bookmarks`.

File format is one bookmark per line: `Name|target`

Target types (adapt to whatever your launcher script actually does with each):
- URL (`https://...`) — opens in your browser of choice
- `dir:/path/to/dir` — opens a terminal in that directory
- `code:/path/to/dir` — opens Claude Code in that directory

This command only maintains the bookmarks *file* — the rofi script that reads it and dispatches on the prefix (`dir:`, `code:`, bare URL) is a separate piece you write once for your own setup.

If the user gives just a URL, derive a short friendly name from the domain.
If they give a path, use the folder name as the display name unless they specify one.
Append the new entry to the file and confirm what was added.

## Install
Assumes rofi and a bookmarks-reading rofi script/mode pointed at `~/.config/rofi/bookmarks` (write one if you don't have it — it's a ~20 line script that reads the file, shows a rofi menu, and dispatches on the prefix). Copy this file to `~/.claude/commands/bookmark.md`. Invoke with `/bookmark <url or path>`.
