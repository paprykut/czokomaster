"""
This plugin upgrades the python packages installed through pip/easy_install.
"""

__pluginname__ = "pippy"
__author__ = "Mikolaj Romel"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Mikolaj Romel"
__license__ = "New-style BSD"

import os
import sys

from termcolor import colored
from czokomaster.meta import __projectname__
from czokomaster.czokomanager import (get_config_option, 
                                      normalize_params,
                                      execute_command)

def version(params):
    """
    Print plugin version.
    """

    print "%s plugin version %s %s\n" % (__pluginname__, __version__,
                                         __copyright__)

def help(params):
    """
    Print plugin help.
    """

    version(params)
    print "This plugin upgrades the python packages installed through", \
          "pip/easy_install.", \
          "Usage:\n\n    # %s %s upgrade [all|base|jail1|jail2|...]\n" % \
          (__projectname__, __pluginname__), \
          "or, to see what is to be upgraded:\n\n   ", \
          "# %s %s diff [all|base|jail1|jail2|...]\n" % \
          (__projectname__, __pluginname__)

    sys.exit(1)

def upgrade(params):
    """
    Upgrade the base system and some of the jails. Get the list of systems to 
    upgrade from the command line. Usage:
    
        # czokomaster pippy upgrade base jail1 jail2
      
    This would upgrade the base system only:
    
        # czokomaster pippy upgrade base
          
    This would upgrade all jails. Caution! Jails' names must be put into
    the config file:
    
        # czokomaster pippy upgrade all
    """

    # Get the list of jails that need to be upgraded.
    jails = normalize_params(__pluginname__, "jails", params)

    # If the base system's python packages are to be upgraded as well, do it 
    # now. In order to upgrade the base system's python packages, add "base" to 
    # the "jails" option within the config file.
    if "base" in jails:
        _print_upgrade_messages("the base system")
        _upgrade("base")

        # Drop "base" from the list, so it does not interfere with the loop 
        # below. Print a new line as well.
        jails.remove("base")
        print ""

    # Upgrade specified jails.
    for jail in jails:
        _print_upgrade_messages(jail)
        _upgrade(jail)
        print ""

def diff(params):
    """
    Show the ports that need to be updated.
    """

    # Get the path to the cache files which contain the information on what
    # is to be upgraded. Also, get the jajil names (which are at the same time
    # the file names in the cache directory).
    jails = normalize_params(__pluginname__, "jails", params)
    pippy_cachedir = get_config_option(__pluginname__, "pippy_cachedir")

    if "base" in jails:
        # Print the packages that need to be updated.
        _print_updates(pippy_cachedir + os.sep + "base", "the base system")

        # Remove "base", so it does not interfere with the loop below.
        jails.remove("base")

    for jail in jails:
        _print_updates(pippy_cachedir + os.sep + jail, jail)


def _get_updates(filename):
    """
    Get the list of the udpates.
    """

    f = open(filename, "r")
    updates = f.readlines()
    f.close()

    return updates

def _print_updates(filename, system_name):
    """
    Check whether there are any updates and return them if so. Also, print some
    info.
    """

    print colored("[Python]", "yellow", attrs=["bold"]), \
          "Available updates for", colored(system_name, "cyan") + ":"

    # Get the list of the udpates.
    updates = _get_updates(filename)

    # If not empty, show packages that need updating. Else, print "None".
    if updates:
        for update in updates:
            print colored("->", "red"), update.replace("\n", "")
        # Print a new line.
        print ""

    else:
        print colored("->", "green"), colored("None\n", attrs=["bold"])

def _print_upgrade_messages(system_name):
    """
    Print information concerning the upgrade process.
    """

    print colored("==>", "green"), \
          colored("[Python]", "red", attrs=["bold"]), \
          colored("Upgrading py-packages in", attrs=["bold"]), \
          colored(system_name, "cyan") + colored(":", attrs=["bold"])

def _upgrade(system_name):
    """
    Do the actual upgrade.
    """

    # Get the path to the cache files which contain the information on what
    # is to be upgraded. Also, get the command by which the system is to be
    # upgraded.
    pippy_cachedir = get_config_option(__pluginname__, "pippy_cachedir")
    py_upgrade_cmd = get_config_option(__pluginname__, "py_upgrade_cmd")

    # Get the list of packages that need to be upgraded.
    updates = _get_updates(pippy_cachedir + os.sep + system_name)
 
    # Do the actual upgrade.
    if updates:
        if system_name == "base":
            for update in updates:
                HERE
                execute_command(["%s %s" % (py_upgrade_cmd, update.split()[0])])
        else:
            # It means we operate on jails now.
            for update in updates:
                execute_command(["jexec %s %s %s" % \
                                (system_name, py_upgrade_cmd, \
                                 update.split()[0])])

        # Do postupgrade update if specified in the config.
        _postupgrade_update(system_name)
    else:
        print colored("->", "green"), \
              colored("Nothing to upgrade.", attrs=["bold"])

def _postupgrade_update(system_name):
    """
    If update_after_upgrade is set to "yes", update the py packages list
    that need upgrading after the upgrade is complete.
    """

    config = get_config_option(__pluginname__, "update_after_upgrade")

    if config.lower() == "yes":
        from czokomaster.plugins.plugin_helpers.pippy_cron_helper import \
             PythonUpdateChecker

        print colored("->", "blue"), \
              colored("Updating the cache file...", attrs=["bold"])

        update = PythonUpdateChecker()
        update.get_updates([system_name])
        print colored("->", "green"), colored("Done.", attrs=["bold"])
        print ""