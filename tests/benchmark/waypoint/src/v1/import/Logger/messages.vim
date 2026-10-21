vim9script

if exists('s:is_loaded') || v:version < 901 || &cp
  finish
endif

var is_loaded: bool = true

##############################################################################
# Plugin_Name: Logger
# Keeps the shared message history for all Logger instances, echoes
# messages with highlight, and holds messages sent before VimEnter until
# Vim has started, because startup redraws hide them.
# License: GNU GPL 3.0
##############################################################################

var history: list<dict<any>> = []
var pending: list<dict<any>> = []

const HISTORY_MAX: number = 200
const HIGHLIGHT: dict<string> = {
  info: 'None',
  warn: 'WarningMsg',
  error: 'ErrorMsg',
  exception: 'ErrorMsg',
}

# FUNCTION: Add one message to the history. Drop the oldest entry when the
# history is full.
export def Record(kind: string, lines: list<string>): void
  history->add({time: strftime('%H:%M:%S'), kind: kind, lines: lines})
  if len(history) > HISTORY_MAX
    history->remove(0)
  endif
enddef

# FUNCTION: Echo one message. Before VimEnter, queue it for Flush.
export def Echo(kind: string, lines: list<string>): void
  if !v:vim_did_enter
    pending->add({kind: kind, lines: lines})
    return
  endif
  EchoNow(kind, lines)
enddef

# FUNCTION: Echo all queued messages in the order they were sent.
export def Flush(): void
  for p in pending
    EchoNow(p.kind, p.lines)
  endfor
  pending = []
enddef

# FUNCTION: Return a copy of the history, oldest first.
export def History(): list<dict<any>>
  return deepcopy(history)
enddef

# FUNCTION: Return a copy of the messages that wait for VimEnter.
export def Pending(): list<dict<any>>
  return deepcopy(pending)
enddef

# FUNCTION: Empty the history and the queue.
export def Clear(): void
  history = []
  pending = []
enddef

# FUNCTION: Show the history in a scratch window.
export def Show(): void
  if empty(history)
    echom 'Logger: no messages recorded.'
    return
  endif
  var lines: list<string> = []
  for h in history
    lines->add($'[{h.time}] {h.lines[0]}')
    lines->extend(h.lines[1 : ]->mapnew((_, l) => $'           {l}'))
  endfor
  new
  setlocal buftype=nofile bufhidden=wipe noswapfile nobuflisted
  setlocal filetype=log
  setline(1, lines)
  setlocal nomodifiable
enddef

def EchoNow(kind: string, lines: list<string>): void
  execute $'echohl {HIGHLIGHT[kind]}'
  for l in lines
    echom l
  endfor
  echohl None
enddef

augroup LoggerFlushPending
  autocmd!
  autocmd VimEnter * Flush()
augroup END
