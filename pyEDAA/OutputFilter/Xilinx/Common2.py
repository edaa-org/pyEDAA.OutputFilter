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

from pyEDAA.OutputFilter.Xilinx import Line, LineKind, VivadoMessage
from pyEDAA.OutputFilter.Xilinx import VivadoInfoMessage, VivadoWarningMessage, VivadoCriticalWarningMessage, VivadoErrorMessage
from pyEDAA.OutputFilter.Xilinx.Exception import ProcessorException


@export
class VivadoMessagesMixin(metaclass=ExtendedType, mixin=True):
	_infoMessages: List[VivadoInfoMessage]
	_warningMessages: List[VivadoWarningMessage]
	_criticalWarningMessages: List[VivadoCriticalWarningMessage]
	_errorMessages: List[VivadoErrorMessage]
	_toolIDs: Dict[int, str]
	_toolNames: Dict[str, int]
	_messagesByID: Dict[int, Dict[int, List[VivadoMessage]]]

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

	_PARSERS: ClassVar[Tuple[Type["Phase"], ...]] = tuple()

	_command:  "Command"
	_duration: float
	_phases:   Dict[Type["Phase"], "Phase"]

	def __init__(self, command: "Command"):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._command = command
		self._phases =  {p: p(self) for p in self._PARSERS}

	@readonly
	def Command(self) -> "Command":
		return self._command

	@readonly
	def Phases(self) -> Dict[Type["Phase"], "Phase"]:
		return self._phases

	def __getitem__(self, key: Type["Phase"]) -> "Phase":
		return self._phases[key]

	def _TaskStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException()

		line._kind = LineKind.TaskStart
		nextLine = yield line
		return nextLine

	def _TaskFinish(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException()

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
class Phase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	_TIME:   ClassVar[str] = "Time (s):"

	_task:     Task
	_duration: float

	def __init__(self, task: Task):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._task = task

	@readonly
	def Task(self) -> Task:
		return self._task

	def _PhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException()

		line._kind = LineKind.PhaseStart
		nextLine = yield line
		return nextLine

	def _PhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException()

		line._kind = LineKind.PhaseEnd
		line = yield line

		if self._TIME is not None:
			while self._TIME is not None:
				if line.StartsWith(self._TIME):
					line._kind = LineKind.PhaseTime
					break

				line = yield line

			line = yield line

		return line

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			elif line.StartsWith(self._FINISH):
				break

			line = yield line

		nextLine = yield from self._PhaseFinish(line)
		return nextLine

@export
class SubPhase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]

	_phase:    Phase
	_duration: float

	def __init__(self, phase: Phase):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._phase = phase

	def _SubPhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException()

		line._kind = LineKind.SubPhaseStart
		nextLine = yield line
		return nextLine

	def _SubPhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException()

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

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith(self._FINISH):
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

	_subphase: SubPhase
	_duration: float

	def __init__(self, subphase: SubPhase):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._subphase = subphase

	def _SubSubPhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException()

		line._kind = LineKind.SubSubPhaseStart
		nextLine = yield line
		return nextLine

	def _SubSubPhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		if not line.StartsWith(self._FINISH):
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

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith(self._FINISH):
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

	_subsubphase: SubSubPhase
	_duration: float

	def __init__(self, subsubphase: SubSubPhase):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._subsubphase = subsubphase

	def _SubSubSubPhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException()

		line._kind = LineKind.SubSubSubPhaseStart
		nextLine = yield line
		return nextLine

	def _SubSubSubPhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		if not line.StartsWith(self._FINISH):
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

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith(self._FINISH):
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)

			line = yield line

		nextLine = yield from self._SubSubSubPhaseFinish(line)
		return nextLine
