vim9script

# Plugin_Name: waypoint
# Tests that a Waypoint follows its line as lines change above it.
# License: GNU GPL 3.0

import autoload 'waypoint.vim' as W

# FUNCTION: Edit a new scratch file of numbered lines and return its path.
def EditSample(): string
  var path = tempname() .. '.txt'
  writefile(range(1, 20)->mapnew((_, n) => $'line {n}'), path)
  execute $'edit! {fnameescape(path)}'
  return path
enddef

def Test_jump_follows_lines_inserted_above(): void
  W.Reset()
  EditSample()
  cursor(10, 1)
  W.Add('k_insert')
  append(0, ['new 1', 'new 2', 'new 3'])
  cursor(1, 1)
  W.Jump('k_insert')
  assert_equal(13, line('.'))
enddef

def Test_write_saves_the_moved_line(): void
  W.Reset()
  EditSample()
  cursor(10, 1)
  W.Add('k_write')
  :1,2delete
  silent write
  W.Reset()
  cursor(1, 1)
  W.Jump('k_write')
  assert_equal(8, line('.'))
enddef

export def RunAll(): void
  Test_jump_follows_lines_inserted_above()
  Test_write_saves_the_moved_line()
enddef
