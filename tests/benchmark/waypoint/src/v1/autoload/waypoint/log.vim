vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true

# Plugin_Name: waypoint
# Gives every Waypoint script a Logger that names the plugin once.
# License: GNU GPL 3.0

import 'Logger/logger.vim' as LO
import 'waypoint/variables/constants.vim' as CO

# FUNCTION: Return a Logger for script, the calling script's file name.
export def New(script: string): LO.Logger
  return LO.Logger.new(CO.PLUGIN_NAME, script)
enddef
