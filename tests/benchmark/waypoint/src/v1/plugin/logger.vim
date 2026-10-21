vim9script

if exists('s:is_loaded') || v:version < 901 || &cp
  finish
endif

var is_loaded: bool = true

##############################################################################
# Plugin_Name: Logger
# Sets the global option defaults and defines :LoggerMessages. A plugin
# option such as g:logger_foo_echo overrides each global option.
# License: GNU GPL 3.0
##############################################################################

import 'Logger/messages.vim' as M

g:logger_echo = get(g:, 'logger_echo', true)
g:logger_level = get(g:, 'logger_level', 2)
g:logger_log_file = get(g:, 'logger_log_file', false)
g:logger_log_level = get(g:, 'logger_log_level', 2)
g:logger_log_retention = get(g:, 'logger_log_retention', 10)
g:logger_log_dir = get(g:, 'logger_log_dir', '~/.Logger')

command -bar LoggerMessages M.Show()
