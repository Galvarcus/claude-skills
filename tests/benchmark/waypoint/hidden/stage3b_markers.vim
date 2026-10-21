vim9script

# Hidden test for feature 3b with custom g:waypoint_root_markers.

import './lib.vim' as H

var dir = tempname()
var base = tempname()
mkdir($'{base}/proj/.wproot', 'p')
mkdir($'{base}/gitonly/.git', 'p')
mkdir($'{base}/outer/.wproot', 'p')
mkdir($'{base}/outer/inner/sub', 'p')
mkdir($'{base}/outer/other', 'p')
writefile([], $'{base}/outer/inner/Makefile')
H.Load({waypoint_dir: dir, waypoint_scope: 'project', waypoint_root_markers: ['.wproot', 'Makefile']})

def Custom_markers_replace_the_default()
  H.EditSample($'{base}/proj', 'p.txt')
  H.Run('WaypointAdd cm')
  H.EditSample($'{base}/gitonly', 'g.txt')
  assert_equal(-1, index(getcompletion('WaypointJump c', 'cmdline'), 'cm'))
enddef

# The nearest folder with any marker is the root, and a marker may be a file.
def Nearest_marker_wins_and_files_count()
  H.EditSample($'{base}/outer/inner/sub', 's.txt')
  H.Run('WaypointAdd nm')
  H.EditSample($'{base}/outer/other', 'o.txt')
  assert_equal(-1, index(getcompletion('WaypointJump n', 'cmdline'), 'nm'), 'inner shares a store with outer')
  H.EditSample($'{base}/outer/inner', 'i.txt')
  assert_true(index(getcompletion('WaypointJump n', 'cmdline'), 'nm') >= 0, 'inner misses its own waypoint')
enddef

H.Finish([
  ['Custom_markers_replace_the_default', Custom_markers_replace_the_default],
  ['Nearest_marker_wins_and_files_count', Nearest_marker_wins_and_files_count],
])
