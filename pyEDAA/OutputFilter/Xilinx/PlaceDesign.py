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
from re     import compile, Pattern
from typing import Generator, ClassVar, List, Type, Dict, Tuple

from pyTooling.Decorators import export
from pyTooling.Versioning import YearReleaseVersion, VersionRange, RangeBoundHandling

from pyEDAA.OutputFilter.Xilinx         import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Common2 import TaskWithPhases, Phase, SubPhase, SubSubPhase, SubSubSubPhase, PhaseWithChildren
from pyEDAA.OutputFilter.Xilinx.Common2 import MAJOR, MAJOR_MINOR, MAJOR_MINOR_MICRO, MAJOR_MINOR_MICRO_NANO





@export
class Phase_PlacerInitializationNetlistSorting(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Placer Initialization Netlist Sorting")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Placer Initialization Netlist Sorting \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_IOPlacement_ClockPlacement_BuildPlacerDevice(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} IO Placement/ Clock Placement/ Build Placer Device")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} IO Placement/ Clock Placement/ Build Placer Device \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_BuildPlacerNetlistModel(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Build Placer Netlist Model")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Build Placer Netlist Model \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_ConstrainClocks_Macros(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Constrain Clocks/Macros")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Constrain Clocks/Macros \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_PlacerInitialization(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Placer Initialization")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR} Placer Initialization \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_SUBPHASE_PREFIX: ClassVar[str] = "Phase {phase}."

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[SubPhase], ...]]] = {
		VersionRange(YearReleaseVersion(2019, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase_PlacerInitializationNetlistSorting,
			Phase_IOPlacement_ClockPlacement_BuildPlacerDevice,
			Phase_BuildPlacerNetlistModel,
			Phase_ConstrainClocks_Macros
		)
	}


@export
class Phase_Floorplanning(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Floorplanning")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Floorplanning \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_UpdateTimingBeforeSLRPathOpt(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Update Timing before SLR Path Opt")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Update Timing before SLR Path Opt \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_PostProcessingInFloorplanning(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Post-Processing in Floorplanning")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Post-Processing in Floorplanning \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_UpdateTimingBeforePhysicalSynthesis(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} UpdateTiming Before Physical Synthesis")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} UpdateTiming Before Physical Synthesis \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_PhysicalSynthesisInPlacer(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Physical Synthesis In Placer")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Physical Synthesis In Placer \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"

@export
class Phase_GlobalPlacementCore(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Placement Core")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Placement Core \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_UpdateTimingBeforePhysicalSynthesis,
		Phase_PhysicalSynthesisInPlacer
	)

	_subsubphases: Dict[Type[SubSubPhase], SubSubPhase]

	def __init__(self, subphase: SubPhase):
		super().__init__(subphase)

		self._subsubphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubPhaseStart(line)

		activeParsers: List[Phase] = list(self._subsubphases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 2.5."):
					for parser in activeParsers:  # type: SubSubPhase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubphase: {line!r}")
					break
				elif self._FINISH.match(line._message):
					nextLine = yield from self._SubPhaseFinish(line)
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
class Phase_GlobalPlacePhase1(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Place Phase1")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Place Phase1 \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_UpdateTimingBeforePhysicalSynthesis(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} UpdateTiming Before Physical Synthesis")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} UpdateTiming Before Physical Synthesis \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_PhysicalSynthesisInPlacer(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Physical Synthesis In Placer")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Physical Synthesis In Placer \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_GlobalPlacePhase2(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Place Phase2")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Place Phase2 \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_UpdateTimingBeforePhysicalSynthesis,
		Phase_PhysicalSynthesisInPlacer
	)

	_subsubphases: Dict[Type[SubSubPhase], SubSubPhase]

	def __init__(self, subphase: SubPhase):
		super().__init__(subphase)

		self._subsubphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubPhaseStart(line)

		activeParsers: List[Phase] = list(self._subsubphases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 2.5."):
					for parser in activeParsers:  # type: SubSubPhase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubphase: {line!r}")
					break
				elif self._FINISH.match(line._message):
					nextLine = yield from self._SubPhaseFinish(line)
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
class Phase_GlobalPlacement(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Global Placement")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR} Global Placement \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_SUBPHASE_PREFIX: ClassVar[str] = "Phase {phase}."

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[Phase], ...]]] = {
		VersionRange(YearReleaseVersion(2019, 1), YearReleaseVersion(2025, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase_Floorplanning,
			Phase_UpdateTimingBeforeSLRPathOpt,
			Phase_PostProcessingInFloorplanning,
			Phase_GlobalPlacePhase1,
			Phase_GlobalPlacePhase2,
			Phase_GlobalPlacementCore
		),
		VersionRange(YearReleaseVersion(2025, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase_Floorplanning,
			Phase_UpdateTimingBeforeSLRPathOpt,
			Phase_PostProcessingInFloorplanning,
			Phase_GlobalPlacePhase1,
			Phase_GlobalPlacePhase2
		)
	}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 2."):
					for parser in activeParsers:  # type: Phase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: {line!r}")
					break
				elif self._FINISH.match(line._message):
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
class Phase_CommitMultiColumnMacros(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Commit Multi Column Macros")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Commit Multi Column Macros \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_CommitMostMacrosLUTRAMs(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Commit Most Macros & LUTRAMs")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Commit Most Macros & LUTRAMs \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_SmallShapeClustering(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Small Shape Clustering")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Small Shape Clustering \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_SliceAreaSwapInitial(SubSubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO_NANO} Slice Area Swap Initial")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO_NANO} Slice Area Swap Initial \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_SliceAreaSwap(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Slice Area Swap")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Slice Area Swap \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_SliceAreaSwapInitial,
	)

	_subsubsubphases: Dict[Type[SubSubSubPhase], SubSubSubPhase]

	def __init__(self, subsubphase: SubSubPhase):
		super().__init__(subsubphase)

		self._subsubsubphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubSubPhaseStart(line)

		activeParsers: List[Phase] = list(self._subsubsubphases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 3.3.2."):
					for parser in activeParsers:  # type: SubSubSubPhase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubsubphase: {line!r}")
					break
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.SubSubPhaseTime
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

@export
class Phase_SmallShapeDP(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Small Shape DP")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Small Shape DP \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_SmallShapeClustering,
		Phase_SliceAreaSwap
	)

	_subsubphases: Dict[Type[SubSubPhase], SubSubPhase]

	def __init__(self, subphase: SubPhase):
		super().__init__(subphase)

		self._subsubphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubPhaseStart(line)

		activeParsers: List[Phase] = list(self._subsubphases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 3.3."):
					for parser in activeParsers:  # type: SubSubPhase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubphase: {line!r}")
					break
				elif self._FINISH.match(line._message):
					nextLine = yield from self._SubPhaseFinish(line)
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
class Phase_AreaSwapOptimization(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Area Swap Optimization")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Area Swap Optimization \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_ReassignLUTPins(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Re-assign LUT pins")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Re-assign LUT pins \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_PipelineRegisterOptimization_1(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Pipeline Register Optimization")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Pipeline Register Optimization \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_PipelineRegisterOptimization_2(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Pipeline Register Optimization")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Pipeline Register Optimization \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_FastOptimization_1(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Fast Optimization")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Fast Optimization \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_FastOptimization_2(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Fast Optimization")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Fast Optimization \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_SmallShapeDetailPlacement(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Small Shape Detail Placement")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Small Shape Detail Placement \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_DetailPlacement(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Detail Placement")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR} Detail Placement \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[Phase], ...]]] = {
		VersionRange(YearReleaseVersion(2019, 1), YearReleaseVersion(2023, 2), RangeBoundHandling.UpperBoundExclusive): (
			Phase_CommitMultiColumnMacros,
			Phase_CommitMostMacrosLUTRAMs,
			Phase_SmallShapeDP,
			Phase_ReassignLUTPins,
			Phase_PipelineRegisterOptimization_1,
			Phase_PipelineRegisterOptimization_2,
			Phase_FastOptimization_1,
			Phase_FastOptimization_2
		),
		VersionRange(YearReleaseVersion(2023, 2), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase_CommitMultiColumnMacros,
			Phase_CommitMostMacrosLUTRAMs,
			Phase_SmallShapeDP,
			Phase_AreaSwapOptimization,
			Phase_PipelineRegisterOptimization_1,
			Phase_PipelineRegisterOptimization_2,
			Phase_FastOptimization_1,
			Phase_FastOptimization_2,
			Phase_SmallShapeDetailPlacement,
			Phase_ReassignLUTPins
		)
	}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		START_PREFIX = f"Phase {self._phaseIndex}."

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith(START_PREFIX):
					for parser in activeParsers:  # type: Section
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: '{line!s}'")
					break
				elif self._FINISH.match(line._message):
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
class Phase_BUFGInsertion(SubSubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO_NANO} BUFG Insertion")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO_NANO} BUFG Insertion \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_PostPlacementTimingOptimization(SubSubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO_NANO} Post Placement Timing Optimization")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO_NANO} Post Placement Timing Optimization \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_PostPlacementOptimization(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Post Placement Optimization")
	_FINISH: ClassVar[str] = None  # Phase 4.1.1 Post Placement Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_BUFGInsertion,
		Phase_PostPlacementTimingOptimization
	)

	_subsubsubphases: Dict[Type[SubSubSubPhase], SubSubSubPhase]

	def __init__(self, subsubphase: SubSubPhase):
		super().__init__(subsubphase)

		self._subsubsubphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubSubPhaseStart(line)

		activeParsers: List[Phase] = list(self._subsubsubphases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 4.1.1."):
					for parser in activeParsers:  # type: SubSubSubPhase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubsubphase: {line!r}")
					break
				elif line.StartsWith(self._TIME):
					line._kind = LineKind.SubSubPhaseTime
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


@export
class Phase_PostCommitOptimization(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Post Commit Optimization")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Post Commit Optimization \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_PostPlacementOptimization,
	)

	_subsubphases: Dict[Type[SubSubPhase], SubSubPhase]

	def __init__(self, subphase: SubPhase):
		super().__init__(subphase)

		self._subsubphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubPhaseStart(line)

		activeParsers: List[Phase] = list(self._subsubphases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 4.1."):
					for parser in activeParsers:  # type: SubSubPhase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubphase: {line!r}")
					break
				elif self._FINISH.match(line._message):
					nextLine = yield from self._SubPhaseFinish(line)
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
class Phase_PostPlacementCleanup(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Post Placement Cleanup")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Post Placement Cleanup \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_PrintEstimatedCongestion(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Print Estimated Congestion")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Print Estimated Congestion \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase_PlacerReporting(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Placer Reporting")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Placer Reporting \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_PrintEstimatedCongestion,
	)

	_subsubphases: Dict[Type[SubSubPhase], SubSubPhase]

	def __init__(self, subphase: SubPhase):
		super().__init__(subphase)

		self._subsubphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubPhaseStart(line)

		activeParsers: List[Phase] = list(self._subsubphases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 4.3."):
					for parser in activeParsers:  # type: SubSubPhase
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubphase: {line!r}")
					break
				elif self._FINISH.match(line._message):
					nextLine = yield from self._SubPhaseFinish(line)
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
class Phase_FinalPlacementCleanup(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Final Placement Cleanup")
	_FINISH: ClassVar[Pattern] = compile("Time \(s\):")
	_TIME:   ClassVar[str] = None


@export
class Phase_PostPlacementOptimizationAndCleanUp(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Placement Optimization and Clean-Up")
	_FINISH: ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Placement Optimization and Clean-Up \| Checksum:")
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[SubPhase], ...]]] = {
		VersionRange(YearReleaseVersion(2019, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase_PostCommitOptimization,
			Phase_PostPlacementCleanup,
			Phase_PlacerReporting,
			Phase_FinalPlacementCleanup
		)
	}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		while True:
			while True:
				if isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 4."):
					for parser in activeParsers:  # type: Section
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: {line!r}")
					break
				elif self._FINISH.match(line._message):
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
class PlacerTask(TaskWithPhases):
	_START:  ClassVar[str] = "Starting Placer Task"
	_FINISH: ClassVar[str] = "Ending Placer Task"

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[Phase], ...]]] = {
		VersionRange(YearReleaseVersion(2019, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase_PlacerInitialization,
			Phase_GlobalPlacement,
			Phase_DetailPlacement,
			Phase_PostPlacementOptimizationAndCleanUp
		)
	}
