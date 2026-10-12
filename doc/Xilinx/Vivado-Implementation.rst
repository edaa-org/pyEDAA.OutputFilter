.. _XIL/Vivado/Impl:

Implementation
##############

.. _XIL/Vivado/Impl/Processing:

Processing the ``*.vdi`` File
*****************************

.. code-block:: Python

   from pathlib import Path

   from pyTooling.Warning          import WarningCollector
   from pyEDAA.OutputFilter.Xilinx import Document

   logfile = Path("tests/data/Stopwatch/toplevel.vdi")
   with WarningCollector() as warnings:
     processor = Document(logfile)
     processor.Parse()

   print(f"Processing duration: {processor.ProcessingDuration:.3f} seconds")


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

   from pathlib import Path

   from pyTooling.Warning          import WarningCollector
   from pyEDAA.OutputFilter.Xilinx import Document

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   with WarningCollector() as warnings:
     processor = Document(logfile)
     processor.Parse()

   print(f"Vivado version: v{processor.Preamble.ToolVersion}")

Synthesis start time and date
=============================

The start timestamp (:class:`~datetime.datetime`) is extracted by the Preamble parser.

.. code-block:: Python

   from pathlib import Path

   from pyTooling.Warning          import WarningCollector
   from pyEDAA.OutputFilter.Xilinx import Document

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   with WarningCollector() as warnings:
     processor = Document(logfile)
     processor.Parse()

   print(f"Synthesis started: {processor.StartDateTime}")

Implementation duration
=======================


.. _XIL/Vivado/Impl/Policies:

Policies
********

Timing Closure
==============

Timing 38-282


.. _XIL/Vivado/Impl/Steps:

Processing Steps
****************

Preamble
========

Extracted information:

 * Tool version
 * Start time and date
