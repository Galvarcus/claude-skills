vim9script

# Hidden tests for feature 3a, :WaypointRename.

import './lib.vim' as H

var dir = tempname()
var work = tempname()
H.Load({waypoint_dir: dir})

def Rename_moves_the_waypoint_to_the_new_name()
  H.EditSample($'{work}/a')
  cursor(4, 1)
  H.Run('WaypointAdd r_old')
  H.Run('WaypointRename r_old r_new')
  assert_equal(['r_new'], H.Names(dir)->filter((_, n) => n =~# '^r_\(old\|new\)$'))
  cursor(1, 1)
  H.Run('WaypointJump r_new')
  assert_equal(4, line('.'))
enddef

def Rename_unknown_old_name_changes_nothing()
  H.EditSample($'{work}/b')
  H.Run('WaypointAdd u_keep')
  var before = H.Names(dir)
  H.Run('WaypointRename u_missing u_other')
  assert_equal(before, H.Names(dir))
enddef

def Rename_to_an_existing_name_changes_nothing()
  H.EditSample($'{work}/c')
  cursor(2, 1)
  H.Run('WaypointAdd e_a')
  cursor(6, 1)
  H.Run('WaypointAdd e_b')
  H.Run('WaypointRename e_a e_b')
  assert_equal([2, 6], [H.LineOf(dir, 'e_a'), H.LineOf(dir, 'e_b')])
enddef

def Rename_with_one_name_does_not_throw()
  H.EditSample($'{work}/d')
  H.Run('WaypointAdd o_one')
  H.Run('WaypointRename o_one')
  assert_true(index(H.Names(dir), 'o_one') >= 0)
enddef

def Rename_completes_names_by_prefix()
  H.EditSample($'{work}/e')
  for n in ['alpha', 'alpine', 'beta']
    H.Run($'WaypointAdd {n}')
  endfor
  assert_equal(['alpha', 'alpine'], getcompletion('WaypointRename alp', 'cmdline'))
enddef

H.Finish([
  ['Rename_moves_the_waypoint_to_the_new_name', Rename_moves_the_waypoint_to_the_new_name],
  ['Rename_unknown_old_name_changes_nothing', Rename_unknown_old_name_changes_nothing],
  ['Rename_to_an_existing_name_changes_nothing', Rename_to_an_existing_name_changes_nothing],
  ['Rename_with_one_name_does_not_throw', Rename_with_one_name_does_not_throw],
  ['Rename_completes_names_by_prefix', Rename_completes_names_by_prefix],
])
