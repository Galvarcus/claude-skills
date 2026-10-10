# Logging

Use the Logger plugin for logging. Do not add logging to a script merely because it could log. Log only where the script shows a message: `echo`, `echom`, `echoerr`, captured warnings, errors, or exceptions.

Logger ships in this skill: `import/Logger/*.vim` (four files) and `plugin/logger.vim`, which sets the option defaults and adds `:LoggerMessages`. Copy them to the build environment's runtime path. Check `git@github.com:Galvarcus/Logger.git` (branch `main`) for the latest version.

## Name the plugin once

Never write the plugin name into each script's `Logger.new()` call. `PLUGIN_NAME` is in the shared constants file, see Shared constants in `SKILL.md`, and one script gives every other script its Logger. Replace `plugin_name` with the plugin's folder name. If the name is unknown, ask the user.

In `autoload/plugin_name/log.vim`:

```vim
vim9script
import 'Logger/logger.vim' as LO
import 'plugin_name/variables/constants.vim' as CO

# FUNCTION: Return a Logger for script, the calling script's file name.
export def New(script: string): LO.Logger
  return LO.Logger.new(CO.PLUGIN_NAME, script)
enddef
```

Every other script:

```vim
import autoload 'plugin_name/log.vim' as L
var log = L.New(expand('<sfile>:t'))
```

The caller passes `expand('<sfile>:t')`: `<sfile>` expanded inside `New()` would not name the caller. `log.vim` imports only Logger and the constants file, so it creates no circular import. Logger's alias is `LO` because `L` is `log.vim`.

Command names, highlight groups, and `g:` settings that carry the plugin name as a prefix are identifiers, not repeated values, and stay as written.

## File logging and other options

Do not add plugin settings that copy Logger's options. Logger reads its options on each message, as `g:logger_<plugin>_<option>` with the plugin name in lowercase, or `g:logger_<option>` for all plugins. Document them in the plugin's README instead. For example, file logging:

```vim
let g:logger_pluginname_log_file = v:true
```

Logger then writes one file per Vim session to `~/.Logger/<plugin>_<date>_<time>.log`, with a retention limit (`log_retention`, default 10).
