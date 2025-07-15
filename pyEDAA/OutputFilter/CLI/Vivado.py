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

			self.WriteVerbose("Reading lines from STDIN ...")
			inputFile = sys_stdin
		elif args.logfile is None:
			self.WriteError(f"No input file (<logfile> or '-' for STDIN) specified via option '--file=<logfile>'.")
			self.Exit(2)
		elif args.logfile == "-":
			self.WriteVerbose("Reading lines from STDIN ...")
			inputFile = sys_stdin
		else:
			logfile = Path(args.logfile)
			if not logfile.exists():
				self.WriteError(f"Vivado log file '{logfile}' doesn't exist.")
				self.Exit(3)

			try:
				inputFile = logfile.open("r")
			except OSError as ex:
				self.WriteError(f"Vivado log file '{logfile}' cannot be opened.")
				self.WriteError(f"  {ex}")
				self.Exit(4)

		processor = Processor()

		if args.colored:
			writeOutput = self._WriteColoredOutput
		else:
			writeOutput = self._WriteOutput

		with Stopwatch() as sw:
			next(generator := processor.LineClassification())
			for rawLine in inputFile.readlines():
				line = generator.send(rawLine.rstrip("\r\n"))

				writeOutput(line)

	def _WriteOutput(self, line: Line):
		self.WriteNormal(f"{line}")

	def _WriteColoredOutput(self, line: Line):
		color = self.GetColorOfLine(line)
		message = str(line).replace("{", "{{").replace("}", "}}")
		self.WriteNormal(f"{{{color}}}{message}{{NOCOLOR}}".format(**self.Foreground))


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

	def GetColorOfLine(self, line: Line) -> str:
		colorDict = {
			"normal":               "WHITE",
			"info":                 "GRAY", # "DARK_BLUE",
			"warning":              "YELLOW",
			"critical":             "MAGENTA",
			"error":                "RED",
			"tcl":                  "CYAN",
			"success":              "GREEN",
			"failed":               "RED",
			"verbose":              "GRAY",
			"unprocessed":          "DARK_GRAY",
			"empty":                "NOCOLOR",
			"sectionDelimiter":     "DARK_GRAY",
			"sectionStart":         "DARK_CYAN",
			"sectionEnd":           "DARK_CYAN",
			"sectionTime":          "DARK_GREEN",
			"subsectionStart":      "DARK_CYAN",
			"subsectionEnd":        "DARK_CYAN",
			"subsectionTime":       "DARK_GREEN",
			"taskStart":            "YELLOW",
			"taskEnd":              "YELLOW",
			"taskTime":             "DARK_GREEN",
			"phaseStart":           "BLUE",
			"phaseEnd":             "BLUE",
			"phaseTime":            "DARK_GREEN",
			"subphaseStart":        "DARK_CYAN",
			"subphaseEnd":          "DARK_CYAN",
			"subphaseTime":         "DARK_GREEN",
			"subsubphaseStart":     "DARK_CYAN",
			"subsubphaseEnd":       "DARK_CYAN",
			"subsubphaseTime":      "DARK_GREEN",
			"subsubsubphaseStart":  "DARK_CYAN",
			"subsubsubphaseEnd":    "DARK_CYAN",
			"subsubsubphaseTime":   "DARK_GREEN",
			"paragraphHeadline":    "DARK_YELLOW",
			"hierarchyStart":       "DARK_CYAN",
			"hierarchyEnd":         "DARK_GRAY",
			"xdcStart":             "DARK_CYAN",
			"xdcEnd":               "DARK_GRAY",
			"table":                "GRAY",
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
		elif line.Kind is LineKind.Unprocessed:
			return colorDict["unprocessed"]
		elif line.Kind is LineKind.Empty:
			return colorDict["empty"]
		elif LineKind.Start in line.Kind:
			if LineKind.Task in line.Kind:
				return colorDict["taskStart"]
			elif LineKind.Phase in line.Kind:
				return colorDict["phaseStart"]
			elif LineKind.SubPhase in line.Kind:
				return colorDict["subphaseStart"]
			elif LineKind.SubSubPhase in line.Kind:
				return colorDict["subsubphaseStart"]
			elif LineKind.SubSubSubPhase in line.Kind:
				return colorDict["subsubsubphaseStart"]
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
			elif LineKind.SubSubPhase in line.Kind:
				return colorDict["subsubphaseEnd"]
			elif LineKind.SubSubSubPhase in line.Kind:
				return colorDict["subsubsubphaseEnd"]
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
			elif LineKind.SubSubPhase in line.Kind:
				return colorDict["subsubphaseTime"]
			elif LineKind.SubSubSubPhase in line.Kind:
				return colorDict["subsubsubphaseTime"]
			elif LineKind.Section in line.Kind:
				return colorDict["sectionTime"]
			elif LineKind.SubSection in line.Kind:
				return colorDict["subsectionTime"]
			else:
				raise Exception(f"Unknown LineKind.****Time '{line._kind}' for line {line._lineNumber}.")
		elif LineKind.Table in line.Kind:
			return colorDict["table"]
		elif LineKind.Delimiter in line.Kind:
			if LineKind.Section in line.Kind:
				return colorDict["sectionDelimiter"]
			else:
				raise Exception(f"Unknown LineKind.****Delimiter '{line._kind}' for line {line._lineNumber}.")
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
