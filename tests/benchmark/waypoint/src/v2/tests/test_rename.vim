vim9script

# Plugin_Name: waypoint
# Tests :WaypointRename through the autoload entry point.
# License: GNU GPL 3.0

import autoload 'waypoint.vim' as W

# FUNCTION: Edit a new scratch file of numbered lines.
def EditSample()
  var path = tempname() .. '.txt'
  writefile(range(1, 10)->mapnew((_, n) => $'line {n}'), path)
  execute $'edit! {fnameescape(path)}'
enddef

def Test_rename_moves_the_waypoint_to_the_new_name(): void
  W.Reset()
  EditSample()
  cursor(4, 1)
  W.Add('r_old')
  W.Rename(['r_old', 'r_new'])
  cursor(1, 1)
  W.Jump('r_new')
  assert_equal(4, line('.'))
  assert_equal([], W.Complete('r_old', '', 0))
enddef

def Test_rename_keeps_an_existing_target(): void
  W.Reset()
  EditSample()
  cursor(2, 1)
  W.Add('r_a')
  cursor(6, 1)
  W.Add('r_b')
  W.Rename(['r_a', 'r_b'])
  W.Jump('r_b')
  assert_equal(6, line('.'))
  assert_equal(['r_a'], W.Complete('r_a', '', 0))
enddef

def Test_rename_needs_two_names(): void
  W.Reset()
  EditSample()
  W.Add('r_one')
  W.Rename(['r_one'])
  assert_equal(['r_one'], W.Complete('r_one', '', 0))
enddef

export def RunAll(): void
  Test_rename_moves_the_waypoint_to_the_new_name()
  Test_rename_keeps_an_existing_target()
  Test_rename_needs_two_names()
enddef
