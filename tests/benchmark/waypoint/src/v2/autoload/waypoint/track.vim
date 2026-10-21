vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true

# Plugin_Name: waypoint
# Keeps each Waypoint on its line while the buffer changes, with one text
# property per Waypoint in each loaded buffer.
# License: GNU GPL 3.0

import autoload 'waypoint/entry.vim' as E

const PROP_TYPE: string = 'waypoint'

# FUNCTION: Return the key of the mark for name in buffer buf.
def Key(buf: number, name: string): string
  return $'{buf}:{name}'
enddef

# CLASS: The text properties that mark Waypoints in loaded buffers. The
# IDs are keyed by buffer and name, because each project scope can use the
# same name for a Waypoint in a different file.
export class Tracker
  var ids: dict<number> = {}
  var next: number = 1

  def new()
    if empty(prop_type_get(PROP_TYPE))
      prop_type_add(PROP_TYPE, {})
    endif
  enddef

  # METHOD: Mark w in buffer buf, replacing an older mark of the same name.
  def Mark(w: E.Waypoint, buf: number)
    this.Unmark(w.name, buf)
    var lines = getbufline(buf, w.line)
    if empty(lines)
      return
    endif
    var id = this.next
    this.next += 1
    this.ids[Key(buf, w.name)] = id
    prop_add(w.line, min([w.col, len(lines[0]) + 1]),
      {type: PROP_TYPE, id: id, bufnr: buf})
  enddef

  # METHOD: Remove the mark of the Waypoint named name from buffer buf.
  def Unmark(name: string, buf: number)
    var key = Key(buf, name)
    if !has_key(this.ids, key)
      return
    endif
    if buf > 0 && bufloaded(buf)
      prop_remove({type: PROP_TYPE, id: this.ids[key], both: true, bufnr: buf,
        all: true})
    endif
    this.ids->remove(key)
  enddef

  # METHOD: Return w at the position of its mark in buffer buf, or w as it
  # is when the mark is gone, as after deleting its line.
  def Current(w: E.Waypoint, buf: number): E.Waypoint
    var key = Key(buf, w.name)
    if !has_key(this.ids, key)
      return w
    endif
    var p = prop_find({type: PROP_TYPE, id: this.ids[key], both: true,
      bufnr: buf, lnum: 1, col: 1}, 'f')
    return empty(p) ? w : w.Moved(p.lnum, p.col)
  enddef
endclass
