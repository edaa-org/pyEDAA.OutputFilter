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
from datetime import datetime
from pathlib  import Path
from unittest import TestCase as TestCase

from pytest                     import mark
from pyTooling.Versioning       import YearReleaseVersion
from pyTooling.Warning          import WarningCollector

from pyEDAA.OutputFilter.Xilinx import Document, VivadoLine, VivadoMessagesMixin
from pyEDAA.OutputFilter.Xilinx import Synth_Design, Link_Design, Opt_Design, Place_Design, Route_Design, PhyOpt_Design, Write_Bitstream
from pyEDAA.OutputFilter.Xilinx import SynthesizeDesign as _SynthDesign

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

		self.assertEqual(42, processor.Duration)
		self.assertEqual(datetime(2025, 6, 12, 18, 38, 16), processor.StartDateTime)
		self.assertEqual(datetime(2025, 6, 12, 18, 38, 58), processor.ExitDateTime)
		self.assertEqual(358, len(processor.Lines))
		self.assertLess(processor.ProcessingDuration, 0.4)

		self.assertEqual(69, len(processor.InfoMessages))
		self.assertEqual(3, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 1), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(66, len(synthesis.InfoMessages))
		self.assertEqual(3, len(synthesis.WarningMessages))
		self.assertEqual(0, len(synthesis.CriticalWarningMessages))
		self.assertEqual(0, len(synthesis.ErrorMessages))

		rtlElaboration = synthesis[_SynthDesign.RTLElaboration]
		self.assertEqual(47, len(rtlElaboration.InfoMessages))
		self.assertEqual(0, len(rtlElaboration.WarningMessages))
		self.assertEqual(0, len(rtlElaboration.CriticalWarningMessages))
		self.assertEqual(0, len(rtlElaboration.ErrorMessages))

		handlingCustomAttributes = synthesis[_SynthDesign.HandlingCustomAttributes]
		self.assertEqual(0, len(handlingCustomAttributes.InfoMessages))
		self.assertEqual(0, len(handlingCustomAttributes.WarningMessages))
		self.assertEqual(0, len(handlingCustomAttributes.CriticalWarningMessages))
		self.assertEqual(0, len(handlingCustomAttributes.ErrorMessages))

		loadingPart = synthesis[_SynthDesign.LoadingPart]
		self.assertEqual(0, len(loadingPart.InfoMessages))
		self.assertEqual(0, len(loadingPart.WarningMessages))
		self.assertEqual(0, len(loadingPart.CriticalWarningMessages))
		self.assertEqual(0, len(loadingPart.ErrorMessages))

		applySetPropertyXDCConstraints = synthesis[_SynthDesign.ApplySetPropertyXDCConstraints]
		self.assertEqual(0, len(applySetPropertyXDCConstraints.InfoMessages))
		self.assertEqual(0, len(applySetPropertyXDCConstraints.WarningMessages))
		self.assertEqual(0, len(applySetPropertyXDCConstraints.CriticalWarningMessages))
		self.assertEqual(0, len(applySetPropertyXDCConstraints.ErrorMessages))

		rtlComponentStatistics = synthesis[_SynthDesign.RTLComponentStatistics]
		self.assertEqual(0, len(rtlComponentStatistics.InfoMessages))
		self.assertEqual(0, len(rtlComponentStatistics.WarningMessages))
		self.assertEqual(0, len(rtlComponentStatistics.CriticalWarningMessages))
		self.assertEqual(0, len(rtlComponentStatistics.ErrorMessages))

		partResourceSummary = synthesis[_SynthDesign.PartResourceSummary]
		self.assertEqual(0, len(partResourceSummary.InfoMessages))
		self.assertEqual(0, len(partResourceSummary.WarningMessages))
		self.assertEqual(0, len(partResourceSummary.CriticalWarningMessages))
		self.assertEqual(0, len(partResourceSummary.ErrorMessages))

		crossBoundaryAndAreaOptimization = synthesis[_SynthDesign.CrossBoundaryAndAreaOptimization]
		self.assertEqual(0, len(crossBoundaryAndAreaOptimization.InfoMessages))
		self.assertEqual(3, len(crossBoundaryAndAreaOptimization.WarningMessages))
		self.assertEqual(0, len(crossBoundaryAndAreaOptimization.CriticalWarningMessages))
		self.assertEqual(0, len(crossBoundaryAndAreaOptimization.ErrorMessages))

		applyingXDCTimingConstraints = synthesis[_SynthDesign.ApplyingXDCTimingConstraints]
		self.assertEqual(0, len(applyingXDCTimingConstraints.InfoMessages))
		self.assertEqual(0, len(applyingXDCTimingConstraints.WarningMessages))
		self.assertEqual(0, len(applyingXDCTimingConstraints.CriticalWarningMessages))
		self.assertEqual(0, len(applyingXDCTimingConstraints.ErrorMessages))

		timingOptimization = synthesis[_SynthDesign.TimingOptimization]
		self.assertEqual(0, len(timingOptimization.InfoMessages))
		self.assertEqual(0, len(timingOptimization.WarningMessages))
		self.assertEqual(0, len(timingOptimization.CriticalWarningMessages))
		self.assertEqual(0, len(timingOptimization.ErrorMessages))

		technologyMapping = synthesis[_SynthDesign.TechnologyMapping]
		self.assertEqual(0, len(technologyMapping.InfoMessages))
		self.assertEqual(0, len(technologyMapping.WarningMessages))
		self.assertEqual(0, len(technologyMapping.CriticalWarningMessages))
		self.assertEqual(0, len(technologyMapping.ErrorMessages))

		ioInsertion = synthesis[_SynthDesign.IOInsertion]
		self.assertEqual(0, len(ioInsertion.InfoMessages))
		self.assertEqual(0, len(ioInsertion.WarningMessages))
		self.assertEqual(0, len(ioInsertion.CriticalWarningMessages))
		self.assertEqual(0, len(ioInsertion.ErrorMessages))

		flatteningBeforeIOInsertion = ioInsertion[_SynthDesign.FlatteningBeforeIOInsertion]
		self.assertEqual(0, len(flatteningBeforeIOInsertion.InfoMessages))
		self.assertEqual(0, len(flatteningBeforeIOInsertion.WarningMessages))
		self.assertEqual(0, len(flatteningBeforeIOInsertion.CriticalWarningMessages))
		self.assertEqual(0, len(flatteningBeforeIOInsertion.ErrorMessages))

		finalNetlistCleanup = ioInsertion[_SynthDesign.FinalNetlistCleanup]
		self.assertEqual(0, len(finalNetlistCleanup.InfoMessages))
		self.assertEqual(0, len(finalNetlistCleanup.WarningMessages))
		self.assertEqual(0, len(finalNetlistCleanup.CriticalWarningMessages))
		self.assertEqual(0, len(finalNetlistCleanup.ErrorMessages))

		renamingGeneratedInstances = synthesis[_SynthDesign.RenamingGeneratedInstances]
		self.assertEqual(0, len(renamingGeneratedInstances.InfoMessages))
		self.assertEqual(0, len(renamingGeneratedInstances.WarningMessages))
		self.assertEqual(0, len(renamingGeneratedInstances.CriticalWarningMessages))
		self.assertEqual(0, len(renamingGeneratedInstances.ErrorMessages))

		rebuildingUserHierarchy = synthesis[_SynthDesign.RebuildingUserHierarchy]
		self.assertEqual(0, len(rebuildingUserHierarchy.InfoMessages))
		self.assertEqual(0, len(rebuildingUserHierarchy.WarningMessages))
		self.assertEqual(0, len(rebuildingUserHierarchy.CriticalWarningMessages))
		self.assertEqual(0, len(rebuildingUserHierarchy.ErrorMessages))

		renamingGeneratedPorts = synthesis[_SynthDesign.RenamingGeneratedPorts]
		self.assertEqual(0, len(renamingGeneratedPorts.InfoMessages))
		self.assertEqual(0, len(renamingGeneratedPorts.WarningMessages))
		self.assertEqual(0, len(renamingGeneratedPorts.CriticalWarningMessages))
		self.assertEqual(0, len(renamingGeneratedPorts.ErrorMessages))

		handlingCustomAttributes = handlingCustomAttributes.Next
		self.assertIsNotNone(handlingCustomAttributes)
		self.assertEqual(0, len(handlingCustomAttributes.InfoMessages))
		self.assertEqual(0, len(handlingCustomAttributes.WarningMessages))
		self.assertEqual(0, len(handlingCustomAttributes.CriticalWarningMessages))
		self.assertEqual(0, len(handlingCustomAttributes.ErrorMessages))

		renamingGeneratedNets = synthesis[_SynthDesign.RenamingGeneratedNets]
		self.assertEqual(0, len(renamingGeneratedNets.InfoMessages))
		self.assertEqual(0, len(renamingGeneratedNets.WarningMessages))
		self.assertEqual(0, len(renamingGeneratedNets.CriticalWarningMessages))
		self.assertEqual(0, len(renamingGeneratedNets.ErrorMessages))

		writingSynthesisReport = synthesis[_SynthDesign.WritingSynthesisReport]
		self.assertEqual(0, len(writingSynthesisReport.Blackboxes))
		self.assertEqual(14, len(writingSynthesisReport.Cells))

		self.assertEqual(0, len(warnings))
		lineCount = len(processor.Lines)
		previousLine = None
		for i, line in enumerate(processor.Lines, start=1):
			self.assertIsInstance(line, VivadoLine)
			self.assertEqual(i, line.LineNumber)
			self.assertIs(previousLine, line.PreviousLine)
			if i < lineCount:
				self.assertIs(processor.Lines[i], line.NextLine)
			else:
				self.assertIsNone(line.NextLine)

			previousLine = line

	def test_ImplementationLogfile(self) -> None:
		print()
		logfile = Path("tests/data/Stopwatch/toplevel.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.ProcessingDuration, 0.4)

		self.assertEqual(152, len(processor.InfoMessages))
		self.assertEqual(2, len(processor.WarningMessages))
		self.assertEqual(2, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(9, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(2, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(2, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(25, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(37, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(22, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		lineCount = len(processor.Lines)
		previousLine = None
		for i, line in enumerate(processor.Lines, start=1):
			self.assertIsInstance(line, VivadoLine)
			self.assertEqual(i, line.LineNumber)
			self.assertIs(previousLine, line.PreviousLine)
			if i < lineCount:
				self.assertIs(processor.Lines[i], line.NextLine)
			else:
				self.assertIsNone(line.NextLine)

			previousLine = line


# class TestCase:
# 	pass


class CERN_DevKit(TestCase):
	def test_SynthesisLogfile(self) -> None:
		print()
		logfile = Path("tests/data/CERN_DevKit/devkit_top_bd_wrapper.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(70, len(processor.InfoMessages))
		self.assertEqual(124, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 2), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(13, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile(self) -> None:
		print()
		logfile = Path("tests/data/CERN_DevKit/devkit_top_bd_wrapper.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(305, len(processor.InfoMessages))
		self.assertEqual(125, len(processor.WarningMessages))
		self.assertEqual(1, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()

		linkDesign = processor[Link_Design]
		self.assertEqual(30, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(117, sumWarn.sum(len(linkDesign.WarningMessages)))  # -14
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(145, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(6,  sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(59, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(1,  sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(6, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(13, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0,  sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0,  sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0,  sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)


class Enclustra_Mercury_ZX5(TestCase):
	def test_SynthesisLogfile_2019_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/system_top.2019.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(71, len(processor.InfoMessages))       # -1
		self.assertEqual(112, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2019, 1), processor._preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()

		synthesis = processor[Synth_Design]
		self.assertEqual(65, sumInfo.sum(len(synthesis.InfoMessages)))      # -12
		self.assertEqual(111, sumWarn.sum(len(synthesis.WarningMessages)))  # -2
		self.assertEqual(0, sumCrit.sum(len(synthesis.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(synthesis.ErrorMessages)))

		self.assertEqual(14, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2019_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/system_top.2019.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(115, len(processor.InfoMessages))   # -12
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2019, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(21, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(24, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(21, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		self.assertNotIn(PhyOpt_Design, processor)

		routeDesign = processor[Route_Design]
		self.assertEqual(12, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		self.assertNotIn(Write_Bitstream, processor)

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2019_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/system_top.2019.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(66, len(processor.InfoMessages))
		self.assertEqual(112, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2019, 2), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(14, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2019_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/system_top.2019.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(131, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(3, len(processor.CriticalWarningMessages))
		self.assertEqual(1, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2019, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(21, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(27, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(24, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		self.assertNotIn(PhyOpt_Design, processor)

		routeDesign = processor[Route_Design]
		self.assertEqual(13, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(9, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2020_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2020.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(41, len(processor.InfoMessages))
		self.assertEqual(5, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2020, 1), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2020_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2020.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(151, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(3, len(processor.CriticalWarningMessages))
		self.assertEqual(1, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2020, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(14, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(26, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(28, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(4, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(13, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2020_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2020.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(41, len(processor.InfoMessages))
		self.assertEqual(2, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2020, 2), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2020_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2020.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(152, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(3, len(processor.CriticalWarningMessages))
		self.assertEqual(1, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2020, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(15, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(26, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(28, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(4, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(12, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2021_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2021.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(41, len(processor.InfoMessages))
		self.assertEqual(2, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2021, 1), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

	def test_ImplementationLogfile_2021_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2021.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(153, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(3, len(processor.CriticalWarningMessages))
		self.assertEqual(1, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2021, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(15, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(26, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(28, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(4, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(13, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2021_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2021.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(42, len(processor.InfoMessages))
		self.assertEqual(105, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2021, 2), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2021_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2021.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(157, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(3, len(processor.CriticalWarningMessages))
		self.assertEqual(1, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2021, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(15, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(30, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(28, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(4, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(13, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2022_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2022.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(47, len(processor.InfoMessages))
		self.assertEqual(106, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2022, 1), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2022_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2022.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(155, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(3, len(processor.CriticalWarningMessages))
		self.assertEqual(1, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2022, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(15, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(28, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(28, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(4, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(13, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2022_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2022.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(55, len(processor.InfoMessages))
		self.assertEqual(106, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2022, 2), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2022_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2022.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(155, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(3, len(processor.CriticalWarningMessages))
		self.assertEqual(1, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2022, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(15, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(28, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(29, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(4, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(13, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2023_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2023.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(53, len(processor.InfoMessages))
		self.assertEqual(106, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2023, 1), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2023_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2023.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(154, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(4, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2023, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(15, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(27, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(29, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(4, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(13, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2023_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2023.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertLess(processor.ProcessingDuration, 0.4)

		self.assertEqual(52, len(processor.InfoMessages))
		self.assertEqual(106, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2023, 2), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2023_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2023.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(158, len(processor.InfoMessages))
		self.assertEqual(201, len(processor.WarningMessages))
		self.assertEqual(4, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2023, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(18, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(101, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(29, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(100, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(29, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(4, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(13, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2024_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2024.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(53, len(processor.InfoMessages))
		self.assertEqual(105, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 1), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2024_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2024.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(161, len(processor.InfoMessages))
		self.assertEqual(103, len(processor.WarningMessages))
		self.assertEqual(4, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(19, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(101, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(28, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(29, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(5, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(12, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2024_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2024.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(51, len(processor.InfoMessages))
		self.assertEqual(105, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 2), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2024_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2024.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(158, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(4, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(15, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(31, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(29, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(5, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2025_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2025.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(57, len(processor.InfoMessages))
		self.assertEqual(106, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 1), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(7, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2025_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2025.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(159, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(4, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 1), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(16, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(31, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(29, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(5, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		writeBitstream = processor[Write_Bitstream]
		self.assertEqual(8, sumInfo.sum(len(writeBitstream.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(writeBitstream.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(writeBitstream.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(writeBitstream.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_SynthesisLogfile_2025_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2025.2.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(45, len(processor.InfoMessages))
		self.assertEqual(102, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 2), processor._preamble.ToolVersion)

		synthesis = processor[Synth_Design]
		self.assertEqual(4, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_ImplementationLogfile_2025_2(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2025.2.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(124, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2025, 2), processor.Preamble.ToolVersion)

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(13, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		# self.assertEqual(29, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(29, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(5, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	@mark.xfail(reason="Not yet supported. Maybe unknown sections.")
	def test_SynthesisLogfile_2026_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2026.1.vds")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(48, len(processor.InfoMessages))
		self.assertEqual(102, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		preamble = processor.Preamble
		self.assertEqual(YearReleaseVersion(2026, 1), preamble.ToolVersion)
		self.assertEqual(1, len(preamble.InfoMessages))
		self.assertEqual(0, len(preamble.WarningMessages))
		self.assertEqual(0, len(preamble.CriticalWarningMessages))
		self.assertEqual(0, len(preamble.ErrorMessages))
		self.assertIn(17, preamble.MessagesByID)
		self.assertIn(3922, preamble.MessagesByID[17])

		synthesis = processor[Synth_Design]
		self.assertEqual(4, len(synthesis[_SynthDesign.WritingSynthesisReport].Blackboxes))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	@mark.xfail(reason="Not yet supported. Maybe unknown sections.")
	def test_ImplementationLogfile_2026_1(self) -> None:
		print()
		logfile = Path("tests/data/Enclustra_Mercury_ZX5/Mercury_ZX5_ST1.2026.1.vdi")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(159, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(4, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		preamble = processor.Preamble
		self.assertEqual(YearReleaseVersion(2026, 1), preamble.ToolVersion)
		self.assertEqual(1, len(preamble.InfoMessages))
		self.assertEqual(0, len(preamble.WarningMessages))
		self.assertEqual(0, len(preamble.CriticalWarningMessages))
		self.assertEqual(0, len(preamble.ErrorMessages))
		self.assertIn(17, preamble.MessagesByID)
		self.assertIn(3922, preamble.MessagesByID[17])

		sumInfo = Aggregator()
		sumWarn = Aggregator()
		sumCrit = Aggregator()
		sumErro = Aggregator()
		linkDesign = processor[Link_Design]
		self.assertEqual(16, sumInfo.sum(len(linkDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(linkDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(linkDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(linkDesign.ErrorMessages)))

		optDesign = processor[Opt_Design]
		self.assertEqual(31, sumInfo.sum(len(optDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(optDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(optDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(optDesign.ErrorMessages)))

		placeDesign = processor[Place_Design]
		self.assertEqual(29, sumInfo.sum(len(placeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(placeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(placeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(placeDesign.ErrorMessages)))

		physOptDesign = processor[PhyOpt_Design]
		self.assertEqual(5, sumInfo.sum(len(physOptDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(physOptDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(physOptDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(physOptDesign.ErrorMessages)))

		routeDesign = processor[Route_Design]
		self.assertEqual(10, sumInfo.sum(len(routeDesign.InfoMessages)))
		self.assertEqual(0, sumWarn.sum(len(routeDesign.WarningMessages)))
		self.assertEqual(0, sumCrit.sum(len(routeDesign.CriticalWarningMessages)))
		self.assertEqual(0, sumErro.sum(len(routeDesign.ErrorMessages)))

		# compare sum of sections with total numbers
		self.assertGreaterEqual(len(processor.InfoMessages), sumInfo.Value)
		self.assertGreaterEqual(len(processor.WarningMessages), sumWarn.Value)
		self.assertGreaterEqual(len(processor.CriticalWarningMessages), sumCrit.Value)
		self.assertGreaterEqual(len(processor.ErrorMessages), sumErro.Value)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)
