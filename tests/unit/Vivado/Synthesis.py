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

from pyTooling.Versioning import YearReleaseVersion
from pyTooling.Warning    import WarningCollector

from pyEDAA.OutputFilter.Xilinx import Processor, Synth_Design, VivadoLine, timestampIterator
from pyEDAA.OutputFilter.Xilinx import SynthesizeDesign as _SynthDesign


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


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
		self.assertEqual(datetime(2025, 9, 2, 8, 44, 13), processor.Preamble.StartDatetime)
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
