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
from typing   import ClassVar, Optional as Nullable, Generator

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Versioning  import YearReleaseVersion

from pyEDAA.OutputFilter.Xilinx import Line, LineKind


@export
class BaseParser(metaclass=ExtendedType, slots=True):
	pass

@export
class Parser(BaseParser):
	_processor: "Processor"

	def __init__(self, processor: "Processor"):
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

		nextLine = yield line
		return nextLine
