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
from queue     import Queue as ThreadSafeQueue, Empty
from sys       import stdin as sys_stdin, stdout as sys_stdout
from threading import Thread, Event
from typing    import Optional as Nullable, Dict, List, TextIO, Iterator, Tuple, Generator

from pyTooling.Common                          import getFullyQualifiedName
from pyTooling.Decorators                      import export
from pyTooling.MetaClasses                     import ExtendedType, abstractmethod, mustoverride
from pyTooling.Attributes.ArgParse             import CommandHandler
from pyTooling.Attributes.ArgParse.Flag        import LongFlag
from pyTooling.Attributes.ArgParse.ValuedFlag  import LongValuedFlag
from pyTooling.TerminalUI                      import TerminalApplication
from pyTooling.Streaming                       import Delay, BlockingPut, QueueReader
from pyTooling.Warning                         import WarningCollector, SupervisedWarningCollector, ThreadSupervisor

from pyEDAA.OutputFilter                   import OutputFilterException
from pyEDAA.OutputFilter.CLI.Configuration import Configuration, Vivado, ProcessingPipeline, OutputFormat, Rule, StdOutOutput, FileOutput, TimestampFormat
from pyEDAA.OutputFilter.Xilinx            import LineKind, VivadoLine, Processor, Command, LineAction, VivadoMessage


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

		warnings = self.RunVivadoPipeline(
			lineIterator,
			pipeline._preprocessing,
			targets
		)

		for warning in warnings:
			self.WriteWarning(warning)

		for target in targets:
			target.Close()

	def RunVivadoPipeline(
		self,
		lineIterator:    Iterator[Tuple[datetime, str]],
		commonRules:     Nullable[List[Rule]],
		targets:         List[Target],
		rawQueueSize:    int = 2000,
		targetQueueSize: int = 1000,
		lookbackDelay:   int = 1
	) -> List[BaseException]:
		"""
		Wires up classification -> raw queue -> common filter -> per-target queues -> target filter
		-> target, runs it to completion, re-raises any worker-thread *exception* on the caller's
		thread, and returns every collected *warning* (each thread's own ``WarningCollector`` results,
		merged — see :class:`ThreadErrorBox`) for the caller to report.
		"""
		stopEvent =        Event()
		threadSupervisor = ThreadSupervisor()

		commonQueue =  ThreadSafeQueue(maxsize=rawQueueSize)
		targetQueues = [ThreadSafeQueue(maxsize=targetQueueSize) for _ in targets]

		consumers =    [TargetConsumerThread(q, t, threadSupervisor, stopEvent) for q, t in zip(targetQueues, targets)]
		commonFilter = CommonFilterThread(commonQueue, commonRules, targetQueues, threadSupervisor, stopEvent)
		classifier =   ClassifierThread(lineIterator, commonQueue, threadSupervisor, stopEvent, lookbackDelay)

		# Start order doesn't matter functionally — queues buffer regardless — but starting
		# downstream-first means consumers are already waiting when the first items arrive.
		for consumer in consumers:
			consumer.start()
		commonFilter.start()
		classifier.start()

		try:
			classifier.join()
			commonFilter.join()
			for consumer in consumers:
				consumer.join()
		except KeyboardInterrupt:
			stopEvent.set()
			classifier.join(timeout=2.0)
			commonFilter.join(timeout=2.0)
			for consumer in consumers:
				consumer.join(timeout=2.0)
			raise

		threadSupervisor.ReRaise()

		return threadSupervisor.Warnings

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


@export
def preprocessing(gen: Generator[VivadoLine, None, None], rules: Nullable[List[Rule]]) -> Generator[VivadoLine, None, None]:
	if rules is None:
		return gen

	def filter(gen: Generator[VivadoLine, None, None]) -> Generator[VivadoLine, None, None]:
		for line in gen:
			for rule in rules:
				if rule.Match(line):
					rule.Process(line)

			yield line

	return filter(gen)


@export
def postprocessing(gen: Generator[VivadoLine, None, None], rules: Nullable[List[Rule]]) -> Generator[VivadoLine, None, None]:
	if rules is None:
		return gen

	def filter(gen: Generator[VivadoLine, None, None]) -> Generator[VivadoLine, None, None]:
		try:
			for line in gen:
				for rule in rules:
					if rule.Match(line):
						rule.Process(line)

				yield line
		except RuntimeError:
			pass

	return filter(gen)


@export
class ClassifierThread(Thread):
	"""
	Runs :meth:`Processor.LineClassification` over the raw ``(timestamp, str)`` line source and
	pushes every classified :class:`VivadoLine` onto ``outputQueue``. Kept as its own thread/queue
	stage (rather than fused with the common filter) so classification I/O and common-rule
	evaluation can overlap once the queue has buffered a few items.
	"""

	def __init__(
		self,
		lineIterator:     Iterator[Tuple[datetime, str]],
		outputQueue:      ThreadSafeQueue[Nullable[VivadoLine]],
		threadSupervisor: ThreadSupervisor,
		stopEvent:        Event,
		lookbackDelay:    int = 1
	) -> None:
		super().__init__(name="Classifier", daemon=True)

		self._lineIterator =     lineIterator
		self._outputQueue =      outputQueue
		self._threadSupervisor = threadSupervisor
		self._stopEvent =        stopEvent
		self._lookbackDelay =    lookbackDelay

	def run(self) -> None:
		try:
			with WarningCollector() as warnings:
				processor = Processor()
				classified = processor.LineClassification(self._lineIterator)

				# Delay by one line, because some classification needs to process the next line until it can decide about the
				# current line. Actually, it processes the current line and alters the previous line, therefore the current line
				# must be hold back from futher processing (e.g. writing to the target).
				for line in Delay(classified, delay=self._lookbackDelay):
					if self._stopEvent.is_set():
						break

					BlockingPut(self._outputQueue, line, self._stopEvent)
		except BaseException as ex:
			self._threadSupervisor.AddException(self.name, ex)
			self._stopEvent.set()
		finally:
			self._threadSupervisor.AddWarnings(self.name, warnings.Warnings)
			self._outputQueue.put(None)


@export
class CommonFilterThread(Thread):
	"""
	Consumes the raw classified stream, applies target-independent ``preprocessing`` rules, and
	fans every surviving line out to every target queue. Filtering happens *before* the fan-out
	so a line dropped here is only evaluated once, not duplicated across N target queues.

	Each target receives its own shallow copy of every surviving line, not a shared reference.
	``VivadoLine`` is mutable (``_action``, and the doubly-linked ``_previousLine``/``_nextLine``),
	and each target's own ``postprocessing`` rules will drop a different subset of lines — so each
	target needs its own chain to splice. Sharing one instance across targets would mean one
	target's removal corrupts another target's linkage. Per-target chains are (re-)built here from
	the common-filtered stream, so each starts from the same content but is independently mutable.
	"""

	def __init__(
		self,
		inputQueue:       ThreadSafeQueue[Nullable[VivadoLine]],
		commonRules:      Nullable[List[Rule]],
		targetQueues:     List[ThreadSafeQueue[Nullable[VivadoLine]]],
		threadSupervisor: ThreadSupervisor,
		stopEvent:        Event
	) -> None:
		super().__init__(name="CommonFilter", daemon=True)

		self._inputQueue =       inputQueue
		self._commonRules =      commonRules
		self._targetQueues =     targetQueues
		self._threadSupervisor = threadSupervisor
		self._stopEvent =        stopEvent

	def run(self) -> None:
		previousLinePerTarget: List[Nullable[VivadoLine]] = [None] * len(self._targetQueues)

		def exHandler(ex: BaseException) -> None:
			self._stopEvent.set()

		def finHandler() -> None:
			for targetQueue in self._targetQueues:
				targetQueue.put(None)

		with SupervisedWarningCollector(
			supervisor=self._threadSupervisor,
			exceptionHandler=exHandler,
			finallyHandler=finHandler
		) as warnings:
			stream =   QueueReader(self._inputQueue)
			filtered = preprocessing(stream, self._commonRules)

			for line in filtered:
				if self._stopEvent.is_set():
					break

				for i, targetQueue in enumerate(self._targetQueues):
					previousLinePerTarget[i] = (targetCopy := VivadoLine.Copy(line, previousLinePerTarget[i]))

					BlockingPut(targetQueue, targetCopy, self._stopEvent)


@export
class TargetConsumerThread(Thread):
	"""
	Consumes one target's queue, applies that target's ``postprocessing`` rules, and writes
	surviving lines to the target. Runs independently of every other target — a slow file write
	no longer throttles stdout output, and vice versa.
	"""

	def __init__(
		self,
		queue:            ThreadSafeQueue[Nullable[VivadoLine]],
		target:           Target,
		threadSupervisor: ThreadSupervisor,
		stopEvent:        Event
	) -> None:
		super().__init__(name=f"Target-{target.__class__.__name__}", daemon=True)

		self._queue =            queue
		self._target =           target
		self._threadSupervisor = threadSupervisor
		self._stopEvent =        stopEvent

	def run(self) -> None:
		def exHandler(ex: BaseException) -> None:
			self._stopEvent.set()

			# On failure, drain (without processing) so an upstream producer blocked on a full queue via BlockingPut() is
			# freed once it next checks stopEvent.
			while True:
				try:
					self._queue.get_nowait()
				except Empty:
					return

		with SupervisedWarningCollector(
			supervisor=self._threadSupervisor,
			exceptionHandler=exHandler
		) as warnings:
			stream = QueueReader(self._queue)
			filtered = postprocessing(stream, self._target._rules)

			for line in filtered:
				if self._stopEvent.is_set():
					break

				self._target.Write(line)
