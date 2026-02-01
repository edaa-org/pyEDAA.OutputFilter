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
"""A filtering anc classification processor for AMD/Xilinx Vivado Synthesis outputs."""
from re     import compile, Pattern
from typing import ClassVar, Type, Tuple

from pyTooling.Decorators import export

from pyEDAA.OutputFilter.Xilinx.Common2 import TaskWithPhases
from pyEDAA.OutputFilter.Xilinx.Common2 import Phase, SubPhase, SubSubPhase, SubSubSubPhase
from pyEDAA.OutputFilter.Xilinx.Common2 import PhaseWithChildren, SubPhaseWithChildren, SubSubPhaseWithChildren
from pyEDAA.OutputFilter.Xilinx.Common2 import MAJOR, MAJOR_MINOR, MAJOR_MINOR_MICRO, MAJOR_MINOR_MICRO_NANO


@export
class SubPhase_PlacerInitializationNetlistSorting(SubPhase):
	"""
	*Placer Initialization Netlist Sorting* subphase.

	Used by phase :class:`Phase_PlacerInitialization`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Placer Initialization Netlist Sorting")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Placer Initialization Netlist Sorting | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_IOPlacement_ClockPlacement_BuildPlacerDevice(SubPhase):
	"""
	*IO Placement/ Clock Placement/ Build Placer Device* subphase.

	Used by phase :class:`Phase_PlacerInitialization`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} IO Placement/ Clock Placement/ Build Placer Device")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} IO Placement/ Clock Placement/ Build Placer Device | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_BuildPlacerNetlistModel(SubPhase):
	"""
	*Build Placer Netlist Model* subphase.

	Used by phase :class:`Phase_PlacerInitialization`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Build Placer Netlist Model")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Build Placer Netlist Model | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_ConstrainClocks_Macros(SubPhase):
	"""
	*Constrain Clocks/Macros* subphase.

	Used by phase :class:`Phase_PlacerInitialization`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Constrain Clocks/Macros")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Constrain Clocks/Macros | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PlacerInitialization(PhaseWithChildren):
	"""
	*Placer Initialization* phase.

	.. topic:: Uses

	* :class:`SubPhase_PlacerInitializationNetlistSorting`
	* :class:`SubPhase_IOPlacement_ClockPlacement_BuildPlacerDevice`
	* :class:`SubPhase_BuildPlacerNetlistModel`
	* :class:`SubPhase_ConstrainClocks_Macros`

	Used by task :class:`PlacerTask`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Placer Initialization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Placer Initialization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str]     = None

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_PlacerInitializationNetlistSorting,
		SubPhase_IOPlacement_ClockPlacement_BuildPlacerDevice,
		SubPhase_BuildPlacerNetlistModel,
		SubPhase_ConstrainClocks_Macros
	)


@export
class SubPhase_Floorplanning(SubPhase):
	"""
	*Floorplanning* subphase.

	Used by phase :class:`Phase_GlobalPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Floorplanning")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Floorplanning | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_UpdateTimingBeforeSLRPathOpt(SubPhase):
	"""
	*Update Timing before SLR Path Opt* subphase.

	Used by phase :class:`Phase_GlobalPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Update Timing before SLR Path Opt")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Update Timing before SLR Path Opt | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_PostProcessingInFloorplanning(SubPhase):
	"""
	*Post-Processing in Floorplanning* subphase.

	Used by phase :class:`Phase_GlobalPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Post-Processing in Floorplanning")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Post-Processing in Floorplanning | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubSubPhase_UpdateTimingBeforePhysicalSynthesis(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} UpdateTiming Before Physical Synthesis")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex} UpdateTiming Before Physical Synthesis | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubSubPhase_PhysicalSynthesisInPlacer(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Physical Synthesis In Placer")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex} Physical Synthesis In Placer | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_GlobalPlacementCore(SubPhaseWithChildren):
	"""
	*Global Placement Core* subphase.

	Used by phase :class:`Phase_GlobalPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Placement Core")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Placement Core | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubSubPhase], ...]] = (
		SubSubPhase_UpdateTimingBeforePhysicalSynthesis,
		SubSubPhase_PhysicalSynthesisInPlacer
	)


@export
class SubPhase_GlobalPlacePhase1(SubPhase):
	"""
	*Global Place Phase1* subphase.

	Used by phase :class:`Phase_GlobalPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Place Phase1")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Place Phase1 | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


# @export
# class SubSubPhase_UpdateTimingBeforePhysicalSynthesis(SubSubPhase):
# 	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} UpdateTiming Before Physical Synthesis")
# 	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex} UpdateTiming Before Physical Synthesis | Checksum:"
# 	_TIME:   ClassVar[str]     = "Time (s):"


# @export
# class SubSubPhase_PhysicalSynthesisInPlacer(SubSubPhase):
# 	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Physical Synthesis In Placer")
# 	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex} Physical Synthesis In Placer | Checksum:"
# 	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_GlobalPlacePhase2(SubPhaseWithChildren):
	"""
	*Global Place Phase2* subphase.

	Used by phase :class:`Phase_GlobalPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Place Phase2")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Place Phase2 | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubSubPhase], ...]] = (
		SubSubPhase_UpdateTimingBeforePhysicalSynthesis,
		SubSubPhase_PhysicalSynthesisInPlacer
	)


@export
class Phase_GlobalPlacement(PhaseWithChildren):
	"""
	*Global Placement* phase.

	.. topic:: Uses

	* :class:`SubPhase_Floorplanning`
	* :class:`SubPhase_UpdateTimingBeforeSLRPathOpt`
	* :class:`SubPhase_PostProcessingInFloorplanning`
	* :class:`SubPhase_GlobalPlacePhase1`
	* :class:`SubPhase_GlobalPlacePhase2`
	* :class:`SubPhase_GlobalPlacementCore`

	Used by task :class:`PlacerTask`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Global Placement")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Global Placement | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str]     = None

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_Floorplanning,
		SubPhase_UpdateTimingBeforeSLRPathOpt,
		SubPhase_PostProcessingInFloorplanning,
		SubPhase_GlobalPlacePhase1,
		SubPhase_GlobalPlacePhase2,
		SubPhase_GlobalPlacementCore
	)


@export
class SubPhase_CommitMultiColumnMacros(SubPhase):
	"""
	*Commit Multi Column Macros* subphase.

	Used by phase :class:`Phase_DetailPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Commit Multi Column Macros")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Commit Multi Column Macros | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_CommitMostMacrosLUTRAMs(SubPhase):
	"""
	*Commit Most Macros & LUTRAMs* subphase.

	Used by phase :class:`Phase_DetailPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Commit Most Macros & LUTRAMs")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Commit Most Macros & LUTRAMs | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubSubPhase_SmallShapeClustering(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Small Shape Clustering")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex} Small Shape Clustering | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubSubSubPhase_SliceAreaSwapInitial(SubSubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO_NANO} Slice Area Swap Initial")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex}.{subSubSubPhaseIndex} Slice Area Swap Initial | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubSubPhase_SliceAreaSwap(SubSubPhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Slice Area Swap")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex} Slice Area Swap | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubSubSubPhase], ...]] = (
		SubSubSubPhase_SliceAreaSwapInitial,
	)


@export
class SubPhase_SmallShapeDP(SubPhaseWithChildren):
	"""
	*Small Shape DP* subphase.

	Used by phase :class:`Phase_DetailPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Small Shape DP")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Small Shape DP | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubSubPhase], ...]] = (
		SubSubPhase_SmallShapeClustering,
		SubSubPhase_SliceAreaSwap
	)


@export
class SubPhase_AreaSwapOptimization(SubPhase):
	"""
	*Area Swap Optimization* subphase.

	Used by phase :class:`Phase_DetailPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Area Swap Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Area Swap Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_ReassignLUTPins(SubPhase):
	"""
	*Re-assign LUT pins* subphase.

	Used by phase :class:`Phase_DetailPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Re-assign LUT pins")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Re-assign LUT pins | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_PipelineRegisterOptimization_1(SubPhase):
	"""
	*Floorplanning* subphase.

	Used by phase :class:`Phase_DetailPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Pipeline Register Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Pipeline Register Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_PipelineRegisterOptimization_2(SubPhase):
	"""
	*Pipeline Register Optimization* subphase.

	Used by phase :class:`Phase_DetailPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Pipeline Register Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Pipeline Register Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_FastOptimization_1(SubPhase):
	"""
	*Fast Optimization* subphase.

	Used by phase :class:`Phase_DetailPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Fast Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Fast Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_FastOptimization_2(SubPhase):
	"""
	*Fast Optimization* subphase.

	Used by phase :class:`Phase_DetailPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Fast Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Fast Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_SmallShapeDetailPlacement(SubPhase):
	"""
	*Small Shape Detail Placement* subphase.

	Used by phase :class:`Phase_DetailPlacement`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Small Shape Detail Placement")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Small Shape Detail Placement | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_DetailPlacement(PhaseWithChildren):
	"""
	*Detail Placement* phase.

	.. topic:: Uses

	* :class:`SubPhase_CommitMultiColumnMacros`
	* :class:`SubPhase_CommitMostMacrosLUTRAMs`
	* :class:`SubPhase_SmallShapeDP`
	* :class:`SubPhase_AreaSwapOptimization`
	* :class:`SubPhase_PipelineRegisterOptimization_1`
	* :class:`SubPhase_PipelineRegisterOptimization_2`
	* :class:`SubPhase_FastOptimization_1`
	* :class:`SubPhase_FastOptimization_2`
	* :class:`SubPhase_SmallShapeDetailPlacement`
	* :class:`SubPhase_ReassignLUTPins`

	Used by task :class:`PlacerTask`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Detail Placement")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Detail Placement | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_CommitMultiColumnMacros,
		SubPhase_CommitMostMacrosLUTRAMs,
		SubPhase_SmallShapeDP,
		SubPhase_AreaSwapOptimization,
		SubPhase_PipelineRegisterOptimization_1,
		SubPhase_PipelineRegisterOptimization_2,
		SubPhase_FastOptimization_1,
		SubPhase_FastOptimization_2,
		SubPhase_SmallShapeDetailPlacement,
		SubPhase_ReassignLUTPins
	)


@export
class SubSubSubPhase_BUFGInsertion(SubSubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO_NANO} BUFG Insertion")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex}.{subSubSubPhaseIndex} BUFG Insertion | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubSubSubPhase_PostPlacementTimingOptimization(SubSubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO_NANO} Post Placement Timing Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex}.{subSubSubPhaseIndex} Post Placement Timing Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubSubPhase_PostPlacementOptimization(SubSubPhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Post Placement Optimization")
	_FINISH: ClassVar[str] = None  # Phase 4.1.1 Post Placement Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubSubSubPhase], ...]] = (
		SubSubSubPhase_BUFGInsertion,
		SubSubSubPhase_PostPlacementTimingOptimization
	)


@export
class SubPhase_PostCommitOptimization(SubPhaseWithChildren):
	"""
	*Post Commit Optimization* subphase.

	Used by phase :class:`Phase_PostPlacementOptimizationAndCleanUp`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Post Commit Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Post Commit Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubSubPhase], ...]] = (
		SubSubPhase_PostPlacementOptimization,
	)


@export
class SubPhase_PostPlacementCleanup(SubPhase):
	"""
	*Post Placement Cleanup* subphase.

	Used by phase :class:`Phase_PostPlacementOptimizationAndCleanUp`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Post Placement Cleanup")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Post Placement Cleanup | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubSubPhase_PrintEstimatedCongestion(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Print Estimated Congestion")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex} Print Estimated Congestion | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_PlacerReporting(SubPhaseWithChildren):
	"""
	*Placer Reporting* subphase.

	Used by phase :class:`Phase_PostPlacementOptimizationAndCleanUp`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Placer Reporting")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Placer Reporting | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubSubPhase], ...]] = (
		SubSubPhase_PrintEstimatedCongestion,
	)


@export
class SubPhase_FinalPlacementCleanup(SubPhase):
	"""
	*Final Placement Cleanup* subphase.

	Used by phase :class:`Phase_PostPlacementOptimizationAndCleanUp`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Final Placement Cleanup")
	_FINISH: ClassVar[Pattern] = compile(r"Time \(s\):")
	_TIME:   ClassVar[str] = None


@export
class Phase_PostPlacementOptimizationAndCleanUp(PhaseWithChildren):
	"""
	*Post Placement Optimization and Clean-Up* phase.

	.. topic:: Uses

	* :class:`SubPhase_PostCommitOptimization`
	* :class:`SubPhase_PostPlacementCleanup`
	* :class:`SubPhase_PlacerReporting`
	* :class:`SubPhase_FinalPlacementCleanup`

	Used by task :class:`PlacerTask`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Placement Optimization and Clean-Up")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Placement Optimization and Clean-Up | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_PostCommitOptimization,
		SubPhase_PostPlacementCleanup,
		SubPhase_PlacerReporting,
		SubPhase_FinalPlacementCleanup
	)


@export
class PlacerTask(TaskWithPhases):
	"""
	*Placer* task.

	.. topic:: Uses

	* :class:`Phase_PlacerInitialization`
	* :class:`Phase_GlobalPlacement`
	* :class:`Phase_DetailPlacement`
	* :class:`Phase_PostPlacementOptimizationAndCleanUp`

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.PlaceDesign`.
	"""
	_START:  ClassVar[str] = "Starting Placer Task"
	_FINISH: ClassVar[str] = "Ending Placer Task"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_PlacerInitialization,
		Phase_GlobalPlacement,
		Phase_DetailPlacement,
		Phase_PostPlacementOptimizationAndCleanUp
	)
