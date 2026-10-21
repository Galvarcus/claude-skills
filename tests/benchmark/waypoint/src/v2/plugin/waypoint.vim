vim9script

if exists('s:is_loaded') || v:version < 902 || &cp
  finish
endif

var is_loaded: bool = true

# Plugin_Name: waypoint
# Defines the Waypoint settings, commands, mappings, and autocommands.
# License: GNU GPL 3.0

import autoload 'waypoint.vim' as W
import 'waypoint/variables/constants.vim' as CO

g:waypoint_dir = get(g:, 'waypoint_dir', '~/.vim/waypoint')
g:waypoint_popup_width = get(g:, 'waypoint_popup_width', 60)
g:waypoint_no_mappings = get(g:, 'waypoint_no_mappings', false)
g:waypoint_scope = get(g:, 'waypoint_scope', CO.SCOPE_GLOBAL)
g:waypoint_root_markers = get(g:, 'waypoint_root_markers', ['.git'])

command -nargs=1 WaypointAdd W.Add(<q-args>)
command -nargs=1 -complete=customlist,W.Complete WaypointJump W.Jump(<q-args>)
command -nargs=0 WaypointList W.List()
command -nargs=1 -complete=customlist,W.Complete WaypointDelete W.Delete(<q-args>)
command -nargs=+ -complete=customlist,W.Complete WaypointRename W.Rename([<f-args>])

nnoremap <Plug>(WaypointAdd) <ScriptCmd>W.AddPrompt()<CR>
nnoremap <Plug>(WaypointList) <ScriptCmd>W.List()<CR>

if !g:waypoint_no_mappings
  if !hasmapto('<Plug>(WaypointAdd)', 'n')
    nmap <Leader>wa <Plug>(WaypointAdd)
  endif
  if !hasmapto('<Plug>(WaypointList)', 'n')
    nmap <Leader>wl <Plug>(WaypointList)
  endif
endif

execute $'augroup {CO.AUGROUP}'
  autocmd!
  autocmd BufReadPost * W.OnRead()
  autocmd BufWritePost * W.OnWrite()
augroup END
