vim9script

# Plugin_Name: waypoint
# Regression tests for the three bugs in BUGS.md.
# License: GNU GPL 3.0

import autoload 'waypoint/entry.vim' as E
import autoload 'waypoint/store.vim' as S

def Test_store_path_expands_a_tilde(): void
  var s = S.Store.new('~/wp_test')
  assert_equal($'{expand("~")}/wp_test/waypoints.json', s.Path())
enddef

def Test_here_saves_the_cursor_line(): void
  enew!
  setline(1, ['a', 'b', 'c', 'd'])
  cursor(3, 2)
  assert_equal(3, E.Waypoint.Here('x').line)
  bwipeout!
enddef

def Test_delete_removes_the_named_waypoint(): void
  var s = S.Store.new(tempname())
  for n in ['beta', 'gamma', 'alpha']
    s.Put(E.Waypoint.new(n, '/tmp/f', 1, 1, ''))
  endfor
  s.Delete('beta')
  assert_equal(['alpha', 'gamma'], s.Names())
enddef

export def RunAll(): void
  Test_store_path_expands_a_tilde()
  Test_here_saves_the_cursor_line()
  Test_delete_removes_the_named_waypoint()
enddef
