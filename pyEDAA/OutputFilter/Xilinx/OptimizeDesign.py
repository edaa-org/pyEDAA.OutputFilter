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
from typing import ClassVar, Type, Tuple

from pyTooling.Decorators  import export

from pyEDAA.OutputFilter.Xilinx.Common2 import Task, Phase, SubPhase, TaskWithPhases, TaskWithSubTasks, SubTask, \
	PhaseWithChildren
from pyEDAA.OutputFilter.Xilinx.Common2 import MAJOR, MAJOR_MINOR


@export
class Phase_Retarget(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Retarget")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Retarget | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Retarget | Checksum:"


@export
class SubPhase_CoreGenerationAndDesignSetup(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Core Generation And Design Setup")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Core Generation And Design Setup | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_SetupConstraintsAndSortNetlist(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Setup Constraints And Sort Netlist")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Setup Constraints And Sort Netlist | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_Initialization(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Initialization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Initialization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_CoreGenerationAndDesignSetup,
		SubPhase_SetupConstraintsAndSortNetlist
	)


@export
class Phase_ConstantPropagation(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Constant propagation")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Constant propagation | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Constant propagation | Checksum:"


@export
class SubPhase_TimerUpdate(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Timer Update")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Timer Update | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_TimingDataCollection(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Timing Data Collection")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Timing Data Collection | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_TimerUpdateAndTimingDataCollection(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Timer Update And Timing Data Collection")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Timer Update And Timing Data Collection | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_TimerUpdate,
		SubPhase_TimingDataCollection
	)


@export
class Phase_Sweep(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Sweep")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Sweep | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Sweep | Checksum:"


@export
class Phase_BUFGOptimization(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} BUFG optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} BUFG optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "BUFG optimization | Checksum:"


@export
class Phase_ConstantPropagation(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Constant propagation")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Constant propagation | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Constant propagation | Checksum:"


@export
class Phase_ShiftRegisterOptimization(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Shift Register Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Shift Register Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Shift Register Optimization | Checksum:"


@export
class Phase_Sweep(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Sweep")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Sweep | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Sweep | Checksum:"


@export
class Phase_PostProcessingNetlist(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Processing Netlist")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Processing Netlist | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Post Processing Netlist | Checksum:"


@export
class Phase_BUFGOptimization(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} BUFG optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} BUFG optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "BUFG optimization | Checksum:"


@export
class Phase_ShiftRegisterOptimization(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Shift Register Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Shift Register Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Shift Register Optimization | Checksum:"


@export
class Phase_PostProcessingNetlist(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Processing Netlist")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Processing Netlist | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Post Processing Netlist | Checksum:"


@export
class SubPhase_FinalizingDesignCoresAndUpdatingShapes(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Finalizing Design Cores and Updating Shapes")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Finalizing Design Cores and Updating Shapes | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_VerifyingNetlistConnectivity(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Verifying Netlist Connectivity")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Verifying Netlist Connectivity | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_Finalization(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Finalization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Finalization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_FinalizingDesignCoresAndUpdatingShapes,
		SubPhase_VerifyingNetlistConnectivity
	)


@export
class DRCTask(Task):
	_START:  ClassVar[str] = "Starting DRC Task"
	_FINISH: ClassVar[str] = "Time (s):"


@export
class CacheTimingInformationTask(Task):
	_START:  ClassVar[str] = "Starting Cache Timing Information Task"
	_FINISH: ClassVar[str] = "Ending Cache Timing Information Task"


@export
class LogicOptimizationTask(TaskWithPhases):
	_START:  ClassVar[str] = "Starting Logic Optimization Task"
	_FINISH: ClassVar[str] = "Ending Logic Optimization Task"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_Initialization,
		Phase_TimerUpdateAndTimingDataCollection,
		Phase_Retarget,
		Phase_ConstantPropagation,
		Phase_Sweep,
		Phase_BUFGOptimization,
		Phase_ShiftRegisterOptimization,
		Phase_PostProcessingNetlist,
		Phase_Finalization
	)


@export
class PowerOptPatchEnablesTask(SubTask):
	_START:  ClassVar[str] = "Starting PowerOpt Patch Enables Task"
	_FINISH: ClassVar[str] = "Ending PowerOpt Patch Enables Task"


@export
class PowerOptimizationTask(TaskWithSubTasks):
	_START:  ClassVar[str] = "Starting Power Optimization Task"
	_FINISH: ClassVar[str] = "Ending Power Optimization Task"

	_PARSERS: ClassVar[Tuple[Type[SubTask], ...]] = (
		PowerOptPatchEnablesTask,
	)


@export
class LogicOptimizationTask(SubTask):
	_START:  ClassVar[str] = "Starting Logic Optimization Task"
	_FINISH: ClassVar[str] = "Ending Logic Optimization Task"


@export
class FinalCleanupTask(TaskWithSubTasks):
	_START:  ClassVar[str] = "Starting Final Cleanup Task"
	_FINISH: ClassVar[str] = "Ending Final Cleanup Task"

	_PARSERS: ClassVar[Tuple[Type[SubTask], ...]] = (
		LogicOptimizationTask,
	)


@export
class NetlistObfuscationTask(Task):
	_START:  ClassVar[str] = "Starting Netlist Obfuscation Task"
	_FINISH: ClassVar[str] = "Ending Netlist Obfuscation Task"
