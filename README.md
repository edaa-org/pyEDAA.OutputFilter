<p align="center">
  <a title="edaa-org.github.io/pyEDAA.OutputFilter" href="https://edaa-org.github.io/pyEDAA.OutputFilter"><img height="80px" src="doc/_static/logo.svg"/></a>
</p>

[![Sourcecode on GitHub](https://img.shields.io/badge/pyEDAA-OUTPUTFILTER-ab47bc.svg?longCache=true&style=flat-square&logo=github&longCache=true&logo=GitHub&labelColor=6a1b9a)](https://GitHub.com/edaa-org/pyEDAA.OUTPUTFILTER)
[![Sourcecode License](https://img.shields.io/pypi/l/pyEDAA.OUTPUTFILTER?longCache=true&style=flat-square&logo=Apache&label=code)](LICENSE.md)
[![Documentation](https://img.shields.io/website?longCache=true&style=flat-square&label=edaa-org.github.io%2FpyEDAA.OUTPUTFILTER&logo=GitHub&logoColor=fff&up_color=blueviolet&up_message=Read%20now%20%E2%9E%9A&url=https%3A%2F%2Fedaa-org.github.io%2FpyEDAA.OUTPUTFILTER%2Findex.html)](https://edaa-org.github.io/pyEDAA.OUTPUTFILTER/)
[![Documentation License](https://img.shields.io/badge/doc-CC--BY%204.0-green?longCache=true&style=flat-square&logo=CreativeCommons&logoColor=fff)](LICENSE.md)  
[![PyPI](https://img.shields.io/pypi/v/pyEDAA.OUTPUTFILTER?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)](https://pypi.org/project/pyEDAA.OUTPUTFILTER/)
![PyPI - Status](https://img.shields.io/pypi/status/pyEDAA.OUTPUTFILTER?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyEDAA.OUTPUTFILTER?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)  
[![GitHub Workflow - Build and Test Status](https://img.shields.io/github/actions/workflow/status/edaa-org/pyEDAA.OUTPUTFILTER/Pipeline.yml?longCache=true&style=flat-square&label=Build%20and%20test&logo=GitHub%20Actions&logoColor=FFFFFF)](https://GitHub.com/edaa-org/pyEDAA.OUTPUTFILTER/actions/workflows/Pipeline.yml)
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyEDAA.OUTPUTFILTER?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff)](https://libraries.io/github/edaa-org/pyEDAA.OUTPUTFILTER)
[![Codacy - Quality](https://img.shields.io/codacy/grade/4918480c41594ffbb62f8ff98433b800?longCache=true&style=flat-square&logo=Codacy)](https://www.codacy.com/gh/edaa-org/pyEDAA.OUTPUTFILTER)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/4918480c41594ffbb62f8ff98433b800?longCache=true&style=flat-square&logo=Codacy)](https://www.codacy.com/gh/edaa-org/pyEDAA.OUTPUTFILTER)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/edaa-org/pyEDAA.OUTPUTFILTER?longCache=true&style=flat-square&logo=Codecov)](https://codecov.io/gh/edaa-org/pyEDAA.OUTPUTFILTER)

<!--
[![Dependent repos (via libraries.io)](https://img.shields.io/librariesio/dependent-repos/pypi/pyEDAA.OUTPUTFILTER?longCache=true&style=flat-square&logo=GitHub)](https://github.com/edaa-org/pyEDAA.OUTPUTFILTER/network/dependents)
[![Requires.io](https://img.shields.io/requires/github/edaa-org/pyEDAA.OUTPUTFILTER?longCache=true&style=flat-square)](https://requires.io/github/edaa-org/pyEDAA.OUTPUTFILTER/requirements/?branch=main)
[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/pyEDAA.OUTPUTFILTER)](https://libraries.io/github/edaa-org/pyEDAA.OUTPUTFILTER/sourcerank)  
-->

<p align="center">
  <img height="275px" src="doc/_static/work-in-progress.png"/>
</p>

# Main Goals

* Live and offline parsing and classification of message lines from tool outputs.
* Provide a data model for tool specific log files.
* Extract values, lists and tables of embedded reports or summaries.
* Implement checks and policies.

# Use Cases

* Write colorized logs to CI server logs or to shells based on classification.
* Increase or decrease the severity level of message.
* List messages of a certain kind (e.g. unused sequential elements).
* Check for existence / non-existence of messages or outputs (e.g. latches).
* Collect statistics and convert to datasets for a time series database (TSDB).

# Examples

```python
from pathlib import Path
from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor

logfile = Path("tests/data/Stopwatch/toplevel.vds")
processor = Processor(logfile)
processor.Parse()

print(f"CRITICAL WARNING Messages ({len(processor.CriticalWarningMessages)}):")
for message in processor.CriticalWarningMessages:
  print(f"  {message}")
```

# Contributors

* [Patrick Lehmann](https://github.com/Paebbels) (Maintainer)
* [Unai Martinez-Corral](https://github.com/umarcor)
* [and more...](https://github.com/edaa-org/pyEDAA.OutputFilter/graphs/contributors)

# License

This Python package (source code) is licensed under [Apache License 2.0](LICENSE.md).
The accompanying documentation is licensed under [Creative Commons - Attribution 4.0 (CC-BY 4.0)](doc/Doc-License.rst).

-------------------------
SPDX-License-Identifier: Apache-2.0
