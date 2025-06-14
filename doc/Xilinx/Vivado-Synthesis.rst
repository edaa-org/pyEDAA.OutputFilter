.. _XIL/Vivado/Synth:

Synthesis
#########

.. _XIL/Vivado/Synth/Processing:

Processing the ``*.vds`` File
*****************************

.. code-block:: Python

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

WARNING Messages
----------------

CRITICAl WARNING Messages
-------------------------

ERROR Messages
--------------

Tool Version
============

The tool version is extratced by the Preamble parser.

.. code-block:: Python

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"Vivado version: v{processor[Preamble].ToolVersion}")

Synthesis start time and date
=============================

The start timestamp (:class:`datetime`) is extratced by the Preamble parser.

.. code-block:: Python

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"Synthesis started: v{processor[Preamble].StartDatetime}")

Synthesis duration
==================

The synthesis runtime is extratced by the WritingSynthesisReport parser.

.. code-block:: Python

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
