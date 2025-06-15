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
from re       import compile as re_compile, Pattern
from typing import ClassVar, Self, Optional as Nullable, Dict, Type, Callable, List

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType, abstractmethod
from pyTooling.Stopwatch import Stopwatch
from pyTooling.Versioning  import YearReleaseVersion


@export
class Line(metaclass=ExtendedType, slots=True):
	_lineNumber:    int
	_message:       str

	def __init__(self, lineNumber: int, message: str) -> None:
		self._lineNumber = lineNumber
		self._message = message

	@readonly
	def LineNumber(self) -> int:
		return self._lineNumber

	@readonly
	def Message(self) -> str:
		return self._message

	def __str__(self) -> str:
		return self._message


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

	def __init__(self, lineNumber: int, tool: str, toolID: int, messageKindID: int, message: str) -> None:
		super().__init__(lineNumber, message)
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
	def Parse(cls, line: str, lineNumber: int) -> Nullable[Self]:
		if (match := cls._REGEXP.match(line)) is not None:
			return cls(lineNumber, match[1], int(match[2]), int(match[3]), match[4])

		return None

	def __str__(self) -> str:
		return f"{self._MESSAGE_KIND}: [{self._toolName} {self._toolID}-{self._messageKindID}] {self._message}"


@export
class VivadoInfoMessage(VivadoMessage):
	"""
	This class represents an AMD/Xilinx Vivado info message.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "INFO"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""INFO: \[(\w+) (\d+)-(\d+)\] (.*)""")
	_REGEXP2:      ClassVar[Pattern] = re_compile(r"""INFO: \[(\w+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, line: str, lineNumber: int) -> Nullable[Self]:
		result = super().Parse(line, lineNumber)
		if result is not None:
			return result

		if (match := cls._REGEXP2.match(line)) is not None:
			return cls(lineNumber, match[1], None, int(match[2]), match[3])

		return None


@export
class VivadoWarningMessage(VivadoMessage):
	"""
	This class represents an AMD/Xilinx Vivado warning message.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "WARNING"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""WARNING: \[(\w+) (\d+)-(\d+)\] (.*)""")

	@classmethod
	def Parse(cls, line: str, lineNumber: int) -> Nullable[Self]:
		result = super().Parse(line, lineNumber)
		if result is not None:
			return result

		if line.startswith("WARNING: "):
			return cls(lineNumber, None, None, None, line[9:])

		return None


@export
class VivadoCriticalWarningMessage(VivadoMessage):
	"""
	This class represents an AMD/Xilinx Vivado critical warning message.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "CRITICAL WARNING"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""CRITICAL WARNING: \[(\w+) (\d+)-(\d+)\] (.*)""")


@export
class VivadoErrorMessage(VivadoMessage):
	"""
	This class represents an AMD/Xilinx Vivado error message.
	"""

	_MESSAGE_KIND: ClassVar[str] =     "ERROR"
	_REGEXP:       ClassVar[Pattern] = re_compile(r"""ERROR: \[(\w+) (\d+)-(\d+)\] (.*)""")


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

	# def __getitem__(self, item: Type["Parser"]) -> "Parsers":
	# 	return self._parsers[item]

	def Parse(self):
		with Stopwatch() as sw:
			with self._logfile.open("r", encoding="utf-8") as f:
				content = f.read()

			lines = content.splitlines()
			for lineNumber, line in enumerate(l.rstrip() for l in lines):
				prefix = line[:4]
				if prefix == "INFO":
					if (message := VivadoInfoMessage.Parse(line, lineNumber)) is None:
						print(f"pattern not detected\n{line}")
						continue

					self._infoMessages.append(message)
				elif prefix == "WARN":
					if (message := VivadoWarningMessage.Parse(line, lineNumber)) is None:
						print(f"pattern not detected\n{line}")
						continue

					self._warningMessages.append(message)
				elif prefix == "CRIT":
					if (message := VivadoCriticalWarningMessage.Parse(line, lineNumber)) is None:
						print(f"pattern not detected\n{line}")
						continue

					self._criticalWarningMessages.append(message)
				elif prefix == "ERRO":
					if (message := VivadoErrorMessage.Parse(line, lineNumber)) is None:
						print(f"pattern not detected\n{line}")
						continue

					self._errorMessages.append(message)
				else:
					self._Parse(lineNumber, line)
					continue

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

		self._duration = sw.Duration

@export
class Parser(metaclass=ExtendedType, slots=True):
	_processor: "BaseProcessor"

	def __init__(self, processor: "BaseProcessor"):
		self._processor = processor

	@readonly
	def Processor(self) -> "BaseProcessor":
		return self._processor

	@abstractmethod
	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		pass


@export
class Preamble(Parser):
	_toolVersion:   Nullable[YearReleaseVersion]
	_startDatetime: Nullable[datetime]

	_VERSION:   ClassVar[Pattern] = re_compile(r"""# Vivado v(\d+\.\d(\.\d)?) \(64-bit\)""")
	_STARTTIME: ClassVar[Pattern] = re_compile(r"""# Start of session at: Thu (\w+) (\d+) (\d+):(\d+):(\d+) (\d+)""")

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

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		if self._toolVersion is not None and line.startswith("#----"):
			return ProcessingState.DelimiterLine | ProcessingState.Last
		elif (match := self._VERSION.match(line)) is not None:
			self._toolVersion = YearReleaseVersion.Parse(match[1])
			return ProcessingState.Processed
		elif (match := self._VERSION.match(line)) is not None:
			self._startDatetime = datetime(int(match[6]), int(match[1]), int(match[2]), int(match[3]), int(match[4]), int(match[5]))
			return ProcessingState.Processed

		return ProcessingState.Skipped
