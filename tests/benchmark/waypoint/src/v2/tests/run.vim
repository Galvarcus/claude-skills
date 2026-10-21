vim9script

# Plugin_Name: waypoint
# Runs every test suite and writes the result to tests/results.txt.
# Run from the plugin root:
#   vim -Nu NONE -i NONE -es -c 'set rtp^=.' -c 'source tests/run.vim'
# License: GNU GPL 3.0

const RESULTS: string = 'tests/results.txt'

g:waypoint_dir = tempname()
g:logger_echo = false
runtime plugin/logger.vim
runtime plugin/waypoint.vim

import './test_store.vim' as TS
import './test_commands.vim' as TC
import './test_rename.vim' as TR
import './test_scope.vim' as TSC
import './test_track.vim' as TT

var suites: list<func(): void> = [
  TS.RunAll, TC.RunAll, TR.RunAll, TSC.RunAll, TT.RunAll,
]
for RunSuite in suites
  try
    RunSuite()
  catch
    add(v:errors, $'{v:throwpoint}: {v:exception}')
  endtry
endfor

if len(v:errors) > 0
  writefile(v:errors + [$'{len(v:errors)} assertion(s) failed'], RESULTS)
  cquit 1
else
  writefile(['All tests passed'], RESULTS)
  qall!
endif
