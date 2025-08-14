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
from typing import Generator, ClassVar, List, Type, Dict, Tuple

from pyTooling.Decorators import export
from pyTooling.Versioning import YearReleaseVersion, VersionRange, RangeBoundHandling

from pyEDAA.OutputFilter.Xilinx         import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Common2 import TaskWithPhases, Phase, SubPhase, SubSubPhase, SubSubSubPhase, PhaseWithChildren


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
class Phase1_PlacerInitialization(PhaseWithChildren):
	_START:  ClassVar[str] = "Phase 1 Placer Initialization"
	_FINISH: ClassVar[str] = "Phase 1 Placer Initialization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_SUBPHASE_PREFIX: ClassVar[str] = "Phase 1."

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[SubPhase], ...]]] = {
		VersionRange(YearReleaseVersion(2020, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase11_PlacerInitializationNetlistSorting,
			Phase12_IOPlacement_ClockPlacement_BuildPlacerDevice,
			Phase13_BuildPlacerNetlistModel,
			Phase14_ConstrainClocks_Macros
		)
	}


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
class Phase241_UpdateTimingBeforePhysicalSynthesis(SubSubPhase):
	_START:  ClassVar[str] = "Phase 2.4.1 UpdateTiming Before Physical Synthesis"
	_FINISH: ClassVar[str] = "Phase 2.4.1 UpdateTiming Before Physical Synthesis | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase242_PhysicalSynthesisInPlacer(SubSubPhase):
	_START:  ClassVar[str] = "Phase 2.4.2 Physical Synthesis In Placer"
	_FINISH: ClassVar[str] = "Phase 2.4.2 Physical Synthesis In Placer | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

@export
class Phase24_GlobalPlacementCore(SubPhase):
	_START:  ClassVar[str] = "Phase 2.4 Global Placement Core"
	_FINISH: ClassVar[str] = "Phase 2.4 Global Placement Core | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase241_UpdateTimingBeforePhysicalSynthesis,
		Phase242_PhysicalSynthesisInPlacer
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
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubphase: {line!r}")
					break
				elif line.StartsWith(self._FINISH):
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
class Phase24_GlobalPlacePhase1(SubPhase):
	_START:  ClassVar[str] = "Phase 2.4 Global Place Phase1"
	_FINISH: ClassVar[str] = "Phase 2.4 Global Place Phase1 | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase251_UpdateTimingBeforePhysicalSynthesis(SubSubPhase):
	_START:  ClassVar[str] = "Phase 2.5.1 UpdateTiming Before Physical Synthesis"
	_FINISH: ClassVar[str] = "Phase 2.5.1 UpdateTiming Before Physical Synthesis | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase252_PhysicalSynthesisInPlacer(SubSubPhase):
	_START:  ClassVar[str] = "Phase 2.5.2 Physical Synthesis In Placer"
	_FINISH: ClassVar[str] = "Phase 2.5.2 Physical Synthesis In Placer | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase25_GlobalPlacePhase2(SubPhase):
	_START:  ClassVar[str] = "Phase 2.5 Global Place Phase2"
	_FINISH: ClassVar[str] = "Phase 2.5 Global Place Phase2 | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase251_UpdateTimingBeforePhysicalSynthesis,
		Phase252_PhysicalSynthesisInPlacer
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
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubphase: {line!r}")
					break
				elif line.StartsWith(self._FINISH):
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
class Phase2_GlobalPlacement(PhaseWithChildren):
	_START:  ClassVar[str] = "Phase 2 Global Placement"
	_FINISH: ClassVar[str] = "Phase 2 Global Placement | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_SUBPHASE_PREFIX: ClassVar[str] = "Phase 2."

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[Phase], ...]]] = {
		VersionRange(YearReleaseVersion(2020, 1), YearReleaseVersion(2025, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase21_Floorplanning,
			Phase22_UpdateTimingBeforeSLRPathOpt,
			Phase23_PostProcessingInFloorplanning,
			Phase24_GlobalPlacementCore
		),
		VersionRange(YearReleaseVersion(2025, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase21_Floorplanning,
			Phase22_UpdateTimingBeforeSLRPathOpt,
			Phase23_PostProcessingInFloorplanning,
			Phase24_GlobalPlacePhase1,
			Phase25_GlobalPlacePhase2
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
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: {line!r}")
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
class Phase331_SmallShapeClustering(SubSubPhase):
	_START:  ClassVar[str] = "Phase 3.3.1 Small Shape Clustering"
	_FINISH: ClassVar[str] = "Phase 3.3.1 Small Shape Clustering | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase3321_SliceAreaSwapInitial(SubSubSubPhase):
	_START:  ClassVar[str] = "Phase 3.3.2.1 Slice Area Swap Initial"
	_FINISH: ClassVar[str] = "Phase 3.3.2.1 Slice Area Swap Initial | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase332_SliceAreaSwap(SubSubPhase):
	_START:  ClassVar[str] = "Phase 3.3.2 Slice Area Swap"
	_FINISH: ClassVar[str] = "Phase 3.3.2 Slice Area Swap | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase3321_SliceAreaSwapInitial,
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
						if line.StartsWith(parser._START):
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
class Phase33_SmallShapeDP(SubPhase):
	_START:  ClassVar[str] = "Phase 3.3 Small Shape DP"
	_FINISH: ClassVar[str] = "Phase 3.3 Small Shape DP | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase331_SmallShapeClustering,
		Phase332_SliceAreaSwap
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
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubphase: {line!r}")
					break
				elif line.StartsWith(self._FINISH):
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
class Phase33_AreaSwapOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 3.3 Area Swap Optimization"
	_FINISH: ClassVar[str] = "Phase 3.3 Area Swap Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase34_ReassignLUTPpins(SubPhase):
	_START:  ClassVar[str] = "Phase 3.4 Re-assign LUT pins"
	_FINISH: ClassVar[str] = "Phase 3.4 Re-assign LUT pins | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase34_PipelineRegisterOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 3.4 Pipeline Register Optimization"
	_FINISH: ClassVar[str] = "Phase 3.4 Pipeline Register Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase35_PipelineRegisterOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 3.5 Pipeline Register Optimization"
	_FINISH: ClassVar[str] = "Phase 3.5 Pipeline Register Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase35_FastOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 3.5 Fast Optimization"
	_FINISH: ClassVar[str] = "Phase 3.5 Fast Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase36_FastOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 3.6 Fast Optimization"
	_FINISH: ClassVar[str] = "Phase 3.6 Fast Optimization | Checksum:"
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
class Phase3_DetailPlacement(PhaseWithChildren):
	_START:  ClassVar[str] = "Phase 3 Detail Placement"
	_FINISH: ClassVar[str] = "Phase 3 Detail Placement | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[Phase], ...]]] = {
		VersionRange(YearReleaseVersion(2020, 1), YearReleaseVersion(2025, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase31_CommitMultiColumnMacros,
			Phase32_CommitMostMacrosLUTRAMs,
			Phase33_SmallShapeDP,
			Phase34_ReassignLUTPpins,
			Phase35_PipelineRegisterOptimization,
			Phase36_FastOptimization
		),
		VersionRange(YearReleaseVersion(2025, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
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
				elif line.StartsWith("Phase 3."):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: {line!r}")
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
class Phase4111_BUFGInsertion(SubSubSubPhase):
	_START:  ClassVar[str] = "Phase 4.1.1.1 BUFG Insertion"
	_FINISH: ClassVar[str] = "Phase 4.1.1.1 BUFG Insertion | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase4112_PostPlacementTimingOptimization(SubSubSubPhase):
	_START:  ClassVar[str] = "Phase 4.1.1.2 Post Placement Timing Optimization"
	_FINISH: ClassVar[str] = "Phase 4.1.1.2 Post Placement Timing Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase411_PostPlacementOptimization(SubSubPhase):
	_START:  ClassVar[str] = "Phase 4.1.1 Post Placement Optimization"
	_FINISH: ClassVar[str] = None  # Phase 4.1.1 Post Placement Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase4111_BUFGInsertion,
		Phase4112_PostPlacementTimingOptimization
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
						if line.StartsWith(parser._START):
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
class Phase41_PostCommitOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 4.1 Post Commit Optimization"
	_FINISH: ClassVar[str] = "Phase 4.1 Post Commit Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase411_PostPlacementOptimization,
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
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubphase: {line!r}")
					break
				elif line.StartsWith(self._FINISH):
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
class Phase42_PostPlacementCleanup(SubPhase):
	_START:  ClassVar[str] = "Phase 4.2 Post Placement Cleanup"
	_FINISH: ClassVar[str] = "Phase 4.2 Post Placement Cleanup | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase431_PrintEstimatedCongestion(SubSubPhase):
	_START:  ClassVar[str] = "Phase 4.3.1 Print Estimated Congestion"
	_FINISH: ClassVar[str] = "Phase 4.3.1 Print Estimated Congestion | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase43_PlacerReporting(SubPhase):
	_START:  ClassVar[str] = "Phase 4.3 Placer Reporting"
	_FINISH: ClassVar[str] = "Phase 4.3 Placer Reporting | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase431_PrintEstimatedCongestion,
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
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subsubphase: {line!r}")
					break
				elif line.StartsWith(self._FINISH):
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
class Phase44_FinalPlacementCleanup(SubPhase):
	_START:  ClassVar[str] = "Phase 4.4 Final Placement Cleanup"
	_FINISH: ClassVar[str] = "Time (s):"
	_TIME:   ClassVar[str] = None


@export
class Phase4_PostPlacementOptimizationAndCleanUp(PhaseWithChildren):
	_START:  ClassVar[str] = "Phase 4 Post Placement Optimization and Clean-Up"
	_FINISH: ClassVar[str] = "Phase 4 Post Placement Optimization and Clean-Up | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[SubPhase], ...]]] = {
		VersionRange(YearReleaseVersion(2020, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase41_PostCommitOptimization,
			Phase42_PostPlacementCleanup,
			Phase43_PlacerReporting,
			Phase44_FinalPlacementCleanup
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
						if line.StartsWith(parser._START):
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: {line!r}")
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
class PlacerTask(TaskWithPhases):
	_START:  ClassVar[str] = "Starting Placer Task"
	_FINISH: ClassVar[str] = "Ending Placer Task"

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[Phase], ...]]] = {
		VersionRange(YearReleaseVersion(2020, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase1_PlacerInitialization,
			Phase2_GlobalPlacement,
			Phase3_DetailPlacement,
			Phase4_PostPlacementOptimizationAndCleanUp
		)
	}
