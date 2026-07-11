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
from enum     import Flag
from pathlib  import Path
from re       import Pattern, compile as re_compile
from typing   import Optional as Nullable, Self, Type, ClassVar, Tuple, List, Dict, Generator, Union, Any, Iterator

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType, abstractmethod
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Stopwatch   import Stopwatch
from pyTooling.Versioning  import YearReleaseVersion
from pyTooling.Warning     import WarningCollector, CriticalWarning

from pyEDAA.OutputFilter   import Line, OutputFilterException
from pyEDAA.OutputFilter   import InfoMessage, WarningMessage, CriticalWarningMessage, ErrorMessage


__all__ = ["MAJOR", "MAJOR_MINOR", "MAJOR_MINOR_MICRO", "MAJOR_MINOR_MICRO_NANO"]

MAJOR =                  r"(?P<major>\d+)"
MAJOR_MINOR =            r"(?P<major>\d+)\.(?P<minor>\d+)"
MAJOR_MINOR_MICRO =      r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)"
MAJOR_MINOR_MICRO_NANO = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)\.(?P<nano>\d+)"


@export
def timestampIterator(iterator: Iterator[str], timestamp: datetime) -> Iterator[Tuple[datetime, str]]:
	for line in iterator:
		yield timestamp, line


@export
class ProcessorException(OutputFilterException):
	"""
	Base-class for exceptions raised by processors parsing log outputs.
	"""


@export
class ClassificationException(ProcessorException):
	"""
	Raised if a log output line couldn't be classified.
	"""
	_lineNumber: int  #: Line number of the unclassified line.
	_rawMessage: str  #: Raw message of the unclassified line.

	def __init__(self, errorMessage: str, lineNumber: int, rawMessageLine: str) -> None:
		"""
		Initializes a classification exception.

		:param errorMessage:   Error message why the line couldn't be classified.
		:param lineNumber:     Line number of the unclassified line.
		:param rawMessageLine: Raw message of the unclassified line.
		"""
		super().__init__(errorMessage)

		self._lineNumber = lineNumber
		self._rawMessage = rawMessageLine

	def __str__(self) -> str:
		return f"{self.message}: {self._rawMessage} (at line {self._lineNumber})"


@export
class ParserStateException(ProcessorException):
	"""
	Raised if a log output parser has a broken state.
	"""


@export
class NotPresentException(ProcessorException):
	pass


@export
class CommandNotPresentException(NotPresentException):
	pass


@export
class SectionNotPresentException(NotPresentException):
	pass


@export
class SubSectionNotPresentException(NotPresentException):
	pass


@export
class SubTaskNotPresentException(NotPresentException):
	pass


@export
class PhaseNotPresentException(NotPresentException):
	pass


@export
class NestedTaskNotPresentException(NotPresentException):
	pass


@export
class UndetectedEnd(CriticalWarning):
	_line: "VivadoLine"

	def __init__(self, message: str, line: "VivadoLine") -> None:
		super().__init__(message)

		self._line = line

	@readonly
	def Line(self) -> "VivadoLine":
		return self._line


@export
class UnknownLine(Warning):
	_line: "VivadoLine"

	def __init__(self, message: str, line: "VivadoLine") -> None:
		super().__init__(message)

		self._line = line

	@readonly
	def Line(self) -> "VivadoLine":
		return self._line


@export
class UnknownTask(UnknownLine):
	pass


@export
class UnknownSubTask(UnknownLine):
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
class LineKind(Flag):
	"""
	Classification of a log message line.
	"""
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

	NestedTask =             2**36
	NestedTaskStart =        NestedTask | Start
	NestedTaskEnd =          NestedTask | End

	NestedPhase =            2**37
	NestedPhaseStart =       NestedPhase | Start
	NestedPhaseEnd =         NestedPhase | End

	Section =                2**38
	SectionDelimiter =       Section | Delimiter
	SectionStart =           Section | Start
	SectionEnd =             Section | End

	SubSection =             2**39
	SubSectionDelimiter =    SubSection | Delimiter
	SubSectionStart =        SubSection | Start
	SubSectionEnd =          SubSection | End

	Paragraph =              2**40
	ParagraphHeadline =      Paragraph | Header

	Hierarchy =              2**41
	HierarchyStart =         Hierarchy | Start
	HierarchyEnd =           Hierarchy | End

	XDC =                    2**42
	XDCStart =               XDC | Start
	XDCEnd =                 XDC | End

	Table =                  2**43
	TableFrame =             Table | Delimiter
	TableHeader =            Table | Header
	TableRow =               Table | Content
	TableFooter =            Table | Footer

	TclCommand =             2**44
	GenericTclCommand =      TclCommand | 2**0
	VivadoTclCommand =       TclCommand | 2**1


@export
class LineAction(Flag):
	Default = 0
	Remove =  1


@export
class VivadoLine(Line[LineKind, LineAction]):
	"""
	This class represents any line in a log file.

	A line has a line number (:attr:`_lineNumber`), a message (:attr:`__message`) and a message kind (:attr:`__kind`). In
	addition, all line objects in a log file form a doubly
	linked list.
	"""
	_processor:     "Processor"
	_command:       "Nullable[Command]"

	def __init__(
		self,
		lineNumber:   int,
		kind:         LineKind,
		action:       LineAction,
		message:      str,
		previousLine: Nullable["VivadoLine"] = None
	) -> None:
		super().__init__(lineNumber, kind, action, message, previousLine)

		self._processor = None
		self._command =   None

	@readonly
	def Processor(self) -> "Processor":
		return self._processor

	@readonly
	def Command(self) -> "Nullable[Command]":
		return self._command

	@classmethod
	def Copy(cls, line: "VivadoLine", previousLine: "VivadoLine") -> "VivadoLine":
		newLine = cls(line._lineNumber, line._kind, line._action, line._message, previousLine)
		newLine._timestamp = line._timestamp
		return newLine


@export
class VivadoMessage(VivadoLine):
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

	_toolName:      Nullable[str]
	_toolID:        Nullable[int]
	_messageKindID: Nullable[int]

	def __init__(
		self,
		lineNumber:    int,
		kind:          LineKind,
		action:        LineAction,
		message:       str,
		toolName:      Nullable[str] = None,
		toolID:        Nullable[int] = None,
		messageKindID: Nullable[int] = None,
		previousLine:  Nullable[VivadoLine] = None
	) -> None:
		super().__init__(lineNumber, kind, action, message, previousLine)
		self._toolName =      toolName
		self._toolID =        toolID
		self._messageKindID = messageKindID

	@readonly
	def ToolName(self) -> Nullable[str]:
		return self._toolName

	@readonly
	def ToolID(self) -> Nullable[int]:
		return self._toolID

	@readonly
	def MessageKindID(self) -> Nullable[int]:
		return self._messageKindID

	@classmethod
	def Parse(cls, lineNumber: int, kind: LineKind, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		if (match := cls._REGEXP.match(rawMessage)) is not None:
			return cls(lineNumber, kind, LineAction.Default, match[4], match[1], int(match[2]), int(match[3]), previousLine)

		return None

	@classmethod
	def Copy(cls, line: "VivadoMessage", previousLine: "VivadoLine") -> "VivadoMessage":
		newLine = cls(line._lineNumber, line._kind, line._action, line._message, line._toolName, line._toolID, line._messageKindID, previousLine)
		newLine._timestamp = line._timestamp
		return newLine

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: [{self._toolName} {self._toolID}-{self._messageKindID}] {self._message}"


@export
class VivadoInfoMessage(VivadoMessage, InfoMessage):
	"""
	This class represents an AMD/Xilinx Vivado info message.

	.. rubric:: Example

	.. code-block::

	   INFO: [Common 17-83] 66-Releasing license: Synthesis
	"""

	_MESSAGE_KIND: ClassVar[str] =     "INFO"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""INFO: \[(\w+) (\d+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		return super().Parse(lineNumber, LineKind.InfoMessage, rawMessage, previousLine)

	@classmethod
	def FromMessage(cls, line: VivadoMessage) -> Self:
		message = cls(
			line._lineNumber,
			LineKind.InfoMessage,
			line._message,
			line._toolName,
			line._toolID,
			line._messageKindID,
			previousLine=line._previousLine)
		message._nextLine = line._nextLine
		line._nextLine._previousLine = message

		return message


@export
class VivadoDRCInfoMessage(VivadoMessage, InfoMessage):
	"""
	This class represents an AMD/Xilinx Vivado Design Rule Check (DRC) info message.

	.. rubric:: Example

	.. code-block::

	   INFO: [DRC AVAL-4] enum_USE_DPORT_FALSE_enum_DREG_ADREG_0_connects_CED_CEAD_RSTD_GND: i_system/xbip_dsp48_macro_0/U0/i_synth/i_synth_option.i_synth_model/opt_7series.i_uniwrap/i_primitive: DSP48E1 is not using the D port (USE_DPORT = FALSE). For improved power characteristics, set DREG and ADREG to '1', tie CED, CEAD, and RSTD to logic '0'.
	"""

	_MESSAGE_KIND: ClassVar[str] = "INFO"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""INFO: \[DRC (\w+)-(\d+)\] (.*)""")

	_drcRuleName: str

	def __init__(
		self,
		lineNumber:    int,
		kind:          LineKind,
		action:        LineAction,
		drcRuleName:   str,
		message:       str,
		toolName:      Nullable[str] = None,
		toolID:        Nullable[int] = None,
		messageKindID: Nullable[int] = None,
		previousLine:  Nullable[VivadoLine] = None
	) -> None:
		super().__init__(lineNumber, kind, action, message, toolName, toolID, messageKindID, previousLine)

		self._drcRuleName = drcRuleName

	@readonly
	def DRCRuleName(self) -> str:
		return self._drcRuleName

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		if (match := cls._REGEXP.match(rawMessage)) is not None:
			return cls(lineNumber, LineKind.WarningMessage, LineAction.Default, match[1], match[3], toolName="DRC", toolID=None,
			           messageKindID=int(match[2]), previousLine=previousLine)

		return None

	@classmethod
	def Copy(cls, line: "VivadoDRCInfoMessage", previousLine: "VivadoLine") -> "VivadoDRCInfoMessage":
		newLine = cls(line._lineNumber, line._kind, line._action, line._drcRuleName, line._message, line._toolName, line._toolID, line._messageKindID, previousLine)
		newLine._timestamp = line._timestamp
		return newLine

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: [DRC {self._drcRuleName}-{self._messageKindID}] {self._message}"


@export
class VivadoIrregularInfoMessage(VivadoMessage, InfoMessage):
	"""
	This class represents an irregular AMD/Xilinx Vivado info message.

	.. rubric:: Example

	.. code-block::

	   INFO: [runtcl-4] Executing : report_io -file system_top_io_placed.rpt
	"""

	_MESSAGE_KIND: ClassVar[str] =     "INFO"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""INFO: \[(\w+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		if (match := cls._REGEXP.match(rawMessage)) is not None:
			return cls(lineNumber, LineKind.InfoMessage, LineAction.Default, match[3], toolName=match[1], messageKindID=int(match[2]), previousLine=previousLine)

		return None

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: [{self._toolName}-{self._messageKindID}] {self._message}"


@export
class VivadoStuntedInfoMessage(VivadoMessage, InfoMessage):
	"""
	This class represents a stunted AMD/Xilinx Vivado info message.

	.. rubric:: Example

	.. code-block::

	   INFO: Helper process launched with PID 29056
	"""

	_MESSAGE_KIND: ClassVar[str] =     "INFO"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""INFO: ([^\[].*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		if (match := cls._REGEXP.match(rawMessage)) is not None:
			return cls(lineNumber, LineKind.InfoMessage, LineAction.Default, match[1], previousLine=previousLine)

		return None

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: {self._message}"


@export
class VivadoWarningMessage(VivadoMessage, WarningMessage):
	"""
	This class represents an AMD/Xilinx Vivado warning message.

	.. rubric:: Example

	.. code-block::

	   WARNING: [Synth 8-7080] Parallel synthesis criteria is not met
	"""

	_MESSAGE_KIND: ClassVar[str] =     "WARNING"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""WARNING: \[(\w+(?: \w+)*?) (\d+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		return super().Parse(lineNumber, LineKind.WarningMessage, rawMessage, previousLine=previousLine)

	@classmethod
	def FromMessage(cls, line: VivadoMessage) -> Self:
		message = cls(
			line._lineNumber,
			LineKind.WarningMessage,
			line._message,
			line._toolName,
			line._toolID,
			line._messageKindID,
			previousLine=line._previousLine)
		message._nextLine = line._nextLine
		line._nextLine._previousLine = message

		return message


@export
class VivadoDRCWarningMessage(VivadoMessage, WarningMessage):
	"""
	This class represents an AMD/Xilinx Vivado Design Rule Check (DRC) warning message.

	.. rubric:: Example

	.. code-block::

	   WARNING: [DRC PDCN-1569] LUT equation term check: Used physical LUT pin 'A1' of cell ps/path/to/cell (pin ps/path/to/cell/I0) is not included in the LUT equation: 'O6=(A6+~A6)*((A3*A2)+(A3*(~A2)*A5)+((~A3)*A4*A5)+((~A3)*(~A4)*A2)+((~A3)*(~A4)*(~A2)*A5))'. If this cell is a user instantiated LUT in the design, please remove connectivity to the pin or change the equation and/or INIT string of the LUT to prevent this issue. If the cell is inferred or IP created LUT, please regenerate the IP and/or resynthesize the design to attempt to correct the issue.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "WARNING"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""WARNING: \[DRC (\w+)-(\d+)\] (.*)""")

	_drcRuleName:     str

	def __init__(
		self,
		lineNumber:    int,
		kind:          LineKind,
		action:        LineAction,
		drcRuleName:   str,
		message:       str,
		toolName:      Nullable[str] = None,
		toolID:        Nullable[int] = None,
		messageKindID: Nullable[int] = None,
		previousLine:  Nullable[VivadoLine] = None
	) -> None:
		super().__init__(lineNumber, kind, action, message, toolName, toolID, messageKindID, previousLine)

		self._drcRuleName = drcRuleName

	@readonly
	def DRCRuleName(self) -> str:
		return self._drcRuleName

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		if (match := cls._REGEXP.match(rawMessage)) is not None:
			return cls(lineNumber, LineKind.WarningMessage, LineAction.Default, match[1], match[3], toolName="DRC", toolID=None, messageKindID=int(match[2]), previousLine=previousLine)

		return None

	@classmethod
	def Copy(cls, line: "VivadoDRCWarningMessage", previousLine: "VivadoLine") -> "VivadoDRCWarningMessage":
		newLine = cls(line._lineNumber, line._kind, line._action, line._drcRuleName, line._message, line._toolName, line._toolID, line._messageKindID, previousLine)
		newLine._timestamp = line._timestamp
		return newLine

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: [DRC {self._drcRuleName}-{self._messageKindID}] {self._message}"


@export
class VivadoXPMWarningMessage(VivadoMessage, WarningMessage):
	"""
	This class represents an AMD/Xilinx Vivado XPM warning message.

	.. rubric:: Example

	.. code-block::

	   WARNING: [XPM_CDC_GRAY: TCL-1000] The source and destination clocks are the same.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "WARNING"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""WARNING: \[(XPM_\w+): (\w+)-(\d+)\] (.*)""")

	_xpmName:      str

	def __init__(
		self,
		lineNumber:    int,
		kind:          LineKind,
		action:        LineAction,
		xpmName:      str,
		message:       str,
		toolName:      Nullable[str] = None,
		toolID:        Nullable[int] = None,
		messageKindID: Nullable[int] = None,
		previousLine:  Nullable[VivadoLine] = None
	) -> None:
		super().__init__(lineNumber, kind, action, message, toolName, toolID, messageKindID, previousLine)

		self._xpmName = xpmName

	@readonly
	def XPMName(self) -> str:
		return self._xpmName

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		if (match := cls._REGEXP.match(rawMessage)) is not None:
			return cls(lineNumber, LineKind.WarningMessage, LineAction.Default, match[1], match[4], toolName=match[2], toolID=None, messageKindID=int(match[3]), previousLine=previousLine)

		return None

	@classmethod
	def Copy(cls, line: "VivadoXPMWarningMessage", previousLine: "VivadoLine") -> "VivadoXPMWarningMessage":
		newLine = cls(line._lineNumber, line._kind, line._action, line._xpmName, line._message, line._toolName, line._toolID, line._messageKindID, previousLine)
		newLine._timestamp = line._timestamp
		return newLine

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: [{self._xpmName}: {self._toolName}-{self._messageKindID}] {self._message}"


@export
class VivadoStuntedWarningMessage(VivadoMessage, WarningMessage):
	"""
	This class represents a stunted AMD/Xilinx Vivado warning message.

	.. rubric:: Example

	.. code-block::

	   WARNING: set_property ASYNC_REG could not find object (constraint file  /path/to/sync_Bits_Xilinx.xdc, line 5).
	"""

	_MESSAGE_KIND: ClassVar[str] =     "WARNING"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""WARNING: ([^\[].*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		if (match := cls._REGEXP.match(rawMessage)) is not None:
			return cls(lineNumber, LineKind.WarningMessage, LineAction.Default, match[1], previousLine=previousLine)

		return None

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: {self._message}"


@export
class VivadoCriticalWarningMessage(VivadoMessage, CriticalWarningMessage):
	"""
	This class represents an AMD/Xilinx Vivado critical warning message.

	.. rubric:: Example

	.. code-block::

	   CRITICAL WARNING: [Constraints 18-1056] Clock 'RefClkA_SFP_Quad' completely overrides clock 'USRCLKA_SFP[P]'.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "CRITICAL WARNING"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""CRITICAL WARNING: \[(\w+) (\d+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		return super().Parse(lineNumber, LineKind.CriticalWarningMessage, rawMessage, previousLine)

	@classmethod
	def FromMessage(cls, line: VivadoMessage) -> Self:
		message = cls(
			line._lineNumber,
			LineKind.CriticalWarningMessage,
			line._message,
			line._toolName,
			line._toolID,
			line._messageKindID,
			previousLine=line._previousLine)
		message._nextLine = line._nextLine
		line._nextLine._previousLine = message

		return message


@export
class VivadoErrorMessage(VivadoMessage, ErrorMessage):
	"""
	This class represents an AMD/Xilinx Vivado error message.

	.. rubric:: Example

	.. code-block::

	   ERROR: [Memdata 28-96] Could not find a BMM_INFO_DESIGN property in the design. Could not generate the merged BMM file: C:/Users/username/git/design.runs/impl_1/system_top_bd.bmm
	"""

	_MESSAGE_KIND: ClassVar[str] =     "ERROR"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""ERROR: \[(\w+) (\d+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		return super().Parse(lineNumber, LineKind.ErrorMessage, rawMessage, previousLine)

	@classmethod
	def FromMessage(cls, line: VivadoMessage) -> Self:
		message = cls(
			line._lineNumber,
			LineKind.ErrorMessage,
			line._message,
			line._toolName,
			line._toolID,
			line._messageKindID,
			previousLine=line._previousLine)
		message._nextLine = line._nextLine
		line._nextLine._previousLine = message

		return message


@export
class VHDLReportMessage(VivadoInfoMessage):
	_REGEXP2: ClassVar[Pattern ] = re_compile(r"""RTL report: "(.*)" \[(.*):(\d+)\]""")  # todo: workaround for ClassVar problem

	_reportMessage:    str
	_sourceFile:       Path
	_sourceLineNumber: int

	def __init__(
		self,
		lineNumber:       int,
		rawMessage:       str,
		toolName:         str,
		toolID:           int,
		messageKindID:    int,
		reportMessage:    str,
		sourceFile:       Path,
		sourceLineNumber: int,
		previousLine:     Nullable[VivadoLine] = None
	) -> None:
		super().__init__(lineNumber, LineKind.InfoMessage, LineAction.Default, rawMessage, toolName, toolID, messageKindID, previousLine)

		self._reportMessage = reportMessage
		self._sourceFile = sourceFile
		self._sourceLineNumber = sourceLineNumber

	@classmethod
	def Convert(cls, line: VivadoInfoMessage) -> Nullable[Self]:
		if (match := cls._REGEXP2.match(line._message)) is not None:
			return cls(line._lineNumber, line._message, line._toolName, line._toolID, line._messageKindID, match[1], Path(match[2]), int(match[3]), previousLine=line._previousLine)

		return None

	@classmethod
	def Copy(cls, line: "VHDLReportMessage", previousLine: "VivadoLine") -> "VHDLReportMessage":
		newLine = cls(line._lineNumber, line._message, line._toolName, line._toolID, line._messageKindID, line._reportMessage, line._sourceFile, line._sourceLineNumber, previousLine)
		newLine._timestamp = line._timestamp
		return newLine

@export
class VHDLAssertionMessage(VHDLReportMessage):
	_REGEXP3: ClassVar[Pattern ] = re_compile(r"""RTL assertion: "(.*)" \[(.*):(\d+)\]""")  # todo: workaround for ClassVar problem

	@classmethod
	def Convert(cls, line: VivadoInfoMessage) -> Nullable[Self]:
		if (match := cls._REGEXP3.match(line._message)) is not None:
			return cls(line._lineNumber, line._message, line._toolName, line._toolID, line._messageKindID, match[1], Path(match[2]), int(match[3]), previousLine=line._previousLine)

		return None


@export
class TclCommand(VivadoLine):
	"""
	Represents a TCL command found in a Vivado log output.

	Besides the full log message (:class:`Line`), this class splits the TCL command into the command name and its
	arguments.
	"""
	_tclCommand: str
	_arguments:  Tuple[str, ...]

	def __init__(
		self,
		lineNumber:   int,
		tclCommand:   str,
		arguments:    Tuple[str, ...],
		rawMessage:   str,
		previousLine: Nullable[VivadoLine] = None
	) -> None:
		super().__init__(lineNumber, LineKind.GenericTclCommand, LineAction.Default, rawMessage, previousLine)

		self._tclCommand = tclCommand
		self._arguments =  arguments

	@readonly
	def TCLCommand(self) -> str:
		return self._tclCommand

	@readonly
	def Arguments(self) -> Tuple[str, ...]:
		return self._arguments

	@classmethod
	def FromLine(cls, line: VivadoLine) -> Nullable[Self]:
		args = line._message.split()

		return cls(line._lineNumber, args[0], tuple(args[1:]), line._message, previousLine=line._previousLine)

	@classmethod
	def Copy(cls, line: "TclCommand", previousLine: VivadoLine) -> "TclCommand":
		newLine = cls(line._lineNumber, line._tclCommand, line._arguments, line._message, previousLine)
		newLine._timestamp = line._timestamp
		return newLine

	def __str__(self) -> str:
		return f"{self._tclCommand} {' '.join(self._arguments)}"


@export
class VivadoTclCommand(TclCommand):
	"""
	Represents a Vivado specific TCL command.
	"""

	_PREFIX: ClassVar[str] = "Command:"

	@classmethod
	def Parse(cls, lineNumber: int, rawMessage: str, previousLine: Nullable[VivadoLine] = None) -> Nullable[Self]:
		tclCommand = rawMessage[len(cls._PREFIX) + 1:]
		args = tclCommand.split()

		vivadoCommand = cls(lineNumber, args[0], tuple(args[1:]), rawMessage, previousLine)
		vivadoCommand._kind = LineKind.VivadoTclCommand
		return vivadoCommand

	def __str__(self) -> str:
		return f"{self._PREFIX} {self._tclCommand} {' '.join(self._arguments)}"


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
			if message._toolID is not None:
				self._toolIDs[message._toolID] = message._toolName
				self._toolNames[message._toolName] = message._toolID

			self._messagesByID[message._toolID] = {message._messageKindID: [message]}


# todo: check usage or merge with parser
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
class Preamble(Parser, VivadoMessagesMixin):
	_toolVersion:   Nullable[YearReleaseVersion]  #: Used Vivado version.
	_startDateTime: Nullable[datetime]            #: Session start timestamp.

	def __init__(self, processor: "BaseProcessor") -> None:
		"""
		Initializes a Vivado preamble parser.

		:param processor: Reference to the Vivado log processor.
		"""
		super().__init__(processor)
		VivadoMessagesMixin.__init__(self)

		self._toolVersion =   None
		self._startDateTime = None

	@readonly
	def ToolVersion(self) -> YearReleaseVersion:
		"""
		Read-only property to access the extracted Vivado tool version.

		:returns: The used Vivado version as reported in the Vivado log messages.
		"""
		return self._toolVersion

	@readonly
	def StartDateTime(self) -> datetime:
		"""
		Read-only property to access the date and time when the Vivado session was started.

		:returns:                   Datatime when the session was started.
		:raises ProcessorException: When start timestamp wasn't extracted from preamble.
		"""
		if self._startDateTime is None:
			raise ProcessorException("No start timestamp extracted from preamble.")

		return self._startDateTime

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		"""
		A generator for processing the Vivado session preamble line-by-line.

		:param line: First line to process.
		:returns:    A generator processing log messages.
		"""
		delimiterCount = 0

		# a normal preamble has up to 23 lines including both delimiter lines.
		for _ in range(30):
			if (match := self._VERSION.match(line._message)) is not None:
				self._toolVersion = YearReleaseVersion.Parse(match[1])
				line._kind = LineKind.Normal
			elif (match := self._STARTTIME.match(line._message)) is not None:
				self._startDateTime = datetime.strptime(match[1], "%a %b %d %H:%M:%S %Y")
				line._kind = LineKind.Normal
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			elif self._IsPreambleDelimiter(line):
				line._kind = LineKind.SectionDelimiter
				if (delimiterCount := delimiterCount + 1) == 2:
					break
			else:
				line._kind = LineKind.Verbose

			line = yield line
		else:
			raise OutputFilterException(f"Preamble is longer than 30 lines or delimiter was not detected.")

		if self._toolVersion is None:
			raise OutputFilterException(f"Tool version not found in preamble.")
		elif self._startDateTime is None:
			raise OutputFilterException(f"Session start time and date not found in preamble.")

		nextLine = yield line
		return nextLine

	def __str__(self) -> str:
		return f"Vivado {self._toolVersion}: started at {self._startDateTime}"


@export
class LogFilePreamble(Preamble):
	"""
	A parser for the preamble emitted by Vivado at session start.

	.. rubric:: Extracted information

	* Vivado tool version. |br|
	  See :data:`ToolVersion`
	* Session start timestamp (date and time). |br|
	  See :data:`StartDateTime`

	.. rubric:: Example

	.. code-block::

	   INFO: [Common 17-3922] A valid Vivado Design Suite ENTERPRISE license has been detected. Your current license is active and will expire on Permanent.
	   #-----------------------------------------------------------
	   # Vivado v2025.1 (64-bit)
	   # SW Build 6140274 on Thu May 22 00:12:29 MDT 2025
	   # IP Build 6138677 on Thu May 22 03:10:11 MDT 2025
	   # SharedData Build 6139179 on Tue May 20 17:58:58 MDT 2025
	   # Start of session at: Thu Jun 12 18:39:05 2025
	   # Process ID         : 28856
	   # Current directory  : C:/Git/.../StopWatch/project/4_WithTiming.runs/impl_1
	   # Command line       : vivado.exe -log toplevel.vdi -applog -product Vivado -messageDb vivado.pb -mode batch -source toplevel.tcl -notrace
	   # Log file           : C:/Git/.../StopWatch/project/4_WithTiming.runs/impl_1/toplevel.vdi
	   # Journal file       : C:/Git/.../StopWatch/project/4_WithTiming.runs/impl_1\vivado.jou
	   # Running On         : Paebbels
	   # Platform           : Windows Server 2016 or Windows 10
	   # Operating System   : 26100
	   # Processor Detail   : 11th Gen Intel(R) Core(TM) i9-11950H @ 2.60GHz
	   # CPU Frequency      : 2611 MHz
	   # CPU Physical cores : 8
	   # CPU Logical cores  : 16
	   # Host memory        : 34048 MB
	   # Swap memory        : 28991 MB
	   # Total Virtual      : 63039 MB
	   # Available Virtual  : 29246 MB
	   #-----------------------------------------------------------
	"""
	_VERSION:       ClassVar[Pattern] = re_compile(r"""# Vivado v(\d+\.\d(\.\d)?) \(64-bit\)""")
	_STARTTIME:     ClassVar[Pattern] = re_compile(r"""# Start of session at: (\w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+\d+)""")

	def _IsPreambleDelimiter(self, line: VivadoLine):
		return line.StartsWith("#----------")


@export
class VivadoPipedPreamble(Preamble):
	"""
	A parser for the preamble emitted by Vivado at session start.

	.. rubric:: Extracted information

	* Vivado tool version. |br|
	  See :data:`ToolVersion`
	* Session start timestamp (date and time). |br|
	  See :data:`StartDateTime`

	.. rubric:: Example

	.. code-block::

	   ****** Vivado v2024.2 (64-bit)
	     **** SW Build 5239630 on Fri Nov 08 22:35:27 MST 2024
	     **** IP Build 5239520 on Sun Nov 10 16:12:51 MST 2024
	     **** SharedData Build 5239561 on Fri Nov 08 14:39:27 MST 2024
	     **** Start of session at: Wed Jul  1 23:50:26 2026
	       ** Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
	       ** Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.

	"""
	_VERSION:       ClassVar[Pattern] = re_compile(r"""\*\*\*\*\*\* Vivado v(\d+\.\d(\.\d)?) \(64-bit\)""")
	_STARTTIME:     ClassVar[Pattern] = re_compile(r"""  \*\*\*\* Start of session at: (\w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+\d+)""")

	def _IsPreambleDelimiter(self, line: VivadoLine):
		return line._kind is LineKind.Empty


@export
class Postamble(Parser, VivadoMessagesMixin):  # todo: double mixin?
	"""
	A parser for the postamble emitted by Vivado at session end.

	.. rubric:: Extracted information

	* Session exit timestamp (date and time). |br|
	  See :data:`ExitDateTime`

	.. rubric:: Example

	.. code-block::

	   INFO: [Common 17-206] Exiting Vivado at Tue Sep  2 08:46:23 2025...

	"""
	_INFO:    Tuple[int, int]   = (17, 206)
	_ENDTIME: ClassVar[Pattern] = re_compile(r"""Exiting Vivado at (\w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+\d+)""")

	_exitDateTime: Nullable[datetime]            #: Session exit timestamp.

	def __init__(self, processor: "BaseProcessor") -> None:
		"""
		Initializes a Vivado postamble parser.

		:param processor: Reference to the Vivado log processor.
		"""
		super().__init__(processor)
		VivadoMessagesMixin.__init__(self)

		self._exitDateTime = None

	@readonly
	def ExitDateTime(self) -> Nullable[datetime]:
		"""
		Read-only property to access the date and time when the Vivado session was exited.

		:returns:                   Datatime when the session was exited.
		:raises ProcessorException: When exit timestamp wasn't extracted from postamble.
		"""
		if self._exitDateTime is None:
			raise ProcessorException("No exit timestamp extracted from postamble.")

		return self._exitDateTime

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		"""
		A generator for processing the Vivado session preamble line-by-line.

		:param line: First line to process.
		:returns:    A generator processing log messages.
		"""
		if isinstance(line, VivadoMessage):
			self._AddMessage(line)

			if not isinstance(line, VivadoInfoMessage):
				raise ProcessorException(f"{self.__class__.__name__}.Generator(): Expected '{self._ENDTIME}' at line {line._lineNumber}.")

		if (match := self._ENDTIME.match(line._message)) is not None:
			self._exitDateTime = datetime.strptime(match[1], "%a %b %d %H:%M:%S %Y")
		else:
			pass

		line = yield line

		# todo: should we receive and expect an ned-token like None?
		return line

@export
class Command(Parser):
	"""
	This parser parses outputs from Vivado TCL commands.

	Depending on the command's output (and how it's implemented), they use different subcategories.

	.. rubric:: Command subcategories

	* :class:`CommandWithSections`
	* :class:`CommandWithtasks`

	.. rubric:: Supported commands

	* :class:`SynthesizeDesign`
	* :class:`LinkDesign`
	* :class:`OptimizeDesign`
	* :class:`PlaceDesign`
	* :class:`PhysicalOptimizeDesign`
	* :class:`RouteDesign`
	* :class:`WriteBitstream`
	* :class:`ReportDRC`
	* :class:`ReportMethodology`
	* :class:`ReportPower`

	.. rubric:: Example

	.. code-block::

     [...]
	   Command: synth_design -top system_top -part xc7z015clg485-2
     Starting synth_design
     [...]
	"""

	# _TCL_COMMAND: ClassVar[str]

	def _CommandStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		"""
		A generator accepting a line containing the expected Vivado TCL command.

		When the generator exits, the returned line is the successor line to the line containing the Vivado TCL command.

		:param line: The first line for the generator to process.
		:returns:    A generator processing Vivado output log lines.
		"""
		if not (isinstance(line, VivadoTclCommand) and line._tclCommand == self._TCL_COMMAND):
			raise ProcessorException()  # FIXME: add exception message

		nextLine = yield line
		return nextLine

	def _CommandFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		if line.StartsWith(f"{self._TCL_COMMAND} completed successfully"):
			line._kind |= LineKind.Success
		else:
			line._kind |= LineKind.Failed

		line = yield line

		if self._TIME is not None:  # and self._processor._preamble._toolVersion > "2022.2":
			end = f"{self._TCL_COMMAND}: {self._TIME}"

			# while True:  # TODO: limit search for time to 10 lines
			# 	if line.StartsWith(end):
			# 		line._kind = LineKind.TaskTime
			# 		line = yield line
			# 		break
			#
			# 	line = yield line

			if line.StartsWith(end):
				line._kind = LineKind.TaskTime
				line = yield line

		return line

	def SectionDetector(self, line: VivadoLine) -> Generator[Union[VivadoLine, ProcessorException], VivadoLine, None]:
		line = yield from self._CommandStart(line)

		end = f"{self._TCL_COMMAND} "
		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			elif line.StartsWith(end):
				nextLine = yield from self._CommandFinish(line)
				return nextLine

			line = yield line

	def __str__(self) -> str:
		return f"{self._TCL_COMMAND}"


@export
class CommandWithSections(Command):
	"""
	A Vivado command writing sections into the output log.

	.. rubric:: Example

	.. code-block::

	   [...]
	   ---------------------------------------------------------------------------------
	   Starting RTL Elaboration : Time (s): cpu = 00:00:03 ; elapsed = 00:00:03 . Memory (MB): peak = 847.230 ; gain = 176.500
	   ---------------------------------------------------------------------------------
	   INFO: [Synth 8-638] synthesizing module 'system_top' [C:/Users/tgomes/git/2019_1/src/system_top_PE1.vhd:257]
	   [...]
	   [...]
	   [...]
	   ---------------------------------------------------------------------------------
	   Finished RTL Elaboration : Time (s): cpu = 00:00:04 ; elapsed = 00:00:04 . Memory (MB): peak = 917.641 ; gain = 246.910
	   ---------------------------------------------------------------------------------
	   [...]
	"""
	# _PARSERS:   ClassVar[Tuple[Type[Section], ...]]

	_sections:  List["Section"]  # Dict[Type["Section"], "Section"]


	def __init__(self, processor: "Processor") -> None:
		super().__init__(processor)

		self._sections =  []  # p: p(self) for p in self._PARSERS}

	@readonly
	def Sections(self) -> List["Section"]:  # Dict[Type["Section"], "Section"]:
		"""
		Read-only property to access a dictionary of found sections within the TCL command's output.

		:returns: A dictionary of found :class:`~pyEDAA.OutputFilter.Xilinx.SynthesizeDesign.Section`s.
		"""
		return self._sections

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, Section):
			ex = TypeError(f"Parameter 'key' is not a Section.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		for section in self._sections:
			if isinstance(section, key):
				return True
		else:
			return False

	def __getitem__(self, key: Type["Section"]) -> "Section":
		if not issubclass(key, Section):
			ex = TypeError(f"Parameter 'key' is not a Section.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		for section in self._sections:
			if isinstance(section, key):
				return section
		else:
			raise SectionNotPresentException(F"Section '{key._NAME}' not present in '{self._parent.logfile}'.")


@export
class CommandWithTasks(Command):
	"""
	A Vivado command writing tasks into the output log.

	.. rubric:: Example

	.. code-block::

     [...]
     Starting Cache Timing Information Task
     INFO: [Timing 38-35] 79-Done setting XDC timing constraints.
     [...]
     [...]
     Ending Cache Timing Information Task | Checksum: 19fe8cb97
     [...]
	"""
	# _PARSERS: Tuple[Type[Task], ...]

	_tasks: Dict[Type["Task"], "Task"]

	def __init__(self, processor: "Processor") -> None:
		super().__init__(processor)

		self._tasks = {p: p(self) for p in self._PARSERS}

	@readonly
	def Tasks(self) -> Dict[Type["Task"], "Task"]:
		"""
		Read-only property to access a dictionary of found tasks within the TCL command's output.

		:returns: A dictionary of found :class:`~pyEDAA.OutputFilter.Xilinx.Common2.Task`s.
		"""
		return self._tasks

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, Task):
			ex = TypeError(f"Parameter 'key' is not a Task.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._tasks

	def __getitem__(self, key: Type["Task"]) -> "Task":
		try:
			return self._tasks[key]
		except KeyError as ex:
			raise SectionNotPresentException(F"Task '{key._NAME}' not present in '{self._parent.logfile}'.") from ex


@export
class BaseSection(metaclass=ExtendedType, mixin=True):
	@abstractmethod
	def _SectionStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		pass

	@abstractmethod
	def _SectionFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, None]:
		pass

	@abstractmethod
	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		pass


@export
class Section(BaseParser, BaseSection):
	"""
	Base-class for sections within log outputs from *synthesize design*.
	"""
	# _NAME:       ClassVar[str]
	# _START:      ClassVar[str]
	# _FINISH:     ClassVar[str]
	# _DUPLICATES: ClassVar[bool]

	_command:  "Command"  #: Reference to the command (parent).
	_next:     Nullable["Section"]
	_duration: float      #: Duration synthesis spent in processing a synthesis step logged in this log output section.

	def __init__(self, command: "Command") -> None:
		"""
		Initialized a section.

		:param command: Reference to the parent TCL command.
		"""
		super().__init__()  #command._processor)

		self._command =  command
		self._next =     None
		self._duration = 0.0

	@readonly
	def Next(self) -> Nullable["Section"]:
		"""
		Read-only property to access the next section in case the section appeared multiple times.

		:returns: Next section of same type.
		"""
		return self._next

	@readonly
	def Duration(self) -> float:
		"""
		Read-only property to access the duration synthesis spent in processing a synthesis step logged in this log output
		section.

		:returns: Synthesis step duration in seconds.
		"""
		return self._duration

	def __iter__(self) -> Generator["Section", None, None]:
		section = self._next
		while section is not None:
			yield section

	def _SectionStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line._kind = LineKind.SectionStart

		line = yield line
		if line.StartsWith("----"):
			line._kind = LineKind.SectionStart | LineKind.SectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		nextLine = yield line
		return nextLine

	def _SectionFinish(self, line: VivadoLine, skipDashes: bool = False) -> Generator[VivadoLine, VivadoLine, None]:
		if not skipDashes:
			if line.StartsWith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
			else:
				line._kind |= LineKind.ProcessorError

			line = yield line

		if line.StartsWith(self._FINISH):
			line._kind = LineKind.SectionEnd
		else:
			line._kind |= LineKind.ProcessorError

		line = yield line
		if line.StartsWith("----"):
			line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		nextLine = yield line
		return nextLine

	# @mustoverride
	# def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
	# 	if len(line) == 0:
	# 		return ProcessingState.EmptyLine
	# 	elif line.startswith("----"):
	# 		return ProcessingState.DelimiterLine
	# 	elif line.startswith(self._START):
	# 		return ProcessingState.Skipped
	# 	elif line.startswith(self._FINISH):
	# 		l = line[len(self._FINISH):]
	# 		if (match := TIME_MEMORY_PATTERN.match(l)) is not None:
	# 			# cpuParts = match[1].split(":")
	# 			elapsedParts = match[2].split(":")
	# 			# peakMemory = float(match[3])
	# 			# gainMemory = float(match[4])
	# 			self._duration = int(elapsedParts[0]) * 3600 + int(elapsedParts[1]) * 60 + int(elapsedParts[2])
	#
	# 		return ProcessingState.Skipped | ProcessingState.Last
	# 	elif line.startswith("Start") or line.startswith("Starting"):
	# 		print(f"ERROR: didn't find finish\n  {line}")
	# 		return ProcessingState.Reprocess
	#
	# 	return ProcessingState.Skipped

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._SectionStart(line)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			else:
				line._kind = LineKind.Verbose

			line = yield line

		# line = yield line
		nextLine = yield from self._SectionFinish(line)
		return nextLine


@export
class SubSection(BaseParser, BaseSection):
	"""
	Base-class for subsections within log outputs from *synthesize design*.
	"""
	# _NAME:    ClassVar[str]

	_section: Section  #: Reference to the section (parent).

	def __init__(self, section: Section) -> None:
		"""
		Initialized a subsection.

		:param section: Reference to the parent section.
		"""
		super().__init__()
		self._section = section

	def _SectionStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line._kind = LineKind.SubSectionStart

		line = yield line
		if line.StartsWith("----"):
			line._kind = LineKind.SubSectionStart | LineKind.SubSectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		nextLine = yield line
		return nextLine

	def _SectionFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, None]:
		if line.StartsWith("----"):
			line._kind = LineKind.SubSectionEnd | LineKind.SubSectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		line = yield line
		if line.StartsWith(self._FINISH):
			line._kind = LineKind.SubSectionEnd
		else:
			line._kind |= LineKind.ProcessorError

		line = yield line
		if line.StartsWith("----"):
			line._kind = LineKind.SubSectionEnd | LineKind.SubSectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		nextLine = yield line
		return nextLine

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._SectionStart(line)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith("----"):
				line._kind = LineKind.SubSectionEnd | LineKind.SubSectionDelimiter
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			else:
				line._kind = LineKind.Verbose

			line = yield line

		nextLine = yield from self._SectionFinish(line)
		return nextLine


@export
class SectionWithChildren(Section):
	"""
	Base-class for sections with subsections.
	"""
	_subsections: Dict[Type[SubSection], SubSection]

	def __init__(self, command: "Command") -> None:
		super().__init__(command)

		self._subsections = {}

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, SubSection):
			ex = TypeError(f"Parameter 'item' is not a SubSection.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._subsections

	def __getitem__(self, item: Type[SubSection]) -> SubSection:
		try:
			return self._subsections[item]
		except KeyError as ex:
			raise SubSectionNotPresentException(f"SubSection '{item._NAME}' not present in '{self._parent._parent.logfile}'.") from ex


@export
class Task(BaseParser, VivadoMessagesMixin):
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
	# _NAME:   ClassVar[str]
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

	def _TaskStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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

	def _TaskFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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

		nextLine = yield line
		return nextLine

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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
	# _PARSERS:  ClassVar[Tuple[Type["SubTask"], ...]]

	_subtasks: Dict[Type["SubTask"], "SubTask"]

	def __init__(self, command: "Command") -> None:
		super().__init__(command)

		self._subtasks =  {p: p(self) for p in self._PARSERS}

	@readonly
	def SubTasks(self) -> Dict[Type["SubTask"], "SubTask"]:
		return self._subtasks

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, SubTask):
			ex = TypeError(f"Parameter 'key' is not a Subtask.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._subtasks

	def __getitem__(self, key: Type["SubTask"]) -> "SubTask":
		try:
			return self._subtasks[key]
		except KeyError as ex:
			raise SubTaskNotPresentException(F"Subtask '{key._NAME}' not present in '{self._parent.logfile}'.") from ex

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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
						WarningCollector.Raise(UnknownSubTask(f"Unknown subtask: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown subtask: '{line!r}'")
						ex.add_note(f"Current task:    start pattern='{self}'")
						ex.add_note(f"Current command: {self._command}")
						raise ex
					break
				elif line.StartsWith("Ending"):
					nextLine = yield from self._TaskFinish(line)
					return nextLine
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.TaskTime
					nextLine = yield line
					return nextLine

				line = yield line

			while True:
				isFinish = False  # line.StartsWith("Ending") # FIXME: detect end, but time might come later

				try:
					processedLine = subtask.send(line)

					if isinstance(processedLine, VivadoMessage):
						self._AddMessage(processedLine)

					if isFinish:
						WarningCollector.Raise(UndetectedEnd(f"Didn't detect finish: '{processedLine!r}'", processedLine))
						line = yield processedLine
						break
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break

				line = yield processedLine


@export
class SubTask(BaseParser, VivadoMessagesMixin):
	# _NAME:     ClassVar[str]
	# _START:    ClassVar[str]
	# _FINISH:   ClassVar[str]
	_TIME:     ClassVar[str] = "Time (s):"

	_task:     TaskWithSubTasks
	_duration: float

	def __init__(self, task: TaskWithSubTasks) -> None:
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._task = task

	@readonly
	def Task(self) -> TaskWithSubTasks:
		return self._task

	def _TaskStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		if not line.StartsWith(self._START):
			raise ProcessorException(f"{self.__class__.__name__}._TaskStart(): Expected '{self._START}' at line {line._lineNumber}.")

		line._kind = LineKind.TaskStart
		nextLine = yield line
		return nextLine

	def _TaskFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException(f"{self.__class__.__name__}._TaskFinish(): Expected '{self._FINISH}' at line {line._lineNumber}.")

		line._kind = LineKind.TaskEnd
		line = yield line
		while self._TIME is not None:
			if line.StartsWith(self._TIME):
				line._kind = LineKind.TaskTime
				break

			line = yield line

		nextLine = yield line
		return nextLine

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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
			ex = TypeError(f"Parameter 'key' is not a Phase.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._phases

	def __getitem__(self, key: Type["Phase"]) -> "Phase":
		try:
			return self._phases[key]
		except KeyError as ex:
			raise PhaseNotPresentException(F"Phase '{key._NAME}' not present in '{self._parent.logfile}'.") from ex

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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
						WarningCollector.Raise(UnknownPhase(f"Unknown phase: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown phase: '{line!r}'")
						ex.add_note(f"Current task:    start pattern='{self}'")
						ex.add_note(f"Current command: {self._command}")
						raise ex
					break
				elif line.StartsWith("Ending"):
					nextLine = yield from self._TaskFinish(line)
					return nextLine
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.TaskTime
					nextLine = yield line
					return nextLine

				line = yield line

			while True:
				isFinish = False  #line.StartsWith("Ending")

				try:
					processedLine = phase.send(line)

					if isinstance(processedLine, VivadoMessage):
						self._AddMessage(processedLine)

					if isFinish:
						WarningCollector.Raise(UndetectedEnd(f"Didn't detect finish: '{processedLine!r}'", processedLine))
						line = yield processedLine
						break
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break

				line = yield processedLine


@export
class Phase(BaseParser, VivadoMessagesMixin):
	# _NAME:   ClassVar[str]
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	# _TIME:   ClassVar[str] = "Time (s):"
	# _FINAL:  ClassVar[Nullable[str]] = None

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

	def _PhaseStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		if (match := self._START.match(line._message)) is None:
			raise ProcessorException(f"{self.__class__.__name__}._PhaseStart(): Expected '{self._START}' at line {line._lineNumber}.")

		self._phaseIndex = int(match["major"])

		line._kind = LineKind.PhaseStart
		nextLine = yield line
		return nextLine

	def _PhaseFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, None]:
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex)
		if not line.StartsWith(FINISH):
			raise ProcessorException(f"{self.__class__.__name__}._PhaseFinish(): Expected '{FINISH}' at line {line._lineNumber}.")

		line._kind = LineKind.PhaseEnd
		line = yield line

		if self._TIME is not None:
			while True:
				if line.StartsWith(self._TIME):
					line._kind = LineKind.PhaseTime
					break
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)

				line = yield line

			line = yield line

		if self._FINAL is not None and self._task._command._processor._preamble._toolVersion >= "2023.2":
			while True:
				if line.StartsWith(self._FINAL):
					line._kind = LineKind.PhaseFinal
					break
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)

				line = yield line

			line = yield line

		# TODO: optionally collect following INFO messages like 31-389, 31-1021, 31-662

		return line

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, SubPhase):
			ex = TypeError(f"Parameter 'item' is not a SubPhase.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._subPhases

	def __getitem__(self, key: Type["SubPhase"]) -> "SubPhase":
		try:
			return self._subPhases[key]
		except KeyError as ex:
			raise PhaseNotPresentException(F"SubPhase '{key._NAME}' not present in '{self._parent.logfile}'.") from ex

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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

			while True:
				isFinish = False  # line.StartsWith(SUBPHASE_PREFIX)  # FIXME: detect end, but end (e.g. time) is later then ending text

				try:
					processedLine = phase.send(line)

					if isinstance(processedLine, VivadoMessage):
						self._AddMessage(processedLine)

					if isFinish:
						WarningCollector.Raise(UndetectedEnd(f"Didn't detect finish: '{processedLine!r}'", processedLine))
						line = yield processedLine
						break
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break

				line = yield processedLine


@export
class SubPhase(BaseParser, VivadoMessagesMixin):
	# _NAME:   ClassVar[str]
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

	def _SubPhaseStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		if (match := self._START.match(line._message)) is None:
			raise ProcessorException(f"{self.__class__.__name__}._SubPhaseStart(): Expected '{self._START}' at line {line._lineNumber}.")

		self._phaseIndex =    int(match["major"])
		self._subPhaseIndex = int(match["minor"])

		line._kind = LineKind.SubPhaseStart
		nextLine = yield line
		return nextLine

	def _SubPhaseFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, None]:
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

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, SubSubPhase):
			ex = TypeError(f"Parameter 'item' is not a SubSubPhase.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._subSubPhases

	def __getitem__(self, key: Type["SubSubPhase"]) -> "SubSubPhase":
		try:
			return self._subSubPhases[key]
		except KeyError as ex:
			raise PhaseNotPresentException(F"SubSubPhase '{key._NAME}' not present in '{self._parent.logfile}'.") from ex

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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
						ex.add_note(f"Current subphase: start pattern='{self}'")
						ex.add_note(f"Current phase: start pattern='{self._phase}'")
						ex.add_note(f"Current task: start pattern='{self._phase._task}'")
						ex.add_note(f"Current cmd:  {self._phase._task._command}")
						raise ex
					break
				elif line.StartsWith(FINISH):
					nextLine = yield from self._SubPhaseFinish(line)
					return nextLine

				line = yield line

			while True:
				isFinish = False  # line.StartsWith("Ending")

				try:
					processedLine = phase.send(line)

					if isinstance(processedLine, VivadoMessage):
						self._AddMessage(processedLine)

					if isFinish:
						WarningCollector.Raise(UndetectedEnd(f"Didn't detect finish: '{processedLine!r}'", processedLine))
						line = yield processedLine
						break
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break

				line = yield processedLine


@export
class SubSubPhase(BaseParser, VivadoMessagesMixin):
	# _NAME:   ClassVar[str]
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

	def _SubSubPhaseStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		if (match := self._START.match(line._message)) is None:
			raise ProcessorException()

		self._phaseIndex =       int(match["major"])
		self._subPhaseIndex =    int(match["minor"])
		self._subSubPhaseIndex = int(match["micro"])

		line._kind = LineKind.SubSubPhaseStart
		nextLine = yield line
		return nextLine

	def _SubSubPhaseFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, None]:
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

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, SubSubSubPhase):
			ex = TypeError(f"Parameter 'item' is not a SubSubSubPhase.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._subSubSubPhases

	def __getitem__(self, key: Type["SubSubSubPhase"]) -> "SubSubSubPhase":
		try:
			return self._subSubSubPhases[key]
		except KeyError as ex:
			raise PhaseNotPresentException(F"SubSubSubPhase '{key._NAME}' not present in '{self._parent.logfile}'.") from ex

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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
						WarningCollector.Raise(UnknownSubPhase(f"Unknown subsubsubphase: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown subsubsubphase: '{line!r}'")
						ex.add_note(f"Current subsubphase: start pattern='{self}'")
						ex.add_note(f"Current subphase: start pattern='{self._subphase}'")
						ex.add_note(f"Current phase: start pattern='{self._subphase._phase}'")
						ex.add_note(f"Current task: start pattern='{self._subphase._phase._task}'")
						ex.add_note(f"Current cmd:  {self._subphase._phase._task._command}")
						raise ex
					break
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.SubSubPhaseTime
					nextLine = yield line
					return nextLine

				line = yield line

			while True:
				isFinish = False  # line.StartsWith("Ending")

				try:
					processedLine = phase.send(line)

					if isinstance(processedLine, VivadoMessage):
						self._AddMessage(processedLine)

					if isFinish:
						WarningCollector.Raise(UndetectedEnd(f"Didn't detect finish: '{processedLine!r}'", processedLine))
						line = yield processedLine
						break
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break

				line = yield processedLine


@export
class SubSubSubPhase(BaseParser, VivadoMessagesMixin):
	# _NAME:   ClassVar[str]
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

	def _SubSubSubPhaseStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		if (match := self._START.match(line._message)) is None:
			raise ProcessorException()

		self._phaseIndex =          int(match["major"])
		self._subPhaseIndex =       int(match["minor"])
		self._subSubPhaseIndex =    int(match["micro"])
		self._subSubSubPhaseIndex = int(match["nano"])

		line._kind = LineKind.SubSubSubPhaseStart
		nextLine = yield line
		return nextLine

	def _SubSubSubPhaseFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, None]:
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

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
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


@export
class SubSubSubPhaseWithTasks(SubSubSubPhase):
	_nestedTasks: Dict[Type["NestedTask"], "NestedTask"]

	def __init__(self, subsubphase: SubSubPhase) -> None:
		super().__init__(subsubphase)

		self._nestedTasks = {p: p(self) for p in self._PARSERS}

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, NestedTask):
			ex = TypeError(f"Parameter 'key' is not a NestedTask.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._nestedTasks

	def __getitem__(self, key: Type["NestedTask"]) -> "NestedTask":
		try:
			return self._nestedTasks[key]
		except KeyError as ex:
			raise NestedTaskNotPresentException(F"NestedTask '{key._NAME}' not present in '{self._parent.logfile}'.") from ex

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._SubSubSubPhaseStart(line)

		activeParsers: List["NestedTask"] = list(self._nestedTasks.values())

		# START_PREFIX = f"Phase {self._phaseIndex}.{self._subPhaseIndex}.{self._subSubPhaseIndex}."

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Starting "):
					for parser in activeParsers:  # type: NestedTask
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						WarningCollector.Raise(UnknownSubPhase(f"Unknown NestedTask: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown NestedTask: '{line!r}'")
						ex.add_note(f"Current subsubsubphase: start pattern='{self}'")
						ex.add_note(f"Current subsubphase: start pattern='{self._subsubphase}'")
						ex.add_note(f"Current subphase: start pattern='{self._subsubphase._subphase}'")
						ex.add_note(f"Current phase: start pattern='{self._subsubphase._subphase._phase}'")
						ex.add_note(f"Current task: start pattern='{self._subsubphase._subphase._phase._task}'")
						ex.add_note(f"Current cmd:  {self._subsubphase._subphase._phase._task._command}")
						raise ex
					break
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.SubSubSubPhaseTime
					nextLine = yield line
					return nextLine

				line = yield line

			while True:
				isFinish = False  # line.StartsWith("Ending")

				try:
					processedLine = phase.send(line)

					if isinstance(processedLine, VivadoMessage):
						self._AddMessage(processedLine)

					if isFinish:
						WarningCollector.Raise(UndetectedEnd(f"Didn't detect finish: '{processedLine!r}'", processedLine))
						line = yield processedLine
						break
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break

				line = yield processedLine


@export
class NestedTask(BaseParser, VivadoMessagesMixin):
	# _NAME:     ClassVar[str]
	# _START:    ClassVar[str]
	# _FINISH:   ClassVar[str]
	# _TIME:     ClassVar[str] = "Time (s):"

	_subsubsubphase: SubSubSubPhaseWithTasks
	_duration:       float

	def __init__(self, subsubsubphase: SubSubSubPhaseWithTasks) -> None:
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._subsubsubphase = subsubsubphase

	@readonly
	def SubSubSubPhase(self) -> SubSubSubPhaseWithTasks:
		return self._subsubsubphase

	def _NestedTaskStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		if not line.StartsWith(self._START):
			raise ProcessorException(f"{self.__class__.__name__}._TaskStart(): Expected '{self._START}' at line {line._lineNumber}.")

		line._kind = LineKind.NestedTaskStart
		nextLine = yield line
		return nextLine

	def _NestedTaskFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException(f"{self.__class__.__name__}._TaskFinish(): Expected '{self._FINISH}' at line {line._lineNumber}.")

		line._kind = LineKind.NestedTaskEnd
		line = yield line

		if self._TIME is not None:
			while True:
				if line.StartsWith(self._TIME):
					line._kind = LineKind.TaskTime
					line = yield line
					break

				line = yield line

		return line

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._NestedTaskStart(line)

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

		nextLine = yield from self._NestedTaskFinish(line)
		return nextLine

	def __str__(self) -> str:
		return self._NAME


@export
class NestedTaskWithPhases(NestedTask):
	"""
	A task's output emitted by a Vivado command.

	.. rubric:: Extracted information

	* Vivado messages (info, warning, critical warning, error).
	* Nested phases

	.. rubric:: Example

	.. code-block::

	   Phase 4.1.1.1 BUFG Insertion

	   Starting Physical Synthesis Task

	   Phase 1 Physical Synthesis Initialization
	   INFO: [Physopt 32-721] Multithreading enabled for phys_opt_design using a maximum of 2 CPUs
	   INFO: [Physopt 32-619] Estimated Timing Summary | WNS=-0.733 | TNS=-0.936 |
	   Phase 1 Physical Synthesis Initialization | Checksum: 1818afcc0

	   Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.014 . Memory (MB): peak = 1865.645 ; gain = 0.000
	   INFO: [Place 46-56] BUFG insertion identified 0 candidate nets. Inserted BUFG: 0, Replicated BUFG Driver: 0, Skipped due to Placement/Routing Conflicts: 0, Skipped due to Timing Degradation: 0, Skipped due to netlist editing failed: 0.
	   Ending Physical Synthesis Task | Checksum: 22839c186

	   Time (s): cpu = 00:00:00 ; elapsed = 00:00:00.016 . Memory (MB): peak = 1865.645 ; gain = 0.000
	   Phase 4.1.1.1 BUFG Insertion | Checksum: 1a8cbaaf2
	"""
	# _PARSERS:  ClassVar[Tuple[Type["SubTask"], ...]]

	_nestedPhases: Dict[Type["NestedPhase"], "NestedPhase"]

	def __init__(self, subsubsubPhase: SubSubSubPhaseWithTasks) -> None:
		super().__init__(subsubsubPhase)

		self._nestedPhases =  {p: p(self) for p in self._PARSERS}

	@readonly
	def NestedPhases(self) -> Dict[Type["NestedPhase"], "NestedPhase"]:
		return self._nestedPhases

	def __contains__(self, key: Any) -> bool:
		if not issubclass(key, NestedPhase):
			ex = TypeError(f"Parameter 'key' is not a NestedPhase.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._nestedPhases

	def __getitem__(self, key: Type["NestedPhase"]) -> "NestedPhase":
		try:
			return self._nestedPhases[key]
		except KeyError as ex:
			raise SubTaskNotPresentException(F"NestedPhase '{key._NAME}' not present in '{self._parent.logfile}'.") from ex

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._NestedTaskStart(line)

		activeParsers: List[Phase] = list(self._nestedPhases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase "):
					for parser in activeParsers:  # type: NestedPhase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						WarningCollector.Raise(UnknownSubPhase(f"Unknown NestedPhase: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown NestedPhase: '{line!r}'")
						ex.add_note(f"Current nestedtask: start pattern='{self}'")
						ex.add_note(f"Current subsubsubphase: start pattern='{self._subsubsubphase}'")
						ex.add_note(f"Current subsubphase: start pattern='{self._subsubsubphase._subsubphase}'")
						ex.add_note(f"Current subphase: start pattern='{self._subsubsubphase._subsubphase._subphase}'")
						ex.add_note(f"Current phase: start pattern='{self._subsubsubphase._subsubphase._subphase._phase}'")
						ex.add_note(f"Current task: start pattern='{self._subsubsubphase._subsubphase._subphase._phase._task}'")
						ex.add_note(f"Current cmd:  {self._subsubsubphase._subsubphase._subphase._phase._task._command}")
						raise ex
					break
				elif line.StartsWith("Ending"):
					nextLine = yield from self._NestedTaskFinish(line)
					return nextLine
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.TaskTime
					nextLine = yield line
					return nextLine

				line = yield line

			while True:
				isFinish = False  # line.StartsWith("Ending") # FIXME: detect end, but time might come later

				try:
					processedLine = phase.send(line)

					if isinstance(processedLine, VivadoMessage):
						self._AddMessage(processedLine)

					if isFinish:
						WarningCollector.Raise(UndetectedEnd(f"Didn't detect finish: '{processedLine!r}'", processedLine))
						line = yield processedLine
						break
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break

				line = yield processedLine


@export
class NestedPhase(BaseParser, VivadoMessagesMixin):
	# _NAME:   ClassVar[str]
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	# _TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[Nullable[str]] = None

	_nestedTask: NestedTaskWithPhases
	_phaseIndex: int
	_duration:   float

	def __init__(self, nestedTask: TaskWithPhases) -> None:
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._nestedTask = nestedTask
		self._phaseIndex = None

	@readonly
	def NestedTask(self) -> NestedTaskWithPhases:
		return self._nestedTask

	def _NestedPhaseStart(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		if (match := self._START.match(line._message)) is None:
			raise ProcessorException(f"{self.__class__.__name__}._PhaseStart(): Expected '{self._START}' at line {line._lineNumber}.")

		self._phaseIndex = int(match["major"])

		line._kind = LineKind.NestedPhaseStart
		nextLine = yield line
		return nextLine

	def _NestedPhaseFinish(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, None]:
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex)
		if not line.StartsWith(FINISH):
			raise ProcessorException(f"{self.__class__.__name__}._PhaseFinish(): Expected '{FINISH}' at line {line._lineNumber}.")

		line._kind = LineKind.NestedPhaseEnd
		line = yield line

		if self._TIME is not None:
			while True:
				if line.StartsWith(self._TIME):
					line._kind = LineKind.PhaseTime
					break
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)

				line = yield line

			line = yield line

		return line

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._NestedPhaseStart(line)

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

		nextLine = yield from self._NestedPhaseFinish(line)
		return nextLine

	def __str__(self) -> str:
		return f"{self.__class__.__name__}: {self._START.pattern}"


@export
class Synth_Design(CommandWithSections):
	"""
	A Vivado command output parser for ``synth_design``.
	"""
	from . import SynthesizeDesign as _SynthDesign

	_TCL_COMMAND: ClassVar[str] = "synth_design"
	_PARSERS:     ClassVar[Tuple[Type[Section], ...]] = (
		_SynthDesign.RTLElaboration,
		_SynthDesign.HandlingCustomAttributes,
		_SynthDesign.ConstraintValidation,
		_SynthDesign.LoadingPart,
		_SynthDesign.ApplySetPropertyXDCConstraints,
		_SynthDesign.RTLComponentStatistics,
		_SynthDesign.RTLHierarchicalComponentStatistics,
		_SynthDesign.PartResourceSummary,
		_SynthDesign.CrossBoundaryAndAreaOptimization,
		_SynthDesign.ROM_RAM_DSP_SR_Retiming,
		_SynthDesign.ApplyingXDCTimingConstraints,
		_SynthDesign.TimingOptimization,
		_SynthDesign.TechnologyMapping,
		_SynthDesign.IOInsertion,
		_SynthDesign.FlatteningBeforeIOInsertion,
		_SynthDesign.FinalNetlistCleanup,
		_SynthDesign.RenamingGeneratedInstances,
		_SynthDesign.RebuildingUserHierarchy,
		_SynthDesign.RenamingGeneratedPorts,
		_SynthDesign.RenamingGeneratedNets,
		_SynthDesign.WritingSynthesisReport,
	)

	@readonly
	def HasLatches(self) -> bool:
		"""
		Read-only property returning if synthesis inferred latches into the design.

		Latch detection is based on:

		* Vivado message ``synth 8-327``
		* Cells of lind ``LD`` listed in the *Cell Usage* report.

		:returns: True, if the design contains latches.
		"""
		from .SynthesizeDesign import WritingSynthesisReport

		if (8 in self._messagesByID) and (327 in self._messagesByID[8]):
			return True

		return "LD" in self._sections[WritingSynthesisReport]._cells

	@readonly
	def Latches(self) -> List[VivadoMessage]:
		"""
		Read-only property to access a list of Vivado output messages for inferred latches.

		:returns: A list of Vivado messages for interred latches.

		.. note::

		   This returns ``[Synth 8-327]`` messages.

		   .. code-block::

          WARNING: [Synth 8-327] inferring latch for variable 'Q_reg'
		"""
		if 8 in self._messagesByID:
			if 327 in (synthMessages := self._messagesByID[8]):
				return [message for message in synthMessages[327]]

		return []

	@readonly
	def Statemachines(self) -> Dict[str, List[str]]:
		"""

		:returns: undocumented

		.. note::

		   INFO: [Synth 8-802] inferred FSM for state register 'State_reg' in module 'stream_Padder'
		   INFO: [Synth 8-802] inferred FSM for state register 'RX_blk.blkRXFSM.State_reg' in module 'eth_XGEMAC_XGMII'
		"""

	@readonly
	def DistributedRAMs(self) -> Dict[str, Any]:
		"""

		:returns: undocumented
		"""

	@readonly
	def BlockRAMs(self) -> Dict[str, Any]:
		"""

		:returns: undocumented
		"""


	@readonly
	def UltraRAMs(self) -> Dict[str, Any]:
		"""

		:returns: undocumented
		"""

	@readonly
	def ShiftRegister(self) -> Dict[str, Dict[str, Any]]:
		"""

		:returns: undocumented

		.. note::

		    Static Shift Register Report:
		    Dynamic Shift Register Report:
		"""

	@readonly
	def UndrivenPins(self) -> Dict[str, str]:
		"""

		:returns: undocumented

		.. note::

		   WARNING: [Synth 8-3295] tying undriven pin AXI4FullPipeLine_M2S[AWID]_inferred:in0 to constant 0
		"""

	# ignored instructions
	#   ignored ram_style WARNING: [Synth 8-5791] The ram_style = "ultra" set on RAM "ocram_sdp__parameterized4:/gInfer.ram_reg" is ignored because clocks on ports do not match.

	@readonly
	def HasBlackboxes(self) -> bool:
		"""
		Read-only property returning if the design contains black-boxes.

		:returns: True, if the design contains black-boxes.
		"""
		from .SynthesizeDesign import WritingSynthesisReport

		return len(self._sections[WritingSynthesisReport]._blackboxes) > 0

	@readonly
	def Blackboxes(self) -> Dict[str, int]:
		"""
		Read-only property to access the dictionary of found blackbox statistics.

		:returns: The dictionary of found blackbox statistics.
		"""
		from .SynthesizeDesign import WritingSynthesisReport

		return self._sections[WritingSynthesisReport]._blackboxes

	@readonly
	def Cells(self) -> Dict[str, int]:
		"""
		Read-only property to access the dictionary of synthesized cell statistics.

		:returns: The dictionary of used cell statistics.
		"""
		from .SynthesizeDesign import WritingSynthesisReport

		return self._sections[WritingSynthesisReport]._cells

	@readonly
	def VHDLReportMessages(self) -> List[VHDLReportMessage]:
		"""
		Read-only property to access a list of Vivado output messages generated by VHDL report statement.

		:returns: A list of VHDL report statement outputs.

		.. note::

		   This returns ``[Synth 8-6031]`` messages.

		   .. code-block::

          INFO: [Synth 8-6031] RTL report: "TimingToCycles(time, freq): period=10.000000 ns -- 0.000000 fs" [C:/[...]/StopWatch/src/Utilities.pkg.vhdl:118]
		"""
		if 8 in self._messagesByID:
			if 6031 in (synthMessages := self._messagesByID[8]):
				return [message for message in synthMessages[6031]]

		return []

	@readonly
	def VHDLAssertMessages(self) -> List[VHDLReportMessage]:
		"""
		Read-only property to access a list of Vivado output messages generated by VHDL assert statement.

		:returns: A list of VHDL assert statement outputs.

		.. note::

		   This returns ``[Synth 8-63]`` messages.

		   .. code-block::

          INFO: [Synth 8-63] RTL assertion: "CLOCK_FREQ:           100.000000 ns" [C:/[...]/StopWatch/src/Debouncer.vhdl:28]
		"""
		if 8 in self._messagesByID:
			if 63 in (synthMessages := self._messagesByID[8]):
				return [message for message in synthMessages[63]]

		return []

	def SectionDetector(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, None]:
		from .SynthesizeDesign import RTLElaboration

		if not (isinstance(line, VivadoTclCommand) and line._tclCommand == self._TCL_COMMAND):
			raise ProcessorException()  # FIXME: add exception message

		activeParsers: List[Section] =   [p(self) for p in self._PARSERS]
		rtlElaboration: RTLElaboration = next(p for p in activeParsers if isinstance(p, RTLElaboration))

		line = yield line
		if line == "Starting synth_design":
			line._kind = LineKind.Verbose
		else:
			raise ProcessorException()  # FIXME: add exception message

		line = yield line
		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Start "):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							# Found a suitable section parser.
							#   Add section parser to list of found sections.
							#   In case of duplicates, create a chain of psrer instances.
							if parser not in self._sections:
								self._sections.append(parser)
							else:
								parser._next = (newParser := parser.__class__(self))
								parser = newParser

							line = next(section := parser.Generator(line))
							line._previousLine._kind = LineKind.SectionStart | LineKind.SectionDelimiter
							break
					else:
						WarningCollector.Raise(UnknownSection(f"Unknown section: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown section: '{line!r}'")
						# ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self}")
						raise ex
					break
				elif line.StartsWith("Starting "):
					if line.StartsWith(rtlElaboration._START):
						self._sections.append(parser := rtlElaboration)
						line = next(section := parser.Generator(line))
						line._previousLine._kind = LineKind.SectionStart | LineKind.SectionDelimiter
						break
				elif line.StartsWith(self._TCL_COMMAND):
					if line[len(self._TCL_COMMAND) + 1:].startswith("completed successfully"):
						line._kind |= LineKind.Success

						# FIXME: use similar style like for _TIME
						line = yield line
						lastLine = yield line
						return lastLine
				elif line.StartsWith("Finished RTL Optimization Phase"):
					line._kind = LineKind.PhaseEnd
					line._previousLine._kind = LineKind.PhaseEnd | LineKind.PhaseDelimiter
				elif line.StartsWith("----"):
					if LineKind.Phase in line._previousLine._kind:
						line._kind = LineKind.PhaseEnd | LineKind.PhaseDelimiter

				line = yield line

			line = yield line

			while True:
				if line.StartsWith("Finished"):
					l = line[9:]
					if not (l.startswith("Flattening") or l.startswith("Final")):
						line = yield section.send(line)
						break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				line = yield section.send(line)

			line = yield section.send(line)

			if not parser._DUPLICATES:
				activeParsers.remove(parser)


@export
class Link_Design(Command):
	"""
	A Vivado command output parser for ``link_design``.
	"""
	_TCL_COMMAND: ClassVar[str] = "link_design"
	_TIME:        ClassVar[str] = "Time (s):"

	_ParsingXDCFile_Pattern = re_compile(r"""^Parsing XDC File \[(.*)\]$""")
	_FinishedParsingXDCFile_Pattern = re_compile(r"""^Finished Parsing XDC File \[(.*)\]$""")
	_ParsingXDCFileForCell_Pattern = re_compile(r"""^Parsing XDC File \[(.*)\] for cell '(.*)'$""")
	_FinishedParsingXDCFileForCell_Pattern = re_compile(r"""^Finished Parsing XDC File \[(.*)\] for cell '(.*)'$""")

	_commonXDCFiles:  Dict[Path, List[VivadoMessage]]
	_perCellXDCFiles: Dict[Path, Dict[str, List[VivadoMessage]]]

	def __init__(self, processor: "Processor") -> None:
		super().__init__(processor)

		self._commonXDCFiles = {}
		self._perCellXDCFiles = {}

	@readonly
	def CommonXDCFiles(self) -> Dict[Path, List[VivadoMessage]]:
		return self._commonXDCFiles

	@readonly
	def PerCellXDCFiles(self) -> Dict[Path, Dict[str, List[VivadoMessage]]]:
		return self._perCellXDCFiles

	def SectionDetector(self, line: VivadoLine) -> Generator[Union[VivadoLine, ProcessorException], VivadoLine, VivadoLine]:
		line = yield from self._CommandStart(line)

		end = f"{self._TCL_COMMAND} "
		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			elif (match := self._ParsingXDCFile_Pattern.match(line._message)) is not None:
				line._kind = LineKind.Normal

				path = Path(match[1])
				self._commonXDCFiles[path] = (messages := [])

				line = yield line
				while True:
					if line._kind is LineKind.Empty:
						line = yield line
						continue
					elif isinstance(line, VivadoMessage):
						self._AddMessage(line)
						messages.append(line)
					elif (match := self._FinishedParsingXDCFile_Pattern.match(line._message)) is not None and path == Path(match[1]):
						line._kind = LineKind.Normal
						break
					elif line.StartsWith("Finished Parsing XDC File"):
						line._kind = LineKind.ProcessorError
						break
					elif line.StartsWith(end):
						break

					line = yield line
			elif (match := self._ParsingXDCFileForCell_Pattern.match(line._message)) is not None:
				line._kind = LineKind.Normal

				path = Path(match[1])
				cell = match[2]
				if path in self._perCellXDCFiles:
					self._perCellXDCFiles[path][cell] = (messages := [])
				else:
					self._perCellXDCFiles[path] = {cell: (messages := [])}

				line = yield line
				while True:
					if line._kind is LineKind.Empty:
						line = yield line
						continue
					elif isinstance(line, VivadoMessage):
						self._AddMessage(line)
						messages.append(line)
					elif (match := self._FinishedParsingXDCFileForCell_Pattern.match(line._message)) is not None and path == Path(match[1]) and cell == match[2]:
						line._kind = LineKind.Normal
						break
					elif line.StartsWith("Finished Parsing XDC File"):
						line._kind = LineKind.ProcessorError
						break
					elif line.StartsWith(end):
						break

					line = yield line

			if line.StartsWith(end):
				nextLine = yield from self._CommandFinish(line)
				return nextLine

			line = yield line


@export
class Opt_Design(CommandWithTasks):
	"""
	A Vivado command output parser for ``opt_design``.
	"""
	from . import OptimizeDesign as _OptDesign

	_TCL_COMMAND: ClassVar[str] = "opt_design"
	_TIME:        ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Task], ...]] = (
		_OptDesign.DRCTask,
		_OptDesign.CacheTimingInformationTask,
		_OptDesign.LogicOptimizationTask,
		_OptDesign.PowerOptimizationTask,
		_OptDesign.FinalCleanupTask,
		_OptDesign.NetlistObfuscationTask
	)

	def SectionDetector(self, line: VivadoLine) -> Generator[Union[VivadoLine, ProcessorException], VivadoLine, VivadoLine]:
		line = yield from self._CommandStart(line)

		activeParsers: List[Task] = list(self._tasks.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Starting ") and not line.StartsWith("Starting Connectivity Check Task"):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = yield next(task := parser.Generator(line))
							break
					else:
						WarningCollector.Raise(UnknownTask(f"Unknown task: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown task: '{line!r}'")
						# ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self}")
						raise ex
					break
				elif line.StartsWith(self._TCL_COMMAND):
					if line[len(self._TCL_COMMAND) + 1:].startswith("completed successfully"):
						line._kind |= LineKind.Success

						# FIXME: use similar style like for _TIME
						line = yield line
						lastLine = yield line
						return lastLine
				# line._kind = LineKind.Unprocessed

				line = yield line

			while True:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield task.send(line)
				except StopIteration as ex:
					task = None
					line = ex.value

					if isinstance(line, VivadoMessage):
						line = yield line

					break

			if task is not None:
				line = yield task.send(line)

			activeParsers.remove(parser)


@export
class Place_Design(CommandWithTasks):
	"""
	A Vivado command output parser for ``place_design``.
	"""
	from . import PlaceDesign as _PlaceDesign

	_TCL_COMMAND: ClassVar[str] = "place_design"
	_TIME:        ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Task], ...]] = (
		_PlaceDesign.PlacerTask,
	)

	def SectionDetector(self, line: VivadoLine) -> Generator[Union[VivadoLine, ProcessorException], VivadoLine, VivadoLine]:
		line = yield from self._CommandStart(line)

		activeParsers: List[Task] = list(self._tasks.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Starting "):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = yield next(task := parser.Generator(line))
							break
					else:
						WarningCollector.Raise(UnknownTask(f"Unknown task: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown task: '{line!r}'")
						# ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self}")
						raise ex
					break
				elif line.StartsWith(self._TCL_COMMAND):
					if line[len(self._TCL_COMMAND) + 1:].startswith("completed successfully"):
						line._kind |= LineKind.Success

						# FIXME: use similar style like for _TIME
						line = yield line
						lastLine = yield line
						return lastLine
				# line._kind = LineKind.Unprocessed

				line = yield line

			while True:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield task.send(line)
				except StopIteration as ex:
					task = None
					line = ex.value

					if isinstance(line, VivadoMessage):
						line = yield line

					break

			if task is not None:
				line = yield task.send(line)

			activeParsers.remove(parser)


@export
class PhyOpt_Design(CommandWithTasks):
	"""
	A Vivado command output parser for ``phy_opt_design``.
	"""
	from . import PhysicalOptimizeDesign as _PhyOptDesign

	_TCL_COMMAND: ClassVar[str] = "phys_opt_design"
	_TIME:        ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Task], ...]] = (
		_PhyOptDesign.InitialUpdateTimingTask,
		_PhyOptDesign.PhysicalSynthesisTask
	)

	def SectionDetector(self, line: VivadoLine) -> Generator[Union[VivadoLine, ProcessorException], VivadoLine, VivadoLine]:
		line = yield from self._CommandStart(line)

		activeParsers: List[Task] = list(self._tasks.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Starting "):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = yield next(task := parser.Generator(line))
							break
					else:
						WarningCollector.Raise(UnknownTask(f"Unknown task: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown task: '{line!r}'")
						# ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self}")
						raise ex
					break
				elif line.StartsWith(self._TCL_COMMAND):
					if line[len(self._TCL_COMMAND) + 1:].startswith("completed successfully"):
						line._kind |= LineKind.Success

						# FIXME: use similar style like for _TIME
						line = yield line
						lastLine = yield line
						return lastLine
				# line._kind = LineKind.Unprocessed

				line = yield line

			while True:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield task.send(line)
				except StopIteration as ex:
					task = None
					line = ex.value

					if isinstance(line, VivadoMessage):
						line = yield line

					break

			if task is not None:
				line = yield task.send(line)

			activeParsers.remove(parser)


@export
class Route_Design(CommandWithTasks):
	"""
	A Vivado command output parser for ``route_design``.
	"""
	from . import RouteDesign as _RouteDesign

	_TCL_COMMAND: ClassVar[str] = "route_design"
	_TIME:        ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Task], ...]] = (
		_RouteDesign.RoutingTask,
	)

	def SectionDetector(self, line: VivadoLine) -> Generator[Union[VivadoLine, ProcessorException], VivadoLine, VivadoLine]:
		line = yield from self._CommandStart(line)

		activeParsers: List[Task] = list(self._tasks.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Starting "):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = yield next(task := parser.Generator(line))
							break
					else:
						WarningCollector.Raise(UnknownTask(f"Unknown task: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown task: '{line!r}'")
						# ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self}")
						raise ex
					break
				elif line.StartsWith(self._TCL_COMMAND):
					if line[len(self._TCL_COMMAND) + 1:].startswith("completed successfully"):
						line._kind |= LineKind.Success

						# FIXME: use similar style like for _TIME
						line = yield line
						lastLine = yield line
						return lastLine
				# line._kind = LineKind.Unprocessed

				line = yield line

			while True:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield task.send(line)
				except StopIteration as ex:
					task = None
					line = ex.value

					if isinstance(line, VivadoMessage):
						line = yield line

					break

			if task is not None:
				line = yield task.send(line)

			activeParsers.remove(parser)


@export
class Write_Bitstream(Command):
	"""
	A Vivado command output parser for ``write_bitstream``.
	"""
	_TCL_COMMAND: ClassVar[str] = "write_bitstream"
	_TIME:        ClassVar[str] = "Time (s):"


@export
class Report_DRC(Command):
	"""
	A Vivado command output parser for ``report_drc``.
	"""
	_TCL_COMMAND: ClassVar[str] = "report_drc"
	_TIME:        ClassVar[str] = "Time (s):"


@export
class Report_Methodology(Command):
	"""
	A Vivado command output parser for ``report_methodology``.
	"""
	_TCL_COMMAND: ClassVar[str] = "report_methodology"
	_TIME:        ClassVar[str] = None


@export
class Report_Power(Command):
	"""
	A Vivado command output parser for ``report_power``.
	"""
	_TCL_COMMAND: ClassVar[str] = "report_power"
	_TIME:        ClassVar[str] = None


@export
class Open_Checkpoint(Command):
	"""
	A Vivado command output parser for ``open_checkpoint``.
	"""
	_TCL_COMMAND: ClassVar[str] = "open_checkpoint"
	_TIME:        ClassVar[str] = "Time (s):"


@export
class Processor(VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	"""
	A processor for Vivado log outputs.

	Each output line from Vivado gets processed and converted into a :class:`ProcessedLine` objects. Such lines form a
	doubly-linked list.
	"""
	_duration:                float  #: Duration of the observed process (e.g. start to end of synthesis).
	_processingDuration:      float  #: Duration for the log output processor to parse all log messages.

	_lines:                   List[VivadoLine]              #: A list of processed log message lines.
	_preamble:                Nullable[Preamble]            #: Reference to the Vivado preamble written after tool startup.
	_postamble:               Nullable[Postamble]           #: Reference to the Vivado postamble written after tool startup.
	_commands:                Dict[Type[Command], Command]  #: A dictionary of processed Vivado commands.

	def __init__(self) -> None:
		"""
		Initializes a Vivado log output processor.
		"""
		super().__init__()

		self._duration =                0.0
		self._processingDuration =      0.0

		self._lines =                   []
		self._preamble =                None
		self._postamble =               None
		self._commands =                {}

	@readonly
	def Lines(self) -> List[VivadoLine]:
		"""
		Read-only property to access the list of processed and classified log lines (messages).

		:returns: A list of processed lines.
		"""
		return self._lines

	@readonly
	def Preamble(self) -> Nullable[Preamble]:
		"""
		Read-only property to access the parsed preamble information.

		:returns: The log's output preamble.
		"""
		return self._preamble

	@readonly
	def Postamble(self) -> Nullable[Postamble]:
		"""
		Read-only property to access the parsed postamble information.

		:returns: The log's output postamble.
		"""
		return self._postamble

	@readonly
	def Commands(self) -> Dict[Type[Command], Command]:
		"""
		Read-only property to access the dictionary of processed Vivado commands.

		:returns: The dictionary of processed Vivado commands.
		"""
		return self._commands

	@readonly
	def StartDateTime(self) -> datetime:
		if self._preamble is None:
			raise ValueError(f"Preamble was not found when parsing the Vivado log outputs.")

		return self._preamble.StartDateTime

	@readonly
	def ExitDateTime(self) -> datetime:
		if self._postamble is None:
			raise ValueError(f"Postamble was not found when parsing the Vivado log outputs.")

		return self._postamble.ExitDateTime

	@readonly
	def Duration(self) -> float:
		"""
		 Duration of the observed process (e.g. start to end of synthesis).

		:returns: The observed process' execution duration in seconds.
		"""
		return (self.ExitDateTime - self.StartDateTime).total_seconds()

	@readonly
	def ProcessingDuration(self) -> float:
		"""
		Processing duration for the log output processor to parse all log messages.

		:returns: The processing duration in seconds.
		"""
		return self._processingDuration

	def __contains__(self, key: Type[Command]) -> bool:
		"""
		Returns True, if log outputs where found for the given command.

		:param key: Vivado command (class).
		:returns:   True, if the Vivado command's outputs were found in log outputs.
		"""
		if not issubclass(key, Command):
			ex = TypeError(f"Parameter 'key' is not a Command.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		return key in self._commands

	def __getitem__(self, key: Type[Command]) -> Command:
		"""
		Access Vivado command specific log outputs and parsed data by the command.

		:param key: Vivado command (class) to access.
		:returns:   A Vivado command instance with parsed log messages and extracted data.
		"""
		if not issubclass(key, Command):
			ex = TypeError(f"Parameter 'key' is not a Command.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		try:
			return self._commands[key]
		except KeyError as ex:
			raise CommandNotPresentException(F"Command '{key._TCL_COMMAND}' not present in '{self._logfile}'.") from ex

	@readonly
	def IsIncompleteLog(self) -> bool:
		"""
		Read-only property returning true if the processed Vivado log output is incomplete.

		A log can be incomplete, because:

		* Vivado disabled messages, because too many messages of the same kind appeared. Usually, a message type is disabled
		  after 100 messages of that type. This is indicated by message ``[Common 17-14]``.

		:returns: True, if messages where silenced by Vivado.

		.. note::

		   .. code-block::

		      INFO: [Common 17-14] Message 'Synth 8-3321' appears 100 times and further instances of the messages will be
		      disabled. Use the Tcl command set_msg_config to change the current settings.
		"""
		return 17 in self._messagesByID and 14 in self._messagesByID[17]

	def LineClassification(self, inputStream: Iterator[Tuple[datetime, str]]) -> Generator[VivadoLine, None, None]:

		# Instantiate and initialize CommandFinder
		next(cmdFinder := self.CommandFinder())

		lastLine = None
		lineNumber = 0
		_errorMessage = "Unknown processing error"

		try:
			while (tup := next(inputStream)) is not None:
				timestamp, rawMessageLine = tup
				lineNumber += 1
				rawMessageLine = rawMessageLine.rstrip()
				errorMessage = _errorMessage

				if len(rawMessageLine) == 0:
					line = VivadoLine(lineNumber, LineKind.Empty, LineAction.Default, rawMessageLine, previousLine=lastLine)
				elif rawMessageLine.startswith("INFO"):
					if (line := VivadoInfoMessage.Parse(lineNumber, rawMessageLine, previousLine=lastLine)) is None:
						if (line := VivadoDRCInfoMessage.Parse(lineNumber, rawMessageLine, previousLine=lastLine)) is None:
							if (line := VivadoIrregularInfoMessage.Parse(lineNumber, rawMessageLine, previousLine=lastLine)) is None:
								line = VivadoStuntedInfoMessage.Parse(lineNumber, rawMessageLine, previousLine=lastLine)

					errorMessage = f"Line starting with 'INFO' was not a VivadoInfoMessage."
				elif rawMessageLine.startswith("WARNING"):
					if (line := VivadoWarningMessage.Parse(lineNumber, rawMessageLine, previousLine=lastLine)) is None:
						if (line := VivadoDRCWarningMessage.Parse(lineNumber, rawMessageLine, previousLine=lastLine)) is None:
							if (line := VivadoXPMWarningMessage.Parse(lineNumber, rawMessageLine, previousLine=lastLine)) is None:
								line = VivadoStuntedWarningMessage.Parse(lineNumber, rawMessageLine, previousLine=lastLine)

					errorMessage = f"Line starting with 'WARNING' was not a VivadoWarningMessage."
				elif rawMessageLine.startswith("CRITICAL WARNING"):
					line = VivadoCriticalWarningMessage.Parse(lineNumber, rawMessageLine, previousLine=lastLine)

					errorMessage = f"Line starting with 'CRITICAL WARNING' was not a VivadoCriticalWarningMessage."
				elif rawMessageLine.startswith("ERROR"):
					line = VivadoErrorMessage.Parse(lineNumber, rawMessageLine, previousLine=lastLine)

					errorMessage = f"Line starting with 'ERROR' was not a VivadoErrorMessage."
				elif rawMessageLine.startswith("Command: "):
					line = VivadoTclCommand.Parse(lineNumber, rawMessageLine, previousLine=lastLine)

					errorMessage = "Line starting with 'Command:' was not a VivadoTclCommand."
				else:
					line = VivadoLine(lineNumber, LineKind.Unprocessed, LineAction.Default, rawMessageLine, previousLine=lastLine)

					if line.StartsWith("Resolution:") and isinstance(lastLine, VivadoMessage):
						line._kind = LineKind.Verbose

				if line is None:
					# TODO: what to do with this line? attache to exception?
					line = VivadoLine(lineNumber, LineKind.ProcessorError, LineAction.Default, rawMessageLine, previousLine=lastLine)

					raise ClassificationException(errorMessage, lineNumber, rawMessageLine)

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				line = cmdFinder.send(line)

				if line._kind is LineKind.ProcessorError:
					line = ClassificationException(errorMessage, lineNumber, rawMessageLine)

				# TODO: find a better solution/location to assign the timestamp.
				line._timestamp = timestamp

				self._lines.append(line)

				lastLine = line
				yield line

		except StopIteration:
			pass

	def CommandFinder(self) -> Generator[VivadoLine, VivadoLine, None]:
		tclProcedures = {"source"}

		# wait for first line
		line = yield

		if isinstance(line, VivadoInfoMessage):
			self._preamble = LogFilePreamble(self)
		elif line.StartsWith("#------"):
			self._preamble = LogFilePreamble(self)
		else:
			self._preamble = VivadoPipedPreamble(self)

		self._postamble = Postamble(self)

		# process preamble
		line = yield from self._preamble.Generator(line)

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoInfoMessage):
					if line.ToolID == 17 and line.MessageKindID == 206:
						lastLine = yield from self._postamble.Generator(line)
						return lastLine
				elif isinstance(line, VivadoTclCommand):
					if line._tclCommand == Synth_Design._TCL_COMMAND:
						self._commands[Synth_Design] = (cmd := Synth_Design(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._tclCommand == Link_Design._TCL_COMMAND:
						self._commands[Link_Design] = (cmd := Link_Design(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._tclCommand == Opt_Design._TCL_COMMAND:
						self._commands[Opt_Design] = (cmd := Opt_Design(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._tclCommand == Place_Design._TCL_COMMAND:
						self._commands[Place_Design] = (cmd := Place_Design(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._tclCommand == PhyOpt_Design._TCL_COMMAND:
						self._commands[PhyOpt_Design] = (cmd := PhyOpt_Design(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._tclCommand == Route_Design._TCL_COMMAND:
						self._commands[Route_Design] = (cmd := Route_Design(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._tclCommand == Write_Bitstream._TCL_COMMAND:
						self._commands[Write_Bitstream] = (cmd := Write_Bitstream(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._tclCommand == Report_DRC._TCL_COMMAND:
						self._commands[Report_DRC] = (cmd := Report_DRC(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._tclCommand == Report_Methodology._TCL_COMMAND:
						self._commands[Report_Methodology] = (cmd := Report_Methodology(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._tclCommand == Report_Power._TCL_COMMAND:
						self._commands[Report_Power] = (cmd := Report_Power(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break

				firstWord = line.Partition(" ")[0]
				if firstWord in tclProcedures:
					line = TclCommand.FromLine(line)

				line = yield line

			# end = f"{cmd._TCL_COMMAND} completed successfully"

			while True:
				# if line.StartsWith(end):
				# 	# line._kind |= LineKind.Success
				# 	lastLine = gen.send(line)
				# 	if LineKind.Last in line._kind:
				# 		line._kind ^= LineKind.Last
				# 	line = yield lastLine
				# 	break

				try:
					line = yield gen.send(line)
				except StopIteration as ex:
					line = ex.value
					break


@export
class Document(Processor):
	"""
	A Vivado log output processor for a log file.

	This processor represents a Vivado log file (e.g. ``*.vds`` or ``*.vdi``). It processees its content line-by-line
	while	classifying each line as a message. The processing duration is available via :data:`ProcessingDuration`.
	"""
	_logfile: Path  #: Path to the processed logfile.

	# FIXME: parse=True parameter
	def __init__(self, logfile: Path) -> None:
		"""
		Initializes a log file.

		:param logfile: Path to the log file.
		"""
		super().__init__()

		# FIXME: check if path
		self._logfile = logfile

	@readonly
	def Logfile(self) -> Path:
		"""
		Read-only property to access the document's path.

		:returns: Path to the log file.
		"""
		return self._logfile

	def Parse(self) -> None:
		with Stopwatch() as sw:
			timestamp = datetime.fromtimestamp(self._logfile.stat().st_mtime)
			with self._logfile.open("r", encoding="utf-8") as file:
				for line in self.LineClassification(timestampIterator(file, timestamp)):
					pass

		self._processingDuration = sw.Duration
