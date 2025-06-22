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
from enum     import Flag
from pathlib  import Path
from re       import compile as re_compile, Pattern
from typing import ClassVar, Self, Optional as Nullable, Dict, Type, Callable, List, Generator, Union, Tuple

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType, abstractmethod
from pyTooling.Stopwatch   import Stopwatch
from pyTooling.TerminalUI  import TerminalApplication
from pyTooling.Versioning  import YearReleaseVersion

from pyEDAA.OutputFilter   import OutputFilterException


@export
class ProcessorException(OutputFilterException):
	pass


@export
class ClassificationException(ProcessorException):
	_lineNumber: int
	_rawMessage: str

	def __init__(self, errorMessage: str, lineNumber: int, rawMessageLine: str):
		super().__init__(errorMessage)

		self._lineNumber = lineNumber
		self._rawMessage = rawMessageLine


@export
class ParserStateException(ProcessorException):
	pass


@export
class LineKind(Flag):
	Unprocessed =                0
	ProcessorError =         2** 0
	Empty =                  2** 1
	Delimiter =              2** 2

	Verbose =                2**10
	Normal =                 2**11
	Info =                   2**12
	Warning =                2**13
	CriticalWarning =        2**14
	Error =                  2**15
	Fatal =                  2**16

	Start =                  2**20
	End =                    2**21
	Header =                 2**22
	Content =                2**23
	Footer =                 2**24

	Last =                   2**29

	Message =                2**30
	InfoMessage =            Message | Info
	WarningMessage =         Message | Warning
	CriticalWarningMessage = Message | CriticalWarning
	ErrorMessage =           Message | Error

	Section =                2**31
	SectionDelimiter =       Section | Delimiter
	SectionStart =           Section | Start
	SectionEnd =             Section | End

	SubSection =             2**32
	SubSectionDelimiter =    SubSection | Delimiter
	SubSectionStart =        SubSection | Start
	SubSectionEnd =          SubSection | End

	Paragraph =              2**33
	ParagraphHeadline =      Paragraph | Header

	Table =                  2**34
	TableFrame =             Table | Delimiter
	TableHeader =            Table | Header
	TableRow =               Table | Content
	TableFooter =            Table | Footer

	Command =                2**35


@export
class Line(metaclass=ExtendedType, slots=True):
	"""
	This class represents any line in a log file.
	"""
	_lineNumber:    int
	_kind:          LineKind
	_message:       str

	def __init__(self, lineNumber: int, kind: LineKind, message: str) -> None:
		self._lineNumber = lineNumber
		self._kind = kind
		self._message = message

	@readonly
	def LineNumber(self) -> int:
		return self._lineNumber

	@readonly
	def Kind(self) -> LineKind:
		return self._kind

	@readonly
	def Message(self) -> str:
		return self._message

	def __str__(self) -> str:
		return self._message


@export
class InfoMessage(metaclass=ExtendedType, mixin=True):
	pass


@export
class WarningMessage(metaclass=ExtendedType, mixin=True):
	pass


@export
class CriticalWarningMessage(metaclass=ExtendedType, mixin=True):
	pass


@export
class ErrorMessage(metaclass=ExtendedType, mixin=True):
	pass


@export
class VivadoMessage(Line):
	"""
	This class represents an AMD/Xilinx Vivado message.

	The usual message format is:

	.. code-block:: text

	   INFO: [Synth 8-7079] Multithreading enabled for synth_design using a maximum of 2 processes.
	   WARNING: [Synth 8-3332] Sequential element (gen[0].Sync/FF2) is unused and will be removed from module sync_Bits_Xilinx.

	The following message severities are defined:

	* ``INFO``
	* ``WARNING``
	* ``CRITICAL WARNING``
	* ``ERROR``

	.. seealso::

	   :class:`VivadoInfoMessage`
	     Representing a Vivado info message.

	   :class:`VivadoWarningMessage`
	     Representing a Vivado warning message.

	   :class:`VivadoCriticalWarningMessage`
	     Representing a Vivado critical warning message.

	   :class:`VivadoErrorMessage`
	     Representing a Vivado error message.
	"""
	# _MESSAGE_KIND:  ClassVar[str]
	# _REGEXP:        ClassVar[Pattern]

	_toolID:        int
	_toolName:      str
	_messageKindID: int

	def __init__(self, lineNumber: int, kind: LineKind, tool: str, toolID: int, messageKindID: int, message: str) -> None:
		super().__init__(lineNumber, kind, message)
		self._toolID = toolID
		self._toolName = tool
		self._messageKindID = messageKindID

	@readonly
	def ToolName(self) -> str:
		return self._toolName

	@readonly
	def ToolID(self) -> int:
		return self._toolID

	@readonly
	def MessageKindID(self) -> int:
		return self._messageKindID

	@classmethod
	def Parse(cls, lineNumber: int, kind: LineKind, rawMessage: str) -> Nullable[Self]:
		if (match := cls._REGEXP.match(rawMessage)) is not None:
			return cls(lineNumber, kind, match[1], int(match[2]), int(match[3]), match[4])

		return None

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: [{self._toolName} {self._toolID}-{self._messageKindID}] {self._message}"


@export
class VivadoInfoMessage(VivadoMessage, InfoMessage):
	"""
	This class represents an AMD/Xilinx Vivado info message.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "INFO"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""INFO: \[(\w+) (\d+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str) -> Nullable[Self]:
		return super().Parse(lineNumber, LineKind.InfoMessage, rawMessage)


@export
class VivadoIrregularInfoMessage(VivadoMessage, InfoMessage):
	"""
	This class represents an irregular AMD/Xilinx Vivado info message.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "INFO"
	_REGEXP:      ClassVar[Pattern] = re_compile(r"""INFO: \[(\w+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str) -> Nullable[Self]:
		if (match := cls._REGEXP.match(rawMessage)) is not None:
			return cls(lineNumber, LineKind.InfoMessage, match[1], None, int(match[2]), match[3])

		return None

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: [{self._toolName}-{self._messageKindID}] {self._message}"


@export
class VivadoWarningMessage(VivadoMessage, WarningMessage):
	"""
	This class represents an AMD/Xilinx Vivado warning message.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "WARNING"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""WARNING: \[(\w+) (\d+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str) -> Nullable[Self]:
		return super().Parse(lineNumber, LineKind.WarningMessage, rawMessage)


@export
class VivadoIrregularWarningMessage(VivadoMessage, WarningMessage):
	"""
	This class represents an AMD/Xilinx Vivado warning message.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "WARNING"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""WARNING: (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str) -> Nullable[Self]:
		if (match := cls._REGEXP.match(rawMessage)) is not None:
			return cls(lineNumber, LineKind.WarningMessage, None, None, None, match[1])

		return None

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: {self._message}"


@export
class VivadoCriticalWarningMessage(VivadoMessage, CriticalWarningMessage):
	"""
	This class represents an AMD/Xilinx Vivado critical warning message.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "CRITICAL WARNING"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""CRITICAL WARNING: \[(\w+) (\d+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str) -> Nullable[Self]:
		return super().Parse(lineNumber, LineKind.CriticalWarningMessage, rawMessage)


@export
class VivadoErrorMessage(VivadoMessage, ErrorMessage):
	"""
	This class represents an AMD/Xilinx Vivado error message.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "ERROR"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""ERROR: \[(\w+) (\d+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str) -> Nullable[Self]:
		return super().Parse(lineNumber, LineKind.ErrorMessage, rawMessage)


@export
class VHDLReportMessage(VivadoInfoMessage):
	_REGEXP: ClassVar[Pattern ] = re_compile(r"""RTL report: "(.*)" \[(.*):(\d+)\]""")

	_reportMessage:    str
	_sourceFile:       Path
	_sourceLineNumber: int

	def __init__(self, lineNumber: int, tool: str, toolID: int, messageKindID: int, rawMessage: str, reportMessage: str, sourceFile: Path, sourceLineNumber: int):
		super().__init__(lineNumber, LineKind.InfoMessage, tool, toolID, messageKindID, rawMessage)

		self._reportMessage = reportMessage
		self._sourceFile = sourceFile
		self._sourceLineNumber = sourceLineNumber

	@classmethod
	def Convert(cls, line: VivadoInfoMessage) -> Nullable[Self]:
		if (match := cls._REGEXP.match(line._message)) is not None:
			return cls(line._lineNumber, line._toolName, line._toolID, line._messageKindID, line._message, match[1], Path(match[2]), int(match[3]))

		return None


@export
class VHDLAssertionMessage(VHDLReportMessage):
	_REGEXP: ClassVar[Pattern ] = re_compile(r"""RTL assertion: "(.*)" \[(.*):(\d+)\]""")


@export
class VivadoTclCommand(Line):
	_PREFIX: ClassVar[str] = "Command:"

	_command: str
	_args:    Tuple[str, ...]

	def __init__(self, lineNumber: int, command: str, arguments: Tuple[str, ...], tclCommand: str) -> None:
		super().__init__(lineNumber, LineKind.Command, tclCommand)

		self._command = command
		self._args = arguments

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str) -> Nullable[Self]:
		command = rawMessage[len(cls._PREFIX) + 1:]
		args = command.split()

		return cls(lineNumber, args[0], tuple(args[1:]), command)

	def __str__(self) -> str:
		return f"{self._PREFIX} {self._command} {' '.join(self._args)}"


@export
class ProcessingState(Flag):
	Processed =        1
	Skipped =          2
	EmptyLine =        4
	CommentLine =      8
	DelimiterLine =   16
	TableLine =       32
	TableHeader =     64
	Reprocess =      512
	Last =          1024


@export
class BaseProcessor(metaclass=ExtendedType, slots=True):
	# _parsers:  Dict[Type["Parser"], "Parsers"]
	# _state:    Callable[[int, str], bool]
	_duration: float

	_infoMessages:            List[VivadoInfoMessage]
	_warningMessages:         List[VivadoWarningMessage]
	_criticalWarningMessages: List[VivadoCriticalWarningMessage]
	_errorMessages:           List[VivadoErrorMessage]
	_toolIDs:                 Dict[int, str]
	_toolNames:               Dict[str, int]
	_messagesByID:            Dict[int, Dict[int, List[VivadoMessage]]]

	def __init__(self):
		# self._parsers =  {}
		# self._state =    None
		self._duration = 0.0

		self._infoMessages =            []
		self._warningMessages =         []
		self._criticalWarningMessages = []
		self._errorMessages =           []
		self._toolIDs =                 {}
		self._toolNames =               {}
		self._messagesByID =            {}

	@readonly
	def Duration(self) -> float:
		return self._duration

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

	@readonly
	def VHDLReportMessages(self) -> List[VHDLReportMessage]:
		if 8 in self._messagesByID:
			if 6031 in (synthMessages := self._messagesByID[8]):
				return [message for message in synthMessages[6031]]

		return []

	@readonly
	def VHDLAssertMessages(self) -> List[VHDLReportMessage]:
		if 8 in self._messagesByID:
			if 63 in (synthMessages := self._messagesByID[8]):
				return [message for message in synthMessages[63]]

		return []

	# def __getitem__(self, item: Type["Parser"]) -> "Parsers":
	# 	return self._parsers[item]

	def _AddMessageByID(self, message: VivadoMessage) -> None:
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

	def LineClassification(self, documentSlicer: Generator[Union[Line, ProcessorException], Line, None]) -> Generator[Union[Line, ProcessorException], str, None]:
		# Initialize generator
		next(documentSlicer)

		# wait for first line
		rawMessageLine = yield
		lineNumber = 0
		_errorMessage = "Unknown processing error."
		errorMessage = _errorMessage

		while rawMessageLine is not None:
			lineNumber += 1
			rawMessageLine = rawMessageLine.rstrip()
			errorMessage = _errorMessage

			if rawMessageLine.startswith(VivadoInfoMessage._MESSAGE_KIND):
				if (line := VivadoInfoMessage.Parse(lineNumber, rawMessageLine)) is None:
					line = VivadoIrregularInfoMessage.Parse(lineNumber, rawMessageLine)

				errorMessage = f"Line starting with 'INFO' was not a VivadoInfoMessage."
			elif rawMessageLine.startswith(VivadoWarningMessage._MESSAGE_KIND):
				if (line := VivadoWarningMessage.Parse(lineNumber, rawMessageLine)) is None:
					line = VivadoIrregularWarningMessage.Parse(lineNumber, rawMessageLine)

				errorMessage = f"Line starting with 'WARNING' was not a VivadoWarningMessage."
			elif rawMessageLine.startswith(VivadoCriticalWarningMessage._MESSAGE_KIND):
				line = VivadoCriticalWarningMessage.Parse(lineNumber, rawMessageLine)

				errorMessage = f"Line starting with 'CRITICAL WARNING' was not a VivadoCriticalWarningMessage."
			elif rawMessageLine.startswith(VivadoErrorMessage._MESSAGE_KIND):
				line = VivadoErrorMessage.Parse(lineNumber, rawMessageLine)

				errorMessage = f"Line starting with 'ERROR' was not a VivadoErrorMessage."
			elif len(rawMessageLine) == 0:
				line = Line(lineNumber, LineKind.Empty, rawMessageLine)
			elif rawMessageLine.startswith("Command: "):
				line = VivadoTclCommand.Parse(lineNumber, rawMessageLine)
			else:
				line = Line(lineNumber, LineKind.Unprocessed, rawMessageLine)
				errorMessage = "Line starting with 'Command:' was not a VivadoTclCommand."

			if line is None:
				line = Line(lineNumber, LineKind.ProcessorError, rawMessageLine)

			line = documentSlicer.send(line)

			if isinstance(line, VivadoMessage):
				self._AddMessageByID(line)
				if isinstance(line, InfoMessage):
					self._infoMessages.append(line)
				elif isinstance(line, WarningMessage):
					self._warningMessages.append(line)
				elif isinstance(line, CriticalWarningMessage):
					self._criticalWarningMessages.append(line)
				elif isinstance(line, ErrorMessage):
					self._errorMessages.append(line)

			if line._kind is LineKind.ProcessorError:
				line = ClassificationException(errorMessage, rawMessageLine, line)

			rawMessageLine = yield line


@export
class Parser(metaclass=ExtendedType, slots=True):
	_processor: "BaseProcessor"

	def __init__(self, processor: "BaseProcessor"):
		self._processor = processor

	@readonly
	def Processor(self) -> "BaseProcessor":
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
		rawMessage = line._message
		if rawMessage.startswith("#----"):
			line._kind = LineKind.SectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		line = yield line

		while line is not None:
			rawMessage = line._message

			if (match := self._VERSION.match(rawMessage)) is not None:
				self._toolVersion = YearReleaseVersion.Parse(match[1])
				line._kind = LineKind.Normal
			elif (match := self._STARTTIME.match(rawMessage)) is not None:
				self._startDatetime = datetime.strptime(match[1], "%a %b %d %H:%M:%S %Y")
				line._kind = LineKind.Normal
			elif rawMessage.startswith("#----"):
				line._kind = LineKind.SectionDelimiter | LineKind.Last
				break
			else:
				line._kind = LineKind.Verbose

			line = yield line

		check = yield line


@export
class BaseDocument(BaseProcessor):
	_logfile: Path
	_lines:   List[Line]
	# _duration: float

	def __init__(self, logfile: Path) -> None:
		super().__init__()

		self._logfile = logfile
		self._lines =   []

	def Parse(self) -> None:
		with Stopwatch() as sw:
			with self._logfile.open("r", encoding="utf-8") as f:
				content = f.read()

			lines = content.splitlines()
			next(generator := self.LineClassification(self.DocumentSlicer()))
			self._lines = [generator.send(rawLine) for rawLine in lines]

		self._duration = sw.Duration

	def DocumentSlicer(self, line: Line) -> Generator[Union[Line, ProcessorException], Line, Line]:
		while line is not None:
			if line._kind is LineKind.Unprocessed:
				line._kind = LineKind.Normal

			line = yield line
