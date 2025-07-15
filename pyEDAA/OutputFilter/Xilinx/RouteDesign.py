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

from pyTooling.Decorators  import export

from pyEDAA.OutputFilter.Xilinx           import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Common2   import Task, Phase, SubPhase


@export
class Phase1_BuildRTDesign(Phase):
	_START:  ClassVar[str] = "Phase 1 Build RT Design"
	_FINISH: ClassVar[str] = "Phase 1 Build RT Design | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase21_FixTopologyConstraints(SubPhase):
	_START:  ClassVar[str] = "Phase 2.1 Fix Topology Constraints"
	_FINISH: ClassVar[str] = "Phase 2.1 Fix Topology Constraints | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase22_PreRouteCleanup(SubPhase):
	_START:  ClassVar[str] = "Phase 2.2 Pre Route Cleanup"
	_FINISH: ClassVar[str] = "Phase 2.2 Pre Route Cleanup | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase23_UpdateTiming(SubPhase):
	_START:  ClassVar[str] = "Phase 2.3 Update Timing"
	_FINISH: ClassVar[str] = "Phase 2.3 Update Timing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase24_SoftConstraintPins_FastBudgeting(SubPhase):
	_START:  ClassVar[str] = "Phase 2.4 Soft Constraint Pins - Fast Budgeting"
	_FINISH: ClassVar[str] = "Phase 2.4 Soft Constraint Pins - Fast Budgeting | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase2_RouterInitialization(Phase):
	_START:  ClassVar[str] = "Phase 2 Router Initialization"
	_FINISH: ClassVar[str] = "Phase 2 Router Initialization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase21_FixTopologyConstraints,
		Phase22_PreRouteCleanup,
		Phase23_UpdateTiming,
		Phase24_SoftConstraintPins_FastBudgeting
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
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 2."):
					for parser in activeParsers:  # type: SubPhase
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
class Phase3_GlobalRouting(Phase):
	_START:  ClassVar[str] = "Phase 3 Global Routing"
	_FINISH: ClassVar[str] = "Phase 3 Global Routing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase41_InitialNetRoutingPass(SubPhase):
	_START:  ClassVar[str] = "Phase 4.1 Initial Net Routing Pass"
	_FINISH: ClassVar[str] = "Phase 4.1 Initial Net Routing Pass | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase4_InitialRouting(Phase):
	_START:  ClassVar[str] = "Phase 4 Initial Routing"
	_FINISH: ClassVar[str] = "Phase 4 Initial Routing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase41_InitialNetRoutingPass,
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
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 4."):
					for parser in activeParsers:  # type: SubPhase
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
class Phase51_GlobalIteration0(SubPhase):
	_START:  ClassVar[str] = "Phase 5.1 Global Iteration 0"
	_FINISH: ClassVar[str] = "Phase 5.1 Global Iteration 0 | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase52_GlobalIteration1(SubPhase):
	_START:  ClassVar[str] = "Phase 5.2 Global Iteration 1"
	_FINISH: ClassVar[str] = "Phase 5.2 Global Iteration 1 | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase5_RipUpAndReroute(Phase):
	_START:  ClassVar[str] = "Phase 5 Rip-up And Reroute"
	_FINISH: ClassVar[str] = "Phase 5 Rip-up And Reroute | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase51_GlobalIteration0,
		Phase52_GlobalIteration1
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
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 5."):
					for parser in activeParsers:  # type: SubPhase
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
class Phase61_DelayCleanUp(SubPhase):
	_START:  ClassVar[str] = "Phase 6.1 Delay CleanUp"
	_FINISH: ClassVar[str] = "Phase 6.1 Delay CleanUp | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase62_ClockSkewOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 6.2 Clock Skew Optimization"
	_FINISH: ClassVar[str] = "Phase 6.2 Clock Skew Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase6_DelayAndSkewOptimization(Phase):
	_START:  ClassVar[str] = "Phase 6 Delay and Skew Optimization"
	_FINISH: ClassVar[str] = "Phase 6 Delay and Skew Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase61_DelayCleanUp,
		Phase62_ClockSkewOptimization
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
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 6."):
					for parser in activeParsers:  # type: SubPhase
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
class Phase71_HoldFixIter(SubPhase):
	_START:  ClassVar[str] = "Phase 7.1 Hold Fix Iter"
	_FINISH: ClassVar[str] = "Phase 7.1 Hold Fix Iter | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase7_PostHoldFix(Phase):
	_START:  ClassVar[str] = "Phase 7 Post Hold Fix"
	_FINISH: ClassVar[str] = "Phase 7 Post Hold Fix | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase71_HoldFixIter,
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
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Phase 7."):
					for parser in activeParsers:  # type: SubPhase
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
class Phase8_RouteFinalize(Phase):
	_START:  ClassVar[str] = "Phase 8 Route finalize"
	_FINISH: ClassVar[str] = "Phase 8 Route finalize | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase9_VerifyingRoutedNets(Phase):
	_START:  ClassVar[str] = "Phase 9 Verifying routed nets"
	_FINISH: ClassVar[str] = "Phase 9 Verifying routed nets | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase10_DepositingRoutes(Phase):
	_START:  ClassVar[str] = "Phase 10 Depositing Routes"
	_FINISH: ClassVar[str] = "Phase 10 Depositing Routes | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase11_PostProcessRouting(Phase):
	_START:  ClassVar[str] = "Phase 11 Post Process Routing"
	_FINISH: ClassVar[str] = "Phase 11 Post Process Routing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase12_PostRouterTiming(Phase):
	_START:  ClassVar[str] = "Phase 12 Post Router Timing"
	_FINISH: ClassVar[str] = "Phase 12 Post Router Timing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase13_PostRouteEventProcessing(Phase):
	_START:  ClassVar[str] = "Phase 13 Post-Route Event Processing"
	_FINISH: ClassVar[str] = "Phase 13 Post-Route Event Processing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class RoutingTask(Task):
	_START:  ClassVar[str] = "Starting Routing Task"
	_FINISH: ClassVar[str] = "Ending Routing Task"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase1_BuildRTDesign,
		Phase2_RouterInitialization,
		Phase3_GlobalRouting,
		Phase4_InitialRouting,
		Phase5_RipUpAndReroute,
		Phase6_DelayAndSkewOptimization,
		Phase7_PostHoldFix,
		Phase8_RouteFinalize,
		Phase9_VerifyingRoutedNets,
		Phase10_DepositingRoutes,
		Phase11_PostProcessRouting,
		Phase12_PostRouterTiming,
		Phase13_PostRouteEventProcessing
	)

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
						raise Exception(f"Unknown phase: {line!r}")
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
