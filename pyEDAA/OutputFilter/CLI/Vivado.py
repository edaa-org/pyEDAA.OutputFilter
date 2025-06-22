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
from argparse import Namespace
from pathlib  import Path
from typing   import NoReturn, Iterable

from pyTooling.Decorators                      import readonly
from pyTooling.MetaClasses                     import ExtendedType
from pyTooling.Attributes.ArgParse             import CommandHandler
from pyTooling.Attributes.ArgParse.Flag        import LongFlag
from pyTooling.Attributes.ArgParse.ValuedFlag  import LongValuedFlag

from pyEDAA.OutputFilter.Xilinx                import Preamble, LineKind, Line
from pyEDAA.OutputFilter.Xilinx.Synthesis      import WritingSynthesisReport, Processor, LoadingPart


class VivadoHandlers(metaclass=ExtendedType, mixin=True):
	@CommandHandler("vivado-synth", help="Parse AMD/Xilinx Vivado Synthesis log files.", description="Parse AMD/Xilinx Vivado Synthesis log files.")
	@LongValuedFlag("--file", dest="logfile", metaName='Synthesis Log', help="Synthesis log file (*.vds).")
	@LongFlag("--colored", dest="colored", help="Render logfile with colored lines.")
	@LongFlag("--summary", dest="summary", help="Print a summary.")
	@LongFlag("--info", dest="info", help="Print info messages.")
	@LongFlag("--warning", dest="warning", help="Print warning messages.")
	@LongFlag("--critical", dest="critical", help="Print critical warning messages.")
	@LongFlag("--error", dest="error", help="Print error messages.")
	@LongFlag("--influxdb", dest="influxdb", help="Write statistics as InfluxDB line protocol file (*.line).")
	# @LongValuedFlag("--file", dest="logfile", metaName='Synthesis Log', help="Synthesis log file (*.vds).")
	def HandleVivadoSynthesis(self, args: Namespace) -> None:
		"""Handle program calls with command ``vivado-synth``."""
		self._PrintHeadline()

		returnCode = 0
		if args.logfile is None:
			self.WriteError(f"Option '--file=<VDS file>' is missing.")
			returnCode = 3

		logfile = Path(args.logfile)
		if not logfile.exists():
			self.WriteError(f"Vivado synthesis log file '{logfile}' doesn't exist.")
			returnCode = 4

		if returnCode != 0:
			self.Exit(returnCode)

		processor = Processor(logfile)
		processor.Parse()

		if args.colored:
			self.ColoredOutput(processor._lines)

		if args.info:
			self.WriteNormal(f"INFO messages: {len(processor.InfoMessages)}")
			for message in processor.InfoMessages:
				self.WriteNormal(f"  {message}")
		if args.warning:
			self.WriteNormal(f"WARNING messages: {len(processor.WarningMessages)}")
			for message in processor.WarningMessages:
				self.WriteNormal(f"  {message}")
		if args.critical:
			self.WriteNormal(f"CRITICAL WARNING: messages {len(processor.CriticalWarningMessages)}")
			for message in processor.CriticalWarningMessages:
				self.WriteNormal(f"  {message}")
		if args.error:
			self.WriteNormal(f"ERROR messages: {len(processor.ErrorMessages)}")
			for message in processor.ErrorMessages:
				self.WriteNormal(f"  {message}")

		if args.influxdb:
			influxString  =  "vivado_synthesis_overview"
			influxString += f",version={processor[Preamble].ToolVersion}"
			influxString += f",branch=main"
			influxString += f",design=Stopwatch"
			influxString += " "
			influxString += f"processing_duration={processor.Duration:.3f}"
			influxString += f",synthesis_duration={processor[WritingSynthesisReport].Duration:.1f}"
			influxString += f",info_count={len(processor.InfoMessages)}u"
			influxString += f",warning_count={len(processor.WarningMessages)}u"
			influxString += f",critical_count={len(processor.CriticalWarningMessages)}u"
			influxString += f",error_count={len(processor.ErrorMessages)}u"
			influxString += f",blackbox_count={len(processor[WritingSynthesisReport].Blackboxes)}u"
			influxString +=  "\n"
			influxString +=  "vivado_synthesis_cells"
			influxString += f",version={processor[Preamble].ToolVersion}"
			influxString += f",branch=main"
			influxString += f",design=Stopwatch"
			influxString += " "
			influxString += ",".join(f"{cellName}={cellCount}" for cellName, cellCount in processor[WritingSynthesisReport].Cells.items() if not cellName.endswith("_bbox"))

			self.WriteNormal(influxString)

		if args.summary:
			self.WriteNormal("Summary:")
			self.WriteNormal(f"  Tool version:        {processor[Preamble].ToolVersion}")
			self.WriteNormal(f"  Started at:          {processor[Preamble].StartDatetime}")
			self.WriteNormal(f"  Processing duration: {processor.Duration:.3f} s")
			self.WriteNormal(f"  Info:                {len(processor.InfoMessages)}")
			self.WriteNormal(f"  Warning:             {len(processor.WarningMessages)}")
			self.WriteNormal(f"  Critical Warning:    {len(processor.CriticalWarningMessages)}")
			self.WriteNormal(f"  Error:               {len(processor.ErrorMessages)}")
			self.WriteNormal(f"  Part:                {processor[LoadingPart].Part}")

			self.WriteNormal("Policies:")
			self.WriteNormal(f"  Latches:             {'found' if processor.HasLatches else '----'}")
			if processor.HasLatches:
				for cellName in ("LD", ):
					try:
						self.WriteNormal(f"    {cellName}: {processor.Cells[cellName]}")
					except KeyError:
						pass
				for latch in processor.Latches:
					self.WriteNormal(f"    {latch}")
			self.WriteNormal(f"  Blackboxes:          {'found' if processor.HasBlackboxes else '----'}")
			if processor.HasBlackboxes:
				for bbox in processor[WritingSynthesisReport].Blackboxes:
					self.WriteNormal(f"    {bbox}")

			self.WriteNormal(f"VHDL report statements ({len(processor.VHDLReportMessages)}):")
			for message in processor.VHDLReportMessages:
				self.WriteNormal(f"  {message}")
			self.WriteNormal(f"VHDL assert statements ({len(processor.VHDLAssertMessages)}):")
			for message in processor.VHDLAssertMessages:
				self.WriteNormal(f"  {message}")

			self.WriteNormal(f"Cells: {len(processor.Cells)}")
			for cell, count in processor.Cells.items():
				self.WriteNormal(f"  {cell}: {count}")

		self.ExitOnPreviousErrors()

	def ColoredOutput(self, lines: Iterable[Line]) -> None:
		for i, line in enumerate(lines, start=1):
			if line.Kind is LineKind.Normal:
				print(f"{i:4}: {line.Message}")
			elif LineKind.Message in line.Kind:
				if line.Kind is LineKind.InfoMessage:
					print(f"{i:4}: {{BLUE}}{line}{{NOCOLOR}}".format(**self.Foreground))
				elif line.Kind is LineKind.WarningMessage:
					print(f"{i:4}: {{YELLOW}}{line}{{NOCOLOR}}".format(**self.Foreground))
				elif line.Kind is LineKind.CriticalWarningMessage:
					print(f"{i:4}: {{MAGENTA}}{line}{{NOCOLOR}}".format(**self.Foreground))
				elif line.Kind is LineKind.ErrorMessage:
					print(f"{i:4}: {{RED}}{line}{{NOCOLOR}}".format(**self.Foreground))
			elif LineKind.Command in line.Kind:
				print(f"{i:4}: {{CYAN}}{line}{{NOCOLOR}}".format(**self.Foreground))
			elif (LineKind.Start in line.Kind) or (LineKind.End in line.Kind):
				print(f"{i:4}: {{DARK_CYAN}}{line}{{NOCOLOR}}".format(**self.Foreground))
			elif line.Kind is LineKind.ParagraphHeadline:
				print(f"{i:4}: {{DARK_YELLOW}}{line}{{NOCOLOR}}".format(**self.Foreground))
			elif LineKind.Table in line.Kind:
				print(f"{i:4}: {{WHITE}}{line}{{NOCOLOR}}".format(**self.Foreground))
			elif LineKind.Delimiter in line.Kind:
				print(f"{i:4}: {{GRAY}}{line}{{NOCOLOR}}".format(**self.Foreground))
			elif LineKind.Verbose in line.Kind:
				print(f"{i:4}: {{DARK_GRAY}}{line}{{NOCOLOR}}".format(**self.Foreground))
			elif line.Kind is LineKind.Empty:
				print(f"{i:4}:")
			elif line.Kind is LineKind.ProcessorError:
				print(f"{i:4}: {{RED}}{line}{{NOCOLOR}}".format(**self.Foreground))
			elif line.Kind is LineKind.Unprocessed:
				print(f"{i:4}: {{DARK_RED}}{line}{{NOCOLOR}}".format(**self.Foreground))
			else:
				print(f"{i:4}: Unknown LineKind '{line._kind}' for line {line._lineNumber}.")
				print(line)
				raise Exception()
