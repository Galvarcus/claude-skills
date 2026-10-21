vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true

# Plugin_Name: waypoint
# Shows the saved Waypoints in a popup menu and jumps to the one picked.
# License: GNU GPL 3.0

import autoload 'waypoint/entry.vim' as E
import autoload 'waypoint/log.vim' as L
import 'waypoint/variables/constants.vim' as CO

var log = L.New(expand('<sfile>:t'))
var width = g:waypoint_popup_width

# FUNCTION: Show items sorted by name. Call OnPick with the picked name.
# Return the popup window ID, or 0 when there is nothing to show.
export def Show(items: list<E.Waypoint>, OnPick: func(string)): number
  if empty(items)
    log.Info('No waypoints saved.')
    return 0
  endif
  var sorted = items->copy()->sort((a, b) => a.name ==# b.name ? 0
    : a.name ># b.name ? 1 : -1)
  return popup_menu(sorted->mapnew((_, w) => w.Label()), {
    title: $' {CO.PLUGIN_NAME} ',
    minwidth: width,
    maxwidth: width,
    callback: (_, idx) => {
      if idx > 0
        OnPick(sorted[idx - 1].name)
      endif
    },
  })
enddef
