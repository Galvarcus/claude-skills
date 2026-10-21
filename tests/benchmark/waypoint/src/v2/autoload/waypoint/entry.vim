vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true

# Plugin_Name: waypoint
# Defines Waypoint, one named cursor position in a file.
# License: GNU GPL 3.0

# Stored on disk in each record, so old stores depend on it.
const TIME_FMT: string = '%Y-%m-%dT%H:%M:%S'

# CLASS: A named cursor position in a file.
export class Waypoint
  var name: string
  var file: string
  var line: number
  var col: number
  var created: string

  def new(this.name, this.file, this.line, this.col, this.created)
  enddef

  # METHOD: Return a Waypoint for the cursor in the current buffer.
  static def Here(name: string): Waypoint
    return Waypoint.new(name, expand('%:p'), line('.'), col('.'),
      strftime(TIME_FMT))
  enddef

  # METHOD: Return a Waypoint from a record of the store file.
  static def FromDict(d: dict<any>): Waypoint
    return Waypoint.new(d.name, d.file, d.line, d.col, d.created)
  enddef

  # METHOD: Return the record that the store file holds.
  def ToDict(): dict<any>
    return {
      name: this.name,
      file: this.file,
      line: this.line,
      col: this.col,
      created: this.created,
    }
  enddef

  # METHOD: Return the line that the list popup shows.
  def Label(): string
    var path = fnamemodify(this.file, ':~:.')
    return $'{this.name}  {path}:{this.line}'
  enddef

  # METHOD: Return a copy named name. Objects stay read only outside.
  def Renamed(name: string): Waypoint
    return Waypoint.new(name, this.file, this.line, this.col, this.created)
  enddef

  # METHOD: Return a copy at line and col.
  def Moved(line: number, col: number): Waypoint
    return Waypoint.new(this.name, this.file, line, col, this.created)
  enddef
endclass
