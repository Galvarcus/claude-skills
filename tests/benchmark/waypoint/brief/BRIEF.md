# Waypoint brief

I keep losing my place when I jump between files in a large project. Marks help, but I can't name them and they don't survive well across sessions. I want a small Vim plugin called Waypoint.

## What it should do

- Save the cursor position under a name I choose, such as `deploy` or `parser-bug`.
- Jump back to a named position later, even after restarting Vim. Jumping should open the file if it isn't open.
- Show all saved positions in a list I can pick from.
- Delete a position I no longer need.
- Complete names when I type a jump or delete command.

## Constraints

- Vim 9.2 and Vim9script only. I don't use Neovim.
- Nothing slow at startup. Most days I won't use the plugin.
- Store the positions in a plain file I can read and back up, in a folder I can change.
- Give me two default keys, one to add and one to list, and a way to turn them off.
- Use my Logger plugin for messages, like my other plugins.
- Tests that run headless, so I can run them in CI.

## Out of scope for now

Renaming positions, separate positions per project, and keeping a position on its line while I edit above it. I may want these later, so the design shouldn't rule them out.
