vim9script

# Hidden tests for feature 3b with g:waypoint_scope set to project.

import './lib.vim' as H

var dir = tempname()
var base = tempname()
for p in ['projA/.git', 'projB/.git', 'projA/src/deep', 'loose1', 'loose2']
  mkdir($'{base}/{p}', 'p')
endfor
H.Load({waypoint_dir: dir, waypoint_scope: 'project'})

def Completions(lead: string): list<string>
  return getcompletion($'WaypointJump {lead}', 'cmdline')
enddef

def Project_waypoints_stay_in_their_project()
  H.EditSample($'{base}/projA', 'a.txt')
  cursor(5, 1)
  H.Run('WaypointAdd sx')
  var bfile = H.EditSample($'{base}/projB', 'b.txt')
  assert_equal(-1, index(Completions('s'), 'sx'), 'projB completes a projA name')
  H.Run('WaypointJump sx')
  assert_equal(bfile, expand('%:p'), 'jumped out of projB to a projA waypoint')
enddef

def Project_waypoints_work_inside_their_project()
  H.EditSample($'{base}/projA/src/deep', 'n.txt')
  assert_true(index(Completions('s'), 'sx') >= 0, 'nested file misses its project')
  H.Run('WaypointJump sx')
  assert_equal('a.txt', expand('%:t'))
  assert_equal(5, line('.'))
enddef

def Files_without_a_root_share_the_global_store()
  H.EditSample($'{base}/loose1', 'l.txt')
  H.Run('WaypointAdd sg')
  H.EditSample($'{base}/loose2', 'm.txt')
  assert_true(index(Completions('s'), 'sg') >= 0)
  H.EditSample($'{base}/projB', 'b.txt')
  assert_equal(-1, index(Completions('s'), 'sg'), 'a project sees global names')
enddef

H.Finish([
  ['Project_waypoints_stay_in_their_project', Project_waypoints_stay_in_their_project],
  ['Project_waypoints_work_inside_their_project', Project_waypoints_work_inside_their_project],
  ['Files_without_a_root_share_the_global_store', Files_without_a_root_share_the_global_store],
])
