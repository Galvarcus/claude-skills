vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true

# Plugin_Name: waypoint
# Reads and writes the saved Waypoints as one JSON file.
# License: GNU GPL 3.0

import autoload 'waypoint/entry.vim' as E
import 'waypoint/variables/constants.vim' as CO

# CLASS: The saved Waypoints of one store file.
export class Store
  var dir: string
  var items: list<E.Waypoint> = []

  def new(this.dir)
  enddef

  # METHOD: Return the full path of the store file.
  def Path(): string
    return $'{expand(this.dir)}/{CO.STORE_FILE}'
  enddef

  # METHOD: Read the store file. A missing or empty file is an empty store.
  def Load()
    this.items = []
    var path = this.Path()
    if !filereadable(path) || getfsize(path) == 0
      return
    endif
    for d in json_decode(readfile(path)->join("\n"))
      this.items->add(E.Waypoint.FromDict(d))
    endfor
  enddef

  # METHOD: Write every Waypoint to the store file.
  def Save()
    var path = this.Path()
    mkdir(fnamemodify(path, ':h'), 'p')
    writefile([json_encode(this.items->mapnew((_, w) => w.ToDict()))], path)
  enddef

  # METHOD: Add w, or replace the Waypoint with the same name.
  def Put(w: E.Waypoint)
    var idx = this.Index(w.name)
    if idx < 0
      this.items->add(w)
    else
      this.items[idx] = w
    endif
  enddef

  # METHOD: Return the Waypoint named name, or null_object.
  def Find(name: string): E.Waypoint
    var idx = this.Index(name)
    return idx < 0 ? null_object : this.items[idx]
  enddef

  # METHOD: Remove the Waypoint named name. Return false when none exists.
  def Delete(name: string): bool
    var idx = this.Index(name)
    if idx < 0
      return false
    endif
    this.items->remove(idx)
    return true
  enddef

  # METHOD: Return every name, sorted for display and completion.
  def Names(): list<string>
    return this.items->mapnew((_, w) => w.name)->sort()
  enddef

  # METHOD: Return the index in items of the Waypoint named name, or -1.
  def Index(name: string): number
    return indexof(this.items, (_, w) => w.name ==# name)
  enddef
endclass
