"""
This plugin is responsible for managing ports for a FreeBSD jailed system.
"""

__pluginname__ = "ports"
__author__ = "Mikolaj Romel"
__version__ = "1.1"
__copyright__ = "Copyright (c) 2012 Mikolaj Romel"
__license__ = "New-style BSD"

import os
import sys

from termcolor import colored

from czokomaster.meta import __projectname__
from czokomaster.czokomanager import (get_config_option, execute_command,
                                      normalize_params)

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
    print "This plugin manages the ports tree for both - the base system", \
          "as well as for the jail systems. Usage:\n\n", \
          "  1) in order to see this help:\n\n", \
          "      # %s %s help\n\n" % (__projectname__, __pluginname__), \
          "  or simply:\n\n      # %s %s\n\n" % (__projectname__, 
                                                 __pluginname__), \
          "  2) in order to see a short version of this help:\n\n", \
          "      # %s %s options\n\n" % (__projectname__, __pluginname__), \
          "  3) in order to see plugin version:\n\n", \
          "      # %s %s version\n\n" % (__projectname__, __pluginname__), \
          "  4) in order to update ports for both - the base system and", \
          "available jails:\n\n", \
          "      # %s %s update\n\n" % (__projectname__, __pluginname__), \
          "  5) in order to see the all the packages that need upgrading:\n\n", \
          "      # %s %s diff all\n\n" % (__projectname__, __pluginname__), \
          "  or, to show the packages to upgrade only in the base system", \
          "and jail named jail1:\n\n", \
          "      # %s %s diff base jail1\n\n" % (__projectname__,
                                                 __pluginname__), \
          "  where 'base' stands for the base system;\n", \
          "  6) in order to upgrade all the systems listed in", \
          "the config file:\n\n", \
          "      # %s %s upgrade all\n\n" % (__projectname__, __pluginname__), \
          "  or, to upgrade only the base system and jail named jail1\n\n", \
          "      # %s %s upgrade base jail1\n\n" % \
          (__projectname__, __pluginname__), \
          "  where 'base' stands for the base system."

    # Exit after printing help.
    sys.exit(1)

def options(params):
    """
    Give just a short output of options.
    """

    version(params)

    print "Usage: %s %s <option>\n\n" % (__projectname__, __pluginname__), \
          "where the possible options include:\n", \
          "- help - show a more detailed help message;\n", \
          "- update - update ports tree;\n", \
          "- diff [all|base|jail1...] - show ports that need upgrading;\n", \
          "- upgrade [all|jail1|jail2...] - upgrade packages;\n", \
          "- options - show this message;\n", \
          "- version - show the plugin version."

    # Exit after printing help.
    sys.exit(0)

def update(params):
    """
    Update the port tree on the base system as well as in jails. 
    """

    # First, update the base system. 
    print colored("==>", "green"), \
          colored("Updating ports on the base system", attrs=["bold"]) + \
          colored(":\n", attrs=["bold"])

    execute_command(["portsnap fetch update"])

    #Update the ports tree for jails now.
    print colored("\n==>", "green"), \
          colored("Updating ports for the jails", attrs=["bold"]) + \
          colored(":\n", attrs=["bold"])

    execute_command(["ezjail-admin update -P"])

def upgrade(params):
    """
    Upgrade base system and some of the jails. Get the list of systems to 
    upgrade from the command line. Usage:
    
        # czokomaster ports upgrade base jail1 jail2
      
    This would upgrade the base system only:
    
        # czokomaster ports upgrade base
          
    This would upgrade all jails. Caution! Jails' names must be put into
    the config file:
    
        # czokomaster ports upgrade all
    """

    # Get base or/and jails that are to be upgraded.
    # normalize_params() requires config section, config variable and params.
    jails = normalize_params(__pluginname__, "jails", params)

    # Get the upgrade command.
    ports_upgrade_cmd = get_config_option(__pluginname__, "ports_upgrade_cmd")

    # If the base system is to be upgraded as well, do it now. In order
    # to upgrade the base system, add "base" to the "jails" option within
    # the config file.
    if "base" in jails:
        # Both "colored(...)" shall be displayed as one text line.
        print colored("\n==>", "green"), \
              colored("Upgrading the base system", attrs=["bold"]) + \
              colored(":\n", attrs=["bold"])

        execute_command([ports_upgrade_cmd])

        # Drop "base" from the list, so it does not interfere with the loop below.
        # Print new line as well.
        jails.remove("base")
        print ""

    # Upgrade specified jails.
    for jail in jails:
        print colored("\n==>", "green"), \
              colored("Upgrading", attrs=["bold"]), \
              colored(jail, "cyan") + colored(":\n", attrs=["bold"])
        
        execute_command(["jexec %s %s" % (jail, ports_upgrade_cmd)])

    # Print new line.
    print ""

def diff(params):
    """
    Show the ports that need to be updated.
    """

    jails = normalize_params(__pluginname__, "jails", params)
    
    # Get the command to show the ports that need updating.
    show_updates_cmd = get_config_option(__pluginname__, "show_updates_cmd")

    # First, the base system, if it is supplied either on the command line
    # or in the config file.
    if "base" in jails:
        print "Available updates for", colored("the base system", "cyan") + ":"

        # Pass the 'func_return=True' as a function argument, so the output is
        # not printed but returned to stdout and stderr variables.
        stdout, stderr = execute_command([show_updates_cmd], func_return=True)

        # If stdout is nil, don't print red '->'. Print green '-> None'.
        if stdout:
            print colored("->", "red"), stdout[:-2].replace("\n", \
                  colored("\n-> ", "red"))
        else:
            print colored("->", "green"), colored("None", "white", \
                                                  attrs=["bold"])

        # Remove "base", so it does not interfere with the loop below.
        jails.remove("base")

    for jail in jails:
        # Print available updates.
        print "\nAvailable updates for", \
              colored(jail, "cyan") + ":"

        stdout, stderr = execute_command(["jexec %s %s" % (jail,
                         show_updates_cmd)], func_return=True)

        # If stdout is nil, don't print red '->'. Print green '-> None'.
        if stdout:
            print colored("->", "red"), stdout[:-2].replace("\n", \
                  colored("\n-> ", "red"))
        else:
            print colored("->", "green"), colored("None", attrs=["bold"])