vim9script

# Plugin_Name: waypoint benchmark
# Shared helpers for the hidden tests. They drive Waypoint only through
# its commands, its store file, the cursor, and completion, so they work
# whatever names an agent chose inside the plugin.
# License: GNU GPL 3.0

# FUNCTION: Load the plugin under test with settings, a dict of g: values.
export def Load(settings: dict<any>)
  g:logger_echo = false
  for [k, v] in items(settings)
    g:[k] = v
  endfor
  runtime plugin/logger.vim
  runtime plugin/waypoint.vim
enddef

# FUNCTION: Write a file of numbered lines in dir and edit it.
export def EditSample(dir: string, name: string = 'sample.txt', count: number = 20): string
  mkdir(dir, 'p')
  var path = $'{dir}/{name}'
  writefile(range(1, count)->mapnew((_, n) => $'line {n}'), path)
  execute $'silent edit! {fnameescape(path)}'
  return fnamemodify(path, ':p')
enddef

# FUNCTION: Return the records of every store file under dir.
export def Records(dir: string): list<dict<any>>
  var out: list<dict<any>> = []
  for f in globpath(expand(dir), '**/*.json', true, true)
    if getfsize(f) > 0
      out += json_decode(readfile(f)->join("\n"))
    endif
  endfor
  return out
enddef

# FUNCTION: Return the sorted names in every store file under dir.
export def Names(dir: string): list<string>
  return Records(dir)->mapnew((_, r) => r.name)->sort()
enddef

# FUNCTION: Return the saved line of the record named name, or -1.
export def LineOf(dir: string, name: string): number
  var hits = Records(dir)->filter((_, r) => r.name ==# name)
  return empty(hits) ? -1 : hits[0].line
enddef

# FUNCTION: Run cmd and record any exception as a failure.
export def Run(cmd: string)
  try
    execute cmd
  catch
    add(v:errors, $'{cmd} threw {v:exception}')
  endtry
enddef

# FUNCTION: Run each test, a pair of name and function, then write one
# PASS or FAIL line per test to the file in WP_RESULTS, and quit.
export def Finish(tests: list<list<any>>)
  var lines: list<string> = []
  for [name, Test] in tests
    var before = len(v:errors)
    try
      Test()
    catch
      add(v:errors, $'{name} threw {v:exception} at {v:throwpoint}')
    endtry
    var errs = v:errors[before :]
    lines->add(empty(errs) ? $'PASS {name}' : $'FAIL {name}: {errs->join(" | ")}')
  endfor
  writefile(lines, $WP_RESULTS)
  qall!
enddef
