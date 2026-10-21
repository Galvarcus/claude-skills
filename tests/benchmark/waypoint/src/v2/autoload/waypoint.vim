vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true

# Plugin_Name: waypoint
# Runs the Waypoint commands, mappings, and autocommands.
# License: GNU GPL 3.0

import autoload 'waypoint/entry.vim' as E
import autoload 'waypoint/log.vim' as L
import autoload 'waypoint/popup.vim' as P
import autoload 'waypoint/scope.vim' as SC
import autoload 'waypoint/store.vim' as S
import autoload 'waypoint/track.vim' as T

var log = L.New(expand('<sfile>:t'))
var stores: dict<S.Store> = {}
var tracker: T.Tracker = null_object

# FUNCTION: Save the cursor position in the current file as name.
export def Add(name: string)
  var file = expand('%:p')
  if file == ''
    log.Error('The buffer has no file. Save it first.')
    return
  endif
  var s = GetStore(file)
  var w = E.Waypoint.Here(name)
  s.Put(w)
  s.Save()
  GetTracker().Mark(w, bufnr())
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
  var w = GetStore(expand('%:p')).Find(name)
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
  w = GetTracker().Current(w, bufnr())
  cursor(w.line, w.col)
enddef

# FUNCTION: Show the Waypoints of the current scope in a popup menu.
export def List()
  P.Show(GetStore(expand('%:p')).items, Jump)
enddef

# FUNCTION: Delete the Waypoint named name.
export def Delete(name: string)
  var s = GetStore(expand('%:p'))
  var w = s.Find(name)
  if w == null_object
    log.Error($'No waypoint named {name}.')
    return
  endif
  s.Delete(name)
  s.Save()
  GetTracker().Unmark(name, bufnr(w.file))
  log.Info($'Deleted waypoint {name}.')
enddef

# FUNCTION: Rename a Waypoint. args holds the old and the new name.
export def Rename(args: list<string>)
  if len(args) != 2
    log.Error('Usage: :WaypointRename {old} {new}')
    return
  endif
  var [old, new] = args
  var s = GetStore(expand('%:p'))
  var w = s.Find(old)
  if w == null_object
    log.Error($'No waypoint named {old}.')
    return
  endif
  if s.Find(new) != null_object
    log.Error($'A waypoint named {new} already exists.')
    return
  endif
  s.Rename(old, new)
  s.Save()
  var buf = bufnr(w.file)
  if buf != -1 && bufloaded(buf)
    GetTracker().Mark(GetTracker().Current(w, buf).Renamed(new), buf)
    GetTracker().Unmark(old, buf)
  endif
  log.Info($'Renamed waypoint {old} to {new}.')
enddef

# FUNCTION: Complete Waypoint names that start with lead.
export def Complete(lead: string, cmdLine: string, pos: number): list<string>
  return GetStore(expand('%:p')).Names()->filter((_, n) => stridx(n, lead) == 0)
enddef

# FUNCTION: Mark the Waypoints of the buffer that was just read.
export def OnRead()
  var file = expand('<afile>:p')
  var buf = str2nr(expand('<abuf>'))
  for w in GetStore(file).InFile(file)
    GetTracker().Mark(w, buf)
  endfor
enddef

# FUNCTION: Save the tracked positions of the buffer that was just written.
export def OnWrite()
  var file = expand('<afile>:p')
  var buf = str2nr(expand('<abuf>'))
  var s = GetStore(file)
  var moved = false
  for w in s.InFile(file)
    var cur = GetTracker().Current(w, buf)
    if cur.line != w.line || cur.col != w.col
      s.Update(cur)
      moved = true
    endif
  endfor
  if moved
    s.Save()
  endif
enddef

# FUNCTION: Drop the cached stores, so the next command reads the files.
export def Reset()
  stores = {}
enddef

# FUNCTION: Return the store for file, read from disk on first use.
def GetStore(file: string): S.Store
  var dir = SC.StoreDir(file)
  if !has_key(stores, dir)
    var s = S.Store.new(dir)
    s.Load()
    stores[dir] = s
  endif
  return stores[dir]
enddef

# FUNCTION: Return the tracker, made on first use.
def GetTracker(): T.Tracker
  if tracker == null_object
    tracker = T.Tracker.new()
  endif
  return tracker
enddef
