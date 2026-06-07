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
from argparse  import Namespace
from pathlib   import Path
from re        import compile as re_compile
from sys       import stdin as sys_stdin, stdout as sys_stdout
from typing    import NoReturn, Optional as Nullable, Dict, List, TextIO, Callable

from pyTooling.Common                            import getFullyQualifiedName
from pyTooling.Decorators                        import readonly, export
from pyTooling.MetaClasses                       import ExtendedType, abstractmethod
from pyTooling.Attributes.ArgParse               import CommandHandler
from pyTooling.Attributes.ArgParse.Flag          import LongFlag
from pyTooling.Attributes.ArgParse.ValuedFlag    import LongValuedFlag
from pyTooling.TerminalUI                        import TerminalApplication
from pyTooling.Warning                           import WarningCollector, Warning

from pyEDAA.OutputFilter                   import OutputFilterException
from pyEDAA.OutputFilter.CLI.Configuration import Configuration, Vivado, ProcessingPipeline, Output, Format, Rule, StdOutOutput, FileOutput
from pyEDAA.OutputFilter.CLI.Filter        import preprocessing, mirror, postprocessing
from pyEDAA.OutputFilter.Xilinx            import Processor, LineKind, VivadoLine, Command, LineAction


@export
class VivadoHandlers(metaclass=ExtendedType, mixin=True):
	@CommandHandler("vivado", help="Parse AMD/Xilinx Vivado log files.", description="Parse AMD/Xilinx Vivado log files.")
	@LongFlag("--stdin", dest="stdin", help="Read log from STDIN.")
	@LongValuedFlag("--file", dest="logfile", metaName='Log file', optional=True, help="Read from log file (*.vds|*.vdi).")
	@LongValuedFlag("--config", dest="configfile", metaName='Config file', optional=True, help="Configuration file (*.yaml).")
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
		if not args.quiet:
			self._PrintHeadline()

		if args.configfile is not None:
			configFile = Path(args.configfile)
			if not configFile.exists():
				self.WriteError(f"Configuration file '{configFile}' doesn't exist.")
				self.Exit(3)
			else:
				with WarningCollector() as warnings:
					config = Configuration(configFile)
				for warning in warnings:
					self.WriteWarning(warning)

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
			logFile = Path(args.logfile)
			if not logFile.exists():
				self.WriteError(f"Vivado log file '{logFile}' doesn't exist.")
				self.Exit(3)

			try:
				inputFile = logFile.open("r")
			except OSError as ex:
				self.WriteError(f"Vivado log file '{logFile}' cannot be opened.")
				self.WriteError(f"  {ex}")
				self.Exit(4)

		vivadoConfig: Vivado =             config._tools["vivado"]
		pipeline:     ProcessingPipeline = vivadoConfig._processingPipeline

		pipeline._outputs["stdout"]._coloring = args.colored

		targets: List[Target] = []
		for output in pipeline._outputs.values():
			if isinstance(output, StdOutOutput):
				targets.append(target := StdOutTarget(
					args.colored,
					vivadoConfig._colors,
					output._format,
					output._commands,
					output._rules
				))
			elif isinstance(output, FileOutput):
				targets.append(target := FileTarget(
					output._format,
					output._commands,
					output._rules
				))
			else:
				ex = OutputFilterException(f"Unknown Output kind.")
				ex.add_note(f"Got '{getFullyQualifiedName(output)}'.")
				raise ex

			target.Open()

		lineIterator = iter(inputFile)

		processor = Processor()
		generator = processor.LineClassification(lineIterator)
		preprocessed = preprocessing(generator, pipeline._preprocessing)
		mirrored = mirror(preprocessed, len(targets))
		postProcessed = tuple(postprocessing(mirror, target._rules) for mirror, target in zip(mirrored, targets))

		with WarningCollector() as warnings:
			for lines in zip(*postProcessed):  # zip_longest(*postProcessed, fillvalue=None):
				for target, line in zip(targets, lines):
					target.Write(line, self.GetColorOfLine)

		for warning in warnings:
			print(warning)

		for target in targets:
			target.Close()

		#
		# if args.influxdb:
		# 	synthesizeDesign = processor[SynthesizeDesign]
		# 	influxString  =  "vivado_synthesis_overview"
		# 	influxString += f",version={processor.Preamble.ToolVersion}"
		# 	influxString += f",branch=main"
		# 	influxString += f",design=Stopwatch"
		# 	influxString += " "
		# 	influxString += f"processing_duration={processor.ProcessingDuration:.3f}"
		# 	influxString += f",duration={processor.Duration:.3f}"
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
		# 	self.WriteNormal(f"  Duration:            {processor.Duration:.3f} s")
		# 	self.WriteNormal(f"  Processing duration: {processor.ProcessingDuration:.3f} s")
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

	def GetColorOfLine(self, line: VivadoLine, colorDict: Dict[str, str]) -> str:
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
			elif LineKind.NestedTask in line.Kind:
				return colorDict["nestedTaskStart"]
			elif LineKind.NestedPhase in line.Kind:
				return colorDict["nestedPhaseStart"]
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
			elif LineKind.NestedTask in line.Kind:
				return colorDict["nestedTaskEnd"]
			elif LineKind.NestedPhase in line.Kind:
				return colorDict["nestedPhaseEnd"]
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


@export
class Target(metaclass=ExtendedType, slots=True):
	_file:     TextIO
	_format:   Format
	_commands: Nullable[List[Command]]
	_rules:    Nullable[List[Rule]]

	def __init__(self, format: Format, commands: Nullable[List[Command]], rules: Nullable[List[Rule]]) -> None:
		self._format =   format
		self._commands = commands
		self._rules =    rules

	@abstractmethod
	def Open(self) -> TextIO:
		pass

	def Write(self, line: VivadoLine, colorFunc: Callable[[VivadoLine], str]) -> None:
		if line is None:
			return
		elif line._action is LineAction.Remove:
			return

		self._file.write(f"{line}\n")

	@abstractmethod
	def Close(self) -> None:
		pass


@export
class StdOutTarget(Target):
	_coloring:    bool
	_colors:      Dict[str, str]
	_lineNumbers: bool
	_timeStamp:   bool

	def __init__(self, coloring: bool, colors: Dict[str, str], format: Format, commands: Nullable[List[Command]], rules: Nullable[List[Rule]]) -> None:
		super().__init__(format, commands, rules)

		self._coloring =    coloring
		self._colors =      colors
		self._lineNumbers = False
		self._timeStamp =   False

	def Open(self) -> TextIO:
		self._file = sys_stdout

		return self._file

	def Write(self, line: VivadoLine, colorFunc: Callable[[VivadoLine, Dict[str, str]], str]) -> None:
		if line is None:
			return
		elif line._action is LineAction.Remove:
			return

		lineNumber = f"{line.LineNumber:4}: " if self._lineNumbers else ""

		if self._coloring:
			color = colorFunc(line, self._colors)
			message = str(line).replace("{", "{{").replace("}", "}}")
			self._file.write(f"{lineNumber}{{{color}}}{message}{{NOCOLOR}}\n".format(**TerminalApplication.Foreground))
		else:
			self._file.write(f"{lineNumber}{line}\n")

		self._file.flush()

	def Close(self) -> None:
		self._file.flush()


@export
class FileTarget(Target):
	_path: Path

	def __init__(self, file: Path, format: Format, commands: List[Command], rules: List[Rule]) -> None:
		super().__init__(format, commands, rules)
		self._path = file

	def Open(self) -> TextIO:
		self._file = self._path.open("w", encoding="utf-8")

		return self._file

	def Close(self) -> None:
		self._file.flush()
		self._file.close()
