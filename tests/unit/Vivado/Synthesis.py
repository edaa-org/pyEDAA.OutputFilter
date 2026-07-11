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
from io       import StringIO
from textwrap import dedent
from typing   import ClassVar
from unittest import TestCase as TestCase

from pytest               import mark
from pyTooling.Versioning import YearReleaseVersion
from pyTooling.Warning    import WarningCollector

from pyEDAA.OutputFilter.Xilinx import Processor, Preamble, Synth_Design, VivadoLine, timestampIterator
from pyEDAA.OutputFilter.Xilinx import SynthesizeDesign as _SynthDesign


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Preambles(TestCase):
	_LICENSE_INFO:   ClassVar[str] = ("""\
		INFO: [Common 17-3922] A valid Vivado Design Suite ENTERPRISE license has been detected. Your current license is active and will expire on Permanent.""")
	_PIPED_PREAMBLE: ClassVar[str] = ("""\

		****** Vivado v2024.2 (64-bit)
		  **** SW Build 5239630 on Fri Nov 08 22:35:27 MST 2024
		  **** IP Build 5239520 on Sun Nov 10 16:12:51 MST 2024
		  **** SharedData Build 5239561 on Fri Nov 08 14:39:27 MST 2024
		  **** Start of session at: Wed Jul  1 23:50:26 2026
		    ** Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
		    ** Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
		""")
	_LOGFILE_PREAMBLE: ClassVar[str] = ("""\
		#-----------------------------------------------------------
		# Vivado v2019.1 (64-bit)
		# SW Build 2552052 on Fri May 24 14:49:42 MDT 2019
		# IP Build 2548770 on Fri May 24 18:01:18 MDT 2019
		# Start of session at: Tue Sep  2 08:44:13 2025
		#-----------------------------------------------------------""")
	_POSTAMBLE: ClassVar[str] = ("""\
		INFO: [Common 17-206] Exiting Vivado at Tue Sep  2 08:44:45 2025...""")
	_OUTER_SOURCE_TCL: ClassVar[str] = ("""\
		source build_project.tcl -notrace
		INFO: [filemgmt 56-3] Default IP Output Path : Could not find the directory 'C:/temp/OutputFilterBug/project_1/project_1.gen/sources_1'.
		Scanning sources...
		Finished scanning sources
		WARNING: [Vivado 12-1017] Problems encountered:
		1. Failed to delete one or more files in run directory C:/temp/OutputFilterBug/project_1/project_1.runs/synth_1""")
	_LAUNCH_SYNTH_1: ClassVar[str] = ("""\

		[Tue Jul  7 09:59:36 2026] Launched synth_1...
		Run output will be captured here: C:/temp/OutputFilterBug/project_1/project_1.runs/synth_1/runme.log

		[Tue Jul  7 09:59:36 2026] Waiting for synth_1 to finish (timeout in 120 minutes)...

		*** Running vivado
				with args -log top.vds -m64 -product Vivado -mode batch -messageDb vivado.pb -notrace -source top.tcl

		""")
	_INNER_SOURCE_TCL: ClassVar[str] = ("""\
		source top.tcl -notrace
		Command: synth_design -top top -part xc7z030ffg676-1
		Starting synth_design
		Attempting to get a license for feature 'Synthesis' and/or device 'xc7z030'
		INFO: [Common 17-349] Got license for feature 'Synthesis' and/or device 'xc7z030'
		INFO: [Synth 8-7079] Multithreading enabled for synth_design using a maximum of 2 processes.
		INFO: [Synth 8-7078] Launching helper process for spawning children vivado processes
		Synth Design complete | Checksum: 12a8949
		INFO: [Common 17-83] Releasing license: Synthesis
		12 Infos, 1 Warnings, 0 Critical Warnings and 0 Errors encountered.
		synth_design completed successfully
		synth_design: Time (s): cpu = 00:00:14 ; elapsed = 00:00:17 . Memory (MB): peak = 1541.031 ; gain = 1146.508
		Write ShapeDB Complete: Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.001 . Memory (MB): peak = 1541.031 ; gain = 0.000
		INFO: [Common 17-1381] The checkpoint 'C:/temp/OutputFilterBug/project_1/project_1.runs/synth_1/top.dcp' has been generated.
		INFO: [Vivado 12-24828] Executing command : report_utilization -file top_utilization_synth.rpt -pb top_utilization_synth.pb""")
	_WAIT_ON_SYNTH_1: ClassVar[str] = ("""\
		[Tue Jul  7 10:00:06 2026] synth_1 finished
		wait_on_runs: Time (s): cpu = 00:00:00 ; elapsed = 00:00:30 . Memory (MB): peak = 399.656 ; gain = 0.000
		INFO: Finished synth_1 successfully (elapsed time = 00:00:18).""")
	_BETWEEN_STEPS: ClassVar[str] = ("""\
		Design is defaulting to impl run constrset: constrs_1
		Design is defaulting to synth run part: xc7z030ffg676-1
		INFO: [Device 21-403] Loading part xc7z030ffg676-1
		Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00 . Memory (MB): peak = 647.754 ; gain = 0.000
		INFO: [Project 1-479] Netlist was created with Vivado 2024.2
		INFO: [Project 1-570] Preparing netlist for logic optimization
		INFO: [Opt 31-138] Pushed 0 inverter(s) to 0 load pin(s).
		Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00 . Memory (MB): peak = 775.246 ; gain = 0.000
		INFO: [Project 1-111] Unisim Transformation Summary:
		No Unisim elements were transformed.

		WARNING: [Vivado 12-1348] No Latch(s) found
		INFO: No latches found.
		Write ShapeDB Complete: Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.001 . Memory (MB): peak = 780.234 ; gain = 0.000""")
	_LAUNCH_IMPL_1: ClassVar[str] = ("""\
		[Tue Jul  7 10:00:11 2026] Launched impl_1...
		Run output will be captured here: C:/temp/OutputFilterBug/project_1/project_1.runs/impl_1/runme.log
		[Tue Jul  7 10:00:11 2026] Waiting for impl_1 to finish (timeout in 120 minutes)...


		*** Running vivado
				with args -log top.vdi -applog -m64 -product Vivado -messageDb vivado.pb -mode batch -source top.tcl -notrace

		""")
	_OPEN_CHECKPOINT: ClassVar[str] = ("""\
		source top.tcl -notrace
		Command: open_checkpoint C:/temp/OutputFilterBug/project_1/project_1.runs/impl_1/top.dcp
		INFO: [Device 21-403] Loading part xc7z030ffg676-1
		Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00 . Memory (MB): peak = 647.539 ; gain = 0.000
		INFO: [Project 1-479] Netlist was created with Vivado 2024.2
		INFO: [Project 1-570] Preparing netlist for logic optimization
		Read ShapeDB Complete: Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.001 . Memory (MB): peak = 751.297 ; gain = 0.000
		Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00 . Memory (MB): peak = 752.504 ; gain = 0.000
		INFO: [Project 1-111] Unisim Transformation Summary:
		No Unisim elements were transformed.

		INFO: [Project 1-604] Checkpoint was created with Vivado v2024.2 (64-bit) build 5239630
		open_checkpoint: Time (s): cpu = 00:00:06 ; elapsed = 00:00:09 . Memory (MB): peak = 760.539 ; gain = 462.125
		""")
	_WAIT_ON_IMPL_1: ClassVar[str] = ("""\
		[Tue Jul  7 10:01:37 2026] impl_1 finished
		wait_on_runs: Time (s): cpu = 00:00:01 ; elapsed = 00:01:25 . Memory (MB): peak = 780.234 ; gain = 0.000""")

	def test_VivadoPipedPreamble(self) -> None:
		print()
		report = StringIO(rpt := dedent(f"""{self._PIPED_PREAMBLE}
{self._INNER_SOURCE_TCL}
{self._POSTAMBLE}""")
		)

		print("%" * 80)
		print(rpt)
		print("%" * 80)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		preamble = processor.Preamble
		self.assertEqual(YearReleaseVersion(2024, 2), preamble.ToolVersion)
		self.assertEqual(datetime(2026, 7, 1, 23, 50, 26), preamble.StartDateTime)
		self.assertEqual(0, len(preamble.InfoMessages))
		self.assertEqual(0, len(preamble.WarningMessages))
		self.assertEqual(0, len(preamble.CriticalWarningMessages))
		self.assertEqual(0, len(preamble.ErrorMessages))

	def test_VivadoPipedPreambleWithLicense(self) -> None:
		print()
		report = StringIO(rpt := dedent(f"""{self._LICENSE_INFO}
{self._PIPED_PREAMBLE}
{self._INNER_SOURCE_TCL}
{self._POSTAMBLE}""")
		)

		print("%" * 80)
		print(rpt)
		print("%" * 80)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		preamble = processor.Preamble
		self.assertEqual(YearReleaseVersion(2024, 2), preamble.ToolVersion)
		self.assertEqual(datetime(2026, 7, 1, 23, 50, 26), preamble.StartDateTime)
		self.assertEqual(1, len(preamble.InfoMessages))
		self.assertEqual(0, len(preamble.WarningMessages))
		self.assertEqual(0, len(preamble.CriticalWarningMessages))
		self.assertEqual(0, len(preamble.ErrorMessages))

	def test_VivadoNestedPipedPreamble(self) -> None:
		print()
		report = StringIO(rpt := dedent(f"""{self._PIPED_PREAMBLE}
{self._OUTER_SOURCE_TCL}
{self._LAUNCH_SYNTH_1}
{self._PIPED_PREAMBLE}
{self._INNER_SOURCE_TCL}
{self._POSTAMBLE}
{self._WAIT_ON_SYNTH_1}
{self._BETWEEN_STEPS}
{self._LAUNCH_IMPL_1}
{self._PIPED_PREAMBLE}
{self._OPEN_CHECKPOINT}
{self._POSTAMBLE}
{self._WAIT_ON_IMPL_1}
{self._POSTAMBLE}""")
		)

		print("%" * 80)
		print(rpt)
		print("%" * 80)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		preamble = processor.Preamble
		self.assertEqual(YearReleaseVersion(2024, 2), preamble.ToolVersion)
		self.assertEqual(datetime(2026, 7, 1, 23, 50, 26), preamble.StartDateTime)
		self.assertEqual(0, len(preamble.InfoMessages))
		self.assertEqual(0, len(preamble.WarningMessages))
		self.assertEqual(0, len(preamble.CriticalWarningMessages))
		self.assertEqual(0, len(preamble.ErrorMessages))

		self.assertTrue(processor.HasNestedLaunches)
		self.assertEqual(2, len(processor.NestedLaunches))


	def test_LogfilePreamble(self) -> None:
		print()
		report = StringIO(rpt := dedent(f"""{self._LOGFILE_PREAMBLE}
{self._INNER_SOURCE_TCL}
{self._POSTAMBLE}""")
		)

		print("%" * 80)
		print(rpt)
		print("%" * 80)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		preamble = processor.Preamble
		self.assertEqual(YearReleaseVersion(2019, 1), preamble.ToolVersion)
		self.assertEqual(datetime(2025, 9, 2, 8, 44, 13), preamble.StartDateTime)
		self.assertEqual(0, len(preamble.InfoMessages))
		self.assertEqual(0, len(preamble.WarningMessages))
		self.assertEqual(0, len(preamble.CriticalWarningMessages))
		self.assertEqual(0, len(preamble.ErrorMessages))

	def test_LogfilePreambleWithLicense(self) -> None:
		print()
		report = StringIO(rpt := dedent(f"""{self._LICENSE_INFO}
{self._LOGFILE_PREAMBLE}
{self._INNER_SOURCE_TCL}
{self._POSTAMBLE}""")
		)

		print("%" * 80)
		print(rpt)
		print("%" * 80)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		preamble = processor.Preamble
		self.assertEqual(YearReleaseVersion(2019, 1), preamble.ToolVersion)
		self.assertEqual(datetime(2025, 9, 2, 8, 44, 13), preamble.StartDateTime)
		self.assertEqual(1, len(preamble.InfoMessages))
		self.assertEqual(0, len(preamble.WarningMessages))
		self.assertEqual(0, len(preamble.CriticalWarningMessages))
		self.assertEqual(0, len(preamble.ErrorMessages))
		self.assertIn(17, preamble.MessagesByID)
		self.assertIn(3922, preamble.MessagesByID[17])


class SynthDesign(TestCase):
	_PREAMBLE: ClassVar[str] = ("""\
			#-----------------------------------------------------------
			# Vivado v2019.1 (64-bit)
			# SW Build 2552052 on Fri May 24 14:49:42 MDT 2019
			# IP Build 2548770 on Fri May 24 18:01:18 MDT 2019
			# Start of session at: Tue Sep  2 08:44:13 2025
			#-----------------------------------------------------------""")
	_POSTAMBLE: ClassVar[str] = ("""\
			INFO: [Common 17-206] Exiting Vivado at Tue Sep  2 08:44:45 2025...""")
	_SYNTHESIS_START: ClassVar[str] = ("""\
			Command: synth_design -top system_top -part xc7z015clg485-2
			Starting synth_design""")
	_SYNTHESIS_FINISH: ClassVar[str] = ("""\
			66 Infos, 111 Warnings, 0 Critical Warnings and 0 Errors encountered.
			synth_design completed successfully
			synth_design: Time (s): cpu = 00:00:24 ; elapsed = 00:00:26 . Memory (MB): peak = 1050.637 ; gain = 665.508
			Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00 . Memory (MB): peak = 1050.637 ; gain = 0.000
			WARNING: [Constraints 18-5210] No constraints selected for write.
			Resolution: This message can indicate that there are no constraints for the design, or it can indicate that the used_in flags are set such that the constraints are ignored. This later case is used when running synth_design to not write synthesis constraints to the resulting checkpoint. Instead, project constraints are read when the synthesized design is opened.
			INFO: [Common 17-1381] 1-The checkpoint 'C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/synth_1/system_top.dcp' has been generated.
			INFO: [runtcl-4] 2-Executing : report_utilization -file system_top_utilization_synth.rpt -pb system_top_utilization_synth.pb""")
	_SOURCE_TCL: ClassVar[str] = ("""\
			source system_top.tcl -notrace""")

	def test_SynthesisLogfile(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._SYNTHESIS_START}
{self._SYNTHESIS_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(YearReleaseVersion(2019, 1), processor.Preamble.ToolVersion)
		self.assertEqual(datetime(2025, 9, 2, 8, 44, 13), processor.Preamble.StartDateTime)
		self.assertEqual(32, processor.Duration)
		self.assertEqual(3, len(processor.InfoMessages))
		self.assertEqual(1, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertIn(Synth_Design, processor)
		synthDesign = processor[Synth_Design]
		self.assertEqual(0, len(synthDesign.InfoMessages))
		self.assertEqual(0, len(synthDesign.WarningMessages))
		self.assertEqual(0, len(synthDesign.CriticalWarningMessages))
		self.assertEqual(0, len(synthDesign.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_RTLElaboration(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._SYNTHESIS_START}
			Attempting to get a license for feature 'Synthesis' and/or device 'xc7z015'
			INFO: [Common 17-349] 1-Got license for feature 'Synthesis' and/or device 'xc7z015'
			INFO: [Device 21-403] 2-Loading part xc7z015clg485-2
			INFO: 3-Launching helper process for spawning children vivado processes
			INFO: 4-Helper process launched with PID 29056
			---------------------------------------------------------------------------------
			Starting RTL Elaboration : Time (s): cpu = 00:00:03 ; elapsed = 00:00:03 . Memory (MB): peak = 847.230 ; gain = 176.500
			---------------------------------------------------------------------------------
			INFO: [Synth 8-638] 5-synthesizing module 'system_top' [C:/Users/tgomes/git/2019_1/src/system_top_PE1.vhd:257]
			INFO: [Common 17-14] 6-Message 'Synth 8-3331' appears 100 times and further instances of the messages will be disabled. Use the Tcl command set_msg_config to change the current settings.
			---------------------------------------------------------------------------------
			Finished RTL Elaboration : Time (s): cpu = 00:00:04 ; elapsed = 00:00:04 . Memory (MB): peak = 917.641 ; gain = 246.910
			---------------------------------------------------------------------------------
{self._SYNTHESIS_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(9, len(processor.InfoMessages))
		self.assertEqual(1, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertIn(Synth_Design, processor)
		synthDesign = processor[Synth_Design]
		self.assertEqual(6, len(synthDesign.InfoMessages))
		self.assertEqual(0, len(synthDesign.WarningMessages))
		self.assertEqual(0, len(synthDesign.CriticalWarningMessages))
		self.assertEqual(0, len(synthDesign.ErrorMessages))

		self.assertIn(_SynthDesign.RTLElaboration, synthDesign)
		rtlElaboration = synthDesign[_SynthDesign.RTLElaboration]
		self.assertEqual(2, len(rtlElaboration.InfoMessages))
		self.assertEqual(0, len(rtlElaboration.WarningMessages))
		self.assertEqual(0, len(rtlElaboration.CriticalWarningMessages))
		self.assertEqual(0, len(rtlElaboration.ErrorMessages))
		# TODO: check duration / elapsed time
		# TODO: check memory consumption

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_LoadingPart(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._SYNTHESIS_START}
			Attempting to get a license for feature 'Synthesis' and/or device 'xc7z015'
			INFO: [Common 17-349] 1-Got license for feature 'Synthesis' and/or device 'xc7z015'
			INFO: [Device 21-403] 2-Loading part xc7z015clg485-2
			INFO: 3-Launching helper process for spawning children vivado processes
			INFO: 4-Helper process launched with PID 29056
			---------------------------------------------------------------------------------
			Start Loading Part and Timing Information
			---------------------------------------------------------------------------------
			Loading part: xc7z015clg485-2
			---------------------------------------------------------------------------------
			Finished Loading Part and Timing Information : Time (s): cpu = 00:00:09 ; elapsed = 00:00:09 . Memory (MB): peak = 1006.605 ; gain = 335.875
			---------------------------------------------------------------------------------
{self._SYNTHESIS_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(7, len(processor.InfoMessages))
		self.assertEqual(1, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertIn(Synth_Design, processor)
		synthDesign = processor[Synth_Design]
		self.assertEqual(4, len(synthDesign.InfoMessages))
		self.assertEqual(0, len(synthDesign.WarningMessages))
		self.assertEqual(0, len(synthDesign.CriticalWarningMessages))
		self.assertEqual(0, len(synthDesign.ErrorMessages))

		self.assertIn(_SynthDesign.LoadingPart, synthDesign)
		loadingPart = synthDesign[_SynthDesign.LoadingPart]
		self.assertEqual(0, len(loadingPart.InfoMessages))
		self.assertEqual(0, len(loadingPart.WarningMessages))
		self.assertEqual(0, len(loadingPart.CriticalWarningMessages))
		self.assertEqual(0, len(loadingPart.ErrorMessages))
		self.assertEqual("xc7z015clg485-2", loadingPart.Part)

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_RTLComponentStatistics(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._SYNTHESIS_START}
			Attempting to get a license for feature 'Synthesis' and/or device 'xc7z015'
			INFO: [Common 17-349] 1-Got license for feature 'Synthesis' and/or device 'xc7z015'
			INFO: [Device 21-403] 2-Loading part xc7z015clg485-2
			INFO: 3-Launching helper process for spawning children vivado processes
			INFO: 4-Helper process launched with PID 29056
			---------------------------------------------------------------------------------
			Start RTL Component Statistics
			---------------------------------------------------------------------------------
			Detailed RTL Component Info :
			+---Registers :
												8 Bit    Registers := 1
			---------------------------------------------------------------------------------
			Finished RTL Component Statistics
			---------------------------------------------------------------------------------
{self._SYNTHESIS_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(7, len(processor.InfoMessages))
		self.assertEqual(1, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertIn(Synth_Design, processor)
		synthDesign = processor[Synth_Design]
		self.assertEqual(4, len(synthDesign.InfoMessages))
		self.assertEqual(0, len(synthDesign.WarningMessages))
		self.assertEqual(0, len(synthDesign.CriticalWarningMessages))
		self.assertEqual(0, len(synthDesign.ErrorMessages))

		self.assertIn(_SynthDesign.RTLComponentStatistics, synthDesign)
		rtlComponentStatistics = synthDesign[_SynthDesign.RTLComponentStatistics]
		self.assertEqual(0, len(rtlComponentStatistics.InfoMessages))
		self.assertEqual(0, len(rtlComponentStatistics.WarningMessages))
		self.assertEqual(0, len(rtlComponentStatistics.CriticalWarningMessages))
		self.assertEqual(0, len(rtlComponentStatistics.ErrorMessages))
		# TODO: nested checks?

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_IOInsertion(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._SYNTHESIS_START}
			Attempting to get a license for feature 'Synthesis' and/or device 'xc7z015'
			INFO: [Common 17-349] 1-Got license for feature 'Synthesis' and/or device 'xc7z015'
			INFO: [Device 21-403] 2-Loading part xc7z015clg485-2
			INFO: 3-Launching helper process for spawning children vivado processes
			INFO: 4-Helper process launched with PID 29056
			---------------------------------------------------------------------------------
			Start IO Insertion
			---------------------------------------------------------------------------------
			---------------------------------------------------------------------------------
			Start Flattening Before IO Insertion
			---------------------------------------------------------------------------------
			---------------------------------------------------------------------------------
			Finished Flattening Before IO Insertion
			---------------------------------------------------------------------------------
			---------------------------------------------------------------------------------
			Start Final Netlist Cleanup
			---------------------------------------------------------------------------------
			---------------------------------------------------------------------------------
			Finished Final Netlist Cleanup
			---------------------------------------------------------------------------------
			---------------------------------------------------------------------------------
			Finished IO Insertion : Time (s): cpu = 00:00:19 ; elapsed = 00:00:19 . Memory (MB): peak = 1034.773 ; gain = 364.043
			---------------------------------------------------------------------------------
{self._SYNTHESIS_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(7, len(processor.InfoMessages))
		self.assertEqual(1, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertIn(Synth_Design, processor)
		synthDesign = processor[Synth_Design]
		self.assertEqual(4, len(synthDesign.InfoMessages))
		self.assertEqual(0, len(synthDesign.WarningMessages))
		self.assertEqual(0, len(synthDesign.CriticalWarningMessages))
		self.assertEqual(0, len(synthDesign.ErrorMessages))

		self.assertIn(_SynthDesign.IOInsertion, synthDesign)
		ioInsertion = synthDesign[_SynthDesign.IOInsertion]
		self.assertEqual(0, len(ioInsertion.InfoMessages))
		self.assertEqual(0, len(ioInsertion.WarningMessages))
		self.assertEqual(0, len(ioInsertion.CriticalWarningMessages))
		self.assertEqual(0, len(ioInsertion.ErrorMessages))

		self.assertIn(_SynthDesign.FlatteningBeforeIOInsertion, ioInsertion)
		flatteningBeforeIOInsertion = ioInsertion[_SynthDesign.FlatteningBeforeIOInsertion]
		self.assertEqual(0, len(flatteningBeforeIOInsertion.InfoMessages))
		self.assertEqual(0, len(flatteningBeforeIOInsertion.WarningMessages))
		self.assertEqual(0, len(flatteningBeforeIOInsertion.CriticalWarningMessages))
		self.assertEqual(0, len(flatteningBeforeIOInsertion.ErrorMessages))

		self.assertIn(_SynthDesign.FinalNetlistCleanup, ioInsertion)
		finalNetlistCleanup = ioInsertion[_SynthDesign.FinalNetlistCleanup]
		self.assertEqual(0, len(finalNetlistCleanup.InfoMessages))
		self.assertEqual(0, len(finalNetlistCleanup.WarningMessages))
		self.assertEqual(0, len(finalNetlistCleanup.CriticalWarningMessages))
		self.assertEqual(0, len(finalNetlistCleanup.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_WritingSynthesisReport(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._SYNTHESIS_START}
			Attempting to get a license for feature 'Synthesis' and/or device 'xc7z015'
			INFO: [Common 17-349] 1-Got license for feature 'Synthesis' and/or device 'xc7z015'
			INFO: [Device 21-403] 2-Loading part xc7z015clg485-2
			INFO: 3-Launching helper process for spawning children vivado processes
			INFO: 4-Helper process launched with PID 29056
			---------------------------------------------------------------------------------
			Start Writing Synthesis Report
			---------------------------------------------------------------------------------

			Report BlackBoxes:
			+------+----------------------------------+----------+
			|      |BlackBox name                     |Instances |
			+------+----------------------------------+----------+
			|1     |MercuryZX5_xbar_0                 |         1|
			|2     |MercuryZX5_auto_pc_0              |         1|
			|3     |MercuryZX5_auto_pc_1              |         1|
			|4     |MercuryZX5_auto_pc_2              |         1|
			|5     |MercuryZX5_auto_pc_3              |         1|
			|6     |MercuryZX5_axi_bram_ctrl_0_0      |         1|
			|7     |MercuryZX5_axi_gpio_0_0           |         1|
			|8     |MercuryZX5_axi_gpio_1_0           |         1|
			|9     |MercuryZX5_blk_mem_gen_0_0        |         1|
			|10    |MercuryZX5_blk_mem_gen_0_1        |         1|
			|11    |MercuryZX5_proc_sys_reset_0       |         1|
			|12    |MercuryZX5_processing_system7_1_0 |         1|
			|13    |MercuryZX5_xadc_wiz_0_0           |         1|
			|14    |MercuryZX5_xbip_dsp48_macro_0_0   |         1|
			+------+----------------------------------+----------+

			Report Cell Usage:
			+------+----------------------------------+------+
			|      |Cell                              |Count |
			+------+----------------------------------+------+
			|1     |MercuryZX5_auto_pc_0              |     1|
			|2     |MercuryZX5_auto_pc_1              |     1|
			|3     |MercuryZX5_auto_pc_2              |     1|
			|4     |MercuryZX5_auto_pc_3              |     1|
			|5     |MercuryZX5_axi_bram_ctrl_0_0      |     1|
			|6     |MercuryZX5_axi_gpio_0_0           |     1|
			|7     |MercuryZX5_axi_gpio_1_0           |     1|
			|8     |MercuryZX5_blk_mem_gen_0_0        |     1|
			|9     |MercuryZX5_blk_mem_gen_0_1        |     1|
			|10    |MercuryZX5_proc_sys_reset_0       |     1|
			|11    |MercuryZX5_processing_system7_1_0 |     1|
			|12    |MercuryZX5_xadc_wiz_0_0           |     1|
			|13    |MercuryZX5_xbar_0                 |     1|
			|14    |MercuryZX5_xbip_dsp48_macro_0_0   |     1|
			|15    |CARRY4                            |     6|
			|16    |LUT1                              |     3|
			|17    |LUT2                              |     1|
			|18    |FDCE                              |     8|
			|19    |FDRE                              |    24|
			|20    |IOBUF                             |     2|
			|21    |OBUF                              |     1|
			+------+----------------------------------+------+

			Report Instance Areas:
			+------+------------------------------------+---------------------------------------------+------+
			|      |Instance                            |Module                                       |Cells |
			+------+------------------------------------+---------------------------------------------+------+
			|1     |top                                 |                                             |  2151|
			|2     |  i_system                          |MercuryZX5                                   |  2106|
			|3     |    processing_system7_1_axi_periph |MercuryZX5_processing_system7_1_axi_periph_0 |  1435|
			|4     |      m00_couplers                  |m00_couplers_imp_1ITI1HA                     |   153|
			|5     |      m01_couplers                  |m01_couplers_imp_18NS0C8                     |   153|
			|6     |      m03_couplers                  |m03_couplers_imp_TH52K4                      |   153|
			|7     |      s00_couplers                  |s00_couplers_imp_1AKJ1HB                     |   254|
			+------+------------------------------------+---------------------------------------------+------+
			---------------------------------------------------------------------------------
			Finished Writing Synthesis Report : Time (s): cpu = 00:00:19 ; elapsed = 00:00:19 . Memory (MB): peak = 1034.773 ; gain = 364.043
			---------------------------------------------------------------------------------
{self._SYNTHESIS_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(7, len(processor.InfoMessages))
		self.assertEqual(1, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertIn(Synth_Design, processor)
		synthDesign = processor[Synth_Design]
		self.assertEqual(4, len(synthDesign.InfoMessages))
		self.assertEqual(0, len(synthDesign.WarningMessages))
		self.assertEqual(0, len(synthDesign.CriticalWarningMessages))
		self.assertEqual(0, len(synthDesign.ErrorMessages))

		self.assertIn(_SynthDesign.WritingSynthesisReport, synthDesign)
		writingSynthesisReport = synthDesign[_SynthDesign.WritingSynthesisReport]
		self.assertEqual(0, len(writingSynthesisReport.InfoMessages))
		self.assertEqual(0, len(writingSynthesisReport.WarningMessages))
		self.assertEqual(0, len(writingSynthesisReport.CriticalWarningMessages))
		self.assertEqual(0, len(writingSynthesisReport.ErrorMessages))

		self.assertEqual(14, len(writingSynthesisReport.Blackboxes))

		self.assertEqual(21, len(writingSynthesisReport.Cells))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)
