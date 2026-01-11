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
# Copyright 2025-2026 Electronic Design Automation Abstraction (EDA²)                                                  #
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
from pyTooling.Warning                           import WarningCollector

from pyEDAA.OutputFilter.Xilinx                  import Document, LinkDesign, OptimizeDesign, PlaceDesign, RouteDesign
from pyEDAA.OutputFilter.Xilinx                  import PhysicalOptimizeDesign, WriteBitstream
from pyEDAA.OutputFilter.Xilinx.Commands         import SynthesizeDesign
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import WritingSynthesisReport, CrossBoundaryAndAreaOptimization, \
	RTLElaboration

if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Aggregator:
	_s: int

	def __init__(self, s: int = 0) -> None:
		self._s = s

	def sum(self, s: int) -> int:
		self._s += s
		return s

	@property
	def Value(self) -> int:
		return self._s


class Stopwatch(TestCase):
	def test_SynthesisLogfile(self) -> None:
		print()
		logfile = Path("tests/data/Stopwatch/toplevel.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

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
		print()
		logfile = Path("tests/data/Stopwatch/toplevel.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		self.assertEqual(152, len(processor.InfoMessages))
		self.assertEqual(2, len(processor.WarningMessages))
		self.assertEqual(2, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)


class CERN_DevKit(TestCase):
	def test_SynthesisLogfile(self) -> None:
		print()
		logfile = Path("tests/data/CERN_DevKit/devkit_top_bd_wrapper.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		self.assertEqual(70, len(processor.InfoMessages))
		self.assertEqual(124, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 2), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile(self) -> None:
		print()
		logfile = Path("tests/data/CERN_DevKit/devkit_top_bd_wrapper.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		self.assertEqual(305, len(processor.InfoMessages))
		self.assertEqual(126, len(processor.WarningMessages))
		self.assertEqual(1, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()

		linkDesign = processor[LinkDesign]
		self.assertEqual(30, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(117, sumWarn.sum(len(linkDesign.WarningMessages)))  # -14
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(145, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(6,  sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(59, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(1,  sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(1,  sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(6, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(13, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)


class Enclustra_Mercury_ZX5(TestCase):
	def test_SynthesisLogfile_2019_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/system_top.2019.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		self.assertEqual(69, len(processor.InfoMessages))       # -1
		self.assertEqual(112, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2019, 1), processor._preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()

		synthesis = processor[SynthesizeDesign]
		self.assertEqual(63, sumInfo.sum(len(synthesis.InfoMessages)))      # -12
		self.assertEqual(111, sumWarn.sum(len(synthesis.WarningMessages)))  # -2
		self.assertEqual(0, sumCrit.sum(len(synthesis.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(synthesis.ErrorMessages)))

		self.assertEqual(14, len(synthesis[WritingSynthesisReport].Blackboxes))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_ImplementationLogfile_2019_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/system_top.2019.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		self.assertEqual(115, len(processor.InfoMessages))   # -12
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2019, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(21, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(24, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(21, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(12, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2019_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/system_top.2019.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2019, 2), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2019_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/system_top.2019.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2019, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2020_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2020.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2020, 1), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2020_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2020.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2020, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2020_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2020.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2020, 2), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2020_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2020.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2020, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2021_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2021.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2021, 1), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2021_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2021.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2021, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2021_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2021.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2021, 2), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2021_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2021.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2021, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2022_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2022.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2022, 1), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2022_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2022.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2022, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2022_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2022.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2022, 2), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2022_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2022.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2022, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2023_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2023.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2023, 1), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2023_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2023.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2023, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2023_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2023.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2023, 2), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2023_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2023.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2023, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2024_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2024.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 1), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2024_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2024.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2024_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2024.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 2), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2024_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2024.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

	def test_SynthesisLogfile_2025_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2025.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(70, len(processor.InfoMessages))
		# self.assertEqual(124, len(processor.WarningMessages))
		# self.assertEqual(0, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 1), processor._preamble.ToolVersion)

		synthesis = processor[SynthesizeDesign]
		# self.assertEqual(13, len(synthesis[WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2025_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2025.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.Duration, 0.2)

		# self.assertEqual(152, len(processor.InfoMessages))
		# self.assertEqual(2, len(processor.WarningMessages))
		# self.assertEqual(2, len(processor.CriticalWarningMessages))
		# self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[LinkDesign]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[OptimizeDesign]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[PlaceDesign]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhysicalOptimizeDesign]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[RouteDesign]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[WriteBitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)
