# Waypoint analysis

## Architecture

The plugin file defines settings, commands, mappings, and two autocommands. Each one calls into `autoload/waypoint.vim`, which caches one `Store` per store folder and one `Tracker`. `Store` reads and writes a JSON file. `Tracker` marks each waypoint with a text property so it follows edits.

## Strengths

- The plugin file loads no autoload code until a command runs or a file is read.
- The store is plain JSON that users can read and back up.
- Hidden state stays in two classes with small interfaces.

## Risks

- Two Vim sessions that save at the same time overwrite each other's store.
- A waypoint whose file was moved or deleted stays in the list.

## Suggested features

### Waypoint history

**Value:** users can step back through the waypoints they visited.

**Design:** keep a list of visited names in `autoload/waypoint.vim` and add `:WaypointBack`.

**Files:** `autoload/waypoint.vim`, `plugin/waypoint.vim`, and `doc/waypoint.txt`.

**Effort:** S

### Stale waypoint cleanup

**Value:** the list shows only waypoints whose files still exist.

**Design:** add `:WaypointPrune`, which deletes waypoints with missing files after asking.

**Files:** `autoload/waypoint/store.vim` and `plugin/waypoint.vim`.

**Effort:** S

### Safe concurrent saves

**Value:** two Vim sessions no longer lose each other's waypoints.

**Design:** reread the store file before each save and merge by name, newest first.

**Files:** `autoload/waypoint/store.vim` and `tests/test_store.vim`.

**Effort:** M
