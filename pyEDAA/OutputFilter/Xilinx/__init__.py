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
from pyEDAA.OutputFilter.Xilinx.Commands import Command, SynthesizeDesign, LinkDesign, OptimizeDesign, PlaceDesign, \
	PhysicalOptimizeDesign, RouteDesign, WriteBitstream, ReportDRC, ReportMethodology, ReportPower
from pyEDAA.OutputFilter.Xilinx.Common2   import Preamble, VivadoMessagesMixin
from pyEDAA.OutputFilter.Xilinx.Exception import ProcessorException, ClassificationException


ProcessedLine = Union[Line, ProcessorException]


@export
class Processor(VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	"""
	A processor for Vivado log outputs.

	Each output line from Vivado gets processed and converted into a :class:`ProcessedLine` objects. Such lines form a
	doubly-linked list.
	"""
	_duration:                float  #: Duration of the observed process (e.g. start to end of synthesis).
	_processingDuration:      float  #: Duration for the log output processor to parse all log messages.

	_lines:                   List[ProcessedLine]           #: A list of processed log message lines.
	_preamble:                Preamble                      #: Reference to the Vivado preamble written after tool startup.
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
		self._commands =                {}

	@readonly
	def Lines(self) -> List[ProcessedLine]:
		"""
		Read-only property to access the list of processed and classified log lines (messages).

		:returns: A list of processed lines.
		"""
		return self._lines

	@readonly
	def Preamble(self) -> Preamble:
		"""
		Read-only property to access the parsed preamble information.

		:returns: The log output preamble.
		"""
		return self._preamble

	@readonly
	def Commands(self) -> Dict[Type[Command], Command]:
		"""
		Read-only property to access the dictionary of processed Vivado commands.

		:returns: The dictionary of processed Vivado commands.
		"""
		return self._commands

	@readonly
	def Duration(self) -> float:
		"""
		 Duration of the observed process (e.g. start to end of synthesis).

		:returns: The observed process' execution duration in seconds.
		"""
		start = self._preamble._startDatetime


		return self._duration

	@readonly
	def ProcessingDuration(self) -> float:
		"""
		Processing duration for the log output processor to parse all log messages.

		:returns: The processing duration in seconds.
		"""
		return self._processingDuration

	def __contains__(self, item: Type[Command]) -> bool:
		"""
		Returns True, if log outputs where found for the given command.

		:param item: Vivado command (class).
		:returns:    True, if the Vivado command's outputs were found in log outputs.
		"""
		return item in self._commands

	def __getitem__(self, item: Type[Command]) -> Command:
		"""
		Access Vivado command specific log outputs and parsed data by the command.

		:param item: Vivado command (class) to access.
		:returns:    A Vivado command instance with parsed log messages and extracted data.
		"""
		return self._commands[item]

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

	def LineClassification(self) -> Generator[ProcessedLine, str, None]:
		# Instantiate and initialize CommandFinder
		next(cmdFinder := self.CommandFinder())

		# wait for first line
		lastLine = None
		rawMessageLine = yield
		lineNumber = 0
		_errorMessage = "Unknown processing error"

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
				errorMessage = "Line starting with 'Command:' was not a VivadoTclCommand."
			else:
				line = Line(lineNumber, LineKind.Unprocessed, rawMessageLine)

			if line is None:
				line = Line(lineNumber, LineKind.ProcessorError, rawMessageLine)
			else:
				if line.StartsWith("Resolution:") and isinstance(lastLine, VivadoMessage):
					line._kind = LineKind.Verbose

			line.PreviousLine = lastLine
			lastLine = line
			line = cmdFinder.send(line)

			if isinstance(line, VivadoMessage):
				self._AddMessage(line)

			if line._kind is LineKind.ProcessorError:
				line = ClassificationException(errorMessage, lineNumber, rawMessageLine)

			self._lines.append(line)

			rawMessageLine = yield line

	def CommandFinder(self) -> Generator[Line, Line, None]:
		self._preamble = Preamble(self)
		cmd = None

		tclProcedures = {"source"}

		# wait for first line
		line = yield
		# process preamble
		line = yield from self._preamble.Generator(line)

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoTclCommand):
					if line._command == SynthesizeDesign._TCL_COMMAND:
						self._commands[SynthesizeDesign] = (cmd := SynthesizeDesign(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._command == LinkDesign._TCL_COMMAND:
						self._commands[LinkDesign] = (cmd := LinkDesign(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._command == OptimizeDesign._TCL_COMMAND:
						self._commands[OptimizeDesign] = (cmd := OptimizeDesign(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._command == OptimizeDesign._TCL_COMMAND:
						self._commands[OptimizeDesign] = (cmd := OptimizeDesign(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._command == PlaceDesign._TCL_COMMAND:
						self._commands[PlaceDesign] = (cmd := PlaceDesign(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._command == PhysicalOptimizeDesign._TCL_COMMAND:
						self._commands[PhysicalOptimizeDesign] = (cmd := PhysicalOptimizeDesign(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._command == RouteDesign._TCL_COMMAND:
						self._commands[RouteDesign] = (cmd := RouteDesign(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._command == WriteBitstream._TCL_COMMAND:
						self._commands[WriteBitstream] = (cmd := WriteBitstream(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._command == ReportDRC._TCL_COMMAND:
						self._commands[ReportDRC] = (cmd := ReportDRC(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._command == ReportMethodology._TCL_COMMAND:
						self._commands[ReportMethodology] = (cmd := ReportMethodology(self))
						line = yield next(gen := cmd.SectionDetector(line))
						break
					elif line._command == ReportPower._TCL_COMMAND:
						self._commands[ReportPower] = (cmd := ReportPower(self))
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
			with self._logfile.open("r", encoding="utf-8") as f:
				content = f.read()

			next(generator := self.LineClassification())
			for rawLine in content.splitlines():
				generator.send(rawLine)

		self._processingDuration = sw.Duration
