vim9script

# Hidden test for bug B1: the store folder setting starts with a tilde.

import './lib.vim' as H

var home = tempname()
var work = tempname()
mkdir(home, 'p')
mkdir(work, 'p')
$HOME = home
execute $'cd {fnameescape(work)}'
H.Load({waypoint_dir: '~/wpstore'})

def B1_store_path_expands_home()
  H.EditSample($'{work}/src')
  H.Run('WaypointAdd b1')
  assert_true(filereadable($'{home}/wpstore/waypoints.json'), 'no store file under HOME')
  assert_false(isdirectory($'{work}/~'), 'a literal ~ folder was created')
enddef

H.Finish([['B1_store_path_expands_home', B1_store_path_expands_home]])
