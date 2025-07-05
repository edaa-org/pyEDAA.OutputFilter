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
from typing   import Optional as Nullable, Dict, List, Generator, Union, Type

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Stopwatch   import Stopwatch

from pyEDAA.OutputFilter.Xilinx.Common    import LineKind, Line
from pyEDAA.OutputFilter.Xilinx.Common    import VivadoMessage, TclCommand, VivadoTclCommand
from pyEDAA.OutputFilter.Xilinx.Common    import InfoMessage, VivadoInfoMessage, VivadoIrregularInfoMessage
from pyEDAA.OutputFilter.Xilinx.Common    import WarningMessage, VivadoWarningMessage, VivadoIrregularWarningMessage
from pyEDAA.OutputFilter.Xilinx.Common    import CriticalWarningMessage, VivadoCriticalWarningMessage
from pyEDAA.OutputFilter.Xilinx.Common    import ErrorMessage, VivadoErrorMessage
from pyEDAA.OutputFilter.Xilinx.Common    import VHDLReportMessage
from pyEDAA.OutputFilter.Xilinx.Commands  import Command, SynthesizeDesign
from pyEDAA.OutputFilter.Xilinx.Common2   import Preamble, VivadoMessagesMixin
from pyEDAA.OutputFilter.Xilinx.Exception import ProcessorException, ClassificationException


ProcessedLine = Union[Line, ProcessorException]


@export
class Processor(VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	_duration:                float

	_preamble:                Preamble
	_commands:                Dict[Type[Command], Command]

	def __init__(self):
		super().__init__()

		self._duration =                0.0

		self._preamble =                None
		self._commands =                {}

	@readonly
	def Preamble(self) -> Preamble:
		return self._preamble

	@readonly
	def Commands(self) -> Dict[Type[Command], Command]:
		return self._commands

	@readonly
	def Duration(self) -> float:
		return self._duration

	def __getitem__(self, item: Type[Command]) -> Command:
		return self._commands[item]

	def LineClassification(self) -> Generator[ProcessedLine, str, None]:
		# Instantiate and initialize CommandFinder
		next(cmdFinder := self.CommandFinder())

		# wait for first line
		lastLine = None
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

			line.PreviousLine = lastLine
			lastLine = line
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
