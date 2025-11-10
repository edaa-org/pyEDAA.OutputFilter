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
"""Basic classes for outputs from AMD/Xilinx Vivado."""
from datetime import datetime
from re       import Pattern, compile as re_compile
from typing   import ClassVar, Optional as Nullable, Generator, List, Dict, Tuple, Type

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Versioning  import YearReleaseVersion
from pyTooling.Warning     import WarningCollector, Warning, CriticalWarning

from pyEDAA.OutputFilter        import OutputFilterException
from pyEDAA.OutputFilter.Xilinx import Line, LineKind, VivadoMessage
from pyEDAA.OutputFilter.Xilinx import VivadoInfoMessage, VivadoWarningMessage, VivadoCriticalWarningMessage, VivadoErrorMessage
from pyEDAA.OutputFilter.Xilinx.Exception import ProcessorException


MAJOR = r"(?P<major>\d+)"
MAJOR_MINOR = r"(?P<major>\d+)\.(?P<minor>\d+)"
MAJOR_MINOR_MICRO = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)"
MAJOR_MINOR_MICRO_NANO = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)\.(?P<nano>\d+)"


@export
class UndetectedEnd(Warning):
	_line: Line

	def __init__(self, message: str, line: Line):
		super().__init__(message)

		self._line = line

	@readonly
	def Line(self) -> Line:
		return self._line


@export
class UnknownLine(CriticalWarning):
	_line: Line

	def __init__(self, message: str, line: Line):
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
		if isinstance(message, VivadoInfoMessage):
			self._infoMessages.append(message)
		elif isinstance(message, VivadoWarningMessage):
			self._warningMessages.append(message)
		elif isinstance(message, VivadoCriticalWarningMessage):
			self._criticalWarningMessages.append(message)
		elif isinstance(message, VivadoErrorMessage):
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

	def __init__(self, processor: "Processor"):
		super().__init__()

		self._processor = processor

	@readonly
	def Processor(self) -> "Processor":
		return self._processor


@export
class Preamble(Parser):
	_toolVersion:   Nullable[YearReleaseVersion]
	_startDatetime: Nullable[datetime]

	_VERSION:   ClassVar[Pattern] = re_compile(r"""# Vivado v(\d+\.\d(\.\d)?) \(64-bit\)""")
	_STARTTIME: ClassVar[Pattern] = re_compile(r"""# Start of session at: (\w+ \w+ \d+ \d+:\d+:\d+ \d+)""")

	def __init__(self, processor: "BaseProcessor"):
		super().__init__(processor)

		self._toolVersion =   None
		self._startDatetime = None

	@readonly
	def ToolVersion(self) -> YearReleaseVersion:
		return self._toolVersion

	@readonly
	def StartDatetime(self) -> datetime:
		return self._startDatetime

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		if line.StartsWith("#----"):
			line._kind = LineKind.SectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		line = yield line

		while True:
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

		nextLine = yield line
		return nextLine


@export
class Task(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	_TIME:   ClassVar[str] = "Time (s):"

	_command:  "Command"
	_duration: float

	def __init__(self, command: "Command"):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._command = command

	@readonly
	def Command(self) -> "Command":
		return self._command

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
		return f"{self.__class__.__name__}: {self._START}"


@export
class TaskWithSubTasks(Task):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	# _TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Dict[YearReleaseVersion,Tuple[Type["SubTask"], ...]]] = dict()

	_subtasks:   Dict[Type["SubTask"], "SubTask"]

	def __init__(self, command: "Command"):
		super().__init__(command)

		self._subtasks =  {p: p(self) for p in self._PARSERS}

	@readonly
	def SubTasks(self) -> Dict[Type["SubTask"], "SubTask"]:
		return self._subtasks

	def __getitem__(self, key: Type["SubTask"]) -> "SubTask":
		return self._subtasks[key]

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._TaskStart(line)

		activeParsers: List[Phase] = list(self._subtasks.values())

		while True:
			while True:
				#				print(line)
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

	def __init__(self, task: TaskWithSubTasks):
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

	_PARSERS: ClassVar[Dict[YearReleaseVersion,Tuple[Type["Phase"], ...]]] = tuple()

	_phases:   Dict[Type["Phase"], "Phase"]

	def __init__(self, command: "Command"):
		super().__init__(command)

		self._phases =  {p: p(self) for p in self._PARSERS}

	@readonly
	def Phases(self) -> Dict[Type["Phase"], "Phase"]:
		return self._phases

	def __getitem__(self, key: Type["Phase"]) -> "Phase":
		return self._phases[key]

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._TaskStart(line)

		activeParsers: List[Phase] = list(self._phases.values())

		while True:
			while True:
				#				print(line)
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
class Phase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[Nullable[str]] = None

	_task:       TaskWithPhases
	_phaseIndex: int
	_duration:   float

	def __init__(self, task: TaskWithPhases):
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

		if self._FINAL is not None:
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


@export
class PhaseWithChildren(Phase):
	_subphases: Dict[Type["SubPhase"], "SubPhase"]

	def __init__(self, task: TaskWithPhases):
		super().__init__(task)

		self._subphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		SUBPHASE_PREFIX = self._SUBPHASE_PREFIX.format(phase=1)
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
						raise Exception(f"Unknown subphase: {line!r}")
					break
				elif line.StartsWith(FINISH):
					nextLine = yield from self._PhaseFinish(line)
					return nextLine

				line = yield line

			while phase is not None:
				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				isFinish = line.StartsWith(SUBPHASE_PREFIX)

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

	def __init__(self, phase: Phase):
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

		if line.StartsWith(FINISH) is None:
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


@export
class SubSubPhase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]

	_subphase:         SubPhase
	_phaseIndex:       int
	_subPhaseIndex:    int
	_subSubPhaseIndex: int
	_duration:         float

	def __init__(self, subphase: SubPhase):
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

		if line.StartsWith(FINISH) is None:
			raise ProcessorException()

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

	def __init__(self, subsubphase: SubSubPhase):
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

		if line.StartsWith(FINISH) is None:
			raise ProcessorException()

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
