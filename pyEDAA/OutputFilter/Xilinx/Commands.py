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
from pathlib import Path
from re      import compile as re_compile
from typing  import ClassVar, Generator, Union, List, Type, Dict, Iterator, Any, Tuple

from pyTooling.Decorators import export, readonly
from pyTooling.Versioning import YearReleaseVersion
from pyTooling.Warning    import WarningCollector

from pyEDAA.OutputFilter                         import OutputFilterException
from pyEDAA.OutputFilter.Xilinx                  import VivadoTclCommand
from pyEDAA.OutputFilter.Xilinx.Exception        import ProcessorException
from pyEDAA.OutputFilter.Xilinx.Common           import Line, LineKind, VivadoMessage, VHDLReportMessage
from pyEDAA.OutputFilter.Xilinx.Common2          import Parser, UnknownSection, UnknownTask, Task
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import Section, RTLElaboration, HandlingCustomAttributes
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import ConstraintValidation, LoadingPart, ApplySetProperty
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import RTLComponentStatistics, RTLHierarchicalComponentStatistics
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import PartResourceSummary, CrossBoundaryAndAreaOptimization
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import ROM_RAM_DSP_SR_Retiming, ApplyingXDCTimingConstraints
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import TimingOptimization, TechnologyMapping, IOInsertion
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import FlatteningBeforeIOInsertion, FinalNetlistCleanup
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import RenamingGeneratedInstances, RebuildingUserHierarchy
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import RenamingGeneratedPorts, RenamingGeneratedNets
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import WritingSynthesisReport
from pyEDAA.OutputFilter.Xilinx.OptimizeDesign   import DRCTask, CacheTimingInformationTask, LogicOptimizationTask
from pyEDAA.OutputFilter.Xilinx.OptimizeDesign   import PowerOptimizationTask, FinalCleanupTask, NetlistObfuscationTask
from pyEDAA.OutputFilter.Xilinx.PlaceDesign      import PlacerTask
from pyEDAA.OutputFilter.Xilinx.PhysicalOptimizeDesign import PhysicalSynthesisTask, InitialUpdateTimingTask
from pyEDAA.OutputFilter.Xilinx.RouteDesign      import RoutingTask


@export
class NotPresentException(ProcessorException):
	pass


@export
class SectionNotPresentException(NotPresentException):
	pass


@export
class HandlingCustomAttributes1(HandlingCustomAttributes):
	pass


@export
class HandlingCustomAttributes2(HandlingCustomAttributes):
	pass


@export
class ROM_RAM_DSP_SR_Retiming1(ROM_RAM_DSP_SR_Retiming):
	pass


@export
class ROM_RAM_DSP_SR_Retiming2(ROM_RAM_DSP_SR_Retiming):
	pass


@export
class ROM_RAM_DSP_SR_Retiming3(ROM_RAM_DSP_SR_Retiming):
	pass


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

	def _CommandStart(self, line: Line) -> Generator[Line, Line, Line]:
		"""
		A generator accepting a line containing the expected Vivado TCL command.

		When the generator exits, the returned line is the successor line to the line containing the Vivado TCL command.

		:param line: The first line for the generator to process.
		:returns:    A generator processing Vivado output log lines.
		"""
		if not (isinstance(line, VivadoTclCommand) and line._command == self._TCL_COMMAND):
			raise ProcessorException()  # FIXME: add exception message

		nextLine = yield line
		return nextLine

	def _CommandFinish(self, line: Line) -> Generator[Line, Line, Line]:
		if line.StartsWith(f"{self._TCL_COMMAND} completed successfully"):
			line._kind |= LineKind.Success
		else:
			line._kind |= LineKind.Failed

		line = yield line
		end = f"{self._TCL_COMMAND}: {self._TIME}"
		while self._TIME is not None:
			if line.StartsWith(end):
				line._kind = LineKind.TaskTime
				break

			line = yield line

		nextLine = yield line
		return nextLine

	def SectionDetector(self, line: Line) -> Generator[Union[Line, ProcessorException], Line, None]:
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

	_sections:  Dict[Type[Section], Section]

	_PARSERS: ClassVar[Tuple[Type[Section], ...]] = dict()

	def __init__(self, processor: "Processor") -> None:
		super().__init__(processor)

		self._sections =  {p: p(self) for p in self._PARSERS}

	@readonly
	def Sections(self) -> Dict[Type[Section], Section]:
		"""
		Read-only property to access a dictionary of found sections within the TCL command's output.

		:returns: A dictionary of found :class:`~pyEDAA.OutputFilter.Xilinx.SynthesizeDesign.Section`s.
		"""
		return self._sections

	def __getitem__(self, key: Type[Section]) -> Section:
		return self._sections[key]


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
	_tasks: Dict[Type[Task], Task]

	def __init__(self, processor: "Processor") -> None:
		super().__init__(processor)

		self._tasks = {t: t(self) for t in self._PARSERS}

	@readonly
	def Tasks(self) -> Dict[Type[Task], Task]:
		"""
		Read-only property to access a dictionary of found tasks within the TCL command's output.

		:returns: A dictionary of found :class:`~pyEDAA.OutputFilter.Xilinx.Common2.Task`s.
		"""
		return self._tasks

	def __getitem__(self, key: Type[Task]) -> Task:
		return self._tasks[key]


@export
class SynthesizeDesign(CommandWithSections):
	"""
	A Vivado command output parser for ``synth_design``.
	"""
	_TCL_COMMAND: ClassVar[str] = "synth_design"
	_PARSERS:     ClassVar[Tuple[Type[Section], ...]] = (
		RTLElaboration,
		HandlingCustomAttributes1,
		ConstraintValidation,
		LoadingPart,
		ApplySetProperty,
		RTLComponentStatistics,
		RTLHierarchicalComponentStatistics,
		PartResourceSummary,
		CrossBoundaryAndAreaOptimization,
		ROM_RAM_DSP_SR_Retiming1,
		ApplyingXDCTimingConstraints,
		TimingOptimization,
		ROM_RAM_DSP_SR_Retiming2,
		TechnologyMapping,
		IOInsertion,
		FlatteningBeforeIOInsertion,
		FinalNetlistCleanup,
		RenamingGeneratedInstances,
		RebuildingUserHierarchy,
		RenamingGeneratedPorts,
		HandlingCustomAttributes2,
		RenamingGeneratedNets,
		ROM_RAM_DSP_SR_Retiming3,
		WritingSynthesisReport,
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
		if (8 in self._messagesByID) and (327 in self._messagesByID[8]):
			return True

		return "LD" in self._sections[WritingSynthesisReport]._cells

	@readonly
	def Latches(self) -> Iterator[VivadoMessage]:
		try:
			yield from iter(self._messagesByID[8][327])
		except KeyError:
			yield from ()

	@readonly
	def HasBlackboxes(self) -> bool:
		"""
		Read-only property returning if the design contains black-boxes.

		:returns: True, if the design contains black-boxes.
		"""
		return len(self._sections[WritingSynthesisReport]._blackboxes) > 0

	@readonly
	def Blackboxes(self) -> Dict[str, int]:
		return self._sections[WritingSynthesisReport]._blackboxes

	@readonly
	def Cells(self) -> Dict[str, int]:
		return self._sections[WritingSynthesisReport]._cells

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

	def __getitem__(self, item: Type[Parser]) -> Union[_PARSERS]:
		try:
			return self._sections[item]
		except KeyError as ex:
			raise SectionNotPresentException(F"Section '{item._NAME}' not present in '{self._parent.logfile}'.") from ex

	def SectionDetector(self, line: Line) -> Generator[Union[Line, ProcessorException], Line, None]:
		if not (isinstance(line, VivadoTclCommand) and line._command == self._TCL_COMMAND):
			raise ProcessorException()  # FIXME: add exception message

		activeParsers: List[Parser] = list(self._sections.values())

		rtlElaboration = self._sections[RTLElaboration]
		# constraintValidation = self._sections[ConstraintValidation]

		line = yield line
		if line == "Starting synth_design":
			line._kind = LineKind.Verbose
		else:
			raise ProcessorException()

		line = yield line
		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif line.StartsWith("Start "):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = next(section := parser.Generator(line))
							line._previousLine._kind = LineKind.SectionStart | LineKind.SectionDelimiter
							break
					else:
						WarningCollector.Raise(UnknownSection(f"Unknown section: '{line!r}'", line))
						ex = Exception(f"How to recover from here? Unknown section: '{line!r}'")
						ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self._task._command}")
						raise ex
					break
				elif line.StartsWith("Starting "):
					if line.StartsWith(rtlElaboration._START):
						parser = rtlElaboration
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
				elif not isinstance(line, VivadoMessage):
					pass
					# line._kind = LineKind.Unprocessed

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

			activeParsers.remove(parser)


@export
class LinkDesign(Command):
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

	def SectionDetector(self, line: Line) -> Generator[Union[Line, ProcessorException], Line, Line]:
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
class OptimizeDesign(CommandWithTasks):
	"""
	A Vivado command output parser for ``opt_design``.
	"""
	_TCL_COMMAND: ClassVar[str] = "opt_design"
	_TIME:        ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Task], ...]] = (
		DRCTask,
		CacheTimingInformationTask,
		LogicOptimizationTask,
		PowerOptimizationTask,
		FinalCleanupTask,
		NetlistObfuscationTask
	)

	def SectionDetector(self, line: Line) -> Generator[Union[Line, ProcessorException], Line, Line]:
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
						ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self._task._command}")
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
class PlaceDesign(CommandWithTasks):
	"""
	A Vivado command output parser for ``place_design``.
	"""
	_TCL_COMMAND: ClassVar[str] = "place_design"
	_TIME:        ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Task], ...]] = (
		PlacerTask,
	)

	def SectionDetector(self, line: Line) -> Generator[Union[Line, ProcessorException], Line, Line]:
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
						ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self._task._command}")
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
class PhysicalOptimizeDesign(CommandWithTasks):
	"""
	A Vivado command output parser for ``phy_opt_design``.
	"""
	_TCL_COMMAND: ClassVar[str] = "phys_opt_design"
	_TIME:        ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Task], ...]] = (
		InitialUpdateTimingTask,
		PhysicalSynthesisTask
	)

	def SectionDetector(self, line: Line) -> Generator[Union[Line, ProcessorException], Line, Line]:
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
						ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self._task._command}")
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
class RouteDesign(CommandWithTasks):
	"""
	A Vivado command output parser for ``route_design``.
	"""
	_TCL_COMMAND: ClassVar[str] = "route_design"
	_TIME:        ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Task], ...]] = (
		RoutingTask,
	)

	def SectionDetector(self, line: Line) -> Generator[Union[Line, ProcessorException], Line, Line]:
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
						ex.add_note(f"Current task: start pattern='{self._task}'")
						ex.add_note(f"Current cmd:  {self._task._command}")
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
class WriteBitstream(Command):
	"""
	A Vivado command output parser for ``write_bitstream``.
	"""
	_TCL_COMMAND: ClassVar[str] = "write_bitstream"
	_TIME:        ClassVar[str] = "Time (s):"


@export
class ReportDRC(Command):
	"""
	A Vivado command output parser for ``report_drc``.
	"""
	_TCL_COMMAND: ClassVar[str] = "report_drc"
	_TIME:        ClassVar[str] = None


@export
class ReportMethodology(Command):
	"""
	A Vivado command output parser for ``report_methodology``.
	"""
	_TCL_COMMAND: ClassVar[str] = "report_methodology"
	_TIME:        ClassVar[str] = None


@export
class ReportPower(Command):
	"""
	A Vivado command output parser for ``report_power``.
	"""
	_TCL_COMMAND: ClassVar[str] = "report_power"
	_TIME:        ClassVar[str] = None
