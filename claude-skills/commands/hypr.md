Help configure, troubleshoot, or reload Hyprland window manager settings.

Config lives at `~/.config/hypr/hyprland.conf`. If the user seems new to Hyprland, explain what a setting does before changing it.

## If the user provides arguments: $ARGUMENTS
Treat as what they want to do (e.g. "add a keybind", "change wallpaper", "fix my monitor").

## Common tasks

### Reload config (no restart needed)
```
hyprctl reload
```
Most changes to hyprland.conf apply immediately after this. Tell the user to run it after any edit.

### Check what's running / connected
```
hyprctl monitors    # display info
hyprctl clients     # open windows
hyprctl workspaces  # workspace list
```

### Add a keybind
Keybinds go in hyprland.conf under the `### KEYBINDINGS ###` section:
```
bind = $mainMod, KEY, exec, command
```
Example — open a browser with Super+B:
```
bind = $mainMod, B, exec, firefox
```
`$mainMod` is usually set to SUPER (the Windows key) near the top of the config — check there if a bind isn't firing.

### Wallpaper
If using `swww`:
```
swww img /path/to/image.jpg --transition-type wipe --transition-duration 1
```
If using `hyprpaper` or a fork like `awww`, the CLI differs slightly (`awww img ...`) — check which daemon is actually running (`pgrep -a swww; pgrep -a hyprpaper; pgrep -a awww-daemon`) before assuming.
To set wallpaper on startup, add to hyprland.conf `exec-once`:
```
exec-once = swww-daemon && swww img /path/to/image.jpg
```

### Waybar
Config typically lives at `~/.config/waybar/config.jsonc` and `~/.config/waybar/style.css`.
Restart waybar after changes:
```
pkill waybar; waybar &
```

### Check Hyprland logs for errors
```
journalctl --user -u hyprland --since today | tail -50
```
Or check the runtime log:
```
cat /tmp/hypr/$(ls /tmp/hypr/)/hyprland.log | tail -50
```

## Notes
- Always explain what a config change does before making it.
- Monitor config (`monitor=` lines) is resolution/refresh/position/scale specific to the user's setup — ask `hyprctl monitors` before suggesting values rather than guessing.

## Install
Assumes Hyprland is already installed and running. Copy this file to `~/.claude/commands/hypr.md`. Invoke with `/hypr` or `/hypr <what you want to do>`.
