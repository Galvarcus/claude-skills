vim9script

# Hidden test for feature 3b: global stays the default scope.

import './lib.vim' as H

var dir = tempname()
var base = tempname()
mkdir($'{base}/projA/.git', 'p')
mkdir($'{base}/projB/.git', 'p')
H.Load({waypoint_dir: dir})

def Global_is_the_default_scope()
  H.EditSample($'{base}/projA', 'a.txt')
  H.Run('WaypointAdd gx')
  H.EditSample($'{base}/projB', 'b.txt')
  assert_true(index(getcompletion('WaypointJump g', 'cmdline'), 'gx') >= 0)
enddef

H.Finish([['Global_is_the_default_scope', Global_is_the_default_scope]])
