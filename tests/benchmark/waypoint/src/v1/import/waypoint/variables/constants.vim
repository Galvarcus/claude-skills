vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true

# Plugin_Name: waypoint
# Holds the values that more than one Waypoint script uses.
# License: GNU GPL 3.0

export const PLUGIN_NAME: string = 'Waypoint'
# Stored on disk, so it stays a literal when the plugin is renamed.
export const STORE_FILE: string = 'waypoints.json'
