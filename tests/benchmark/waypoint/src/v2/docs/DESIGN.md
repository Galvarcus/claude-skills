# Waypoint design

Waypoint saves named cursor positions and jumps back to them. This document describes version 2, which adds three features to version 1.

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
| `autoload/waypoint/scope.vim` | Finds the store folder for a file |
| `autoload/waypoint/track.vim` | `Tracker` class, the text properties |
| `import/waypoint/variables/constants.vim` | Names shared by more than one script |
| `import/Logger/` | Vendored Logger |

## Classes

| Class | Script | Role |
| --- | --- | --- |
| `Waypoint` | `entry.vim` | One record. Builds itself from the cursor or from a stored record. |
| `Store` | `store.vim` | The list of waypoints in one store file. Loads, saves, adds, finds, renames, and deletes. |
| `Tracker` | `track.vim` | The text properties that keep each waypoint on its line. |

## Errors

Every user error, such as an unknown name or a buffer with no file, goes through Logger as an error message. No command throws.

## Tests

`tests/run.vim` runs `tests/test_store.vim` and `tests/test_commands.vim` and writes `tests/results.txt`. Each test uses a temporary store folder.

## Feature: Rename

### Commands and settings

`:WaypointRename {old} {new}` completes names. It fails, through Logger, when `{old}` does not exist, when `{new}` already exists, or when it gets other than two names.

### Data changes

None. The record keeps its file, line, column, and created time.

### Files touched

`plugin/waypoint.vim`, `autoload/waypoint.vim`, `autoload/waypoint/entry.vim`, and `autoload/waypoint/store.vim`.

### Tests

`tests/test_rename.vim` covers a rename, a rename onto an existing name, and a wrong number of names.

## Feature: Project scope

### Commands and settings

`g:waypoint_scope` is `'global'` by default or `'project'`. `g:waypoint_root_markers` defaults to `['.git']`. The commands are unchanged and act on the scope of the current file.

### Data changes

In project scope, each project root has its own store folder, `projects/<key>/` in `g:waypoint_dir`. The key is the root path with every separator replaced by `%`. A file with no root uses the global store.

### Files touched

`plugin/waypoint.vim`, `autoload/waypoint.vim`, the new `autoload/waypoint/scope.vim`, and the constants file. `autoload/waypoint.vim` caches one store per folder.

### Tests

`tests/test_scope.vim` covers the root search and the global default.

## Feature: Line tracking

### Commands and settings

No new commands or settings. `:WaypointJump` goes to the tracked line.

### Data changes

None on disk. A text property of type `waypoint` marks each waypoint in a loaded buffer. Lookups set `both: true`, because without it `prop_find()` and `prop_remove()` match on the ID or the type alone.

### Files touched

`plugin/waypoint.vim` adds a `BufReadPost` and a `BufWritePost` autocommand. `autoload/waypoint.vim` marks waypoints when a buffer is read and saves moved lines when it is written. The new `autoload/waypoint/track.vim` holds the `Tracker` class.

The autocommands load the autoload scripts the first time a file is read. That cost is the price of tracking from the first edit.

### Tests

`tests/test_track.vim` covers a jump after inserting lines and a write after deleting lines.
