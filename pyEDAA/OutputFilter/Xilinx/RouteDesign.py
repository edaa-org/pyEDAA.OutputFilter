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
from pyTooling.Versioning import YearReleaseVersion

from pyEDAA.OutputFilter.Xilinx             import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Common2     import Task, Phase, SubPhase
from pyEDAA.OutputFilter.Xilinx.PlaceDesign import SubSubPhase


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
class Phase23_GlobalClockNetRouting(SubPhase):
	_START:  ClassVar[str] = "Phase 2.3 Global Clock Net Routing"
	_FINISH: ClassVar[str] = "Phase 2.3 Global Clock Net Routing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase23_UpdateTiming(SubPhase):
	_START:  ClassVar[str] = "Phase 2.3 Update Timing"
	_FINISH: ClassVar[str] = "Phase 2.3 Update Timing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase24_UpdateTiming(SubPhase):
	_START:  ClassVar[str] = "Phase 2.4 Update Timing"
	_FINISH: ClassVar[str] = "Phase 2.4 Update Timing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase24_SoftConstraintPins_FastBudgeting(SubPhase):
	_START:  ClassVar[str] = "Phase 2.4 Soft Constraint Pins - Fast Budgeting"
	_FINISH: ClassVar[str] = "Phase 2.4 Soft Constraint Pins - Fast Budgeting | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase251_UpdateTiming(SubPhase):
	_START:  ClassVar[str] = "Phase 2.5.1 Update Timing"
	_FINISH: ClassVar[str] = "Phase 2.5.1 Update Timing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase25_UpdateTimingForBusSkew(SubPhase):
	_START:  ClassVar[str] = "Phase 2.5 Update Timing for Bus Skew"
	_FINISH: ClassVar[str] = "Phase 2.5 Update Timing for Bus Skew | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase251_UpdateTiming,
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
class Phase2_RouterInitialization(Phase):
	_START:  ClassVar[str] = "Phase 2 Router Initialization"
	_FINISH: ClassVar[str] = "Phase 2 Router Initialization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Dict[YearReleaseVersion, Tuple[Type[Phase], ...]]] = {
		YearReleaseVersion(2020, 1): (
			Phase21_FixTopologyConstraints,
			Phase22_PreRouteCleanup,
			Phase23_GlobalClockNetRouting,
			Phase24_UpdateTiming,
			Phase25_UpdateTimingForBusSkew
		),
		YearReleaseVersion(2025, 1): (
			Phase21_FixTopologyConstraints,
			Phase22_PreRouteCleanup,
			Phase23_UpdateTiming,
			Phase24_SoftConstraintPins_FastBudgeting
		)
	}

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, task: Task):
		super().__init__(task)

		processor: "Processor" = task._command._processor
		toolVersion: YearReleaseVersion = processor.Preamble.ToolVersion

		if (toolVersion.Major, toolVersion.Minor) in ((2020, 1), (2020, 2), (2021, 1), (2021, 2), (2022, 1), (2022, 2), (2023, 1), (2023, 2), (2024, 1), (2024, 2)):
			parsers = self._PARSERS[YearReleaseVersion(2020, 1)]
		else:
			parsers = self._PARSERS[YearReleaseVersion(2025, 1)]

		self._subphases = {p: p(self) for p in parsers}

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
class Phase31_GlobalRouting(SubPhase):
	_START:  ClassVar[str] = "Phase 3.1 Global Routing"
	_FINISH: ClassVar[str] = "Phase 3.1 Global Routing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

@export
class Phase32_InitialNetRouting(SubPhase):
	_START:  ClassVar[str] = "Phase 3.2 Initial Net Routing"
	_FINISH: ClassVar[str] = "Phase 3.2 Initial Net Routing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

@export
class Phase3_Initial_Routing(Phase):
	_START:  ClassVar[str] = "Phase 3 Initial Routing"
	_FINISH: ClassVar[str] = "Phase 3 Initial Routing | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase31_GlobalRouting,
		Phase32_InitialNetRouting
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
				elif line.StartsWith("Phase 3."):
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
class Phase41_GlobalIteration0(SubPhase):
	_START:  ClassVar[str] = "Phase 4.1 Global Iteration 0"
	_FINISH: ClassVar[str] = "Phase 4.1 Global Iteration 0 | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase42_GlobalIteration1(SubPhase):
	_START:  ClassVar[str] = "Phase 4.2 Global Iteration 1"
	_FINISH: ClassVar[str] = "Phase 4.2 Global Iteration 1 | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase43_GlobalIteration2(SubPhase):
	_START:  ClassVar[str] = "Phase 4.3 Global Iteration 2"
	_FINISH: ClassVar[str] = "Phase 4.3 Global Iteration 2 | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase4_RipUpAndReroute(Phase):
	_START:  ClassVar[str] = "Phase 4 Rip-up And Reroute"
	_FINISH: ClassVar[str] = "Phase 4 Rip-up And Reroute | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase41_GlobalIteration0,
		Phase42_GlobalIteration1,
		Phase43_GlobalIteration2
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


# 5.1.1 Update Timing
# 5.1.2 Update Timing

@export
class Phase51_DelayCleanUp(SubPhase):
	_START:  ClassVar[str] = "Phase 5.1 Delay CleanUp"
	_FINISH: ClassVar[str] = "Phase 5.1 Delay CleanUp | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase52_ClockSkewOptimization(SubPhase):
	_START:  ClassVar[str] = "Phase 5.2 Clock Skew Optimization"
	_FINISH: ClassVar[str] = "Phase 5.2 Clock Skew Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase5_DelayAndSkewOptimization(Phase):
	_START:  ClassVar[str] = "Phase 5 Delay and Skew Optimization"
	_FINISH: ClassVar[str] = "Phase 5 Delay and Skew Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase51_DelayCleanUp,
		Phase52_ClockSkewOptimization
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

# 6.1.1 Update Timing

@export
class Phase61_HoldFixIter(SubPhase):
	_START:  ClassVar[str] = "Phase 6.1 Hold Fix Iter"
	_FINISH: ClassVar[str] = "Phase 6.1 Hold Fix Iter | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase6_PostHoldFix(Phase):
	_START:  ClassVar[str] = "Phase 6 Post Hold Fix"
	_FINISH: ClassVar[str] = "Phase 6 Post Hold Fix | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase61_HoldFixIter,
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
class Phase7_RouteFinalize(Phase):
	_START:  ClassVar[str] = "Phase 7 Route finalize"
	_FINISH: ClassVar[str] = "Phase 7 Route finalize | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


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
class Phase8_VerifyingRoutedNets(Phase):
	_START:  ClassVar[str] = "Phase 8 Verifying routed nets"
	_FINISH: ClassVar[str] = "Phase 8 Verifying routed nets | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase8_RouteFinalize(Phase):
	_START:  ClassVar[str] = "Phase 8 Route finalize"
	_FINISH: ClassVar[str] = "Phase 8 Route finalize | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase9_DepositingRoutes(Phase):
	_START:  ClassVar[str] = "Phase 9 Depositing Routes"
	_FINISH: ClassVar[str] = "Phase 9 Depositing Routes | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase9_VerifyingRoutedNets(Phase):
	_START:  ClassVar[str] = "Phase 9 Verifying routed nets"
	_FINISH: ClassVar[str] = "Phase 9 Verifying routed nets | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase10_ResolveXTalk(Phase):
	_START:  ClassVar[str] = "Phase 10 Resolve XTalk"
	_FINISH: ClassVar[str] = "Phase 10 Resolve XTalk | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase10_DepositingRoutes(Phase):
	_START:  ClassVar[str] = "Phase 10 Depositing Routes"
	_FINISH: ClassVar[str] = "Phase 10 Depositing Routes | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase11_RouteFinalize(Phase):
	_START:  ClassVar[str] = "Phase 11 Route finalize"
	_FINISH: ClassVar[str] = "Phase 11 Route finalize | Checksum:"
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

	_PARSERS: ClassVar[Dict[YearReleaseVersion, Tuple[Type[Phase], ...]]] = {
		YearReleaseVersion(2020, 1): (
			Phase1_BuildRTDesign,
			Phase2_RouterInitialization,
			Phase3_Initial_Routing,
			Phase4_RipUpAndReroute,
			Phase5_DelayAndSkewOptimization,
			Phase6_PostHoldFix,
			Phase7_RouteFinalize,
			Phase8_VerifyingRoutedNets,
			Phase9_DepositingRoutes,
			Phase10_ResolveXTalk,
			Phase11_RouteFinalize,
			Phase12_PostRouterTiming,
			Phase13_PostRouteEventProcessing
		),
		YearReleaseVersion(2025, 1): (
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
	}

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
