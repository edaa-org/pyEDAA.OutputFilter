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
"""Basic classes for outputs from AMD/Xilinx Vivado."""
from datetime import datetime
from re       import Pattern, compile as re_compile
from typing import ClassVar, Optional as Nullable, Generator, List, Dict, Tuple, Type, Any

from pyTooling.Common import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Versioning  import YearReleaseVersion
from pyTooling.Warning     import WarningCollector, Warning, CriticalWarning

from pyEDAA.OutputFilter        import OutputFilterException
from pyEDAA.OutputFilter.Xilinx import Line, LineKind, VivadoMessage, InfoMessage, WarningMessage, CriticalWarningMessage, ErrorMessage
from pyEDAA.OutputFilter.Xilinx import VivadoInfoMessage, VivadoWarningMessage, VivadoCriticalWarningMessage, VivadoErrorMessage
from pyEDAA.OutputFilter.Xilinx.Exception import ProcessorException, NotPresentException

MAJOR = r"(?P<major>\d+)"
MAJOR_MINOR = r"(?P<major>\d+)\.(?P<minor>\d+)"
MAJOR_MINOR_MICRO = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)"
MAJOR_MINOR_MICRO_NANO = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)\.(?P<nano>\d+)"


@export
class UndetectedEnd(CriticalWarning):
	_line: Line

	def __init__(self, message: str, line: Line) -> None:
		super().__init__(message)

		self._line = line

	@readonly
	def Line(self) -> Line:
		return self._line


@export
class UnknownLine(Warning):
	_line: Line

	def __init__(self, message: str, line: Line) -> None:
		super().__init__(message)

		self._line = line

	@readonly
	def Line(self) -> Line:
		return self._line


@export
class UnknownTask(UnknownLine):
	pass


@export
class UnknownSection(UnknownLine):
	pass


@export
class UnknownPhase(UnknownLine):
	pass


@export
class UnknownSubPhase(UnknownLine):
	pass


@export
class SubTaskNotPresentException(NotPresentException):
	pass


@export
class PhaseNotPresentException(NotPresentException):
	pass


@export
class VivadoMessagesMixin(metaclass=ExtendedType, mixin=True):
	_infoMessages:            List[VivadoInfoMessage]
	_warningMessages:         List[VivadoWarningMessage]
	_criticalWarningMessages: List[VivadoCriticalWarningMessage]
	_errorMessages:           List[VivadoErrorMessage]
	_toolIDs:                 Dict[int, str]
	_toolNames:               Dict[str, int]
	_messagesByID:            Dict[int, Dict[int, List[VivadoMessage]]]

	def __init__(self) -> None:
		self._infoMessages = []
		self._warningMessages = []
		self._criticalWarningMessages = []
		self._errorMessages = []
		self._toolIDs = {}
		self._toolNames = {}
		self._messagesByID = {}

	@readonly
	def ToolIDs(self) -> Dict[int, str]:
		return self._toolIDs

	@readonly
	def ToolNames(self) -> Dict[str, int]:
		return self._toolNames

	@readonly
	def MessagesByID(self) -> Dict[int, Dict[int, List[VivadoMessage]]]:
		return self._messagesByID

	@readonly
	def InfoMessages(self) -> List[VivadoInfoMessage]:
		return self._infoMessages

	@readonly
	def WarningMessages(self) -> List[VivadoWarningMessage]:
		return self._warningMessages

	@readonly
	def CriticalWarningMessages(self) -> List[VivadoCriticalWarningMessage]:
		return self._criticalWarningMessages

	@readonly
	def ErrorMessages(self) -> List[VivadoErrorMessage]:
		return self._errorMessages

	def _AddMessage(self, message: VivadoMessage) -> None:
		if isinstance(message, InfoMessage):
			self._infoMessages.append(message)
		elif isinstance(message, WarningMessage):
			self._warningMessages.append(message)
		elif isinstance(message, CriticalWarningMessage):
			self._criticalWarningMessages.append(message)
		elif isinstance(message, ErrorMessage):
			self._errorMessages.append(message)

		if message._toolID in self._messagesByID:
			sub = self._messagesByID[message._toolID]
			if message._messageKindID in sub:
				sub[message._messageKindID].append(message)
			else:
				sub[message._messageKindID] = [message]
		else:
			self._toolIDs[message._toolID] = message._toolName
			self._toolNames[message._toolName] = message._toolID
			self._messagesByID[message._toolID] = {message._messageKindID: [message]}


@export
class BaseParser(VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	def __init__(self) -> None:
		super().__init__()


@export
class Parser(BaseParser):
	_processor: "Processor"

	def __init__(self, processor: "Processor") -> None:
		super().__init__()

		self._processor = processor

	@readonly
	def Processor(self) -> "Processor":
		return self._processor


@export
class Preamble(Parser):
	"""
	A parser for the preamble emitted by Vivado at session start.

	.. rubric:: Extracted information

	* Vivado tool version. |br|
	  See :data:`ToolVersion`
	* Session start timestamp (date and time). |br|
	  See :data:`StartDatetime`

	.. rubric:: Example

	.. code-block::

	   #-----------------------------------------------------------
	   # Vivado v2019.1 (64-bit)
	   # SW Build 2552052 on Fri May 24 14:49:42 MDT 2019
	   # IP Build 2548770 on Fri May 24 18:01:18 MDT 2019
	   # Start of session at: Tue Sep  2 08:44:13 2025
	   # Process ID: 35680
	   # Current directory: C:/[...]/MercuryZX5_PE1.runs/synth_1
	   # Command line: vivado.exe -log system_top.vds -product Vivado -mode batch -messageDb vivado.pb -notrace -source system_top.tcl
	   # Log file: C:/[...]/MercuryZX5_PE1.runs/synth_1/system_top.vds
	   # Journal file: C:/[...]/MercuryZX5_PE1.runs/synth_1/vivado.jou
	   #-----------------------------------------------------------

	"""
	_VERSION:   ClassVar[Pattern] = re_compile(r"""# Vivado v(\d+\.\d(\.\d)?) \(64-bit\)""")
	_STARTTIME: ClassVar[Pattern] = re_compile(r"""# Start of session at: (\w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+\d+)""")

	_toolVersion:   Nullable[YearReleaseVersion]  #: Used Vivado version.
	_startDatetime: Nullable[datetime]            #: Session start timestamp.

	def __init__(self, processor: "BaseProcessor") -> None:
		"""
		Initializes a Vivado preamble parser.

		:param processor: Reference to the Vivado log processor.
		"""
		super().__init__(processor)

		self._toolVersion =   None
		self._startDatetime = None

	@readonly
	def ToolVersion(self) -> YearReleaseVersion:
		"""
		Read-only property to access the extracted Vivado tool version.

		:returns: The used Vivado version as reported in the Vivado log messages.
		"""
		return self._toolVersion

	@readonly
	def StartDatetime(self) -> datetime:
		"""
		Read-only property to access the date and time when the Vivado session was started.

		:returns: Datatime when the session was started.
		"""
		return self._startDatetime

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		"""
		A generator for processing the Vivado session preamble line-by-line.

		:param line: First line to process.
		:returns:    A generator processing log messages.
		"""
		if line.StartsWith("#----"):
			line._kind = LineKind.SectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError  # TODO: throw / return error

		line = yield line

		# a normal preamble has 11 lines including both delimiter lines.
		for _ in range(15):
			if (match := self._VERSION.match(line._message)) is not None:
				self._toolVersion = YearReleaseVersion.Parse(match[1])
				line._kind = LineKind.Normal
			elif (match := self._STARTTIME.match(line._message)) is not None:
				self._startDatetime = datetime.strptime(match[1], "%a %b %d %H:%M:%S %Y")
				line._kind = LineKind.Normal
			elif line.StartsWith("#----"):
				line._kind = LineKind.SectionDelimiter
				break
			else:
				line._kind = LineKind.Verbose

			line = yield line
		else:
			line._kind |= LineKind.ProcessorError  # TODO: throw / return error

		nextLine = yield line
		return nextLine


@export
class Postamble(Parser):
	_INFO:    Tuple[int, int]   = (17, 206)
	_ENDTIME: ClassVar[Pattern] = re_compile(r"""Exiting Vivado at (\w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+\d+)""")

	_exitDatetime: Nullable[datetime]            #: Session exit timestamp.

	def __init__(self, processor: "BaseProcessor") -> None:
		"""
		Initializes a Vivado postamble parser.

		:param processor: Reference to the Vivado log processor.
		"""
		super().__init__(processor)

		self._exitDatetime = None

	@readonly
	def ExitDatetime(self) -> datetime:
		"""
		Read-only property to access the date and time when the Vivado session was exited.

		:returns: Datatime when the session was exited.
		"""
		return self._exitDatetime

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		"""
		A generator for processing the Vivado session preamble line-by-line.

		:param line: First line to process.
		:returns:    A generator processing log messages.
		"""
		if (match := self._ENDTIME.match(line._message)) is not None:
			self._exitDatetime = datetime.strptime(match[1], "%a %b %d %H:%M:%S %Y")
		else:
			pass

		line = yield line

		return line


@export
class Task(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	"""
	A task's output emitted by a Vivado command.

	.. rubric:: Extracted information

	* Vivado messages (info, warning, critical warning, error).

	.. rubric:: Example

	.. code-block::

	   Starting Cache Timing Information Task
	   INFO: [Timing 38-35] 79-Done setting XDC timing constraints.
	   Ending Cache Timing Information Task | Checksum: 19fe8cb97

	   Time (s): cpu = 00:00:09 ; elapsed = 00:00:09 . Memory (MB): peak = 1370.594 ; gain = 493.266

	"""
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	_TIME:   ClassVar[str] = "Time (s):"

	_command:  "Command"  #: Reference to the command (parent).
	_duration: float      #: Duration of a task according to reported times by Vivado.

	def __init__(self, command: "Command") -> None:
		"""
		Initializes a task (without child elements).

		:param command: Reference to the command.
		"""
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._command = command

	@readonly
	def Command(self) -> "Command":
		"""
		Read-only property to access the command.

		:returns: The command this task's output was logged for.
		"""
		return self._command

	def _TaskStart(self, line: Line) -> Generator[Line, Line, Line]:
		"""
		A generator for processing a task start (single line).

		:param line:                First line to process (task start).
		:returns:                   A generator processing log messages.
		:raises ProcessorException: If first line doesn't conform to the *task start* pattern.
		"""
		if not line.StartsWith(self._START):
			raise ProcessorException(f"{self.__class__.__name__}._TaskStart(): Expected '{self._START}' at line {line._lineNumber}.")

		line._kind = LineKind.TaskStart
		nextLine = yield line
		return nextLine

	def _TaskFinish(self, line: Line) -> Generator[Line, Line, Line]:
		"""
		A generator for processing a task finish line-by-line.

		:param line:                First line to process (task finish).
		:returns:                   A generator processing log messages.
		:raises ProcessorException: If finish line doesn't conform to the *task finish* pattern.
		"""
		if not line.StartsWith(self._FINISH):
			raise ProcessorException(f"{self.__class__.__name__}._TaskFinish(): Expected '{self._FINISH}' at line {line._lineNumber}.")

		line._kind = LineKind.TaskEnd
		line = yield line
		while self._TIME is not None:       # TODO: limit search for time pattern to XX lines
			if line.StartsWith(self._TIME):
				line._kind = LineKind.TaskTime
				break

			line = yield line

		line = yield line
		return line

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		"""
		A generator for processing a task without child elements line-by-line.

		.. rubric:: Algorithm

		1. Send first line to :meth:`_TaskStart`.
		2. Process body lines

		   * Collect Vivado messages (info, warning, critical warning, error).
		   * Check for *task finish* pattern.
		   * Check for *time* pattern.

		3. Send last lines to :meth:`_TaskFinish`.

		:param line:                First line to process.
		:returns:                   A generator processing log messages.
		"""
		line = yield from self._TaskStart(line)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif self._FINISH is not None and line.StartsWith("Ending"):
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			elif line.StartsWith(self._TIME):
				line._kind = LineKind.TaskTime
				nextLine = yield line
				return nextLine

			line = yield line

		nextLine = yield from self._TaskFinish(line)
		return nextLine

	def __str__(self) -> str:
		return f"{self.__class__.__name__}: {self._START}"


@export
class TaskWithSubTasks(Task):
	"""
	A task's output emitted by a Vivado command.

	.. rubric:: Extracted information

	* Vivado messages (info, warning, critical warning, error).
	* Subtasks

	.. rubric:: Example

	.. code-block::

	   Starting Cache Timing Information Task
	   INFO: [Timing 38-35] 79-Done setting XDC timing constraints.
	   Ending Cache Timing Information Task | Checksum: 19fe8cb97

	   Time (s): cpu = 00:00:09 ; elapsed = 00:00:09 . Memory (MB): peak = 1370.594 ; gain = 493.266

	"""
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	# _TIME:   ClassVar[str] = "Time (s):"

	# _PARSERS:  ClassVar[Tuple[Type["SubTask"], ...]]

	_subtasks: Dict[Type["SubTask"], "SubTask"]

	def __init__(self, command: "Command") -> None:
		super().__init__(command)

		self._subtasks =  {p: p(self) for p in self._PARSERS}

	@readonly
	def SubTasks(self) -> Dict[Type["SubTask"], "SubTask"]:
		return self._subtasks

	# todo: raise proper task not present exception
	def __getitem__(self, key: Type["SubTask"]) -> "SubTask":
		return self._subtasks[key]

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, SubTask):
			ex = TypeError(f"Parameter 'key' is not a Task.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._subtasks

	def __getitem__(self, key: Type[SubTask]) -> SubTask:
		try:
			return self._subtasks[key]
		except KeyError as ex:
			raise SubTaskNotPresentException(F"Task '{key._NAME}' not present in '{self._parent.logfile}'.") from ex


	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._TaskStart(line)

		activeParsers: List[Phase] = list(self._subtasks.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Starting "):
					for parser in activeParsers:  # type: SubTask
						if line.StartsWith(parser._START):
							line = yield next(subtask := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subtask: {line!r}")
					break
				elif line.StartsWith("Ending"):
					nextLine = yield from self._TaskFinish(line)
					return nextLine
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.TaskTime
					nextLine = yield line
					return nextLine

				line = yield line

			while subtask is not None:
				#				print(line)
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield subtask.send(line)
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break

@export
class SubTask(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	_TIME:   ClassVar[str] = "Time (s):"

	_task:     TaskWithSubTasks
	_duration: float

	def __init__(self, task: TaskWithSubTasks) -> None:
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._task = task

	@readonly
	def Task(self) -> TaskWithSubTasks:
		return self._task

	def _TaskStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException(f"{self.__class__.__name__}._TaskStart(): Expected '{self._START}' at line {line._lineNumber}.")

		line._kind = LineKind.TaskStart
		nextLine = yield line
		return nextLine

	def _TaskFinish(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException(f"{self.__class__.__name__}._TaskFinish(): Expected '{self._FINISH}' at line {line._lineNumber}.")

		line._kind = LineKind.TaskEnd
		line = yield line
		while self._TIME is not None:
			if line.StartsWith(self._TIME):
				line._kind = LineKind.TaskTime
				break

			line = yield line

		line = yield line
		return line

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._TaskStart(line)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif self._FINISH is not None and line.StartsWith("Ending"):
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			elif line.StartsWith(self._TIME):
				line._kind = LineKind.TaskTime
				nextLine = yield line
				return nextLine

			line = yield line

		nextLine = yield from self._TaskFinish(line)
		return nextLine

	def __str__(self) -> str:
		return self._NAME


@export
class TaskWithPhases(Task):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	# _TIME:   ClassVar[str] = "Time (s):"

	# _PARSERS: ClassVar[Tuple[Type["Phase"], ...]]

	_phases:  Dict[Type["Phase"], "Phase"]

	def __init__(self, command: "Command") -> None:
		super().__init__(command)

		self._phases =  {p: p(self) for p in self._PARSERS}

	@readonly
	def Phases(self) -> Dict[Type["Phase"], "Phase"]:
		return self._phases

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, Phase):
			ex = TypeError(f"Parameter 'item' is not a Phase.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._phases

	def __getitem__(self, key: Type[Phase]) -> Phase:
		try:
			return self._phases[key]
		except KeyError as ex:
			raise PhaseNotPresentException(F"Task '{key._NAME}' not present in '{self._parent.logfile}'.") from ex

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._TaskStart(line)

		activeParsers: List[Phase] = list(self._phases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase "):
					for parser in activeParsers:  # type: Phase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown phase: {line!r}")
					break
				elif line.StartsWith("Ending"):
					nextLine = yield from self._TaskFinish(line)
					return nextLine
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.TaskTime
					nextLine = yield line
					return nextLine

				line = yield line

			while phase is not None:
				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				isFinish = line.StartsWith("Ending")

				try:
					line = yield phase.send(line)
					if isFinish:
						previousLine = line._previousLine
						WarningCollector.Raise(UndetectedEnd(f"Didn't detect finish: '{previousLine!r}'", previousLine))
						break
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break


@export
class Phase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[Nullable[str]] = None

	_task:       TaskWithPhases
	_phaseIndex: int
	_duration:   float

	def __init__(self, task: TaskWithPhases) -> None:
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._task =       task
		self._phaseIndex = None

	@readonly
	def Task(self) -> TaskWithPhases:
		return self._task

	def _PhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if (match := self._START.match(line._message)) is None:
			raise ProcessorException(f"{self.__class__.__name__}._PhaseStart(): Expected '{self._START}' at line {line._lineNumber}.")

		self._phaseIndex = int(match["major"])

		line._kind = LineKind.PhaseStart
		nextLine = yield line
		return nextLine

	def _PhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex)
		if not line.StartsWith(FINISH):
			raise ProcessorException(f"{self.__class__.__name__}._PhaseFinish(): Expected '{FINISH}' at line {line._lineNumber}.")

		line._kind = LineKind.PhaseEnd
		line = yield line

		if self._TIME is not None:
			while self._TIME is not None:
				if line.StartsWith(self._TIME):
					line._kind = LineKind.PhaseTime
					break

				line = yield line

			line = yield line

		if self._FINAL is not None and self._task._command._processor._preamble._toolVersion >= "2023.2":
			while self._FINAL is not None:
				if line.StartsWith(self._FINAL):
					line._kind = LineKind.PhaseFinal
					break

				line = yield line

			line = yield line

		return line

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			elif line.StartsWith(FINISH):
				break

			line = yield line

		nextLine = yield from self._PhaseFinish(line)
		return nextLine

	def __str__(self) -> str:
		return f"{self.__class__.__name__}: {self._START.pattern}"


@export
class PhaseWithChildren(Phase):
	_SUBPHASE_PREFIX: ClassVar[str] = "Phase {phaseIndex}."

	_subPhases: Dict[Type["SubPhase"], "SubPhase"]

	def __init__(self, task: TaskWithPhases) -> None:
		super().__init__(task)

		self._subPhases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[SubPhase] = list(self._subPhases.values())

		SUBPHASE_PREFIX = self._SUBPHASE_PREFIX.format(phaseIndex=self._phaseIndex)
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex)

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith(SUBPHASE_PREFIX):
					for parser in activeParsers:  # type: Section
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						WarningCollector.Raise(UnknownSubPhase(f"Unknown subphase: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown subphase: '{line!r}'")
						ex.add_note(f"Current phase:   start pattern='{self}'")
						ex.add_note(f"Current task:    start pattern='{self._task}'")
						ex.add_note(f"Current command: {self._task._command}")
						raise ex
					break
				elif line.StartsWith(FINISH):
					nextLine = yield from self._PhaseFinish(line)
					return nextLine

				line = yield line

			while phase is not None:
				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				isFinish = False  # line.StartsWith(SUBPHASE_PREFIX)

				try:
					line = yield phase.send(line)
					if isFinish:
						previousLine = line._previousLine
						WarningCollector.Raise(UndetectedEnd(
							f"Didn't detect finish: '{previousLine!r}'",
							previousLine
						))
						break
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break


@export
class SubPhase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]

	_phase:         Phase
	_phaseIndex:    int
	_subPhaseIndex: int
	_duration:      float

	def __init__(self, phase: Phase) -> None:
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._phase =         phase
		self._phaseIndex =    None
		self._subPhaseIndex = None

	def _SubPhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if (match := self._START.match(line._message)) is None:
			raise ProcessorException(f"{self.__class__.__name__}._SubPhaseStart(): Expected '{self._START}' at line {line._lineNumber}.")

		self._phaseIndex =    int(match["major"])
		self._subPhaseIndex = int(match["minor"])

		line._kind = LineKind.SubPhaseStart
		nextLine = yield line
		return nextLine

	def _SubPhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex, subPhaseIndex=self._subPhaseIndex)

		if not line.StartsWith(FINISH):
			raise ProcessorException(f"{self.__class__.__name__}._SubPhaseFinish(): Expected '{FINISH}' at line {line._lineNumber}.")

		if self._TIME is None:
			line._kind = LineKind.SubPhaseTime
		else:
			line._kind = LineKind.SubPhaseEnd

			line = yield line
			while self._TIME is not None:
				if line.StartsWith(self._TIME):
					line._kind = LineKind.SubPhaseTime
					break

				line = yield line

		nextLine = yield line
		return nextLine

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubPhaseStart(line)

		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex, subPhaseIndex=self._subPhaseIndex)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith(FINISH):
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)

			line = yield line

		nextLine = yield from self._SubPhaseFinish(line)
		return nextLine

	def __str__(self) -> str:
		return f"{self.__class__.__name__}: {self._START.pattern}"


@export
class SubPhaseWithChildren(SubPhase):
	_subSubPhases: Dict[Type["SubSubPhase"], "SubSubPhase"]

	def __init__(self, phase: Phase) -> None:
		super().__init__(phase)

		self._subSubPhases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubPhaseStart(line)

		activeParsers: List["SubSubPhase"] = list(self._subSubPhases.values())

		START_PREFIX = f"Phase {self._phaseIndex}.{self._subPhaseIndex}."
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex, subPhaseIndex=self._subPhaseIndex)

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith(START_PREFIX):
					for parser in activeParsers:  # type: SubSubPhase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						WarningCollector.Raise(UnknownSubPhase(f"Unknown subsubphase: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown subsubphase: '{line!r}'")
						ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self._task._command}")
						raise ex
					break
				elif line.StartsWith(FINISH):
					nextLine = yield from self._SubPhaseFinish(line)
					return nextLine

				line = yield line

			while phase is not None:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield phase.send(line)
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break


@export
class SubSubPhase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]

	_subphase:         SubPhase
	_phaseIndex:       int
	_subPhaseIndex:    int
	_subSubPhaseIndex: int
	_duration:         float

	def __init__(self, subphase: SubPhase) -> None:
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._subphase =         subphase
		self._phaseIndex =       None
		self._subPhaseIndex =    None
		self._subSubPhaseIndex = None

	def _SubSubPhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if (match := self._START.match(line._message)) is None:
			raise ProcessorException()

		self._phaseIndex =       int(match["major"])
		self._subPhaseIndex =    int(match["minor"])
		self._subSubPhaseIndex = int(match["micro"])

		line._kind = LineKind.SubSubPhaseStart
		nextLine = yield line
		return nextLine

	def _SubSubPhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex, subPhaseIndex=self._subPhaseIndex, subSubPhaseIndex=self._subSubPhaseIndex)

		if not line.StartsWith(FINISH):
			raise ProcessorException(f"{self.__class__.__name__}._SubSubPhaseFinish(): Expected '{FINISH}' at line {line._lineNumber}.")

		line._kind = LineKind.SubSubPhaseEnd
		line = yield line

		while self._TIME is not None:
			if line.StartsWith(self._TIME):
				line._kind = LineKind.SubSubPhaseTime
				break

			line = yield line

		nextLine = yield line
		return nextLine

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubSubPhaseStart(line)

		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex, subPhaseIndex=self._subPhaseIndex, subSubPhaseIndex=self._subSubPhaseIndex)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith(FINISH):
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)

			line = yield line

		nextLine = yield from self._SubSubPhaseFinish(line)
		return nextLine

	def __str__(self) -> str:
		return f"{self.__class__.__name__}: {self._START.pattern}"


@export
class SubSubPhaseWithChildren(SubSubPhase):
	_subSubSubPhases: Dict[Type["SubSubSubPhase"], "SubSubSubPhase"]

	def __init__(self, subphase: SubPhase) -> None:
		super().__init__(subphase)

		self._subSubSubPhases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubSubPhaseStart(line)

		activeParsers: List["SubSubSubPhase"] = list(self._subSubSubPhases.values())

		START_PREFIX = f"Phase {self._phaseIndex}.{self._subPhaseIndex}.{self._subSubPhaseIndex}."

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith(START_PREFIX):
					for parser in activeParsers:  # type: SubSubSubPhase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubsubphase: {line!r}")
					break
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.SubSubPhaseTime
					nextLine = yield line
					return nextLine

				line = yield line

			while phase is not None:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield phase.send(line)
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break


@export
class SubSubSubPhase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]

	_subsubphase:         SubSubPhase
	_phaseIndex:          int
	_subPhaseIndex:       int
	_subSubPhaseIndex:    int
	_subSubSubPhaseIndex: int
	_duration:            float

	def __init__(self, subsubphase: SubSubPhase) -> None:
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._subsubphase =         subsubphase
		self._phaseIndex =          None
		self._subPhaseIndex =       None
		self._subSubPhaseIndex =    None
		self._subSubSubPhaseIndex = None

	def _SubSubSubPhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if (match := self._START.match(line._message)) is None:
			raise ProcessorException()

		self._phaseIndex =          int(match["major"])
		self._subPhaseIndex =       int(match["minor"])
		self._subSubPhaseIndex =    int(match["micro"])
		self._subSubSubPhaseIndex = int(match["nano"])

		line._kind = LineKind.SubSubSubPhaseStart
		nextLine = yield line
		return nextLine

	def _SubSubSubPhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex, subPhaseIndex=self._subPhaseIndex, subSubPhaseIndex=self._subSubPhaseIndex, subSubSubPhaseIndex=self._subSubSubPhaseIndex)

		if not line.StartsWith(FINISH):
			raise ProcessorException(f"{self.__class__.__name__}._SubSubSubPhaseFinish(): Expected '{FINISH}' at line {line._lineNumber}.")

		line._kind = LineKind.SubSubSubPhaseEnd
		line = yield line

		while self._TIME is not None:
			if line.StartsWith(self._TIME):
				line._kind = LineKind.SubSubSubPhaseTime
				break

			line = yield line

		nextLine = yield line
		return nextLine

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubSubSubPhaseStart(line)

		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex, subPhaseIndex=self._subPhaseIndex, subSubPhaseIndex=self._subSubPhaseIndex, subSubSubPhaseIndex=self._subSubSubPhaseIndex)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith(FINISH):
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)

			line = yield line

		nextLine = yield from self._SubSubSubPhaseFinish(line)
		return nextLine

	def __str__(self) -> str:
		return f"{self.__class__.__name__}: {self._START.pattern}"
