vim9script

# Plugin_Name: waypoint
# Tests the project root search of scope.vim.
# License: GNU GPL 3.0

import autoload 'waypoint/scope.vim' as SC

def Test_root_is_the_folder_that_holds_the_marker(): void
  var root = tempname()
  mkdir($'{root}/.git', 'p')
  mkdir($'{root}/src/deep', 'p')
  assert_equal(fnamemodify(root, ':p:h'), SC.Root($'{root}/src/deep/file.vim'))
enddef

def Test_root_is_empty_without_a_marker(): void
  var dir = tempname()
  mkdir(dir, 'p')
  assert_equal('', SC.Root($'{dir}/file.vim'))
enddef

def Test_global_scope_uses_the_global_folder(): void
  assert_equal(g:waypoint_dir, SC.StoreDir('/tmp/any/file.vim'))
enddef

export def RunAll(): void
  Test_root_is_the_folder_that_holds_the_marker()
  Test_root_is_empty_without_a_marker()
  Test_global_scope_uses_the_global_folder()
enddef
