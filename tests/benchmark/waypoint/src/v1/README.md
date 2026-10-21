# Waypoint

Waypoint saves named cursor positions in Vim and jumps back to them, across files and sessions.

Requires Vim 9.2 or later.

## Installation

Clone the repository into a package directory:

```sh
git clone https://github.com/example/waypoint ~/.vim/pack/plugins/start/waypoint
```

Then run `:helptags ALL`.

## Usage

| Command | Action |
| --- | --- |
| `:WaypointAdd {name}` | Save the cursor position as `{name}` |
| `:WaypointJump {name}` | Jump to waypoint `{name}` |
| `:WaypointList` | Pick a waypoint from a popup menu |
| `:WaypointDelete {name}` | Delete waypoint `{name}` |

The default keys are `<Leader>wa`, which asks for a name and adds a waypoint, and `<Leader>wl`, which opens the list.

## Configuration

| Setting | Default | Meaning |
| --- | --- | --- |
| `g:waypoint_dir` | `'~/.vim/waypoint'` | Folder of the store file |
| `g:waypoint_popup_width` | `60` | Width of the list popup |
| `g:waypoint_no_mappings` | `false` | Skip the default keys |

Waypoint logs through Logger. To write a log file, set:

```vim
let g:logger_waypoint_log_file = v:true
```

## Development

Run the tests from the repository root:

```sh
vim -Nu NONE -i NONE -es -c 'set rtp^=.' -c 'source tests/run.vim'
cat tests/results.txt
```

## License

GNU GPL 3.0
