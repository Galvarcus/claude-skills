vim9script

# Hidden tests for bugs B2 and B3.

import './lib.vim' as H

var dir = tempname()
var work = tempname()
H.Load({waypoint_dir: dir})

def B2_jump_lands_on_the_saved_line()
  H.EditSample($'{work}/b2')
  cursor(7, 3)
  H.Run('WaypointAdd b2')
  cursor(1, 1)
  H.Run('WaypointJump b2')
  assert_equal([7, 3], [line('.'), col('.')])
  assert_equal(7, H.LineOf(dir, 'b2'))
enddef

def B3_delete_removes_the_named_waypoint()
  H.EditSample($'{work}/b3')
  for n in ['b3_beta', 'b3_gamma', 'b3_alpha']
    H.Run($'WaypointAdd {n}')
  endfor
  H.Run('WaypointDelete b3_beta')
  assert_equal(['b3_alpha', 'b3_gamma'], H.Names(dir)->filter((_, n) => n =~# '^b3_'))
enddef

H.Finish([
  ['B2_jump_lands_on_the_saved_line', B2_jump_lands_on_the_saved_line],
  ['B3_delete_removes_the_named_waypoint', B3_delete_removes_the_named_waypoint],
])
