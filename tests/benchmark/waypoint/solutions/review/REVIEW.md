# Waypoint code review

## Bugs

- `autoload/waypoint/store.vim:33`: `Load()` passes an empty store file to `json_decode()`, which throws E491. Treat a zero-size file as an empty store again.
- `autoload/waypoint.vim:113`: `Complete()` filters with `n =~ lead`, an unanchored regex that also follows `ignorecase`. Use a prefix match: `stridx(n, lead) == 0`.

## vim9script-plugin rules

- `autoload/waypoint/popup.vim:30`: `Show()` reads the global `g:waypoint_popup_width` inside a function. Copy it to a script-local variable near the top.
- `autoload/waypoint.vim:81`: the message types `waypoints.json` instead of using `CO.STORE_FILE`.
- `plugin/waypoint.vim:31`: the plugin file calls `W.KeysFree()` at load time, which loads the autoload scripts at every start. Move the check into the mapping's action.

## code-comments rules

- `autoload/waypoint/store.vim:70`: inline comment `# drop it`. Remove it.
- `autoload/waypoint/entry.vim:55`: `# ---- copies ----` is a delimiter made of dashes. Remove it.

## Documentation

- `doc/waypoint.txt:31`: `:WaypointRename` has no help tag. Add `*:WaypointRename*`.
