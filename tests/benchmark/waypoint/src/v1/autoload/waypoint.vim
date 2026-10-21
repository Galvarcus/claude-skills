vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true

# Plugin_Name: waypoint
# Runs the Waypoint commands and mappings.
# License: GNU GPL 3.0

import autoload 'waypoint/entry.vim' as E
import autoload 'waypoint/log.vim' as L
import autoload 'waypoint/popup.vim' as P
import autoload 'waypoint/store.vim' as S

var log = L.New(expand('<sfile>:t'))
var dir = g:waypoint_dir
var store: S.Store = null_object

# FUNCTION: Save the cursor position in the current file as name.
export def Add(name: string)
  if expand('%:p') == ''
    log.Error('The buffer has no file. Save it first.')
    return
  endif
  var s = GetStore()
  s.Put(E.Waypoint.Here(name))
  s.Save()
  log.Info($'Saved waypoint {name} in {s.Path()}.')
enddef

# FUNCTION: Ask for a name, then save the cursor position under it.
export def AddPrompt()
  var name = input('Waypoint name: ')
  if name != ''
    Add(name)
  endif
enddef

# FUNCTION: Open the file of the Waypoint named name and move the cursor.
export def Jump(name: string)
  var w = GetStore().Find(name)
  if w == null_object
    log.Error($'No waypoint named {name}.')
    return
  endif
  if expand('%:p') !=# w.file
    if &modified && !&hidden
      log.Error('The buffer has unsaved changes. Save it first.')
      return
    endif
    execute $'edit {fnameescape(w.file)}'
  endif
  cursor(w.line, w.col)
enddef

# FUNCTION: Show the saved Waypoints in a popup menu.
export def List()
  P.Show(GetStore().items, Jump)
enddef

# FUNCTION: Delete the Waypoint named name.
export def Delete(name: string)
  var s = GetStore()
  if !s.Delete(name)
    log.Error($'No waypoint named {name}.')
    return
  endif
  s.Save()
  log.Info($'Deleted waypoint {name}.')
enddef

# FUNCTION: Complete Waypoint names that start with lead.
export def Complete(lead: string, cmdLine: string, pos: number): list<string>
  return GetStore().Names()->filter((_, n) => stridx(n, lead) == 0)
enddef

# FUNCTION: Drop the cached store, so the next command reads the file.
export def Reset()
  store = null_object
enddef

# FUNCTION: Return the store, read from disk on first use.
def GetStore(): S.Store
  if store == null_object
    store = S.Store.new(dir)
    store.Load()
  endif
  return store
enddef
