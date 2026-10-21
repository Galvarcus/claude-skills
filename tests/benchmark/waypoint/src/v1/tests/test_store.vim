vim9script

# Plugin_Name: waypoint
# Tests the Store class: reading, writing, and editing the store file.
# License: GNU GPL 3.0

import autoload 'waypoint/entry.vim' as E
import autoload 'waypoint/store.vim' as S

# FUNCTION: Return a Waypoint with fixed values for name.
def Point(name: string, line: number = 3): E.Waypoint
  return E.Waypoint.new(name, '/tmp/waypoint_test.txt', line, 2, '2026-10-01T09:00:00')
enddef

def Test_missing_file_is_an_empty_store(): void
  var s = S.Store.new(tempname())
  s.Load()
  assert_equal([], s.items)
enddef

def Test_empty_file_is_an_empty_store(): void
  var s = S.Store.new(tempname())
  mkdir(expand(s.dir), 'p')
  writefile([], s.Path())
  s.Load()
  assert_equal([], s.items)
enddef

def Test_save_then_load_keeps_every_field(): void
  var dir = tempname()
  var s = S.Store.new(dir)
  s.Put(Point('alpha', 7))
  s.Save()
  var t = S.Store.new(dir)
  t.Load()
  assert_equal([Point('alpha', 7).ToDict()], t.items->mapnew((_, w) => w.ToDict()))
enddef

def Test_put_replaces_the_same_name(): void
  var s = S.Store.new(tempname())
  s.Put(Point('alpha', 1))
  s.Put(Point('alpha', 9))
  assert_equal(1, len(s.items))
  assert_equal(9, s.Find('alpha').line)
enddef

def Test_find_unknown_name_is_null(): void
  var s = S.Store.new(tempname())
  assert_true(s.Find('nope') == null_object)
enddef

def Test_names_are_sorted(): void
  var s = S.Store.new(tempname())
  s.Put(Point('gamma'))
  s.Put(Point('alpha'))
  s.Put(Point('beta'))
  assert_equal(['alpha', 'beta', 'gamma'], s.Names())
enddef

def Test_delete_unknown_name_returns_false(): void
  var s = S.Store.new(tempname())
  assert_false(s.Delete('nope'))
enddef

export def RunAll(): void
  Test_missing_file_is_an_empty_store()
  Test_empty_file_is_an_empty_store()
  Test_save_then_load_keeps_every_field()
  Test_put_replaces_the_same_name()
  Test_find_unknown_name_is_null()
  Test_names_are_sorted()
  Test_delete_unknown_name_returns_false()
enddef
