vim9script

# Plugin_Name: waypoint
# Tests the Waypoint commands through the autoload entry points.
# License: GNU GPL 3.0

import autoload 'waypoint.vim' as W

const SAMPLE_LINES: number = 20

# FUNCTION: Edit a new scratch file of numbered lines and return its path.
def EditSample(): string
  var path = tempname() .. '.txt'
  writefile(range(1, SAMPLE_LINES)->mapnew((_, n) => $'line {n}'), path)
  execute $'edit! {fnameescape(path)}'
  return path
enddef

def Test_add_then_jump_returns_to_the_line(): void
  W.Reset()
  EditSample()
  cursor(5, 3)
  W.Add('t_jump')
  cursor(1, 1)
  W.Jump('t_jump')
  assert_equal(3, col('.'))
enddef

def Test_jump_opens_the_saved_file(): void
  W.Reset()
  var path = EditSample()
  cursor(2, 1)
  W.Add('t_open')
  enew!
  W.Jump('t_open')
  assert_equal(path, expand('%:p'))
enddef

def Test_add_persists_across_reset(): void
  W.Reset()
  EditSample()
  W.Add('t_persist')
  W.Reset()
  assert_true(index(W.Complete('t_pers', '', 0), 't_persist') >= 0)
enddef

def Test_complete_filters_by_prefix(): void
  W.Reset()
  EditSample()
  W.Add('t_cmp_one')
  W.Add('x_cmp_two')
  assert_equal([], W.Complete('t_cmp', '', 0)->filter((_, n) => n =~# '^x_'))
enddef

def Test_list_opens_a_popup(): void
  W.Reset()
  EditSample()
  W.Add('t_list')
  W.List()
  assert_equal(1, len(popup_list()))
  popup_clear()
enddef

export def RunAll(): void
  Test_add_then_jump_returns_to_the_line()
  Test_jump_opens_the_saved_file()
  Test_add_persists_across_reset()
  Test_complete_filters_by_prefix()
  Test_list_opens_a_popup()
enddef
