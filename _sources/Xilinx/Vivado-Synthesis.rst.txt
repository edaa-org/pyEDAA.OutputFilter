.. _XIL/Vivado/Synth:

Synthesis
#########

A Vivado synthesis log output (:file:`*.vds` log file) is comprised of mostly one-liner human-readable text outputs. The
document starts with a preamble, has circa :ref:`20 sections <XIL/Vivado/Synth/Steps>` and ends with a epilog. Each
sections is framed by ``Start xxx`` and ``Finished xxx`` lines. In between, :ref:`messages <XIL/Vivado/Synth/Messages>`
of categories: ``INFO``, ``WARNING``, ``CRITICAL WARNING`` or ``ERROR`` are interweaved.

.. _XIL/Vivado/Synth/Processing:

Processing the ``*.vds`` File
*****************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      A logfile can be processed by :class:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Processor`. First, it reads a logfile
      into a list of lines, which get pre-classified as normal output lines or :ref:`messages <XIL/Vivado/Synth/Messages>`.
      At next, lines are passed to a parser for :ref:`extracting information <XIL/Vivado/Synth/ExtractedInformation>` of
      the synthesis log's sections. Each section might have different output formatting styles like trees or tables.

      Besides low-level information extraction, also complex results can be derived from the collected data. This allows
      higher software layers to implement :ref:`policies <XIL/Vivado/Synth/Policies>`. A common use case is the
      detection of :ref:`unused code <XIL/Vivado/Synth/UnusedSignals>` or the detection of
      :ref:`latches <XIL/Vivado/Synth/Latches>`.

      The whole processing duration is measured and accessible via
      :data:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Processor.Duration`.

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

         logfile = Path("tests/data/Stopwatch/toplevel.vds")
         processor = Processor(logfile)
         processor.Parse()

         print(f"Processing duration: {processor.Duration:.3f} seconds")


.. _XIL/Vivado/Synth/ExtractedInformation:

Extracted Information
*********************

.. _XIL/Vivado/Synth/Messages:

Messages
========

.. grid:: 2

   .. grid-item::
      :columns: 6

      All messages (besides some irregular formats) have the following format:

      .. code-block:: text

         INFO: [Synth 8-7075] Helper process launched with PID 24240

      Messages are classified into 4 categories: ``INFO``, ``WARNING``, ``CRITICAL WARNING`` or ``ERROR``. Each message
      mentions the generating tool (e.g. ``Synth``), the tool's ID (e.g. ``8``) and a message kind ID (e.g. ``7075``)
      followed by the message string.

      All messages of the same category can be accessed in order of appearance in the tool's output via read-only
      properties:

      * :data:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Processor.InfoMessages`
      * :data:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Processor.WarningMessages`
      * :data:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Processor.CriticalWarningMessages`
      * :data:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Processor.ErrorMessages`

      In addition, messages are grouped in two stages by tool ID and message kind ID. These can be accessed via
      data:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Processor.MessagesByID`.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Message by ID
            :sync: ByID

            .. code-block:: Python

               from pathlib import Path
               from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

               logfile = Path("tests/data/Stopwatch/toplevel.vds")
               processor = Processor(logfile)
               processor.Parse()

               print(f"Messages by ID:")
               for toolID, messageGroup in processor.MessagesByID.items():
                 print(f"{processor.ToolNames[toolID]} {toolID}:")
                 for messageID, messages in messageGroup.items():
                   print(f"  {messageID} ({len(messages)}):")
                   for message in messages:
                     print(f"    {message}")

         .. tab-item:: INFO
            :sync: INFO

            .. code-block:: Python

               from pathlib import Path
               from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

               logfile = Path("tests/data/Stopwatch/toplevel.vds")
               processor = Processor(logfile)
               processor.Parse()

               print(f"INFO Messages ({len(processor.InfoMessages)}):")
               for message in processor.InfoMessages:
                 print(f"  {message}")

         .. tab-item:: WARNING
            :sync: WARNING

            .. code-block:: Python

               from pathlib import Path
               from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

               logfile = Path("tests/data/Stopwatch/toplevel.vds")
               processor = Processor(logfile)
               processor.Parse()

               print(f"WARNING Messages ({len(processor.WarningMessages)}):")
               for message in processor.WarningMessages:
                 print(f"  {message}")

         .. tab-item:: CRITICAL WARNING
            :sync: CRITICAL

            .. code-block:: Python

               from pathlib import Path
               from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

               logfile = Path("tests/data/Stopwatch/toplevel.vds")
               processor = Processor(logfile)
               processor.Parse()

               print(f"CRITICAL WARNING Messages ({len(processor.CriticalWarningMessages)}):")
               for message in processor.CriticalWarningMessages:
                 print(f"  {message}")

         .. tab-item:: ERROR
            :sync: ERROR

            .. code-block:: Python

               from pathlib import Path
               from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

               logfile = Path("tests/data/Stopwatch/toplevel.vds")
               processor = Processor(logfile)
               processor.Parse()

               print(f"ERROR Messages ({len(processor.ErrorMessages)}):")
               for message in processor.ErrorMessages:
                 print(f"  {message}")


.. _XIL/Vivado/Synth/ToolVersion:

Tool Version
============

.. grid:: 2

   .. grid-item::
      :columns: 6

      The used Vivado version is extracted by the :class:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Preamble` parser and can
      be accessed via :data:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Processor.ToolVersion` as :class:`~pyTooling.Versioning.YearReleaseVersion`.

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pathlib import Path
         from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

         logfile = Path("tests/data/Stopwatch/toplevel.vds")
         processor = Processor(logfile)
         processor.Parse()

         print(f"Vivado version: v{processor[Preamble].ToolVersion}")


.. _XIL/Vivado/Synth/SynthStart:

Synthesis start time and date
=============================

.. grid:: 2

   .. grid-item::
      :columns: 6

      The start timestamp (as :class:`~datetime.datetime`) is extracted by the :class:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Preamble`
      parser and can be accessed via :data:`~pyEDAA.OutputFilter.Xilinx.Synthesis.Processor.StartDateTime`.

      .. seealso::

         :ref:`XIL/Vivado/Synth/SynthDuration`

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pathlib import Path
         from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

         logfile = Path("tests/data/Stopwatch/toplevel.vds")
         processor = Processor(logfile)
         processor.Parse()

         print(f"Synthesis started: v{processor[Preamble].StartDatetime}")


.. _XIL/Vivado/Synth/SynthDuration:

Synthesis duration
==================

.. grid:: 2

   .. grid-item::
      :columns: 6

      The synthesis runtime is extracted by the WritingSynthesisReport parser.

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pathlib import Path
         from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

         logfile = Path("tests/data/Stopwatch/toplevel.vds")
         processor = Processor(logfile)
         processor.Parse()

         print(f"Synthesis duration: v{processor[WritingSynthesisReport].Duration:.1f} seconds")

.. _XIL/Vivado/Synth/Blackboxes:

Blackboxes
==========

.. grid:: 2

   .. grid-item::
      :columns: 6

      tbd

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pathlib import Path
         from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

         logfile = Path("tests/data/Stopwatch/toplevel.vds")
         processor = Processor(logfile)
         processor.Parse()

.. _XIL/Vivado/Synth/Cells:

FPGA Low-Level Cells
====================

.. grid:: 2

   .. grid-item::
      :columns: 6

      tbd

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pathlib import Path
         from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

         logfile = Path("tests/data/Stopwatch/toplevel.vds")
         processor = Processor(logfile)
         processor.Parse()


.. _XIL/Vivado/Synth/Policies:

Policies
********

.. _XIL/Vivado/Synth/Latches:

Latches
=======

.. grid:: 2

   .. grid-item::
      :columns: 6

      Latches are present in the design, if warning ``Synth 8-327`` was found or when the low-level cell report contains
      cell ``LD``.


   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pathlib import Path
         from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

         logfile = Path("tests/data/Stopwatch/toplevel.vds")
         processor = Processor(logfile)
         processor.Parse()

         print(f"Synthesis duration: v{processor[WritingSynthesisReport].Duration:.1f} seconds")


.. _XIL/Vivado/Synth/SensitivityList:

Sensitivity List
================

.. grid:: 2

   .. grid-item::
      :columns: 6

      Synth 8-614

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pathlib import Path
         from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

         logfile = Path("tests/data/Stopwatch/toplevel.vds")
         processor = Processor(logfile)
         processor.Parse()


.. _XIL/Vivado/Synth/UnusedSignals:

Unused Signals
==============

.. grid:: 2

   .. grid-item::
      :columns: 6

      Synth 8-3332

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pathlib import Path
         from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

         logfile = Path("tests/data/Stopwatch/toplevel.vds")
         processor = Processor(logfile)
         processor.Parse()



.. _XIL/Vivado/Synth/Steps:

Processing Steps
****************

.. _XIL/Vivado/Synth/Preamble:

Preamble
========

Extracted information:

 * Tool version
 * Start time and date

RTLElaboration
==============

HandlingCustomAttributes1
=========================

.. _XIL/Vivado/Synth/LoadingPart:

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

.. _XIL/Vivado/Synth/SynthesisReport:

WritingSynthesisReport
======================

Extracted information:

 * List of blackboxes
 * Low-level resource usage (cells)

Derived information:

 * Are latches (``LD``) present?
