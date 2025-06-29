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
from pathlib  import Path
from typing import Optional as Nullable, Dict, List, Generator, Union, Type

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Stopwatch   import Stopwatch

from pyEDAA.OutputFilter.Xilinx.Common import LineKind, Line, InfoMessage, WarningMessage, CriticalWarningMessage, \
	ErrorMessage, VivadoMessage, VivadoInfoMessage, VivadoIrregularInfoMessage, VivadoWarningMessage, \
	VivadoIrregularWarningMessage, VivadoCriticalWarningMessage, VivadoErrorMessage, VHDLReportMessage, VivadoTclCommand, \
	TclCommand
from pyEDAA.OutputFilter.Xilinx.Commands import Command, SynthesizeDesign
from pyEDAA.OutputFilter.Xilinx.Common2 import Preamble
from pyEDAA.OutputFilter.Xilinx.Exception import ProcessorException, ClassificationException


ProcessedLine = Union[Line, ProcessorException]


@export
class Processor(metaclass=ExtendedType, slots=True):
	_duration:                float

	_preamble:                Preamble
	_commands:                Dict[Type[Command], Command]

	_infoMessages:            List[VivadoInfoMessage]
	_warningMessages:         List[VivadoWarningMessage]
	_criticalWarningMessages: List[VivadoCriticalWarningMessage]
	_errorMessages:           List[VivadoErrorMessage]
	_toolIDs:                 Dict[int, str]
	_toolNames:               Dict[str, int]
	_messagesByID:            Dict[int, Dict[int, List[VivadoMessage]]]

	def __init__(self):
		self._duration =                0.0

		self._preamble =                None
		self._commands =                {}

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

	# TODO: Synthesis specific !!
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

	def __getitem__(self, item: Type[Command]) -> Command:
		return self._commands[item]

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

	def LineClassification(self) -> Generator[ProcessedLine, str, None]:
		# Instantiate and initialize CommandFinder
		next(cmdFinder := self.CommandFinder())

		# wait for first line
		rawMessageLine = yield
		lineNumber = 0
		_errorMessage = "Unknown processing error."

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

			line = cmdFinder.send(line)

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

	def CommandFinder(self) -> Generator[Line, Line, None]:
		self._preamble = Preamble(self)
		cmd = None

		tclProcedures = {"source"}

		# wait for first line
		line = yield
		# process preable
		line = yield from self._preamble.Generator(line)

		while True:
			while True:
				if isinstance(line, VivadoTclCommand):
					if line._command == "synth_design":
						self._commands[SynthesizeDesign] = (cmd := SynthesizeDesign(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break

				firstWord = line.Partition(" ")[0]
				if firstWord in tclProcedures:
					line = TclCommand.FromLine(line)

				line = yield line

			while True:
				if line.StartsWith("synth_design:"):
					lastLine = gen.send(line)
					if LineKind.Last in line._kind:
						line._kind ^= LineKind.Last
					line = yield lastLine
					break

				line = yield gen.send(line)


@export
class Document(Processor):
	_logfile: Path
	_lines:   List[Line]

	def __init__(self, logfile: Path) -> None:
		super().__init__()

		self._logfile = logfile
		self._lines =   []

	def Parse(self) -> None:
		with Stopwatch() as sw:
			with self._logfile.open("r", encoding="utf-8") as f:
				content = f.read()

			self._lines = []
			next(generator := self.LineClassification())
			for rawLine in content.splitlines():
				line = generator.send(rawLine)
				self._lines.append(line)

		self._duration = sw.Duration
