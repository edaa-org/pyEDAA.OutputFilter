# ==================================================================================================================== #
#               _____ ____    _        _      ___        _               _   _____ _ _ _                               #
#   _ __  _   _| ____|  _ \  / \      / \    / _ \ _   _| |_ _ __  _   _| |_|  ___(_) | |_ ___ _ __                    #
#  | '_ \| | | |  _| | | | |/ _ \    / _ \  | | | | | | | __| '_ \| | | | __| |_  | | | __/ _ \ '__|                   #
#  | |_) | |_| | |___| |_| / ___ \  / ___ \ | |_| | |_| | |_| |_) | |_| | |_|  _| | | | ||  __/ |                      #
#  | .__/ \__, |_____|____/_/   \_\/_/   \_(_)___/ \__,_|\__| .__/ \__,_|\__|_|   |_|_|\__\___|_|                      #
#  |_|    |___/                                             |_|                                                        #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2025-2025 Electronic Design Automation Abstraction (EDA²)                                                  #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""Unit tests for Vivado synthesis log files."""
from pathlib  import Path
from unittest import TestCase as TestCase

from pyTooling.Versioning                        import YearReleaseVersion

from pyEDAA.OutputFilter.Xilinx                  import Document
from pyEDAA.OutputFilter.Xilinx.Commands         import SynthesizeDesign
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import WritingSynthesisReport

if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Stopwatch(TestCase):
	def test_SynthesisLogfile(self) -> None:
		logfile = Path("tests/data/Stopwatch/toplevel.vds")
		processor = Document(logfile)
		processor.Parse()

		self.assertLess(processor.Duration, 0.1)

		self.assertEqual(69, len(processor.InfoMessages))
		self.assertEqual(3, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 1), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]

		self.assertEqual(0, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile(self) -> None:
		logfile = Path("tests/data/Stopwatch/toplevel.vdi")
		processor = Document(logfile)
		processor.Parse()

		self.assertLess(processor.Duration, 0.1)
