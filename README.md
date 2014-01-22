czokomaster
===========

Freebsd jail packages updater/upgrader.

###Note to the people

I have once started this project in order to provide easy updater/upgrader for packages in different jails. There is still a lot to be done (e.g. creating a cache for a package once built, so the other jails can reuse it instead of compiling it once more), yet I simply do not administer these servers anymore, thus I do not take care of it at this particular moment. Nevertheless, it worked on production for about a year and did not damage anything in the meantime. So far, I have written two plugins - one for upgrading ports and one for upgrading python packages. Possibilities for extension are endless.

The code itself is well-documented, probably even too-well - you read it like a novel, plot twists everywhere. Perhaps, this is not the best coding style and a lot of things (maybe even the whole framework structure that is not class-based) might seem to be naive, yet I am not a computer programmer by profession.

Hopefully, one day someone will find this code in the internet abyss and put it into use. If so, you might drop me a line, so I could keep a sentimental eye on the progress.

###Usage

There was a quick build script and a freebsd port for this package, yet the former stopped working and I am ashamed of the latter, so these are not included. If you want to try czokomaster, please move the czokomaster dir to ```/wherever/you/keep/your/python/site-packages/```. Then, either move czokomaster.py to ```/usr/local/sbin/``` or start it simply by issuing ```./czokomaster [options]```.

Need help? Run:
```
czokomaster help
```

P.S. Do not mind the name, it is a long story.

Cheers.
