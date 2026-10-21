vim9script

if exists('s:is_loaded') || v:version < 901 || &cp
  finish
endif

var is_loaded: bool = true

##############################################################################
# Plugin_Name: Logger
# Writes the messages of one plugin to one file for each Vim session, such
# as foo_20260926_140311.log. On the first write of a session, deletes the
# oldest files of that plugin so that only the given number of old files
# remain.
# License: GNU GPL 3.0
##############################################################################

# All plugins share one timestamp, so the files of one session sort together.
var session: string = strftime('%Y%m%d_%H%M%S')

# CLASS: Session log file for one plugin.
export class LogFile
  var key: string
  var folder: string = ''
  var path: string = ''

  def new(this.key)
  enddef

  # METHOD: Append lines to the session file in dir. Create dir when it
  # does not exist. Start the file on the first write, and again when dir
  # changes. Throws when Vim cannot write the file.
  def Write(lines: list<string>, dir: string, retention: number): void
    var expanded: string = expand(dir)
    if !isdirectory(expanded)
      mkdir(expanded, 'p')
    endif
    # Only an existing folder gets a trailing separator from :p.
    var target: string = fnamemodify(expanded, ':p')
    if target !=# this.folder
      this.folder = target
      this.path = $'{target}{this.key}_{session}.log'
      writefile([], this.path, 'a')
      this.Prune(retention)
    endif
    writefile(lines, this.path, 'a')
  enddef

  # METHOD: Delete the oldest files of this plugin until retention old
  # files remain. The current file does not count. Zero or less keeps all.
  def Prune(retention: number): void
    if retention <= 0
      return
    endif
    var current: string = fnamemodify(this.path, ':t')
    # The exact pattern keeps foo from matching the files of foo_bar.
    var pattern: string = printf('^%s_\d\{8}_\d\{6}\.log$', this.key)
    var old: list<string> = readdir(this.folder,
      (n) => n =~# pattern && n !=# current)->sort()
    for f in old[: -retention - 1]
      delete($'{this.folder}{f}')
    endfor
  enddef
endclass
