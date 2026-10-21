vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true

# Plugin_Name: waypoint
# Picks the store folder for a file: one for all files, or one per project.
# License: GNU GPL 3.0

import 'waypoint/variables/constants.vim' as CO

var dir = g:waypoint_dir
var scope = g:waypoint_scope
var markers = g:waypoint_root_markers
# Holds one store folder per project, named after the project root.
const PROJECTS_DIR: string = 'projects'

# FUNCTION: Return the store folder for file. Fall back to the global
# folder when the scope is global or file has no project root.
export def StoreDir(file: string): string
  if scope !=# CO.SCOPE_PROJECT
    return dir
  endif
  var root = Root(file)
  return root == '' ? dir : $'{dir}/{PROJECTS_DIR}/{Key(root)}'
enddef

# FUNCTION: Return the project root of file, the nearest folder above it
# that holds a root marker, or an empty string.
export def Root(file: string): string
  var cur = file == '' ? getcwd() : fnamemodify(file, ':p:h')
  while true
    for m in markers
      var path = $'{cur}/{m}'
      if isdirectory(path) || filereadable(path)
        return cur
      endif
    endfor
    var parent = fnamemodify(cur, ':h')
    if parent ==# cur
      return ''
    endif
    cur = parent
  endwhile
  return ''
enddef

# FUNCTION: Return a folder name that stands for root on every platform.
def Key(root: string): string
  return substitute(fnamemodify(root, ':p'), '[/\\:]', '%', 'g')
enddef
