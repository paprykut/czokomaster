#!/usr/bin/env python
"""
This is a standalone scripy to be run from cron. It gathers the information
about the python packages that need to be updated. Why here, not in in 
czokomaster itself? Because, yolk -U takes approximately 1,5 minute for one jail
(not heavily populated with python packages anyway), to show the respective
updates. This is far too long. Thus, this script should gather, possibly daily,
information about new versions of python packages available on pip. This 
information is then written to the respective files. Then, when the following 
command is issued:

  # czokomaster pippy diff all

the possible updates will be shown for all of the jails (+ the base system) in
no time rather than 10 minutes.
"""

__helpername__ = "pippy-cron-helper"
__author__ = "Mikolaj Romel"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Mikolaj Romel"
__license__ = "New-style BSD"

import os
import os.path

from czokomaster.meta import CZOKOMASTER_CONFIG_PATH
from czokomaster.czokomanager import get_config_option, execute_command

class PythonUpdateChecker:
    """
    Check updates for the installed python packages.
    """

    def __init__(self):
        """
        Check whether the infrastructure exists.
        """

        # Get the path to the cache dir.
        self.pippy_cachedir = get_config_option("pippy", "pippy_cachedir")

        # If the directory does not exist, create one. Recursively.
        if not os.path.exists(self.pippy_cachedir):
            os.makedirs(self.pippy_cachedir, 0700)

    def get_updates(self, system_name=None):
        """
        Get the information which python packages need to be updated. Use 
        "yolk -U" to get this info.

        Attributes:

        system_name = give the name of the base system or a jail in order to
                      process just one unit. REMINDER: system_name must be given
                      as a list. Thus, get_updates("jail") will not work, while
                      get_updates(["jail"]) will.
        """

        self.jails = system_name

        if self.jails == None:
            # Get the names of the jails. Afterwards, list and save the update list.
            self.jails = get_config_option("pippy", "jails")

        # Show updates for the base system.
        if "base" in self.jails:
            update, error = execute_command(["yolk -U"], func_return=True)
            self._save_updates("base", update)

            # Remove "base" from the list, so it is not invoked in the loop
            # below.
            self.jails.remove("base")

        for jail in self.jails:
            update, error = execute_command(["jexec %s yolk -U" % \
                                            jail], func_return=True)

            self._save_updates(jail, update)

    def _save_updates(self, filename, update_list):
        """
        Helper function - save the output of "yolk -U" to the respective
        files named after the jails.
        """

        self.filename = filename
        # Process the list, so there are no whitespaces at the beginning of 
        # each verse.
        self.update_list = update_list.strip().replace("\n ", "\n")
        jail_cachefile = self.pippy_cachedir + os.sep + self.filename

        f = open(jail_cachefile, "w")
        f.write(self.update_list)
        f.close()

if __name__ == "__main__":
    update = PythonUpdateChecker()
    update.get_updates()