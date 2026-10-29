.. _NEWS:

News
####

See :gh:`pyEDAA.OutputFilter Release Pages <edaa-org/pyEDAA.OutputFilter/releases>` for detail release notes on every
release.


Version 0.17.0 (2026)
*********************

.. topic:: :gh:`v0.17.0 - 29.10.2026 <edaa-org/pyEDAA.OutputFilter/releases/v0.17.0>`

   .. rubric:: Changes

   * pyTooling 10.1 is required; Python 3.11 to 3.15 are supported.
   * The program :program:`pyedaa-outputfilter` starts again; v0.16.0 failed at every invocation.
   * The CLI's headline is the class variable ``HEADLINE`` (was ``programTitle``).
   * Durations of the Vivado processors are pyTooling ``Duration`` objects instead of a ``float`` in seconds.
   * The copyright holder is *Electronic Design Automation Abstraction (EDA²)*.

   .. rubric:: Documentation

   * The documentation is built with pyTooling.Sphinx: dependency tables, and report pages per testsuite, source file
     and module.
