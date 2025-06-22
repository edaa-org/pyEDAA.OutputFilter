.. include:: shields.inc

.. image:: _static/logo.svg
   :height: 90 px
   :align: center
   :target: https://GitHub.com/edaa-org/pyEDAA.OutputFilter

.. raw:: html

    <br>

.. raw:: latex

   \part{Introduction}

.. only:: html

   |  |SHIELD:svg:OutputFilter-github| |SHIELD:svg:OutputFilter-src-license| |SHIELD:svg:OutputFilter-ghp-doc| |SHIELD:svg:OutputFilter-doc-license|
   |  |SHIELD:svg:OutputFilter-pypi-tag| |SHIELD:svg:OutputFilter-pypi-status| |SHIELD:svg:OutputFilter-pypi-python|
   |  |SHIELD:svg:OutputFilter-gha-test| |SHIELD:svg:OutputFilter-lib-status| |SHIELD:svg:OutputFilter-codacy-quality| |SHIELD:svg:OutputFilter-codacy-coverage| |SHIELD:svg:OutputFilter-codecov-coverage|

.. Disabled shields: |SHIELD:svg:OutputFilter-lib-dep| |SHIELD:svg:OutputFilter-req-status| |SHIELD:svg:OutputFilter-lib-rank|

.. only:: latex

   |SHIELD:png:OutputFilter-github| |SHIELD:png:OutputFilter-src-license| |SHIELD:png:OutputFilter-ghp-doc| |SHIELD:png:OutputFilter-doc-license|
   |SHIELD:png:OutputFilter-pypi-tag| |SHIELD:png:OutputFilter-pypi-status| |SHIELD:png:OutputFilter-pypi-python|
   |SHIELD:png:OutputFilter-gha-test| |SHIELD:png:OutputFilter-lib-status| |SHIELD:png:OutputFilter-codacy-quality| |SHIELD:png:OutputFilter-codacy-coverage| |SHIELD:png:OutputFilter-codecov-coverage|

.. Disabled shields: |SHIELD:png:OutputFilter-lib-dep| |SHIELD:png:OutputFilter-req-status| |SHIELD:png:OutputFilter-lib-rank|

The pyEDAA.OutputFilter Documentation
#####################################

Proposal to define an abstract model for outputs from EDA tools and logging libraries.

.. image:: _static/work-in-progress.png
   :height: 150 px
   :align: center

.. #   :target: https://GitHub.com/edaa-org/pyEDAA.OutputFilter

Main Goals
**********

* Live and offline parsing and classification of message lines from tool outputs.
* Provide a data model for tool specific log files.
* Extract values, lists and tables of embedded reports or summaries.
* Implement checks and policies.

Use Cases
*********

* Write colorized logs to CI server logs or to shells based on classification.
* Increase or decrease the severity level of message.
* List messages of a certain kind (e.g. unused sequential elements).
* Check for existence / non-existence of messages or outputs (e.g. latches).
* Collect statistics and convert to datasets for a time series database (TSDB).

Examples
********

List all warnings
=================

.. code-block:: Python

   from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

   logfile = Path("tests/data/Stopwatch/toplevel.vds")
   processor = Processor(logfile)
   processor.Parse()

   print(f"CRITICAL WARNING Messages ({len(processor.CriticalWarningMessages}):")
   for message in processor.CriticalWarningMessages:
     print(f"  {message}")


.. _CONTRIBUTORS:

Contributors
************

* :gh:`Patrick Lehmann <Paebbels>` (Maintainer)
* `and more... <https://GitHub.com/edaa-org/pyEDAA.OutputFilter/graphs/contributors>`__


.. _LICENSE:

.. todo:: add license texts here

.. toctree::
   :hidden:

   Used as a layer of EDA² ➚ <https://edaa-org.github.io/>


.. toctree::
   :caption: Introduction
   :hidden:

   Installation
   Dependency


.. raw:: latex

   \part{Main Documentation}

.. toctree::
   :caption: Main Documentation
   :hidden:

   Xilinx/Vivado

.. raw:: latex

   \part{References and Reports}

.. toctree::
   :caption: References and Reports
   :hidden:

   CommandLineInterface
   Python Class Reference <pyEDAA.OutputFilter/pyEDAA.OutputFilter>
   unittests/index
   coverage/index
   CodeCoverage
   Doc. Coverage Report <DocCoverage>
   Static Type Check Report ➚ <typing/index>

.. Coverage Report ➚ <coverage/index>

.. raw:: latex

   \part{Appendix}

.. toctree::
   :caption: Appendix
   :hidden:

   License
   Doc-License
   Glossary
   genindex
   Python Module Index <modindex>
   TODO
