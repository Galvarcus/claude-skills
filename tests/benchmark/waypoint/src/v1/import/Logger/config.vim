vim9script

if exists('s:is_loaded') || v:version < 901 || &cp
  finish
endif

var is_loaded: bool = true

##############################################################################
# Plugin_Name: Logger
# Reads Logger options for one plugin. A plugin option such as
# g:logger_foo_log_retention overrides the global g:logger_log_retention,
# which overrides the default the caller gives. Values are read on each
# call, so a change applies without a restart.
# License: GNU GPL 3.0
##############################################################################

# CLASS: Option lookup for one plugin.
export class Config
  var key: string

  # METHOD: Make the plugin name safe for a variable or file name. Foo
  # becomes foo and My-Plugin becomes my_plugin.
  def new(plugin: string)
    this.key = plugin->tolower()->substitute('[^a-z0-9_]', '_', 'g')
  enddef

  # METHOD: Return the plugin variable name for an option.
  def Name(option: string): string
    return $'logger_{this.key}_{option}'
  enddef

  # METHOD: Return true when the plugin variable for an option exists.
  def HasOwn(option: string): bool
    return has_key(g:, this.Name(option))
  enddef

  # METHOD: Return the plugin value, else the global value, else default.
  # With perPlugin false, skip the plugin value.
  def Get(option: string, default: any, perPlugin: bool = true): any
    if perPlugin && this.HasOwn(option)
      return get(g:, this.Name(option))
    endif
    return get(g:, $'logger_{option}', default)
  enddef

  # METHOD: Return a number option. Accept a bool as 0 or 1. Return
  # default for any other type.
  def GetNumber(option: string, default: number): number
    var value: any = this.Get(option, default)
    if type(value) == v:t_number
      return value
    elseif type(value) == v:t_bool
      return value ? 1 : 0
    endif
    return default
  enddef

  # METHOD: Return a bool option. Accept a number, nonzero is true.
  # Return default for any other type.
  def GetBool(option: string, default: bool): bool
    var value: any = this.Get(option, default)
    if type(value) == v:t_bool
      return value
    elseif type(value) == v:t_number
      return value != 0
    endif
    return default
  enddef

  # METHOD: Return a string option. Return default for any other type.
  def GetString(option: string, default: string, perPlugin: bool = true): string
    var value: any = this.Get(option, default, perPlugin)
    return type(value) == v:t_string ? value : default
  enddef
endclass
