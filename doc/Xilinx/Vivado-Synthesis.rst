.. _XIL/Vivado/Synth:

Synthesis
#########

.. _XIL/Vivado/Synth/Processing:

Processing the ``*.vds`` File
*****************************

.. code-block:: Python

   from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"Processing duration: {processor.Duration:.3f} seconds")


.. _XIL/Vivado/Synth/ExtractedInformation:

Extracted Information
*********************

Messages
========

INFO Messages
-------------

.. code-block:: Python

   from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"INFO Messages ({len(processor.InfoMessages)}):")
   for message in processor.InfoMessages:
     print(f"  {message}")

WARNING Messages
----------------

.. code-block:: Python

   from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"WARNING Messages ({len(processor.WarningMessages)}):")
   for message in processor.WarningMessages:
     print(f"  {message}")

CRITICAl WARNING Messages
-------------------------

.. code-block:: Python

   from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"CRITICAL WARNING Messages ({len(processor.CriticalWarningMessages)}):")
   for message in processor.CriticalWarningMessages:
     print(f"  {message}")

ERROR Messages
--------------

.. code-block:: Python

   from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"ERROR Messages ({len(processor.ErrorMessages)}):")
   for message in processor.ErrorMessages:
     print(f"  {message}")

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

Synthesis duration
==================

The synthesis runtime is extracted by the WritingSynthesisReport parser.

.. code-block:: Python

   from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"Synthesis duration: v{processor[WritingSynthesisReport].Duration:.1f} seconds")

.. _XIL/Vivado/Synth/Steps:

Processing Steps
****************

Preamble
========

Extracted information:

 * Tool version
 * Start time and date

RTLElaboration
==============

HandlingCustomAttributes1
=========================

LoadingPart
===========

Extracted information:

 * 🚧 Part name

ApplySetProperty
================

RTLComponentStatistics
======================

PartResourceSummary
===================

CrossBoundaryAndAreaOptimization
================================

ApplyingXDCTimingConstraints
============================

TimingOptimization
==================

TechnologyMapping
=================

IOInsertion
===========

FlatteningBeforeIOInsertion
===========================

FinalNetlistCleanup
===================

RenamingGeneratedInstances
==========================

RebuildingUserHierarchy
=======================

RenamingGeneratedPorts
======================

HandlingCustomAttributes2
=========================

RenamingGeneratedNets
=====================

WritingSynthesisReport
======================

Extracted information:

 * List of blackboxes
 * Low-level resource usage (cells)
