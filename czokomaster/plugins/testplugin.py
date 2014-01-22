"""
This is an exemplary plugin. What comes within it is the general 
template on which the rest of the plugins shall be built.

It is advised to mentioned that "params" variable passed to all the plugins
has the following structure:

  params[0] - name of the mother app (together with its path), would probably 
              extend to "/usr/local/sbin/czokomaster" or wherever the main 
              command is installed;
  params[1] - name of the plugin invoked, in this case would be "testplugin";
  params[2] - name of the function to be invoked, e.g. "help", "version", etc.
              Thus, the following command:
              
                  # czokomaster testplugin version
              
              would invoke the plugin named "testplugin" and later on invoke
              the function named "version" within that plugin;
  params[3-X] - specific params passed to the function if any are needed. Could
                e.g. be the username if the plugin creates users. Thus, the
                following command:
                
                    # czokomaster testplugin help param
                
                would send an additional parameter to the plugin function with
                value extending to "param".          
"""

__pluginname__ = "testplugin"
__author__ = "Mikolaj Romel"
__version__ = "0.1-r1"
__copyright__ = "Copyright (c) 2012 Mikolaj Romel"
__license__ = "New-style BSD"

def version(params, *args, **kwargs):
    """
    This function prints the name, version and copyrights of this plugin.
    """

    print "%s version %s %s" % (__pluginname__, __version__, __copyright__)

def help(params, *args, **kwargs):
    """
    This function is invoked when help for the plugin is called.
    Put here all the help that might help the user to use this plugin.
    Help must be printed to stdout, so use "print" to do it.
    """

    ## Print plugin version followed by some help.
    ## All the functions within this script must be invoked
    ## with "params" as a parameter.
    version(params)
    print "Here comes the help how to use the plugin."

def some_function(params, *args, **kwargs):
    """
    Change the name of this function to whatever you like. Also, you might
    add as many functions as you want. Each function within this plugin will
    be invoked by the user in the following manner:
      
        $ czokomaster testplugin functionname
    
    Where "testplugin" is the name of this plugin and "functionname" is the 
    name of the function that is to be invoked. Thus, in order to invoke this
    particular function, the user would need to type the following:
    
        $ czokomaster testplugin some_function
      
    """

    a = 2
    b = 50
    mymath = a * b

    print "This function prints some basic math: %d" % mymath
