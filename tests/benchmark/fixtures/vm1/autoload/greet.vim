" greet.vim - say hello
let s:greeting = 'Hello'

function! greet#Say(name) abort
  let l:msg = s:greeting . ', ' . a:name . '!'
  if len(a:name) > 20
    let l:msg = s:greeting . ', friend!'
  endif
  echomsg l:msg
  return l:msg
endfunction
