"""
This is the main manager for czokomaster. The functions
available here might be used within the plugins as well as they
are used within the main app.

handle_event is called from the main script. The main script supplies
the list of parameters supplied by the user through calling 
czokomaster.czokomanager.handle_event(sys.argv). Thus, the arguments normally
accessed via sys.argv[x] are now accessible under handle_event() function via
params[x].
"""

import os
import shlex
import configobj
import subprocess

from meta import (__projectname__, 
                  __version__,
                  __copyright__,
                  CZOKOMASTER_CONFIG_PATH)

def handle_event(params):
    """
    Handle events trigerred by the user on the command line.
    """

    ## First, get the list of registered plugins.
    plugins = _register_plugins()

    ## If the first argument supplied is 'help' or the argument does
    ## not exist in the plugins list (registered plugins are within
    ## this list) - print help to stdout. Also, print help if no argument
    ## is supplied at al_l.
    try:
        if params[1] == "version":
            _version()
        elif params[1] == "plugins":
            _list_plugins()
        elif params[1] == "help" or params[1] not in plugins:
            _help()
        ## If the parameter is not "help", "plugins" or empty and it is
        ## in the plugins list, invoke the _trigger_plugin(params) function.
        else:
            _trigger_plugin(params)
    except IndexError:
        _help()

def get_config_option(section, option):
    """
    Load the configuration file and get the particular value out of it.
    - First, supply the section within the config file - e.g. 
      get_config_option("foo", ...) to retrieve the section
      named [foo] within the configuration file.
    - Second, supply the option to be retrieved - e.g.
      get_config_option("foo", "bar") to get the value of "bar"
      variable within the "foo" section.

    configobj is used here instead of ConfigParser as the former one does not
    properly recognise comma-separated values within a variable.
    """

    config = configobj.ConfigObj(CZOKOMASTER_CONFIG_PATH)
    return config[section][option]

def normalize_params(config_section, config_option, params):
    """
    Normalize the parameters supplied on the command line. Return the list 
    of base or/and jails that are to be upgraded.

    Parameters:
    - section - which section of the config file should be read;
    - config_option - which variable from the given section from the config file
                      should be read;
    - params - the rest of the parameters (same as sys.argv).
    """

    # Apply to base/jails specified in the config file if "<plugin> all"
    # is invoked.
    if "all" in params:
        # Get the option from the config file which specifies which particular
        # jails are to be upgraded if the "upgrade all" command is invoked. 
        # It also checks whether the base system should be upgraded by the 
        # abovementioned command.
        jails = get_config_option(config_section, config_option)

    # If "all" is not supplied, respective jails should be upgraded. Get them
    # from the command line.
    else:
        # Upgrade only the jails specified on the command line. They should
        # start from the 4th argument of params (params[3:]).
        jails = params[3:]

        # If "jails" variable is empty, no argument was supplied on the 
        # command line, print help in such a case.
        if jails == []:
            _help()

    return jails

def execute_command(commands=[], func_return=False):
    """
    Helper responsible for executing commands. Iterate through the list
    of commands and execute each of them.
    
    IMPORTANT: The command must be supplied as a list. Thus, the following:
    
        execute_command("ls -l") 
    
    will not work. The example below, however, will:
    
        execute_command(["ls -l"])

    Supply the 'func_return' argument in order to decide whether the function
    should print the output of the process it starts (func_return=False) or
    whether the value should be returned to the function that invokes 
    execute_command (func_return=True).
    """

    if func_return:
        for command in commands:
           output = subprocess.Popen(shlex.split(command), \
                    stdout=subprocess.PIPE)
           stdout, stderr = output.communicate()
           return stdout, stderr
    else:
        for command in commands:
            output = subprocess.Popen(shlex.split(command))
            output.communicate()

def _register_plugins():
    """
    Register the plugins by iterating over the plugins dir.
    Also, the name of the plugin should be the first argument supplied
    by the user for czokomaster. E.g. czokomaster testplugin help shall
    show help for the testplugin plugin.
    """

    ## Initialize plugins variable to which the available plugins
    ## will be appended.
    plugins = []

    ## Iterate over plugins, leave out __init__.py and *pyc files. Also,
    ## cut off the .py extensions. 
    for plugin in os.listdir(os.path.join(\
                  os.path.dirname(os.path.abspath(__file__)), 'plugins')):
        if plugin != "__init__.py" and plugin.endswith('.py'):
            plugins.append(plugin[:-3])

    return plugins

def _version():
    """
    Print simple czokomaster info - name, version, copyright.
    """

    print "%s version %s %s\n" % (__projectname__, __version__, __copyright__)

def _help():
    """
    Print help for czokomaster.
    """

    _version()
    print "Usage: %s <plugin> <option>\n" \
          "For the list of available plugins type: %s plugins" \
          % (__projectname__, __projectname__)

def _list_plugins():
    """
    List the available plugins for czokomaster.
    """

    _version()
    print "Plugins available for %s:" % __projectname__

    ## Get the list of available plugins, iterate and print
    ## in stdout.
    plugins = _register_plugins()

    for plugin in plugins:
        print "    - %s" % plugin

def _trigger_plugin(params):
    """
    After event is handled by the handle_event() function, trigger
    the plugin.
    """

    try:
        ## Import the plugin supplied on the command line.
        plugin = __import__("czokomaster.plugins.%s" % params[1], globals(),
                            locals(), ["%s" % params[2]], -1)

        ## Invoke a method (also supplied on the command line) on the
        ## plugin. Invoking itself is done by "(params)" at the end.
        getattr(plugin, params[2])(params)

    ## If params[2] is not supplied on the command line, the method of 
    ## the plugin cannot be invoked. Thus, print help of the plugin. 
    ## Help is accessed through plugin.help(). In order to do this, the
    ## module must be imported and "help" must be supplied as an 
    ## argument.
    except (IndexError, AttributeError):
        plugin = __import__("czokomaster.plugins.%s" % params[1], globals(),
                            locals(), ["help"], -1)

        getattr(plugin, "help")(params)