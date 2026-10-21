vim9script

if exists('s:is_loaded') || v:version < 901 || &cp
  finish
endif

var is_loaded: bool = true

##############################################################################
# Plugin_Name: Logger
# Shows and logs the info, warning, error, and exception messages of a
# Vim9 plugin. Each message starts with the plugin, script, and method
# name when known: MyPlugin - foo.vim - Bar: text
#
# Usage in each script:
#   import 'Logger/logger.vim' as Log
#   var log = Log.Logger.new('MyPlugin', expand('<sfile>:t'))
#
#   def Bar()
#     log.Info('Started.')
#     log.Warn('No config found. Using defaults.')
#     log.Error('Cannot write the file.')
#     try
#       Risky()
#     catch
#       log.Exception()
#     endtry
#     log.Try(() => Risky())
#     throw log.Fmt('No match.')
#   enddef
#
# Options are global variables, read on each message. See doc/logger.txt.
# License: GNU GPL 3.0
##############################################################################

import './config.vim' as C
import './logfile.vim' as L
import './messages.vim' as M

# A level no user can set. Marks a Logger made without a level argument.
const LEVEL_UNSET: number = -2
const SEVERITY: dict<number> = {error: 0, exception: 0, warn: 1, info: 2}
const TAG: dict<string> = {
  info: '',
  warn: '[WARN] ',
  error: '[ERROR] ',
  exception: '[EXCEPTION] ',
}
const LABEL: dict<string> = {
  info: 'INFO',
  warn: 'WARN',
  error: 'ERROR',
  exception: 'EXCEPTION',
}

# CLASS: Message output for one script of one plugin.
export class Logger
  var plugin: string
  var script: string = ''
  var level: number = LEVEL_UNSET
  var config: C.Config
  var file: L.LogFile
  var fileFailed: bool = false

  def new(this.plugin = v:none, this.script = v:none, this.level = v:none)
    this.config = C.Config.new(this.plugin)
    this.file = L.LogFile.new(this.config.key)
  enddef

  # METHOD: Return the message prefix. Omit the parts that are empty.
  def Prefix(method: string): string
    var parts: list<string> = [this.plugin, this.script, method]
      ->filter((_, p) => p != '')
    return $"{parts->join(' - ')}: "
  enddef

  # METHOD: Return the name of the function skip frames up the call stack.
  # Return an empty string for script level code, lambdas, and the
  # command line. The default skips this method and the public method
  # that calls it.
  def CallerName(skip: number = 2): string
    var frames: list<string> = expand('<stack>')->split('\.\.')
    var idx: number = len(frames) - 1 - skip
    if idx < 0
      return ''
    endif
    var name: string = frames[idx]
      ->substitute('\[\d\+\]$', '', '')
      ->substitute('^function ', '', '')
      ->substitute('^<SNR>\d\+_', '', '')
      ->substitute('^.*#', '', '')
    return name =~# '^\h[[:alnum:]_.]*$' ? name : ''
  enddef

  # METHOD: Show an info message, as echom does.
  def Info(msg: string, method: string = ''): void
    var m: string = method != '' ? method : this.CallerName()
    this._Emit('info', this.Prefix(m), msg, '', true)
  enddef

  # METHOD: Show a warning message.
  def Warn(msg: string, method: string = ''): void
    var m: string = method != '' ? method : this.CallerName()
    this._Emit('warn', this.Prefix(m), msg, '', true)
  enddef

  # METHOD: Show an error message.
  def Error(msg: string, method: string = ''): void
    var m: string = method != '' ? method : this.CallerName()
    this._Emit('error', this.Prefix(m), msg, '', true)
  enddef

  # METHOD: Show a caught exception. With no arguments, use v:exception
  # and v:throwpoint. Fmt already recorded and logged a formatted text,
  # so only show it.
  def Exception(
      exception: string = v:exception,
      throwpoint: string = v:throwpoint,
      method: string = ''): void
    if stridx(exception, TAG.exception) >= 0
      if this._Shown('exception')
        var lines: list<string> = [exception]
        if throwpoint != ''
          lines->add($'  at {throwpoint}')
        endif
        M.Echo('exception', lines)
      endif
      return
    endif
    var m: string = method != '' ? method : this.CallerName()
    this._Emit('exception', this.Prefix(m), exception, throwpoint, true)
  enddef

  # METHOD: Return a formatted exception text to throw. Record and log it
  # now, because Vim shows an uncaught exception without Logger.
  def Fmt(msg: string, method: string = ''): string
    var m: string = method != '' ? method : this.CallerName()
    var prefix: string = this.Prefix(m)
    this._Emit('exception', prefix, msg, '', false)
    return $'{prefix}{TAG.exception}{msg}'
  enddef

  # METHOD: Call Fn and return its result. On an exception, show it and
  # return v:none.
  def Try(Fn: func(): any, method: string = ''): any
    var m: string = method != '' ? method : this.CallerName()
    try
      return Fn()
    catch
      this.Exception(v:exception, v:throwpoint, m)
      return v:none
    endtry
  enddef

  # METHOD: Return the echo level. A plugin option overrides the level
  # argument of new, which overrides the global option.
  def _EchoLevel(): number
    if !this.config.HasOwn('level') && this.level != LEVEL_UNSET
      return this.level
    endif
    return this.config.GetNumber('level', 2)
  enddef

  def _Shown(kind: string): bool
    return this.config.GetBool('echo', true)
      && SEVERITY[kind] <= this._EchoLevel()
  enddef

  def _Logged(kind: string): bool
    return this.config.GetBool('log_file', false)
      && SEVERITY[kind] <= this.config.GetNumber('log_level', 2)
  enddef

  # METHOD: Record, echo, and log one message, as the options allow. With
  # echo false, record and log only.
  def _Emit(
      kind: string,
      prefix: string,
      msg: string,
      throwpoint: string,
      echo: bool): void
    var shown: bool = this._Shown(kind)
    var logged: bool = this._Logged(kind)
    if !shown && !logged
      return
    endif
    var lines: list<string> = [$'{prefix}{TAG[kind]}{msg}']
    if throwpoint != ''
      lines->add($'  at {throwpoint}')
    endif
    M.Record(kind, lines)
    if shown && echo
      M.Echo(kind, lines)
    endif
    if logged
      this._WriteFile(kind, prefix, msg, throwpoint)
    endif
  enddef

  # METHOD: Append one message to the log file. After one failure, stop
  # for this session, so that each message does not repeat the warning.
  def _WriteFile(
      kind: string,
      prefix: string,
      msg: string,
      throwpoint: string): void
    if this.fileFailed
      return
    endif
    var stamp: string = strftime('%Y-%m-%d %H:%M:%S')
    var lines: list<string> = [$'{stamp} {LABEL[kind]} {prefix}{msg}']
    if throwpoint != ''
      lines->add($'  at {throwpoint}')
    endif
    try
      this.file.Write(
        lines,
        this.config.GetString('log_dir', '~/.Logger', false),
        this.config.GetNumber('log_retention', 10))
    catch
      this.fileFailed = true
      var warning: list<string> = [
        $'Logger: cannot write the log file of {this.plugin}: {v:exception}'
      ]
      M.Record('warn', warning)
      M.Echo('warn', warning)
    endtry
  enddef
endclass
