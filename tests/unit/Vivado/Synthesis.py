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
from textwrap import dedent
from unittest import TestCase as TestCase

from pyEDAA.OutputFilter.Xilinx import Processor, SynthesizeDesign

if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SynthDesign(TestCase):
	def test_SynthesisLogfile(self) -> None:
		print()
		report = dedent("""\
			#-----------------------------------------------------------
			# Vivado v2019.1 (64-bit)
			# SW Build 2552052 on Fri May 24 14:49:42 MDT 2019
			# IP Build 2548770 on Fri May 24 18:01:18 MDT 2019
			# Start of session at: Tue Sep  2 08:44:13 2025
			#-----------------------------------------------------------
			source system_top.tcl -notrace
			Command: synth_design -top system_top -part xc7z015clg485-2
			Starting synth_design
			66 Infos, 111 Warnings, 0 Critical Warnings and 0 Errors encountered.
			synth_design completed successfully
			synth_design: Time (s): cpu = 00:00:24 ; elapsed = 00:00:26 . Memory (MB): peak = 1050.637 ; gain = 665.508
			Netlist sorting complete. Time (s): cpu = 00:00:00 ; elapsed = 00:00:00 . Memory (MB): peak = 1050.637 ; gain = 0.000
			WARNING: [Constraints 18-5210] No constraints selected for write.
			Resolution: This message can indicate that there are no constraints for the design, or it can indicate that the used_in flags are set such that the constraints are ignored. This later case is used when running synth_design to not write synthesis constraints to the resulting checkpoint. Instead, project constraints are read when the synthesized design is opened.
			INFO: [Common 17-1381] The checkpoint 'C:/Users/tgomes/git/2019_1/Vivado_PE1/MercuryZX5_PE1.runs/synth_1/system_top.dcp' has been generated.
			INFO: [runtcl-4] Executing : report_utilization -file system_top_utilization_synth.rpt -pb system_top_utilization_synth.pb
			INFO: [Common 17-206] Exiting Vivado at Tue Sep  2 08:44:45 2025...
			""")

		processor = Processor()
		next(generator := processor.LineClassification())
		for rawLine in report.splitlines():
			generator.send(rawLine)

		# self.assertEqual(datetime(2025, 9, 2, 8, 44, 13), processor.Preamble.StartDatetime)
		# self.assertEqual(32, processor.Duration)
		self.assertEqual(3, len(processor.InfoMessages))
		self.assertIn(SynthesizeDesign, processor)

		synthDesign = processor[SynthesizeDesign]
