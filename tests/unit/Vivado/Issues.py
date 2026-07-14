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
# Copyright 2026-2026 Electronic Design Automation Abstraction (EDA²)                                                  #
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
"""Unit tests for Vivado log files reported in issues."""
from datetime import datetime
from pathlib  import Path
from unittest import TestCase as TestCase

from pyTooling.Versioning       import YearReleaseVersion
from pyTooling.Warning          import WarningCollector

from pyEDAA.OutputFilter.Xilinx import Document, Launch, Open_Checkpoint
from pyEDAA.OutputFilter.Xilinx import Synth_Design, Opt_Design, Place_Design, Route_Design, PhyOpt_Design

if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Issue87(TestCase):
	def test_Logfile(self) -> None:
		print()
		logfile = Path("tests/data/Issues/87/vivado.log")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(104, len(processor.InfoMessages))
		self.assertEqual(6, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 2), processor._preamble.ToolVersion)

		preamble = processor.Preamble
		self.assertEqual(YearReleaseVersion(2024, 2), preamble.ToolVersion)
		self.assertEqual(datetime(2026, 7, 7, 9, 59, 29), preamble.StartDateTime)
		self.assertEqual(0, len(preamble.InfoMessages))
		self.assertEqual(0, len(preamble.WarningMessages))
		self.assertEqual(0, len(preamble.CriticalWarningMessages))
		self.assertEqual(0, len(preamble.ErrorMessages))

		postamble = processor.Postamble
		# self.assertEqual(datetime(2026, 7, 7, 10, 1, 37), postamble.ExitDateTime)

		self.assertTrue(processor.HasNestedLaunches)
		self.assertEqual(2, len(processor.NestedLaunches))

		synth1: Launch = processor.NestedLaunches[0]
		self.assertEqual("synth_1", synth1.Name)
		self.assertEqual(datetime(2026, 7, 7, 9, 59, 36), synth1.LaunchDateTime)  # launch
		self.assertEqual(datetime(2026, 7, 7, 9, 59, 39), synth1.StartDateTime)   #   preamble
		self.assertEqual(datetime(2026, 7, 7, 10, 0, 2), synth1.ExitDateTime)     #   postamble
		self.assertEqual(datetime(2026, 7, 7, 10, 0, 6), synth1.FinishDateTime)   # finished

		self.assertEqual(16, len(synth1.InfoMessages))
		self.assertEqual(1, len(synth1.WarningMessages))
		self.assertEqual(0, len(synth1.CriticalWarningMessages))
		self.assertEqual(0, len(synth1.ErrorMessages))

		self.assertIn(Synth_Design, synth1)

		impl1: Launch = processor.NestedLaunches[1]
		self.assertEqual("impl_1", impl1.Name)
		self.assertEqual(datetime(2026, 7, 7, 10, 0, 11), impl1.LaunchDateTime)  # launch
		self.assertEqual(datetime(2026, 7, 7, 10, 0, 20), impl1.StartDateTime)   #   preamble
		self.assertEqual(datetime(2026, 7, 7, 10, 1, 35), impl1.ExitDateTime)     #   postamble
		self.assertEqual(datetime(2026, 7, 7, 10, 1, 37), impl1.FinishDateTime)   # finished

		self.assertEqual(80, len(impl1.InfoMessages))
		self.assertEqual(3, len(impl1.WarningMessages))
		self.assertEqual(0, len(impl1.CriticalWarningMessages))
		self.assertEqual(0, len(impl1.ErrorMessages))

		self.assertIn(Open_Checkpoint, impl1)
		self.assertIn(Opt_Design, impl1)
		self.assertIn(Place_Design, impl1)
		self.assertIn(PhyOpt_Design, impl1)
		self.assertIn(Route_Design, impl1)

	def test_EnAxiRbInterface(self) -> None:
		print()
		logfile = Path("tests/data/Issues/87/en_axi_rb_interface.log")
		with WarningCollector() as warnings:
			processor = Document(logfile)
			processor.Parse()

		for warning in warnings:
			print(f"Warning: {warning}")

		self.assertEqual(186, len(processor.InfoMessages))
		self.assertEqual(37, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertEqual(YearReleaseVersion(2024, 2), processor._preamble.ToolVersion)

		preamble = processor.Preamble
		self.assertEqual(YearReleaseVersion(2024, 2), preamble.ToolVersion)
		self.assertEqual(datetime(2026, 7, 1, 23, 47, 43), preamble.StartDateTime)
		self.assertEqual(0, len(preamble.InfoMessages))
		self.assertEqual(0, len(preamble.WarningMessages))
		self.assertEqual(0, len(preamble.CriticalWarningMessages))
		self.assertEqual(0, len(preamble.ErrorMessages))

		postamble = processor.Postamble
		# self.assertEqual(datetime(2026, 7, 7, 10, 1, 37), postamble.ExitDateTime)

		self.assertTrue(processor.HasNestedLaunches)
		self.assertEqual(2, len(processor.NestedLaunches))

		synth1: Launch = processor.NestedLaunches[0]
		self.assertEqual("synth_xczu5ev-fbvb900-1-i", synth1.Name)
		self.assertEqual(datetime(2026, 7, 1, 23, 47, 54), synth1.LaunchDateTime)  # launch
		self.assertEqual(datetime(2026, 7, 1, 23, 47, 58), synth1.StartDateTime)   #   preamble
		self.assertEqual(datetime(2026, 7, 1, 23, 49, 40), synth1.ExitDateTime)     #   postamble
		self.assertEqual(datetime(2026, 7, 1, 23, 49, 44), synth1.FinishDateTime)   # finished

		self.assertEqual(26, len(synth1.InfoMessages))
		self.assertEqual(25, len(synth1.WarningMessages))
		self.assertEqual(0, len(synth1.CriticalWarningMessages))
		self.assertEqual(0, len(synth1.ErrorMessages))

		self.assertIn(Synth_Design, synth1)

		impl1: Launch = processor.NestedLaunches[1]
		self.assertEqual("impl_xczu5ev-fbvb900-1-i", impl1.Name)

		self.assertEqual(datetime(2026, 7, 1, 23, 50, 17), impl1.LaunchDateTime)  # launch
		self.assertEqual(datetime(2026, 7, 1, 23, 50, 26), impl1.StartDateTime)   #   preamble
		self.assertEqual(datetime(2026, 7, 1, 23, 52, 44), impl1.ExitDateTime)     #   postamble
		self.assertEqual(datetime(2026, 7, 1, 23, 52, 48), impl1.FinishDateTime)   # finished

		self.assertEqual(117, len(impl1.InfoMessages))
		self.assertEqual(7, len(impl1.WarningMessages))
		self.assertEqual(0, len(impl1.CriticalWarningMessages))
		self.assertEqual(0, len(impl1.ErrorMessages))

		self.assertIn(Opt_Design, impl1)
		self.assertIn(Place_Design, impl1)
		self.assertNotIn(PhyOpt_Design, impl1)
		self.assertIn(Route_Design, impl1)
