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
from sys      import stdin as sys_stdin
from typing   import NoReturn, Iterable

from pyTooling.Decorators                        import readonly
from pyTooling.MetaClasses                       import ExtendedType
from pyTooling.Attributes.ArgParse               import CommandHandler
from pyTooling.Attributes.ArgParse.Flag          import LongFlag
from pyTooling.Attributes.ArgParse.ValuedFlag    import LongValuedFlag
from pyTooling.Stopwatch                         import Stopwatch

from pyEDAA.OutputFilter.Xilinx                  import Document, ProcessorException, SynthesizeDesign, Processor
from pyEDAA.OutputFilter.Xilinx.Common           import LineKind, Line
from pyEDAA.OutputFilter.Xilinx.Common2          import Preamble
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import WritingSynthesisReport, LoadingPart



class VivadoHandlers(metaclass=ExtendedType, mixin=True):
	@CommandHandler("vivado", help="Parse AMD/Xilinx Vivado log files.", description="Parse AMD/Xilinx Vivado log files.")
	@LongFlag("--stdin", dest="stdin", help="Read log from STDIN.")
	@LongValuedFlag("--file", dest="logfile", metaName='Log file', optional=True, help="Read from log file (*.vds|*.vdi).")
	@LongFlag("--colored", dest="colored", help="Render logfile with colored lines.")
	@LongFlag("--summary", dest="summary", help="Print a summary.")
	@LongFlag("--info", dest="info", help="Print info messages.")
	@LongFlag("--warning", dest="warning", help="Print warning messages.")
	@LongFlag("--critical", dest="critical", help="Print critical warning messages.")
	@LongFlag("--error", dest="error", help="Print error messages.")
	@LongFlag("--influxdb", dest="influxdb", help="Write statistics as InfluxDB line protocol file (*.line).")
	# @LongValuedFlag("--file", dest="logfile", metaName='Synthesis Log', help="Synthesis log file (*.vds).")
	def HandleVivado(self, args: Namespace) -> None:
		"""Handle program calls with command ``vivado``."""
		self._PrintHeadline()

		if args.stdin is True:
			if args.logfile is not None:
				self.WriteError(f"If option '--stdin' is set, then option '--file' can't be set, too.")
				self.Exit(2)

			self._Streaming(args)
		else:
			if args.logfile is None:
				self.WriteError(f"Either option '--stdin' or '--file=<logfile>' is missing.")
				self.Exit(3)

			logfile = Path(args.logfile)
			if not logfile.exists():
				self.WriteError(f"Vivado log file '{logfile}' doesn't exist.")
				self.Exit(4)

			processor = Document(logfile)
			processor.Parse()

			if args.colored:
				getColor = self.GetColorOfLine

				for line in processor.Lines:
					color = getColor(line)
					self.WriteNormal(f"{{{color}}}{line}{{NOCOLOR}}".format(**self.Foreground))

		# if args.info:
		# 	self.WriteNormal(f"INFO messages: {len(processor.InfoMessages)}")
		# 	for message in processor.InfoMessages:
		# 		self.WriteNormal(f"  {message}")
		# if args.warning:
		# 	self.WriteNormal(f"WARNING messages: {len(processor.WarningMessages)}")
		# 	for message in processor.WarningMessages:
		# 		self.WriteNormal(f"  {message}")
		# if args.critical:
		# 	self.WriteNormal(f"CRITICAL WARNING: messages {len(processor.CriticalWarningMessages)}")
		# 	for message in processor.CriticalWarningMessages:
		# 		self.WriteNormal(f"  {message}")
		# if args.error:
		# 	self.WriteNormal(f"ERROR messages: {len(processor.ErrorMessages)}")
		# 	for message in processor.ErrorMessages:
		# 		self.WriteNormal(f"  {message}")
		#
		# if args.influxdb:
		# 	synthesizeDesign = processor[SynthesizeDesign]
		# 	influxString  =  "vivado_synthesis_overview"
		# 	influxString += f",version={processor.Preamble.ToolVersion}"
		# 	influxString += f",branch=main"
		# 	influxString += f",design=Stopwatch"
		# 	influxString += " "
		# 	influxString += f"processing_duration={processor.Duration:.3f}"
		# 	influxString += f",synthesis_duration={synthesizeDesign[WritingSynthesisReport].Duration:.1f}"
		# 	influxString += f",info_count={len(processor.InfoMessages)}u"
		# 	influxString += f",warning_count={len(processor.WarningMessages)}u"
		# 	influxString += f",critical_count={len(processor.CriticalWarningMessages)}u"
		# 	influxString += f",error_count={len(processor.ErrorMessages)}u"
		# 	influxString += f",blackbox_count={len(synthesizeDesign[WritingSynthesisReport].Blackboxes)}u"
		# 	influxString +=  "\n"
		# 	influxString +=  "vivado_synthesis_cells"
		# 	influxString += f",version={processor.Preamble.ToolVersion}"
		# 	influxString += f",branch=main"
		# 	influxString += f",design=Stopwatch"
		# 	influxString += " "
		# 	influxString += ",".join(f"{cellName}={cellCount}" for cellName, cellCount in synthesizeDesign[WritingSynthesisReport].Cells.items() if not cellName.endswith("_bbox"))
		#
		# 	self.WriteNormal(influxString)
		#
		# if args.summary:
		# 	synthesizeDesign : SynthesizeDesign = processor[SynthesizeDesign]
		# 	self.WriteNormal("Summary:")
		# 	self.WriteNormal(f"  Tool version:        {processor.Preamble.ToolVersion}")
		# 	self.WriteNormal(f"  Started at:          {processor.Preamble.StartDatetime}")
		# 	self.WriteNormal(f"  Processing duration: {processor.Duration:.3f} s")
		# 	self.WriteNormal(f"  Info:                {len(processor.InfoMessages)}")
		# 	self.WriteNormal(f"  Warning:             {len(processor.WarningMessages)}")
		# 	self.WriteNormal(f"  Critical Warning:    {len(processor.CriticalWarningMessages)}")
		# 	self.WriteNormal(f"  Error:               {len(processor.ErrorMessages)}")
		# 	self.WriteNormal(f"  Part:                {synthesizeDesign[LoadingPart].Part}")
		#
		# 	self.WriteNormal("Policies:")
		# 	self.WriteNormal(f"  Latches:             {'found' if synthesizeDesign.HasLatches else '----'}")
		# 	if synthesizeDesign.HasLatches:
		# 		for cellName in ("LD", ):
		# 			try:
		# 				self.WriteNormal(f"    {cellName}: {synthesizeDesign.Cells[cellName]}")
		# 			except KeyError:
		# 				pass
		# 		for latch in synthesizeDesign.Latches:
		# 			self.WriteNormal(f"    {latch}")
		# 	self.WriteNormal(f"  Blackboxes:          {'found' if synthesizeDesign.HasBlackboxes else '----'}")
		# 	if synthesizeDesign.HasBlackboxes:
		# 		for bbox in synthesizeDesign.Blackboxes:
		# 			self.WriteNormal(f"    {bbox}")
		#
		# 	self.WriteNormal(f"VHDL report statements ({len(synthesizeDesign.VHDLReportMessages)}):")
		# 	for message in synthesizeDesign.VHDLReportMessages:
		# 		self.WriteNormal(f"  {message}")
		# 	self.WriteNormal(f"VHDL assert statements ({len(synthesizeDesign.VHDLAssertMessages)}):")
		# 	for message in synthesizeDesign.VHDLAssertMessages:
		# 		self.WriteNormal(f"  {message}")
		#
		# 	self.WriteNormal(f"Cells: {len(synthesizeDesign.Cells)}")
		# 	for cell, count in synthesizeDesign.Cells.items():
		# 		self.WriteNormal(f"  {cell}: {count}")

		self.ExitOnPreviousErrors()

	# def ColoredOutput(self, lines: Iterable[Line]) -> None:
	# 	for i, line in enumerate(lines, start=1):
	# 		message = str(line).replace("{", "{{").replace("}", "}}")
	# 		if isinstance(line, ProcessorException):
	# 			print(f"{i:4}: {{RED}}EXCEPTION:{{NOCOLOR}} {message}".format(**self.Foreground))
	# 		elif line.Kind is LineKind.Normal:
	# 			print(f"{i:4}: {line.Message}")
	# 		elif LineKind.Message in line.Kind:
	# 			if line.Kind is LineKind.InfoMessage:
	# 				print(f"{i:4}: {{BLUE}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 			elif line.Kind is LineKind.WarningMessage:
	# 				print(f"{i:4}: {{YELLOW}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 			elif line.Kind is LineKind.CriticalWarningMessage:
	# 				print(f"{i:4}: {{MAGENTA}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 			elif line.Kind is LineKind.ErrorMessage:
	# 				print(f"{i:4}: {{RED}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif LineKind.TclCommand in line.Kind:
	# 			print(f"{i:4}: {{CYAN}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif (LineKind.Start in line.Kind) or (LineKind.End in line.Kind):
	# 			if LineKind.Phase in line.Kind:
	# 				print(f"{i:4}: {{YELLOW}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 			else:
	# 				print(f"{i:4}: {{DARK_CYAN}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif line.Kind is LineKind.TaskTime or line.Kind is LineKind.PhaseTime or line.Kind is LineKind.SubPhaseTime or line.Kind is LineKind.SubSubPhaseTime:
	# 			print(f"{i:4}: {{DARK_GREEN}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif line.Kind is LineKind.PhaseFinal:
	# 			print(f"{i:4}: {{DARK_GRAY}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif line.Kind is LineKind.ParagraphHeadline:
	# 			print(f"{i:4}: {{DARK_YELLOW}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif LineKind.Table in line.Kind:
	# 			print(f"{i:4}: {{WHITE}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif LineKind.Delimiter in line.Kind:
	# 			print(f"{i:4}: {{GRAY}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif LineKind.Verbose in line.Kind:
	# 			print(f"{i:4}: {{DARK_GRAY}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif LineKind.Success in line.Kind:
	# 			print(f"{i:4}: {{GREEN}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif line.Kind is LineKind.Empty:
	# 			print(f"{i:4}:")
	# 		elif line.Kind is LineKind.ProcessorError:
	# 			print(f"{i:4}: {{RED}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		elif line.Kind is LineKind.Unprocessed:
	# 			print(f"{i:4}: {{DARK_RED}}{message}{{NOCOLOR}}".format(**self.Foreground))
	# 		else:
	# 			print(f"{i:4}: Unknown LineKind '{line._kind}' for line {line._lineNumber}.")
	# 			print(line)
	# 			raise Exception(f"Unknown LineKind '{line._kind}' for line {line._lineNumber}.")

	def _Streaming(self, args: Namespace) -> None:
		processor = Processor()

		if args.colored:
			getColor = self.GetColorOfLine
		else:
			getColor = None

		with Stopwatch() as sw:
			next(generator := processor.LineClassification())
			for rawLine in sys_stdin.readlines():
				line = generator.send(rawLine.rstrip("\r\n"))

				if getColor is not None:
					color = getColor(line)
					self.WriteNormal(f"{{{color}}}{line}{{NOCOLOR}}".format(**self.Foreground))

	def GetColorOfLine(self, line: Line) -> str:
		colorDict = {
			"normal":            "WHITE",
			"info":              "BLUE",
			"warning":           "YELLOW",
			"critical":          "MAGENTA",
			"error":             "RED",
			"tcl":               "CYAN",
			"success":           "GREEN",
			"failed":            "RED",
			"verbose":           "GRAY",
			"unprocessed":       "DARK_RED",  #"DARK_GRAY",
			"sectionStart":      "DARK_CYAN",
			"sectionEnd":        "DARK_CYAN",
			"sectionTime":       "DARK_GREEN",
			"subsectionStart":   "DARK_CYAN",
			"subsectionEnd":     "DARK_CYAN",
			"subsectionTime":    "DARK_GREEN",
			"taskStart":         "DARK_CYAN",
			"taskEnd":           "DARK_CYAN",
			"taskTime":          "DARK_GREEN",
			"phaseStart":        "YELLOW",
			"phaseEnd":          "YELLOW",
			"phaseTime":         "DARK_GREEN",
			"subphaseStart":     "YELLOW",
			"subphaseEnd":       "YELLOW",
			"subphaseTime":      "DARK_GREEN",
			"paragraphHeadline": "DARK_YELLOW"
		}

		if line._kind is LineKind.Normal:
			return colorDict["normal"]
		elif LineKind.Message in line.Kind:
			if line.Kind is LineKind.InfoMessage:
				return colorDict["info"]
			elif line.Kind is LineKind.WarningMessage:
				return colorDict["warning"]
			elif line.Kind is LineKind.CriticalWarningMessage:
				return colorDict["critical"]
			elif line.Kind is LineKind.ErrorMessage:
				return colorDict["error"]
		elif LineKind.TclCommand in line.Kind:
			return colorDict["tcl"]
		elif LineKind.Success in line.Kind:
			return colorDict["success"]
		elif LineKind.Failed in line.Kind:
			return colorDict["failed"]
		elif LineKind.Verbose in line.Kind:
			return colorDict["verbose"]
		elif LineKind.Unprocessed in line.Kind:
			return colorDict["unprocessed"]
		elif LineKind.Start in line.Kind:
			if LineKind.Task in line.Kind:
				return colorDict["taskStart"]
			elif LineKind.Phase in line.Kind:
				return colorDict["phaseStart"]
			elif LineKind.SubPhase in line.Kind:
				return colorDict["subphaseStart"]
			elif LineKind.Section in line.Kind:
				return colorDict["sectionStart"]
			elif LineKind.SubSection in line.Kind:
				return colorDict["subsectionStart"]
			else:
				raise Exception(f"Unknown LineKind.****Start '{line._kind}' for line {line._lineNumber}.")
		elif LineKind.End in line.Kind:
			if LineKind.Task in line.Kind:
				return colorDict["taskEnd"]
			elif LineKind.Phase in line.Kind:
				return colorDict["phaseEnd"]
			elif LineKind.SubPhase in line.Kind:
				return colorDict["subphaseEnd"]
			elif LineKind.Section in line.Kind:
				return colorDict["sectionEnd"]
			elif LineKind.SubSection in line.Kind:
				return colorDict["subsectionEnd"]
			else:
				raise Exception(f"Unknown LineKind.****End '{line._kind}' for line {line._lineNumber}.")
		elif LineKind.Time in line.Kind:
			if LineKind.Task in line.Kind:
				return colorDict["taskTime"]
			elif LineKind.Phase in line.Kind:
				return colorDict["phaseTime"]
			elif LineKind.SubPhase in line.Kind:
				return colorDict["subphaseTime"]
			elif LineKind.Section in line.Kind:
				return colorDict["sectionTime"]
			elif LineKind.SubSection in line.Kind:
				return colorDict["subsectionTime"]
			else:
				raise Exception(f"Unknown LineKind.****Time '{line._kind}' for line {line._lineNumber}.")
		elif line.Kind is LineKind.PhaseFinal:
			return colorDict["verbose"]
		elif line.Kind is LineKind.ParagraphHeadline:
			return colorDict["paragraphHeadline"]
		elif line.Kind is LineKind.ProcessorError:
			raise Exception(f"Erroneous line {line._lineNumber} '{line._kind}' should have been wrapped in an exception.")
		elif LineKind.Table in line.Kind:
			raise Exception()
		elif LineKind.Delimiter in line.Kind:
			raise Exception()
		else:
			raise Exception(f"Unknown LineKind '{line._kind}' for line {line._lineNumber}.")
