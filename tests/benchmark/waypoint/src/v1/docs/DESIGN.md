# Waypoint design

Waypoint saves named cursor positions and jumps back to them. This document describes version 1.

## Commands

| Command | Behavior |
| --- | --- |
| `:WaypointAdd {name}` | Saves the cursor position of the current file. Replaces a waypoint with the same name. Fails on a buffer with no file. |
| `:WaypointJump {name}` | Opens the waypoint's file unless it is already current, then moves the cursor. |
| `:WaypointList` | Shows a popup menu sorted by name. Picking an entry jumps to it. |
| `:WaypointDelete {name}` | Deletes the waypoint. |

`:WaypointJump` and `:WaypointDelete` complete names by prefix.

## Mappings

`<Plug>(WaypointAdd)` asks for a name. `<Plug>(WaypointList)` runs `:WaypointList`. The default keys `<Leader>wa` and `<Leader>wl` are mapped unless `g:waypoint_no_mappings` is true or the user has mapped the `<Plug>` name.

## Settings

| Setting | Default |
| --- | --- |
| `g:waypoint_dir` | `'~/.vim/waypoint'` |
| `g:waypoint_popup_width` | `60` |
| `g:waypoint_no_mappings` | `false` |

## Storage

One JSON file, `waypoints.json`, in `g:waypoint_dir`. It holds a list of records:

```json
[{"name": "deploy", "file": "/home/sam/src/api/deploy.sh", "line": 42, "col": 5, "created": "2026-10-01T09:00:00"}]
```

A missing or empty file is an empty store. The keys are saved to disk and keep their full names.

## Files

| File | Contents |
| --- | --- |
| `plugin/waypoint.vim` | Settings, commands, and mappings. Calls nothing at load time. |
| `autoload/waypoint.vim` | Command entry points and the cached store |
| `autoload/waypoint/entry.vim` | `Waypoint` class, one record |
| `autoload/waypoint/store.vim` | `Store` class, which reads and writes the JSON file |
| `autoload/waypoint/popup.vim` | The list popup |
| `autoload/waypoint/log.vim` | Gives each script a Logger |
| `import/waypoint/variables/constants.vim` | `PLUGIN_NAME` and `STORE_FILE` |
| `import/Logger/` | Vendored Logger |

## Classes

| Class | Script | Role |
| --- | --- | --- |
| `Waypoint` | `entry.vim` | One record. Builds itself from the cursor or from a stored record. |
| `Store` | `store.vim` | The list of waypoints in one store file. Loads, saves, adds, finds, and deletes. |

## Errors

Every user error, such as an unknown name or a buffer with no file, goes through Logger as an error message. No command throws.

## Tests

`tests/run.vim` runs `tests/test_store.vim` and `tests/test_commands.vim` and writes `tests/results.txt`. Each test uses a temporary store folder.
