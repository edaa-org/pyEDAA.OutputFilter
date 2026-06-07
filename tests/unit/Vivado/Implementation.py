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
"""Unit tests for Vivado implementation log files."""
from datetime import datetime
from io       import StringIO
from textwrap import dedent
from typing   import ClassVar
from unittest import TestCase as TestCase

from pyTooling.Versioning import YearReleaseVersion
from pyTooling.Warning    import WarningCollector

from pyEDAA.OutputFilter.Xilinx import VivadoLine, Processor, timestampIterator
from pyEDAA.OutputFilter.Xilinx import Link_Design, Opt_Design, Place_Design, Route_Design, Report_DRC
from pyEDAA.OutputFilter.Xilinx import OptimizeDesign as _OptDesign


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class LinkDesign(TestCase):
	_PREAMBLE: ClassVar[str] = """\
			#-----------------------------------------------------------
			# Vivado v2019.1 (64-bit)
			# SW Build 2552052 on Fri May 24 14:49:42 MDT 2019
			# IP Build 2548770 on Fri May 24 18:01:18 MDT 2019
			# Start of session at: Tue Sep  2 08:44:52 2025
			# Process ID: 10540
			# Current directory: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1
			# Command line: vivado.exe -log system_top.vdi -applog -product Vivado -messageDb vivado.pb -mode batch -source system_top.tcl -notrace
			# Log file: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1/system_top.vdi
			# Journal file: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1\\vivado.jou
			#-----------------------------------------------------------"""
	_SOURCE_TCL: ClassVar[str] = """\
			source system_top.tcl -notrace"""
	_LINKDESIGN_START: ClassVar[str] = """\
			INFO: [IP_Flow 19-234] 1-Refreshing IP repositories
			INFO: [IP_Flow 19-1704] 2-No user IP repositories specified
			INFO: [IP_Flow 19-2313] 3-Loaded Vivado IP repository 'W:/Xilinx/Vivado/2019.1/data/ip'.
			Command: link_design -top system_top -part xc7z015clg485-2
			Design is defaulting to srcset: sources_1
			Design is defaulting to constrset: constrs_1
			INFO: [Device 21-403] 4-Loading part xc7z015clg485-2
			INFO: [Project 1-454] 5-Reading design checkpoint 'c:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.srcs/sources_1/bd/MercuryZX5/ip/MercuryZX5_axi_bram_ctrl_0_0/MercuryZX5_axi_bram_ctrl_0_0.dcp' for cell 'i_system/axi_bram_ctrl_0'"""
	_LINKDESIGN_FINISH: ClassVar[str] = """\
			Parsing XDC File [C:/Users/tgomes/git/2019_1/src/MercuryZX5_PE1_15.xdc]
			Finished Parsing XDC File [C:/Users/tgomes/git/2019_1/src/MercuryZX5_PE1_15.xdc]
			INFO: [Opt 31-138] 6-Pushed 0 inverter(s) to 0 load pin(s).
			Generating merged BMM file for the design top 'system_top'...
			Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.003 . Memory (MB): peak = 854.375 ; gain = 0.000
			INFO: [Project 1-111] 7-Unisim Transformation Summary:
				A total of 2 instances were transformed.
				IOBUF => IOBUF (IBUF, OBUFT): 2 instances

			24 Infos, 0 Warnings, 0 Critical Warnings and 0 Errors encountered.
			link_design completed successfully
			link_design: Time (s): cpu = 00:00:10 ; elapsed = 00:00:15 . Memory (MB): peak = 854.375 ; gain = 448.512"""
	_POSTAMBLE: ClassVar[str] = """\
			INFO: [Common 17-206] Exiting Vivado at Tue Sep  2 08:46:23 2025..."""

	def test_ImplementationLogfile(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._LINKDESIGN_START}
{self._LINKDESIGN_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(YearReleaseVersion(2019, 1), processor.Preamble.ToolVersion)
		self.assertEqual(datetime(2025, 9, 2, 8, 44, 52), processor.Preamble.StartDatetime)
		self.assertEqual(91, processor.Duration)
		self.assertEqual(8, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertIn(Link_Design, processor)
		linkDesign = processor[Link_Design]
		self.assertEqual(4, len(linkDesign.InfoMessages))
		self.assertEqual(0, len(linkDesign.WarningMessages))
		self.assertEqual(0, len(linkDesign.CriticalWarningMessages))
		self.assertEqual(0, len(linkDesign.ErrorMessages))

		# TODO: check collected XDC files.

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)


class OptimizeDesign(TestCase):
	_PREAMBLE: ClassVar[str] = """\
			#-----------------------------------------------------------
			# Vivado v2019.1 (64-bit)
			# SW Build 2552052 on Fri May 24 14:49:42 MDT 2019
			# IP Build 2548770 on Fri May 24 18:01:18 MDT 2019
			# Start of session at: Tue Sep  2 08:44:52 2025
			# Process ID: 10540
			# Current directory: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1
			# Command line: vivado.exe -log system_top.vdi -applog -product Vivado -messageDb vivado.pb -mode batch -source system_top.tcl -notrace
			# Log file: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1/system_top.vdi
			# Journal file: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1\\vivado.jou
			#-----------------------------------------------------------"""
	_SOURCE_TCL: ClassVar[str] = """\
			source system_top.tcl -notrace"""
	_OPTDESIGN_START: ClassVar[str] = """\
			Command: opt_design
			Attempting to get a license for feature 'Implementation' and/or device 'xc7z015'
			INFO: [Common 17-349] 1-Got license for feature 'Implementation' and/or device 'xc7z015'
			Running DRC as a precondition to command opt_design"""
	_OPTDESIGN_FINISH: ClassVar[str] = """\
			INFO: [Common 17-83] 2-Releasing license: Implementation
			48 Infos, 0 Warnings, 0 Critical Warnings and 0 Errors encountered.
			opt_design completed successfully
			opt_design: Time (s): cpu = 00:00:16 ; elapsed = 00:00:15 . Memory (MB): peak = 1652.383 ; gain = 798.008
			Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.003 . Memory (MB): peak = 1652.383 ; gain = 0.000
			INFO: [Timing 38-480] 3-Writing timing data to binary archive.
			Writing placer database...
			Writing XDEF routing.
			Writing XDEF routing logical nets.
			Writing XDEF routing special nets.
			Write XDEF Complete: Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.066 . Memory (MB): peak = 1652.383 ; gain = 0.000
			INFO: [Common 17-1381] 4-The checkpoint 'C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1/system_top_opt.dcp' has been generated.
			INFO: [runtcl-4] 5-Executing : report_drc -file system_top_drc_opted.rpt -pb system_top_drc_opted.pb -rpx system_top_drc_opted.rpx
			Command: report_drc -file system_top_drc_opted.rpt -pb system_top_drc_opted.pb -rpx system_top_drc_opted.rpx
			INFO: [IP_Flow 19-1839] 6-IP Catalog is up to date.
			INFO: [DRC 23-27] 7-Running DRC with 2 threads
			INFO: [Coretcl 2-168] 8-The results of DRC are in file C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1/system_top_drc_opted.rpt.
			report_drc completed successfully"""
	_POSTAMBLE: ClassVar[str] = """\
			INFO: [Common 17-206] 9-Exiting Vivado at Tue Sep  2 08:46:23 2025..."""

	def test_ImplementationLogfile(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._OPTDESIGN_START}
{self._OPTDESIGN_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(9, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertIn(Opt_Design, processor)
		optimizeDesign = processor[Opt_Design]
		self.assertEqual(2, len(optimizeDesign.InfoMessages))
		self.assertEqual(0, len(optimizeDesign.WarningMessages))
		self.assertEqual(0, len(optimizeDesign.CriticalWarningMessages))
		self.assertEqual(0, len(optimizeDesign.ErrorMessages))

		self.assertIn(Report_DRC, processor)
		reportDRC = processor[Report_DRC]
		self.assertEqual(3, len(reportDRC.InfoMessages))
		self.assertEqual(0, len(reportDRC.WarningMessages))
		self.assertEqual(0, len(reportDRC.CriticalWarningMessages))
		self.assertEqual(0, len(reportDRC.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_DRCTask(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._OPTDESIGN_START}
			Starting DRC Task
			INFO: [DRC 23-27] Running DRC with 2 threads
			INFO: [Project 1-461] DRC finished with 0 Errors
			INFO: [Project 1-462] Please refer to the DRC report (report_drc) for more information.

			Time (s): cpu = 00:00:01 ; elapsed = 00:00:00.707 . Memory (MB): peak = 877.328 ; gain = 22.953

{self._OPTDESIGN_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		optimizeDesign = processor[Opt_Design]

		self.assertIn(_OptDesign.DRCTask, optimizeDesign)
		drcTask = optimizeDesign[_OptDesign.DRCTask]
		self.assertEqual(3, len(drcTask.InfoMessages))
		self.assertEqual(0, len(drcTask.WarningMessages))
		self.assertEqual(0, len(drcTask.CriticalWarningMessages))
		self.assertEqual(0, len(drcTask.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_CacheTimingInformationTask(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._OPTDESIGN_START}
			Starting Cache Timing Information Task
			INFO: [Timing 38-35] Done setting XDC timing constraints.
			Ending Cache Timing Information Task | Checksum: 19fe8cb97

			Time (s): cpu = 00:00:09 ; elapsed = 00:00:09 . Memory (MB): peak = 1370.594 ; gain = 493.266

{self._OPTDESIGN_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		optimizeDesign = processor[Opt_Design]

		self.assertIn(_OptDesign.CacheTimingInformationTask, optimizeDesign)
		cacheTimingInformationTask = optimizeDesign[_OptDesign.CacheTimingInformationTask]
		self.assertEqual(1, len(cacheTimingInformationTask.InfoMessages))
		self.assertEqual(0, len(cacheTimingInformationTask.WarningMessages))
		self.assertEqual(0, len(cacheTimingInformationTask.CriticalWarningMessages))
		self.assertEqual(0, len(cacheTimingInformationTask.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_LogicOptimizationTask(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._OPTDESIGN_START}
			Starting Logic Optimization Task

			Phase 1 Retarget
			INFO: [Opt 31-138] 1-Pushed 1 inverter(s) to 4 load pin(s).
			INFO: [Opt 31-49] 2-Retargeted 0 cell(s).
			Phase 1 Retarget | Checksum: 160bb552c

			Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.368 . Memory (MB): peak = 1515.172 ; gain = 0.000
			INFO: [Opt 31-389] 3-Phase Retarget created 20 cells and removed 99 cells
			INFO: [Opt 31-1021] 4-In phase Retarget, 1 netlist objects are constrained preventing optimization. Please run opt_design with -debug_log to get more detail.

			Phase 2 Constant propagation
			INFO: [Opt 31-138] 5-Pushed 1 inverter(s) to 2 load pin(s).
			Phase 2 Constant propagation | Checksum: 1cf5a7919

			Time (s): cpu = 00:00:01 ; elapsed = 00:00:00.603 . Memory (MB): peak = 1515.172 ; gain = 0.000
			INFO: [Opt 31-389] 6-Phase Constant propagation created 90 cells and removed 462 cells

			Phase 3 Sweep
			Phase 3 Sweep | Checksum: 10a3ccb0f

			Time (s): cpu = 00:00:02 ; elapsed = 00:00:02 . Memory (MB): peak = 1515.172 ; gain = 0.000
			INFO: [Opt 31-389] 7-Phase Sweep created 0 cells and removed 778 cells

			Phase 4 BUFG optimization
			Phase 4 BUFG optimization | Checksum: 10a3ccb0f

			Time (s): cpu = 00:00:02 ; elapsed = 00:00:02 . Memory (MB): peak = 1515.172 ; gain = 0.000
			INFO: [Opt 31-662] 8-Phase BUFG optimization created 0 cells of which 0 are BUFGs and removed 0 cells.

			Phase 5 Shift Register Optimization
			INFO: [Opt 31-1064] 9-SRL Remap converted 0 SRLs to 0 registers and converted 0 registers of register chains to 0 SRLs
			Phase 5 Shift Register Optimization | Checksum: 10a3ccb0f

			Time (s): cpu = 00:00:02 ; elapsed = 00:00:02 . Memory (MB): peak = 1515.172 ; gain = 0.000
			INFO: [Opt 31-389] 10-Phase Shift Register Optimization created 0 cells and removed 0 cells

			Phase 6 Post Processing Netlist
			Phase 6 Post Processing Netlist | Checksum: 12e9e2477

			Time (s): cpu = 00:00:02 ; elapsed = 00:00:02 . Memory (MB): peak = 1515.172 ; gain = 0.000
			INFO: [Opt 31-389] 11-Phase Post Processing Netlist created 0 cells and removed 1 cells
			Opt_design Change Summary
			=========================


			-------------------------------------------------------------------------------------------------------------------------
			|  Phase                        |  #Cells created  |  #Cells Removed  |  #Constrained objects preventing optimizations  |
			-------------------------------------------------------------------------------------------------------------------------
			|  Retarget                     |              20  |              99  |                                              1  |
			|  Constant propagation         |              90  |             462  |                                              0  |
			|  Sweep                        |               0  |             778  |                                              0  |
			|  BUFG optimization            |               0  |               0  |                                              0  |
			|  Shift Register Optimization  |               0  |               0  |                                              0  |
			|  Post Processing Netlist      |               0  |               1  |                                              0  |
			-------------------------------------------------------------------------------------------------------------------------



			#Starting Connectivity Check Task

			#Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.010 . Memory (MB): peak = 1515.172 ; gain = 0.000
			Ending Logic Optimization Task | Checksum: a7afd030

			Time (s): cpu = 00:00:02 ; elapsed = 00:00:02 . Memory (MB): peak = 1515.172 ; gain = 0.000

{self._OPTDESIGN_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(20, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		optimizeDesign = processor[Opt_Design]
		self.assertEqual(13, len(optimizeDesign.InfoMessages))
		self.assertEqual(0, len(optimizeDesign.WarningMessages))
		self.assertEqual(0, len(optimizeDesign.CriticalWarningMessages))
		self.assertEqual(0, len(optimizeDesign.ErrorMessages))

		self.assertIn(_OptDesign.LogicOptimizationTask, optimizeDesign)
		logicOptimizationTask = optimizeDesign[_OptDesign.LogicOptimizationTask]
		self.assertEqual(11, len(logicOptimizationTask.InfoMessages))
		self.assertEqual(0, len(logicOptimizationTask.WarningMessages))
		self.assertEqual(0, len(logicOptimizationTask.CriticalWarningMessages))
		self.assertEqual(0, len(logicOptimizationTask.ErrorMessages))

		self.assertIn(_OptDesign.Phase_Retarget, logicOptimizationTask)
		retarget = logicOptimizationTask[_OptDesign.Phase_Retarget]
		self.assertEqual(2, len(retarget.InfoMessages))
		self.assertEqual(0, len(retarget.WarningMessages))
		self.assertEqual(0, len(retarget.CriticalWarningMessages))
		self.assertEqual(0, len(retarget.ErrorMessages))

		self.assertIn(_OptDesign.Phase_ConstantPropagation, logicOptimizationTask)
		constantPropagation = logicOptimizationTask[_OptDesign.Phase_ConstantPropagation]
		self.assertEqual(1, len(constantPropagation.InfoMessages))
		self.assertEqual(0, len(constantPropagation.WarningMessages))
		self.assertEqual(0, len(constantPropagation.CriticalWarningMessages))
		self.assertEqual(0, len(constantPropagation.ErrorMessages))

		self.assertIn(_OptDesign.Phase_Sweep, logicOptimizationTask)
		sweep = logicOptimizationTask[_OptDesign.Phase_Sweep]
		self.assertEqual(0, len(sweep.InfoMessages))
		self.assertEqual(0, len(sweep.WarningMessages))
		self.assertEqual(0, len(sweep.CriticalWarningMessages))
		self.assertEqual(0, len(sweep.ErrorMessages))

		self.assertIn(_OptDesign.Phase_BUFGOptimization, logicOptimizationTask)
		bufgOptimization = logicOptimizationTask[_OptDesign.Phase_BUFGOptimization]
		self.assertEqual(0, len(bufgOptimization.InfoMessages))
		self.assertEqual(0, len(bufgOptimization.WarningMessages))
		self.assertEqual(0, len(bufgOptimization.CriticalWarningMessages))
		self.assertEqual(0, len(bufgOptimization.ErrorMessages))

		self.assertIn(_OptDesign.Phase_ShiftRegisterOptimization, logicOptimizationTask)
		shiftRegisterOptimization = logicOptimizationTask[_OptDesign.Phase_ShiftRegisterOptimization]
		self.assertEqual(1, len(shiftRegisterOptimization.InfoMessages))
		self.assertEqual(0, len(shiftRegisterOptimization.WarningMessages))
		self.assertEqual(0, len(shiftRegisterOptimization.CriticalWarningMessages))
		self.assertEqual(0, len(shiftRegisterOptimization.ErrorMessages))

		self.assertIn(_OptDesign.Phase_PostProcessingNetlist, logicOptimizationTask)
		postProcessingNetlist = logicOptimizationTask[_OptDesign.Phase_PostProcessingNetlist]
		self.assertEqual(0, len(postProcessingNetlist.InfoMessages))
		self.assertEqual(0, len(postProcessingNetlist.WarningMessages))
		self.assertEqual(0, len(postProcessingNetlist.CriticalWarningMessages))
		self.assertEqual(0, len(postProcessingNetlist.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_PowerOptimizationTask(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._OPTDESIGN_START}
			Starting Power Optimization Task
			INFO: [Pwropt 34-132] Skipping clock gating for clocks with a period < 2.00 ns.
			INFO: [Pwropt 34-9] Applying IDT optimizations ...
			INFO: [Pwropt 34-10] Applying ODC optimizations ...
			INFO: [Timing 38-35] Done setting XDC timing constraints.
			INFO: [Physopt 32-619] Estimated Timing Summary | WNS=5.346 | TNS=0.000 |
			Running Vector-less Activity Propagation...

			Finished Running Vector-less Activity Propagation


			Starting PowerOpt Patch Enables Task
			INFO: [Pwropt 34-162] WRITE_MODE attribute of 0 BRAM(s) out of a total of 2 has been updated to save power. Run report_power_opt to get a complete listing of the BRAMs updated.
			INFO: [Pwropt 34-201] Structural ODC has moved 0 WE to EN ports
			Number of BRAM Ports augmented: 0 newly gated: 0 Total Ports: 4
			Ending PowerOpt Patch Enables Task | Checksum: a7afd030

			Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.024 . Memory (MB): peak = 1652.383 ; gain = 0.000
			Ending Power Optimization Task | Checksum: a7afd030

			Time (s): cpu = 00:00:03 ; elapsed = 00:00:02 . Memory (MB): peak = 1652.383 ; gain = 137.211

{self._OPTDESIGN_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		optimizeDesign = processor[Opt_Design]

		self.assertIn(_OptDesign.PowerOptimizationTask, optimizeDesign)
		powerOptimizationTask = optimizeDesign[_OptDesign.PowerOptimizationTask]
		self.assertEqual(7, len(powerOptimizationTask.InfoMessages))
		self.assertEqual(0, len(powerOptimizationTask.WarningMessages))
		self.assertEqual(0, len(powerOptimizationTask.CriticalWarningMessages))
		self.assertEqual(0, len(powerOptimizationTask.ErrorMessages))

		self.assertIn(_OptDesign.PowerOptPatchEnablesTask, powerOptimizationTask)
		powerOptPatchEnablesTask = powerOptimizationTask[_OptDesign.PowerOptPatchEnablesTask]
		self.assertEqual(2, len(powerOptPatchEnablesTask.InfoMessages))
		self.assertEqual(0, len(powerOptPatchEnablesTask.WarningMessages))
		self.assertEqual(0, len(powerOptPatchEnablesTask.CriticalWarningMessages))
		self.assertEqual(0, len(powerOptPatchEnablesTask.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_FinalCleanupTask(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._OPTDESIGN_START}
			Starting Final Cleanup Task
			Ending Final Cleanup Task | Checksum: a7afd030

			Time (s): cpu = 00:00:00 ; elapsed = 00:00:00 . Memory (MB): peak = 1652.383 ; gain = 0.000

{self._OPTDESIGN_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		optimizeDesign = processor[Opt_Design]

		self.assertIn(_OptDesign.FinalCleanupTask, optimizeDesign)
		finalCleanupTask = optimizeDesign[_OptDesign.FinalCleanupTask]
		self.assertEqual(0, len(finalCleanupTask.InfoMessages))
		self.assertEqual(0, len(finalCleanupTask.WarningMessages))
		self.assertEqual(0, len(finalCleanupTask.CriticalWarningMessages))
		self.assertEqual(0, len(finalCleanupTask.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)

	def test_NetlistObfuscationTask(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._OPTDESIGN_START}
			Starting Netlist Obfuscation Task
			Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.003 . Memory (MB): peak = 1652.383 ; gain = 0.000
			Ending Netlist Obfuscation Task | Checksum: a7afd030

			Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.003 . Memory (MB): peak = 1652.383 ; gain = 0.000

{self._OPTDESIGN_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		optimizeDesign = processor[Opt_Design]

		self.assertIn(_OptDesign.NetlistObfuscationTask, optimizeDesign)
		netlistObfuscationTask = optimizeDesign[_OptDesign.NetlistObfuscationTask]
		self.assertEqual(0, len(netlistObfuscationTask.InfoMessages))
		self.assertEqual(0, len(netlistObfuscationTask.WarningMessages))
		self.assertEqual(0, len(netlistObfuscationTask.CriticalWarningMessages))
		self.assertEqual(0, len(netlistObfuscationTask.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)


class PlaceDesign(TestCase):
	_PREAMBLE: ClassVar[str] = """\
			#-----------------------------------------------------------
			# Vivado v2019.1 (64-bit)
			# SW Build 2552052 on Fri May 24 14:49:42 MDT 2019
			# IP Build 2548770 on Fri May 24 18:01:18 MDT 2019
			# Start of session at: Tue Sep  2 08:44:52 2025
			# Process ID: 10540
			# Current directory: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1
			# Command line: vivado.exe -log system_top.vdi -applog -product Vivado -messageDb vivado.pb -mode batch -source system_top.tcl -notrace
			# Log file: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1/system_top.vdi
			# Journal file: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1\\vivado.jou
			#-----------------------------------------------------------"""
	_SOURCE_TCL: ClassVar[str] = """\
			source system_top.tcl -notrace"""
	_PLACEDESIGN_START: ClassVar[str] = """\
			Command: place_design
			Attempting to get a license for feature 'Implementation' and/or device 'xc7z015'
			INFO: [Common 17-349] Got license for feature 'Implementation' and/or device 'xc7z015'
			INFO: [DRC 23-27] Running DRC with 2 threads
			INFO: [Vivado_Tcl 4-198] DRC finished with 0 Errors
			INFO: [Vivado_Tcl 4-199] Please refer to the DRC report (report_drc) for more information."""
	_PLACEDESIGN_FINISH: ClassVar[str] = """\
			INFO: [Common 17-83] Releasing license: Implementation
			75 Infos, 0 Warnings, 0 Critical Warnings and 0 Errors encountered.
			place_design completed successfully
			place_design: Time (s): cpu = 00:00:14 ; elapsed = 00:00:09 . Memory (MB): peak = 1652.383 ; gain = 0.000
			Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.002 . Memory (MB): peak = 1652.383 ; gain = 0.000
			INFO: [Timing 38-480] Writing timing data to binary archive.
			Writing placer database...
			Writing XDEF routing.
			Writing XDEF routing logical nets.
			Writing XDEF routing special nets.
			Write XDEF Complete: Time (s): cpu = 00:00:01 ; elapsed = 00:00:00.302 . Memory (MB): peak = 1652.383 ; gain = 0.000
			INFO: [Common 17-1381] The checkpoint 'C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1/system_top_placed.dcp' has been generated.
			INFO: [runtcl-4] Executing : report_io -file system_top_io_placed.rpt
			report_io: Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.113 . Memory (MB): peak = 1652.383 ; gain = 0.000
			INFO: [runtcl-4] Executing : report_utilization -file system_top_utilization_placed.rpt -pb system_top_utilization_placed.pb
			INFO: [runtcl-4] Executing : report_control_sets -verbose -file system_top_control_sets_placed.rpt
			report_control_sets: Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.092 . Memory (MB): peak = 1652.383 ; gain = 0.000"""
	_POSTAMBLE: ClassVar[str] = """\
			INFO: [Common 17-206] 8-Exiting Vivado at Tue Sep  2 08:46:23 2025..."""

	def test_ImplementationLogfile(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._PLACEDESIGN_START}
{self._PLACEDESIGN_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(11, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertIn(Place_Design, processor)
		placeDesign = processor[Place_Design]
		self.assertEqual(5, len(placeDesign.InfoMessages))
		self.assertEqual(0, len(placeDesign.WarningMessages))
		self.assertEqual(0, len(placeDesign.CriticalWarningMessages))
		self.assertEqual(0, len(placeDesign.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)


# class PhysicalOpt_Design(TestCase):
# 	pass


class RouteDesign(TestCase):
	_PREAMBLE: ClassVar[str] = """\
			#-----------------------------------------------------------
			# Vivado v2019.1 (64-bit)
			# SW Build 2552052 on Fri May 24 14:49:42 MDT 2019
			# IP Build 2548770 on Fri May 24 18:01:18 MDT 2019
			# Start of session at: Tue Sep  2 08:44:52 2025
			# Process ID: 10540
			# Current directory: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1
			# Command line: vivado.exe -log system_top.vdi -applog -product Vivado -messageDb vivado.pb -mode batch -source system_top.tcl -notrace
			# Log file: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1/system_top.vdi
			# Journal file: C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1\\vivado.jou
			#-----------------------------------------------------------"""
	_SOURCE_TCL: ClassVar[str] = """\
			source system_top.tcl -notrace"""
	_ROUTEDESIGN_START: ClassVar[str] = """\
			Command: route_design
			Attempting to get a license for feature 'Implementation' and/or device 'xc7z015'
			INFO: [Common 17-349] 1-Got license for feature 'Implementation' and/or device 'xc7z015'
			Running DRC as a precondition to command route_design
			INFO: [DRC 23-27] 2-Running DRC with 2 threads
			INFO: [Vivado_Tcl 4-198] 3-DRC finished with 0 Errors"""
	_ROUTEDESIGN_FINISH: ClassVar[str] = """\
			Routing Is Done.
			INFO: [Common 17-83] 4-Releasing license: Implementation
			92 Infos, 0 Warnings, 0 Critical Warnings and 0 Errors encountered.
			route_design completed successfully
			route_design: Time (s): cpu = 00:00:40 ; elapsed = 00:00:34 . Memory (MB): peak = 1698.082 ; gain = 45.699
			Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.002 . Memory (MB): peak = 1698.082 ; gain = 0.000
			INFO: [Timing 38-480] 5-Writing timing data to binary archive.
			Writing placer database...
			Writing XDEF routing.
			Writing XDEF routing logical nets.
			Writing XDEF routing special nets.
			Write XDEF Complete: Time (s): cpu = 00:00:01 ; elapsed = 00:00:00.367 . Memory (MB): peak = 1716.816 ; gain = 18.734
			INFO: [Common 17-1381] 6-The checkpoint 'C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1/system_top_routed.dcp' has been generated.
			INFO: [runtcl-4] 7-Executing : report_drc -file system_top_drc_routed.rpt -pb system_top_drc_routed.pb -rpx system_top_drc_routed.rpx
			Command: report_drc -file system_top_drc_routed.rpt -pb system_top_drc_routed.pb -rpx system_top_drc_routed.rpx
			INFO: [IP_Flow 19-1839] 8-IP Catalog is up to date.
			INFO: [DRC 23-27] 9-Running DRC with 2 threads
			INFO: [Coretcl 2-168] 10-The results of DRC are in file C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1/system_top_drc_routed.rpt.
			report_drc completed successfully
			INFO: [runtcl-4] 11-Executing : report_methodology -file system_top_methodology_drc_routed.rpt -pb system_top_methodology_drc_routed.pb -rpx system_top_methodology_drc_routed.rpx
			Command: report_methodology -file system_top_methodology_drc_routed.rpt -pb system_top_methodology_drc_routed.pb -rpx system_top_methodology_drc_routed.rpx
			INFO: [Timing 38-35] 12-Done setting XDC timing constraints.
			INFO: [DRC 23-133] 13-Running Methodology with 2 threads
			INFO: [Coretcl 2-1520] 14-The results of Report Methodology are in file C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/impl_1/system_top_methodology_drc_routed.rpt.
			report_methodology completed successfully
			INFO: [runtcl-4] 15-Executing : report_power -file system_top_power_routed.rpt -pb system_top_power_summary_routed.pb -rpx system_top_power_routed.rpx
			Command: report_power -file system_top_power_routed.rpt -pb system_top_power_summary_routed.pb -rpx system_top_power_routed.rpx
			INFO: [Timing 38-35] 16-Done setting XDC timing constraints.
			Running Vector-less Activity Propagation...

			Finished Running Vector-less Activity Propagation
			104 Infos, 0 Warnings, 0 Critical Warnings and 0 Errors encountered.
			report_power completed successfully
			INFO: [runtcl-4] 17-Executing : report_route_status -file system_top_route_status.rpt -pb system_top_route_status.pb
			INFO: [runtcl-4] 18-Executing : report_timing_summary -max_paths 10 -file system_top_timing_summary_routed.rpt -pb system_top_timing_summary_routed.pb -rpx system_top_timing_summary_routed.rpx -warn_on_violation
			INFO: [Timing 38-91] 19-UpdateTimingParams: Speed grade: -2, Delay Type: min_max.
			INFO: [Timing 38-191] 20-Multithreading enabled for timing update using a maximum of 2 CPUs
			INFO: [runtcl-4] 21-Executing : report_incremental_reuse -file system_top_incremental_reuse_routed.rpt
			INFO: [Vivado_Tcl 4-1062] 22-Incremental flow is disabled. No incremental reuse Info to report.
			INFO: [runtcl-4] 23-Executing : report_clock_utilization -file system_top_clock_utilization_routed.rpt
			INFO: [runtcl-4] 24-Executing : report_bus_skew -warn_on_violation -file system_top_bus_skew_routed.rpt -pb system_top_bus_skew_routed.pb -rpx system_top_bus_skew_routed.rpx
			INFO: [Timing 38-91] 25-UpdateTimingParams: Speed grade: -2, Delay Type: min_max.
			INFO: [Timing 38-191] 26-Multithreading enabled for timing update using a maximum of 2 CPUs"""
	_POSTAMBLE: ClassVar[str] = """\
			INFO: [Common 17-206] 27-Exiting Vivado at Tue Sep  2 08:46:23 2025..."""

	def test_ImplementationLogfile(self) -> None:
		print()
		report = StringIO(dedent(f"""{self._PREAMBLE}
{self._SOURCE_TCL}
{self._ROUTEDESIGN_START}
{self._ROUTEDESIGN_FINISH}
{self._POSTAMBLE}""")
		)

		processor = Processor()
		generator = processor.LineClassification(timestampIterator(report, datetime.now()))
		with WarningCollector() as warnings:
			for line in generator:
				pass

		self.assertEqual(27, len(processor.InfoMessages))
		self.assertEqual(0, len(processor.WarningMessages))
		self.assertEqual(0, len(processor.CriticalWarningMessages))
		self.assertEqual(0, len(processor.ErrorMessages))

		self.assertIn(Route_Design, processor)
		routeDesign = processor[Route_Design]
		self.assertEqual(4, len(routeDesign.InfoMessages))
		self.assertEqual(0, len(routeDesign.WarningMessages))
		self.assertEqual(0, len(routeDesign.CriticalWarningMessages))
		self.assertEqual(0, len(routeDesign.ErrorMessages))

		self.assertEqual(0, len(warnings))
		for line in processor.Lines:
			self.assertIsInstance(line, VivadoLine)


# class WriteBitstream(TestCase):
# 	pass
