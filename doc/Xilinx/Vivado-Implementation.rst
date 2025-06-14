.. _XIL/Vivado/Impl:

Implementation
##############

.. _XIL/Vivado/Impl/Processing:

Processing the ``*.vdi`` File
*****************************

.. code-block:: Python

   from pyEDAA.OutputFilter.Xilinx.Implementation import Processor

   logfile = Path("tests/data/Stopwatch/toplevel.vdi")
   processor = Processor(logfile)
   processor.Parse()

   print(f"Processing duration: {processor.Duration:.3f} seconds")


.. _XIL/Vivado/Impl/ExtractedInformation:

Extracted Information
*********************

Messages
========

INFO Messages
-------------

WARNING Messages
----------------

CRITICAl WARNING Messages
-------------------------

ERROR Messages
--------------

Tool Version
============

The tool version is extracted by the Preamble parser.

.. code-block:: Python

   from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"Vivado version: v{processor[Preamble].ToolVersion}")

Synthesis start time and date
=============================

The start timestamp (:class:`datetime`) is extracted by the Preamble parser.

.. code-block:: Python

   from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"Synthesis started: v{processor[Preamble].StartDatetime}")

Implementation duration
=======================


.. _XIL/Vivado/Impl/Steps:

Processing Steps
****************

Preamble
========

Extracted information:

 * Tool version
 * Start time and date
