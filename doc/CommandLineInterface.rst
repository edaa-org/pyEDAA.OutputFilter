Command Line Interfaces
#######################

When installed via PIP, the command line program ``pyedaa-outputfilter`` is registered in the Python installation's
``Scripts`` directory. Usually this path is listed in ``PATH``, thus this program is globally available after
installation.

The program is self-describing. Use ``pyedaa-outputfilter`` without parameters or ``pyedaa-outputfilter help`` to see
all available common options and commands. Each command has then it's own help page for command specific options, which
can be listed by calling ``pyedaa-outputfilter <cmd> -h`` or ``pyedaa-outputfilter help <cmd>``. The
``pyedaa-outputfilter``'s version and license information is shown by calling ``pyedaa-outputfilter version``.

.. _References/cli:

.. autoprogram:: pyEDAA.OutputFilter.CLI:Application().MainParser
  :prog: pyedaa-outputfilter
  :groups:
