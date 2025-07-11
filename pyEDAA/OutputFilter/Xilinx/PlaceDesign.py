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
"""A filtering anc classification processor for AMD/Xilinx Vivado Synthesis outputs."""
from typing import Generator, ClassVar, List, Type, Dict

from pyTooling.Decorators  import export
from pyTooling.MetaClasses import ExtendedType, abstractmethod

from pyEDAA.OutputFilter.Xilinx           import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Exception import ProcessorException
from pyEDAA.OutputFilter.Xilinx.Common2   import BaseParser, VivadoMessagesMixin


@export
class Task(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	_TIME:   ClassVar[str] = "Time (s):"

	_command:  "Command"
	_duration: float

	def __init__(self, command: "Command"):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._command = command

	def _TaskStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException()

		line._kind = LineKind.TaskStart
		nextLine = yield line
		return nextLine

	def _TaskFinish(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException()

		line._kind = LineKind.TaskEnd
		line = yield line
		while self._TIME is not None:
			if line.StartsWith(self._TIME):
				line._kind = LineKind.TaskTime
				break

			line = yield line

		line = yield line
		return line

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._TaskStart(line)

		while True:
			if line.StartsWith("Ending"):
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


@export
class Phase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]

	_task:     Task
	_duration: float

	def __init__(self, task: Task):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._task = task

	def _PhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException()

		line._kind = LineKind.PhaseStart
		nextLine = yield line
		return nextLine

	def _PhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException()

		line._kind = LineKind.PhaseEnd
		line = yield line

		while self._TIME is not None:
			if line.StartsWith(self._TIME):
				line._kind = LineKind.PhaseTime
				break

			line = yield line

		line = yield line
		while self._FINAL is not None:
			if line.StartsWith(self._FINAL):
				line._kind = LineKind.PhaseFinal
				break

			line = yield line

		nextLine = yield line
		return nextLine

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		while True:
			if line.StartsWith(self._FINISH):
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)

			line = yield line

		nextLine = yield from self._PhaseFinish(line)
		return nextLine


@export
class SubPhase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]

	_phase:    Phase
	_duration: float

	def __init__(self, phase: Phase):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._phase = phase

	def _SubPhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException()

		line._kind = LineKind.SubPhaseStart
		nextLine = yield line
		return nextLine

	def _SubPhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException()

		line._kind = LineKind.SubPhaseEnd
		line = yield line

		while self._TIME is not None:
			if line.StartsWith(self._TIME):
				line._kind = LineKind.SubPhaseTime
				break

			line = yield line

		nextLine = yield line
		return nextLine

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubPhaseStart(line)

		while True:
			if line.StartsWith(self._FINISH):
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)

			line = yield line

		nextLine = yield from self._SubPhaseFinish(line)
		return nextLine


@export
class Phase11_PlacerInitializationNetlistSorting(SubPhase):
	_START:  ClassVar[str] = "Phase 1.1 Placer Initialization Netlist Sorting"
	_FINISH: ClassVar[str] = "Phase 1.1 Placer Initialization Netlist Sorting | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase12_IOPlacement_ClockPlacement_BuildPlacerDevice(SubPhase):
	_START:  ClassVar[str] = "Phase 1.2 IO Placement/ Clock Placement/ Build Placer Device"
	_FINISH: ClassVar[str] = "Phase 1.2 IO Placement/ Clock Placement/ Build Placer Device | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase13_BuildPlacerNetlistModel(SubPhase):
	_START:  ClassVar[str] = "Phase 1.3 Build Placer Netlist Model"
	_FINISH: ClassVar[str] = "Phase 1.3 Build Placer Netlist Model | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase14_ConstrainClocks_Macros(SubPhase):
	_START:  ClassVar[str] = "Phase 1.4 Constrain Clocks/Macros"
	_FINISH: ClassVar[str] = "Phase 1.4 Constrain Clocks/Macros | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase1_PlacerInitialization(Phase):
	_START:  ClassVar[str] = "Phase 1 Placer Initialization"
	_FINISH: ClassVar[str] = "Phase 1 Placer Initialization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[List[Type[Phase]]] = (
		Phase11_PlacerInitializationNetlistSorting,
		Phase12_IOPlacement_ClockPlacement_BuildPlacerDevice,
		Phase13_BuildPlacerNetlistModel,
		Phase14_ConstrainClocks_Macros
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		while True:
			while True:
				if isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 1."):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: {line}")
					break
				elif line.StartsWith(self._FINISH):
					nextLine = yield from self._PhaseFinish(line)
					return nextLine

				line = yield line

			while phase is not None:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield phase.send(line)
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break


@export
class Phase21_Floorplanning(SubPhase):
	_START:  ClassVar[str] = "Phase 2.1 Floorplanning"
	_FINISH: ClassVar[str] = "Phase 2.1 Floorplanning | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase22_UpdateTimingBeforeSLRPathOpt(SubPhase):
	_START:  ClassVar[str] = "Phase 2.2 Update Timing before SLR Path Opt"
	_FINISH: ClassVar[str] = "Phase 2.2 Update Timing before SLR Path Opt | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase23_PostProcessingInFloorplanning(SubPhase):
	_START:  ClassVar[str] = "Phase 2.3 Post-Processing in Floorplanning"
	_FINISH: ClassVar[str] = "Phase 2.3 Post-Processing in Floorplanning | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase24_GlobalPlacePhase1(SubPhase):
	_START:  ClassVar[str] = "Phase 2.4 Global Place Phase1"
	_FINISH: ClassVar[str] = "Phase 2.4 Global Place Phase1 | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


# 2.5.1 UpdateTiming Before Physical Synthesis
# 2.5.2 Physical Synthesis In Placer

@export
class Phase25_GlobalPlacePhase2(SubPhase):
	_START:  ClassVar[str] = "Phase 2.5 Global Place Phase2"
	_FINISH: ClassVar[str] = "Phase 2.5 Global Place Phase2 | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase2_GlobalPlacement(Phase):
	_START:  ClassVar[str] = "Phase 2 Global Placement"
	_FINISH: ClassVar[str] = "Phase 2 Global Placement | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[List[Type[Phase]]] = (
		Phase21_Floorplanning,
		Phase22_UpdateTimingBeforeSLRPathOpt,
		Phase23_PostProcessingInFloorplanning,
		Phase24_GlobalPlacePhase1,
		Phase25_GlobalPlacePhase2
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		while True:
			while True:
				if isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 2."):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: {line}")
					break
				elif line.StartsWith(self._FINISH):
					nextLine = yield from self._PhaseFinish(line)
					return nextLine

				line = yield line

			while phase is not None:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield phase.send(line)
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break


@export
class Phase31_CommitMultiColumnMacros(SubPhase):
	_START:  ClassVar[str] = "Phase 3.1 Commit Multi Column Macros"
	_FINISH: ClassVar[str] = "Phase 3.1 Commit Multi Column Macros | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase32_CommitMostMacrosLUTRAMs(SubPhase):
	_START:  ClassVar[str] = "Phase 3.2 Commit Most Macros & LUTRAMs"
	_FINISH: ClassVar[str] = "Phase 3.2 Commit Most Macros & LUTRAMs | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase33_AreaSwapOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 3.3 Area Swap Optimization"
	_FINISH: ClassVar[str] = "Phase 3.3 Area Swap Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase34_PipelineRegisterOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 3.4 Pipeline Register Optimization"
	_FINISH: ClassVar[str] = "Phase 3.4 Pipeline Register Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase35_FastOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 3.5 Fast Optimization"
	_FINISH: ClassVar[str] = "Phase 3.5 Fast Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase36_SmallShapeDetailPlacement(SubPhase):
	_START:  ClassVar[str] = "Phase 3.6 Small Shape Detail Placement"
	_FINISH: ClassVar[str] = "Phase 3.6 Small Shape Detail Placement | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase37_ReassignLUTPins(SubPhase):
	_START:  ClassVar[str] = "Phase 3.7 Re-assign LUT pins"
	_FINISH: ClassVar[str] = "Phase 3.7 Re-assign LUT pins | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase38_PipelineRegisterOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 3.8 Pipeline Register Optimization"
	_FINISH: ClassVar[str] = "Phase 3.8 Pipeline Register Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase39_FastOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 3.9 Fast Optimization"
	_FINISH: ClassVar[str] = "Phase 3.9 Fast Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase3_DetailPlacement(Phase):
	_START:  ClassVar[str] = "Phase 3 Detail Placement"
	_FINISH: ClassVar[str] = "Phase 3 Detail Placement | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[List[Type[Phase]]] = (
		Phase31_CommitMultiColumnMacros,
		Phase32_CommitMostMacrosLUTRAMs,
		Phase33_AreaSwapOptimization,
		Phase34_PipelineRegisterOptimization,
		Phase35_FastOptimization,
		Phase36_SmallShapeDetailPlacement,
		Phase37_ReassignLUTPins,
		Phase38_PipelineRegisterOptimization,
		Phase39_FastOptimization
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		while True:
			while True:
				if isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 3."):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: {line}")
					break
				elif line.StartsWith(self._FINISH):
					nextLine = yield from self._PhaseFinish(line)
					return nextLine

				line = yield line

			while phase is not None:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield phase.send(line)
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break


@export
class Phase41_PostCommitOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 4.1 Post Commit Optimization"
	_FINISH: ClassVar[str] = "Phase 4.1 Post Commit Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase42_PostPlacementCleanup(SubPhase):
	_START:  ClassVar[str] = "Phase 4.2 Post Placement Cleanup"
	_FINISH: ClassVar[str] = "Phase 4.2 Post Placement Cleanup | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase43_PlacerReporting(SubPhase):
	_START:  ClassVar[str] = "Phase 4.3 Placer Reporting"
	_FINISH: ClassVar[str] = "Phase 4.3 Placer Reporting | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase44_FinalPlacementCleanup(SubPhase):
	_START:  ClassVar[str] = "Phase 4.4 Final Placement Cleanup"
	_FINISH: ClassVar[str] = "Phase 4.4 Final Placement Cleanup | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase4_PostPlacementOptimizationAndCleanUp(Phase):
	_START:  ClassVar[str] = "Phase 4 Post Placement Optimization and Clean-Up"
	_FINISH: ClassVar[str] = "Phase 4 Post Placement Optimization and Clean-Up | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[List[Type[Phase]]] = (
		Phase41_PostCommitOptimization,
		Phase42_PostPlacementCleanup,
		Phase43_PlacerReporting,
		Phase44_FinalPlacementCleanup
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		while True:
			while True:
				if isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 4."):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: {line}")
					break
				elif line.StartsWith(self._FINISH):
					nextLine = yield from self._PhaseFinish(line)
					return nextLine

				line = yield line

			while phase is not None:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield phase.send(line)
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break


@export
class PlacerTask(Task):
	_START:  ClassVar[str] = "Starting Placer Task"
	_FINISH: ClassVar[str] = "Ending Placer Task"

	_PARSERS: ClassVar[List[Type[Phase]]] = (
		Phase1_PlacerInitialization,
		Phase2_GlobalPlacement,
		Phase3_DetailPlacement,
		Phase4_PostPlacementOptimizationAndCleanUp
	)

	_phases: Dict[Type[Phase], Phase]

	def __init__(self, command: "Command"):
		super().__init__(command)

		self._phases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._TaskStart(line)

		activeParsers: List[Phase] = list(self._phases.values())

		while True:
			while True:
				if isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase "):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown phase: {line}")
					break
				elif line.StartsWith("Ending"):
					nextLine = yield from self._TaskFinish(line)
					return nextLine
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.TaskTime
					nextLine = yield line
					return nextLine

				line = yield line

			while phase is not None:
				# if line.StartsWith("Ending"):
				# 	line = yield task.send(line)
				# 	break

				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				try:
					line = yield phase.send(line)
				except StopIteration as ex:
					activeParsers.remove(parser)
					line = ex.value
					break
