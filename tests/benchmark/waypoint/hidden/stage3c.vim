vim9script

# Hidden tests for feature 3c, line tracking.

import './lib.vim' as H

var dir = tempname()
var work = tempname()
H.Load({waypoint_dir: dir})

def Jump_follows_lines_inserted_above()
  H.EditSample($'{work}/a', 'a.txt')
  cursor(10, 1)
  H.Run('WaypointAdd k_ins')
  append(0, ['new 1', 'new 2', 'new 3'])
  cursor(1, 1)
  H.Run('WaypointJump k_ins')
  assert_equal(13, line('.'))
enddef

def Write_saves_lines_inserted_above()
  H.EditSample($'{work}/b', 'b.txt')
  cursor(10, 1)
  H.Run('WaypointAdd k_wins')
  append(0, ['new 1', 'new 2', 'new 3'])
  silent write
  assert_equal(13, H.LineOf(dir, 'k_wins'))
enddef

def Write_saves_lines_deleted_above()
  H.EditSample($'{work}/c', 'c.txt')
  cursor(10, 1)
  H.Run('WaypointAdd k_del')
  silent :1,2delete
  silent write
  assert_equal(8, H.LineOf(dir, 'k_del'))
enddef

def Edits_below_do_not_move_it()
  H.EditSample($'{work}/d', 'd.txt')
  cursor(5, 1)
  H.Run('WaypointAdd k_below')
  append(15, ['x', 'y'])
  silent write
  assert_equal(5, H.LineOf(dir, 'k_below'))
enddef

def Unloaded_buffers_keep_their_lines()
  H.EditSample($'{work}/e', 'e.txt')
  cursor(5, 1)
  H.Run('WaypointAdd k_unl')
  silent bwipeout!
  H.EditSample($'{work}/f', 'f.txt')
  append(0, ['x'])
  silent write
  assert_equal(5, H.LineOf(dir, 'k_unl'))
enddef

def A_reopened_buffer_tracks_again()
  execute $'silent edit! {fnameescape(work)}/e/e.txt'
  append(0, ['x', 'y'])
  silent write
  assert_equal(7, H.LineOf(dir, 'k_unl'))
enddef

H.Finish([
  ['Jump_follows_lines_inserted_above', Jump_follows_lines_inserted_above],
  ['Write_saves_lines_inserted_above', Write_saves_lines_inserted_above],
  ['Write_saves_lines_deleted_above', Write_saves_lines_deleted_above],
  ['Edits_below_do_not_move_it', Edits_below_do_not_move_it],
  ['Unloaded_buffers_keep_their_lines', Unloaded_buffers_keep_their_lines],
  ['A_reopened_buffer_tracks_again', A_reopened_buffer_tracks_again],
])
