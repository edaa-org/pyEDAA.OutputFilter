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

from pyEDAA.OutputFilter.Xilinx import Document, LinkDesign, OptimizeDesign, PlaceDesign, RouteDesign, \
	PhysicalOptimizeDesign, WriteBitstream
from pyEDAA.OutputFilter.Xilinx.Commands         import SynthesizeDesign
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import WritingSynthesisReport, CrossBoundaryAndAreaOptimization, \
	RTLElaboration

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
		self.assertEqual(69 - (5 + 5 + 2 + 10), len(synthesis.InfoMessages))
		self.assertEqual(3, len(synthesis.WarningMessages))
		self.assertEqual(0, len(synthesis.CriticalWarningMessages))
		self.assertEqual(0, len(synthesis.ErrorMessages))

		rtlElaboration = synthesis[RTLElaboration]
		self.assertEqual(47, len(rtlElaboration.InfoMessages))
		self.assertEqual(0, len(rtlElaboration.WarningMessages))
		self.assertEqual(0, len(rtlElaboration.CriticalWarningMessages))
		self.assertEqual(0, len(rtlElaboration.ErrorMessages))

		crossBoundaryAndAreaOptimization = synthesis[CrossBoundaryAndAreaOptimization]
		self.assertEqual(0, len(crossBoundaryAndAreaOptimization.InfoMessages))
		self.assertEqual(3, len(crossBoundaryAndAreaOptimization.WarningMessages))
		self.assertEqual(0, len(crossBoundaryAndAreaOptimization.CriticalWarningMessages))
		self.assertEqual(0, len(crossBoundaryAndAreaOptimization.ErrorMessages))

		self.assertEqual(0, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile(self) -> None:
		logfile = Path("tests/data/Stopwatch/toplevel.vdi")
		processor = Document(logfile)
		processor.Parse()

		self.assertLess(processor.Duration, 0.1)

		self.assertEqual(152, len(processor.InfoMessages))
		self.assertEqual(2, len(processor.WarningMessages))
		self.assertEqual(2, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 1), processor.Preamble.ToolVersion)

		linkDesign = processor[LinkDesign]
		self.assertEqual(9, len(linkDesign.InfoMessages))
		self.assertEqual(2, len(linkDesign.WarningMessages))
		self.assertEqual(2, len(linkDesign.CriticalWarningMessages))
		self.assertEqual(0, len(linkDesign.ErrorMessages))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(26, len(optDesign.InfoMessages))
		self.assertEqual(0, len(optDesign.WarningMessages))
		self.assertEqual(0, len(optDesign.CriticalWarningMessages))
		self.assertEqual(0, len(optDesign.ErrorMessages))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, len(placeDesign.InfoMessages))
		self.assertEqual(0, len(placeDesign.WarningMessages))
		self.assertEqual(0, len(placeDesign.CriticalWarningMessages))
		self.assertEqual(0, len(placeDesign.ErrorMessages))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, len(physOptDesign.InfoMessages))
		self.assertEqual(0, len(physOptDesign.WarningMessages))
		self.assertEqual(0, len(physOptDesign.CriticalWarningMessages))
		self.assertEqual(0, len(physOptDesign.ErrorMessages))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, len(routeDesign.InfoMessages))
		self.assertEqual(0, len(routeDesign.WarningMessages))
		self.assertEqual(0, len(routeDesign.CriticalWarningMessages))
		self.assertEqual(0, len(routeDesign.ErrorMessages))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, len(writeBitstream.InfoMessages))
		self.assertEqual(0, len(writeBitstream.WarningMessages))
		self.assertEqual(0, len(writeBitstream.CriticalWarningMessages))
		self.assertEqual(0, len(writeBitstream.ErrorMessages))
