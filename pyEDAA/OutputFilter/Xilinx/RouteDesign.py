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
from typing import Generator, ClassVar, List, Type, Dict, Tuple

from pyTooling.Decorators import export
from pyTooling.Warning    import WarningCollector

from pyEDAA.OutputFilter.Xilinx             import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Common2 import TaskWithPhases, Phase, SubPhase, UnknownSubPhase, PhaseWithChildren, \
	SubPhaseWithChildren
from pyEDAA.OutputFilter.Xilinx.Common2     import MAJOR, MAJOR_MINOR, MAJOR_MINOR_MICRO
from pyEDAA.OutputFilter.Xilinx.PlaceDesign import SubSubPhase


@export
class Phase_BuildRTDesign(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Build RT Design")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Build RT Design | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_CreateTimer(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Create Timer")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Create Timer | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_FixTopologyConstraints(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Fix Topology Constraints")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Fix Topology Constraints | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_PreRouteCleanup(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Pre Route Cleanup")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Pre Route Cleanup | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_GlobalClockNetRouting(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Clock Net Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Clock Net Routing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_UpdateTiming(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Update Timing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Update Timing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_SoftConstraintPins_FastBudgeting(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Soft Constraint Pins - Fast Budgeting")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Soft Constraint Pins - Fast Budgeting | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubSubPhase_UpdateTiming(SubSubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Update Timing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex} Update Timing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_UpdateTimingForBusSkew(SubPhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Update Timing for Bus Skew")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Update Timing for Bus Skew | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubSubPhase], ...]] = (
		SubSubPhase_UpdateTiming,
	)


@export
class Phase_RouterInitialization(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Router Initialization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Router Initialization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_CreateTimer,
		SubPhase_FixTopologyConstraints,
		SubPhase_PreRouteCleanup,
		SubPhase_GlobalClockNetRouting,
		SubPhase_UpdateTiming,
		SubPhase_UpdateTimingForBusSkew,
		SubPhase_SoftConstraintPins_FastBudgeting
	)


@export
class SubPhase_GlobalRouting(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Routing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_InitialNetRouting(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Initial Net Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Initial Net Routing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_Initial_Routing(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Initial Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Initial Routing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_GlobalRouting,
		SubPhase_InitialNetRouting
	)


@export
class Phase_GlobalRouting(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Global Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Global Routing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_GlobalIteration0(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Iteration 0")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Iteration 0 | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_AdditionalIterationForHold(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Additional Iteration for Hold")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Additional Iteration for Hold | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_GlobalIteration1(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Iteration 1")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Iteration 1 | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_GlobalIteration2(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Iteration 2")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Iteration 2 | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_RipUpAndReroute(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Rip-up And Reroute")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Rip-up And Reroute | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_GlobalIteration0,
		SubPhase_AdditionalIterationForHold,
		SubPhase_GlobalIteration1,
		SubPhase_GlobalIteration2
	)


@export
class SubPhase_InitialNetRoutingPass(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Initial Net Routing Pass")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Initial Net Routing Pass | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_InitialRouting(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Initial Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Initial Routing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_InitialNetRoutingPass,
		SubPhase_GlobalRouting,
		SubPhase_InitialNetRouting
	)


@export
class SubPhase_DelayCleanUp(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Delay CleanUp")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Delay CleanUp | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_ClockSkewOptimization(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Clock Skew Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Clock Skew Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_DelayAndSkewOptimization(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Delay and Skew Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Delay and Skew Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_DelayCleanUp,
		SubPhase_ClockSkewOptimization
	)


@export
class SubPhase_HoldFixIter(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Hold Fix Iter")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Hold Fix Iter | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PostHoldFix(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Hold Fix")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Hold Fix | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_HoldFixIter,
	)


@export
class SubPhase_DelayCleanUp(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Delay CleanUp")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Delay CleanUp | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_ClockSkewOptimization(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Clock Skew Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Clock Skew Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_DelayAndSkewOptimization(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Delay and Skew Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Delay and Skew Optimization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_DelayCleanUp,
		SubPhase_ClockSkewOptimization
	)


@export
class Phase_RouteFinalize_1(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Route finalize")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Route finalize | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_RouteFinalize_2(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Route finalize")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Route finalize | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubPhase_HoldFixIter(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Hold Fix Iter")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Hold Fix Iter | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PostHoldFix(PhaseWithChildren):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Hold Fix")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Hold Fix | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[SubPhase], ...]] = (
		SubPhase_HoldFixIter,
	)


@export
class Phase_VerifyingRoutedNets(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Verifying routed nets")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Verifying routed nets | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_DepositingRoutes(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Depositing Routes")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Depositing Routes | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_VerifyingRoutedNets(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Verifying routed nets")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Verifying routed nets | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_ResolveXTalk(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Resolve XTalk")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Resolve XTalk | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_DepositingRoutes(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Depositing Routes")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Depositing Routes | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PostProcessRouting(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Process Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Process Routing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PostRouterTiming(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Router Timing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Router Timing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PostRouteEventProcessing(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post-Route Event Processing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post-Route Event Processing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class RoutingTask(TaskWithPhases):
	_START:  ClassVar[str] = "Starting Routing Task"
	_FINISH: ClassVar[str] = "Ending Routing Task"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_BuildRTDesign,
		Phase_RouterInitialization,
		Phase_GlobalRouting,
		Phase_InitialRouting,
		Phase_RipUpAndReroute,
		Phase_DelayAndSkewOptimization,
		Phase_PostHoldFix,
		Phase_RouteFinalize_1,
		Phase_VerifyingRoutedNets,
		Phase_DepositingRoutes,
		Phase_ResolveXTalk,
		Phase_RouteFinalize_2,
		Phase_PostRouterTiming,
		Phase_PostProcessRouting,
		Phase_PostRouterTiming,    # FIXME: duplicate
		Phase_PostRouteEventProcessing
	)
