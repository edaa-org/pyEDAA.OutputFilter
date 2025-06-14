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
from re     import compile as re_compile, Pattern
from typing import ClassVar, Self, Optional as Nullable

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType


@export
class VivadoMessage(metaclass=ExtendedType, slots=True):
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

	_lineNumber:    int
	_toolID:        int
	_toolName:      str
	_messageKindID: int
	_message:       str

	def __init__(self, lineNumber: int, tool: str, toolID: int, messageKindID: int, message: str) -> None:
		self._lineNumber = lineNumber
		self._toolID = toolID
		self._toolName = tool
		self._messageKindID = messageKindID
		self._message = message

	@readonly
	def LineNumber(self) -> int:
		return self._lineNumber

	@readonly
	def ToolName(self) -> int:
		return self._toolName

	@readonly
	def ToolID(self) -> int:
		return self._toolID

	@readonly
	def MessageKindID(self) -> int:
		return self._messageKindID

	@readonly
	def Message(self) -> int:
		return self._message

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
