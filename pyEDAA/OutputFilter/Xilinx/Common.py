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
from enum    import Flag
from pathlib import Path
from re      import Pattern, compile as re_compile
from typing import Optional as Nullable, Self, ClassVar, Tuple, Union, Any

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType


@export
class LineKind(Flag):
	Unprocessed =                0
	ProcessorError =         2** 0
	Empty =                  2** 1
	Delimiter =              2** 2

	Success =                2** 3
	Failed =                 2** 4

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
	Time =                   2**24
	Footer =                 2**25

	Last =                   2**29

	Message =                2**30
	InfoMessage =            Message | Info
	WarningMessage =         Message | Warning
	CriticalWarningMessage = Message | CriticalWarning
	ErrorMessage =           Message | Error

	Task =                   2**31
	TaskStart =              Task | Start
	TaskEnd =                Task | End
	TaskTime =               Task | Time

	Phase =                  2**32
	PhaseDelimiter =         Phase | Delimiter
	PhaseStart =             Phase | Start
	PhaseEnd =               Phase | End
	PhaseTime =              Phase | Time
	PhaseFinal =             Phase | Footer

	SubPhase =               2**33
	SubPhaseStart =          SubPhase | Start
	SubPhaseEnd =            SubPhase | End
	SubPhaseTime =           SubPhase | Time

	SubSubPhase =            2**34
	SubSubPhaseStart =       SubSubPhase | Start
	SubSubPhaseEnd =         SubSubPhase | End
	SubSubPhaseTime =        SubSubPhase | Time

	SubSubSubPhase =         2**35
	SubSubSubPhaseStart =    SubSubSubPhase | Start
	SubSubSubPhaseEnd =      SubSubSubPhase | End
	SubSubSubPhaseTime =     SubSubSubPhase | Time

	Section =                2**36
	SectionDelimiter =       Section | Delimiter
	SectionStart =           Section | Start
	SectionEnd =             Section | End

	SubSection =             2**37
	SubSectionDelimiter =    SubSection | Delimiter
	SubSectionStart =        SubSection | Start
	SubSectionEnd =          SubSection | End

	Paragraph =              2**38
	ParagraphHeadline =      Paragraph | Header

	Hierarchy =              2**39
	HierarchyStart =         Hierarchy | Start
	HierarchyEnd =           Hierarchy | End

	XDC =                    2**40
	XDCStart =               XDC | Start
	XDCEnd =                 XDC | End

	Table =                  2**41
	TableFrame =             Table | Delimiter
	TableHeader =            Table | Header
	TableRow =               Table | Content
	TableFooter =            Table | Footer

	TclCommand =             2**42
	GenericTclCommand =      TclCommand | 2**0
	VivadoTclCommand =       TclCommand | 2**1


@export
class Line(metaclass=ExtendedType, slots=True):
	"""
	This class represents any line in a log file.
	"""
	_lineNumber:    int
	_kind:          LineKind
	_message:       str
	_previousLine:  "Line"
	_nextLine:      "Line"

	def __init__(self, lineNumber: int, kind: LineKind, message: str) -> None:
		self._lineNumber =   lineNumber
		self._kind =         kind
		self._message =      message
		self._previousLine = None
		self._nextLine =     None

	@readonly
	def LineNumber(self) -> int:
		return self._lineNumber

	@readonly
	def Kind(self) -> LineKind:
		return self._kind

	@readonly
	def Message(self) -> str:
		return self._message

	@property
	def PreviousLine(self) -> "Line":
		return self._previousLine

	@PreviousLine.setter
	def PreviousLine(self, line: "Line") -> None:
		self._previousLine = line
		if line is not None:
			line._nextLine = self

	@readonly
	def NextLine(self) -> "Line":
		return self._nextLine

	def Partition(self, separator: str) -> Tuple[str, str, str]:
		return self._message.partition(separator)

	def StartsWith(self, prefix: Union[str, Tuple[str, ...]]):
		return self._message.startswith(prefix)

	def __getitem__(self, item: slice) -> str:
		return self._message[item]

	def __eq__(self, other: Any):
		return self._message == other

	def __ne__(self, other: Any):
		return self._message != other

	def __str__(self) -> str:
		return self._message

	def __repr__(self) -> str:
		return f"{self._lineNumber}: {self._message}"


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

	def __init__(self, lineNumber: int, tool: str, toolID: int, messageKindID: int, rawMessage: str, reportMessage: str, sourceFile: Path, sourceLineNumber: int) -> None:
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
class TclCommand(Line):
	_command: str
	_args:    Tuple[str, ...]

	def __init__(self, lineNumber: int, command: str, arguments: Tuple[str, ...], tclCommand: str) -> None:
		super().__init__(lineNumber, LineKind.GenericTclCommand, tclCommand)

		self._command = command
		self._args = arguments

	@readonly
	def Command(self) -> str:
		return self._command

	@readonly
	def Arguments(self) -> Tuple[str]:
		return self._args

	@classmethod
	def FromLine(cls, line: Line) -> Nullable[Self]:
		args = line._message.split()

		return cls(line._lineNumber, args[0], tuple(args[1:]), line._message)

	def __str__(self) -> str:
		return f"{self._command} {' '.join(self._args)}"


@export
class VivadoTclCommand(TclCommand):
	_PREFIX: ClassVar[str] = "Command:"

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str) -> Nullable[Self]:
		command = rawMessage[len(cls._PREFIX) + 1:]
		args = command.split()

		command = cls(lineNumber, args[0], tuple(args[1:]), command)
		command._kind = LineKind.VivadoTclCommand
		return command

	def __str__(self) -> str:
		return f"{self._PREFIX} {self._command} {' '.join(self._args)}"
