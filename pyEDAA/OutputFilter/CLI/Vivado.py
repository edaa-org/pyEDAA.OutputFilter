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
from datetime  import datetime
from json      import dumps
from pathlib   import Path
from sys       import stdin as sys_stdin, stdout as sys_stdout
from typing    import Optional as Nullable, Dict, List, TextIO, Iterator, Tuple

from pyTooling.Common                          import getFullyQualifiedName
from pyTooling.Decorators                      import export
from pyTooling.MetaClasses                     import ExtendedType, abstractmethod, mustoverride
from pyTooling.Attributes.ArgParse             import CommandHandler
from pyTooling.Attributes.ArgParse.Flag        import LongFlag
from pyTooling.Attributes.ArgParse.ValuedFlag  import LongValuedFlag
from pyTooling.TerminalUI                      import TerminalApplication
from pyTooling.Warning                         import WarningCollector

from pyEDAA.OutputFilter                   import OutputFilterException
from pyEDAA.OutputFilter.CLI.Configuration import Configuration, Vivado, ProcessingPipeline, OutputFormat, Rule, StdOutOutput, FileOutput, TimestampFormat
from pyEDAA.OutputFilter.CLI.Filter        import preprocessing, mirror, postprocessing
from pyEDAA.OutputFilter.Xilinx            import Processor, LineKind, VivadoLine, Command, LineAction, VivadoMessage


@export
class VivadoHandlers(metaclass=ExtendedType, mixin=True):
	@CommandHandler("vivado", help="Parse AMD/Xilinx Vivado log files.", description="Parse AMD/Xilinx Vivado log files.")
	@LongFlag("--stdin", dest="stdin", help="Read log from STDIN.")
	@LongValuedFlag("--file", dest="logfile", metaName='Log file', optional=True, help="Read from log file (*.vds|*.vdi).")
	@LongValuedFlag("--config", dest="configfile", metaName='Config file', optional=True, help="Configuration file (*.yaml).")
	@LongFlag("--colored", dest="colored", help="Render logfile with colored lines.")
	# @LongFlag("--summary", dest="summary", help="Print a summary.")
	# @LongFlag("--info", dest="info", help="Print info messages.")
	# @LongFlag("--warning", dest="warning", help="Print warning messages.")
	# @LongFlag("--critical", dest="critical", help="Print critical warning messages.")
	# @LongFlag("--error", dest="error", help="Print error messages.")
	# @LongFlag("--influxdb", dest="influxdb", help="Write statistics as InfluxDB line protocol file (*.line).")
	# @LongValuedFlag("--file", dest="logfile", metaName='Synthesis Log', help="Synthesis log file (*.vds).")
	def HandleVivado(self, args: Namespace) -> None:
		"""Handle program calls with command ``vivado``."""
		if not args.quiet:
			self._PrintHeadline()

		config = Configuration()
		if args.configfile is not None:
			configFile = Path(args.configfile)
			if not configFile.exists():
				self.WriteError(f"Configuration file '{configFile}' doesn't exist.")
				self.Exit(3)
			else:
				with WarningCollector() as warnings:
					config.Load(configFile)
				for warning in warnings:
					self.WriteWarning(warning)
					for note in warning.Notes:
						self.WriteWarningNote(note)

		if args.stdin is True:
			if args.logfile is not None:
				self.WriteError(f"If option '--stdin' is set, then option '--file' can't be set, too.")
				self.Exit(2)

			self.WriteVerbose("Reading lines from STDIN ...")
			inputSource = StdInSource(self)
		elif args.logfile is None:
			self.WriteError(f"No input file (<logfile> or '-' for STDIN) specified via option '--file=<logfile>'.")
			self.Exit(2)
		elif args.logfile == "-":
			self.WriteVerbose("Reading lines from STDIN ...")
			inputSource = StdInSource(self)
		else:
			logFile = Path(args.logfile)
			if not logFile.exists():
				self.WriteError(f"Vivado log file '{logFile}' doesn't exist.")
				self.Exit(3)

			inputSource = FileSource(logFile, self)

		self.ExitOnPreviousErrors()

		vivadoConfig: Vivado = config._tools["vivado"]
		pipeline: ProcessingPipeline = vivadoConfig._processingPipeline

		inputSource.Open()
		lineIterator = iter(inputSource)

		targets: List[Target] = []
		for output in pipeline._outputs.values():
			if isinstance(output, StdOutOutput):
				targets.append(target := StdOutTarget(
					inputSource._startTime,
					output._coloring or args.colored,
					vivadoConfig._colors,
					output._format,
					output._lineNumbers,
					output._timestampFormat,
					output._commands,
					output._rules
				))
			elif isinstance(output, FileOutput):
				targets.append(target := FileTarget(
					output._path,
					output._format,
					output._commands,
					output._rules
				))
			else:
				ex = OutputFilterException(f"Unknown Output kind.")
				ex.add_note(f"Got '{getFullyQualifiedName(output)}'.")
				raise ex

			target.Open()

		processor = Processor()
		generator = processor.LineClassification(lineIterator)
		preprocessed = preprocessing(generator, pipeline._preprocessing)
		mirrored = mirror(preprocessed, len(targets))
		postProcessed = tuple(postprocessing(mirror, target._rules) for mirror, target in zip(mirrored, targets))

		with WarningCollector() as warnings:
			for lines in zip(*postProcessed):  # zip_longest(*postProcessed, fillvalue=None):
				for target, line in zip(targets, lines):
					target.Write(line)

		for warning in warnings:
			self.WriteWarning(warning)

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
		# 	self.WriteNormal(f"  Started at:          {processor.Preamble.StartDateTime}")
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


@export
class Source(metaclass=ExtendedType, slots=True):
	_parent:    VivadoHandlers
	_file:      TextIO
	_startTime: datetime

	@mustoverride
	def __init__(self, parent: VivadoHandlers) -> None:
		self._parent = parent

	@abstractmethod
	def __iter__(self) -> Iterator[Tuple[datetime, str]]:
		pass

	@abstractmethod
	def Open(self) -> TextIO:
		pass


@export
class StdInSource(Source):
	def __init__(self, parent: VivadoHandlers) -> None:
		super().__init__(parent)

		self._startTime = datetime.now()

	def __iter__(self) -> Iterator[Tuple[datetime, str]]:
		for line in self._file:
			yield datetime.now(), line

	def Open(self) -> TextIO:
		self._file = sys_stdin

		return self._file


@export
class FileSource(Source):
	_path: Path

	def __init__(self, path: Path, parent: VivadoHandlers) -> None:
		super().__init__(parent)

		self._path = path
		self._startTime = datetime.fromtimestamp(self._path.stat().st_mtime)

	def __iter__(self) -> Iterator[Tuple[datetime, str]]:
		for line in self._file:
			yield self._startTime, line

	def Open(self) -> TextIO:
		try:
			self._file = open(self._path, "r", encoding="utf-8")
		except OSError as ex:
			raise OutputFilterException(f"Vivado log file '{self._path}' cannot be opened.") from ex

		return self._file


@export
class Target(metaclass=ExtendedType, slots=True):
	_file:     TextIO
	_format:   OutputFormat
	_commands: Nullable[List[Command]]
	_rules:    Nullable[List[Rule]]

	def __init__(
		self,
		format:   OutputFormat,
		commands: Nullable[List[Command]],
		rules:    Nullable[List[Rule]]
	) -> None:
		self._format =   format
		self._commands = commands
		self._rules =    rules

	@abstractmethod
	def Open(self) -> TextIO:
		pass

	def Write(self, line: VivadoLine) -> None:
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
	_coloring:        bool
	_colors:          Dict[str, str]
	_lineNumbers:     bool
	_timestampFormat: TimestampFormat

	_startTime:       datetime

	def __init__(
		self,
		startTime:       datetime,
		coloring:        bool,
		colors:          Dict[str, str],
		format:          OutputFormat,
		lineNumbers:     bool,
		timestampFormat: TimestampFormat,
		commands:        Nullable[List[Command]],
		rules:           Nullable[List[Rule]]
	) -> None:
		super().__init__(format, commands, rules)

		self._startTime =       startTime
		self._coloring =        coloring
		self._colors =          colors
		self._lineNumbers =     lineNumbers
		self._timestampFormat = timestampFormat

	def Open(self) -> TextIO:
		self._file =      sys_stdout

		return self._file

	def Write(self, line: VivadoLine) -> None:
		if line is None:
			return
		elif line._action is LineAction.Remove:
			return

		if self._format is OutputFormat.Plain:
			self._WritePlain(line)
		elif self._format is OutputFormat.JSONLine:
			self._WriteJSONLine(line)
		else:
			raise OutputFilterException(f"Unknown format '{self._format}'.")

		self._file.flush()

	def _WritePlain(self, line: VivadoLine) -> None:
		if self._timestampFormat == TimestampFormat.DateTime:
			timestamp =  f"{line._timestamp:%d.%m.%Y %H:%M:%S} - "
		elif self._timestampFormat == TimestampFormat.TimeOnly:
			timestamp = f"{line._timestamp:%H:%M:%S} - "
		elif self._timestampFormat == TimestampFormat.Runtime:
			delta = line._timestamp - self._startTime
			seconds = int(delta.total_seconds())
			hours = seconds // 3600
			minutes = (seconds % 3600) // 60
			secondss = seconds % 60
			milliseconds = delta.microseconds // 1000

			timestamp = f"{hours:02d}:{minutes:02d}:{secondss:02d}.{milliseconds:03d} - "
		elif self._timestampFormat == TimestampFormat.Undefined:
			timestamp = ""
		else:
			raise OutputFilterException(f"Unknown timestamp format '{self._timestampFormat}'.")

		lineNumber = f"{line.LineNumber:4}: " if self._lineNumbers else ""

		if self._coloring:
			color = self._GetColorOfLine(line)
			message = str(line).replace("{", "{{").replace("}", "}}")
			self._file.write(f"{timestamp}{lineNumber}{{{color}}}{message}{{NOCOLOR}}\n".format(**TerminalApplication.Foreground))
		else:
			self._file.write(f"{timestamp}{lineNumber}{line}\n")

	def _WriteJSONLine(self, line: VivadoLine) -> None:
		if isinstance(line, VivadoMessage):
			jsonLine = {
				"line":      line._lineNumber,
				"timestamp": line._timestamp.isoformat(),
				"kind":      line._kind.name,
				"tool":      line._toolName,
				"toolID":    line._toolID,
				"messageID": line._messageKindID,
				"message":   line._message,
			}
		else:
			jsonLine = {
				"line":      line._lineNumber,
				"timestamp": line._timestamp.isoformat(),
				"kind":      line._kind.name,
				"message":   line._message,
			}

		self._file.write(dumps(jsonLine, indent=None) + "\n")

	def Close(self) -> None:
		self._file.flush()

	def _GetColorOfLine(self, line: VivadoLine) -> str:
		if line._kind is LineKind.Normal:
			return self._colors["normal"]
		elif LineKind.Message in line.Kind:
			if line.Kind is LineKind.InfoMessage:
				return self._colors["info"]
			elif line.Kind is LineKind.WarningMessage:
				return self._colors["warning"]
			elif line.Kind is LineKind.CriticalWarningMessage:
				return self._colors["critical"]
			elif line.Kind is LineKind.ErrorMessage:
				return self._colors["error"]
			else:
				raise OutputFilterException(f"Unknown LineKind '{line._kind}' for line {line._lineNumber}.")
		elif LineKind.TclCommand in line.Kind:
			return self._colors["tcl"]
		elif LineKind.Success in line.Kind:
			return self._colors["success"]
		elif LineKind.Failed in line.Kind:
			return self._colors["failed"]
		elif LineKind.Verbose in line.Kind:
			return self._colors["verbose"]
		elif line.Kind is LineKind.Unprocessed:
			return self._colors["unprocessed"]
		elif line.Kind is LineKind.Empty:
			return self._colors["empty"]
		elif LineKind.Start in line.Kind:
			if LineKind.Task in line.Kind:
				return self._colors["taskStart"]
			elif LineKind.Phase in line.Kind:
				return self._colors["phaseStart"]
			elif LineKind.SubPhase in line.Kind:
				return self._colors["subphaseStart"]
			elif LineKind.SubSubPhase in line.Kind:
				return self._colors["subsubphaseStart"]
			elif LineKind.SubSubSubPhase in line.Kind:
				return self._colors["subsubsubphaseStart"]
			elif LineKind.Section in line.Kind:
				return self._colors["sectionStart"]
			elif LineKind.SubSection in line.Kind:
				return self._colors["subsectionStart"]
			elif LineKind.NestedTask in line.Kind:
				return self._colors["nestedTaskStart"]
			elif LineKind.NestedPhase in line.Kind:
				return self._colors["nestedPhaseStart"]
			elif LineKind.Launch in line.Kind:
				return self._colors["launchStart"]
			else:
				raise OutputFilterException(f"Unknown LineKind.****Start '{line._kind}' for line {line._lineNumber}.")
		elif LineKind.End in line.Kind:
			if LineKind.Task in line.Kind:
				return self._colors["taskEnd"]
			elif LineKind.Phase in line.Kind:
				return self._colors["phaseEnd"]
			elif LineKind.SubPhase in line.Kind:
				return self._colors["subphaseEnd"]
			elif LineKind.SubSubPhase in line.Kind:
				return self._colors["subsubphaseEnd"]
			elif LineKind.SubSubSubPhase in line.Kind:
				return self._colors["subsubsubphaseEnd"]
			elif LineKind.Section in line.Kind:
				return self._colors["sectionEnd"]
			elif LineKind.SubSection in line.Kind:
				return self._colors["subsectionEnd"]
			elif LineKind.NestedTask in line.Kind:
				return self._colors["nestedTaskEnd"]
			elif LineKind.NestedPhase in line.Kind:
				return self._colors["nestedPhaseEnd"]
			elif LineKind.Launch in line.Kind:
				return self._colors["launchFinished"]
			else:
				raise OutputFilterException(f"Unknown LineKind.****End '{line._kind}' for line {line._lineNumber}.")
		elif LineKind.Time in line.Kind:
			if LineKind.Task in line.Kind:
				return self._colors["taskTime"]
			elif LineKind.Phase in line.Kind:
				return self._colors["phaseTime"]
			elif LineKind.SubPhase in line.Kind:
				return self._colors["subphaseTime"]
			elif LineKind.SubSubPhase in line.Kind:
				return self._colors["subsubphaseTime"]
			elif LineKind.SubSubSubPhase in line.Kind:
				return self._colors["subsubsubphaseTime"]
			elif LineKind.Section in line.Kind:
				return self._colors["sectionTime"]
			elif LineKind.SubSection in line.Kind:
				return self._colors["subsectionTime"]
			elif LineKind.Launch in line.Kind:
				return self._colors["launchTime"]
			else:
				raise OutputFilterException(f"Unknown LineKind.****Time '{line._kind}' for line {line._lineNumber}.")
		elif LineKind.Table in line.Kind:
			return self._colors["table"]
		elif LineKind.Delimiter in line.Kind:
			if LineKind.Section in line.Kind:
				return self._colors["sectionDelimiter"]
			else:
				raise OutputFilterException(f"Unknown LineKind.****Delimiter '{line._kind}' for line {line._lineNumber}.")
		elif line.Kind is LineKind.PhaseFinal:
			return self._colors["verbose"]
		elif line.Kind is LineKind.ParagraphHeadline:
			return self._colors["paragraphHeadline"]
		elif line.Kind is LineKind.LaunchArguments:
			return self._colors["launchArguments"]
		elif line.Kind is LineKind.ProcessorError:
			raise OutputFilterException(f"Erroneous line {line._lineNumber} '{line._kind}' should have been wrapped in an exception.")
		elif LineKind.Table in line.Kind:
			raise OutputFilterException()
		elif LineKind.Delimiter in line.Kind:
			raise OutputFilterException()
		else:
			raise OutputFilterException(f"Unknown LineKind '{line._kind}' for line {line._lineNumber}.")


@export
class FileTarget(Target):
	_path: Path

	def __init__(
		self,
		file:      Path,
		format:    OutputFormat,
		commands:  List[Command],
		rules:     List[Rule]
	) -> None:
		super().__init__(format, commands, rules)
		self._path = file

	def Open(self) -> TextIO:
		self._file =      self._path.open("w", encoding="utf-8")

		return self._file

	def Close(self) -> None:
		self._file.flush()
		self._file.close()
