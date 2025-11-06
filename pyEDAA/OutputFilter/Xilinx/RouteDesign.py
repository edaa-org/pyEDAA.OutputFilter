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

from pyEDAA.OutputFilter                    import OutputFilterException
from pyEDAA.OutputFilter.Xilinx             import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Common2     import TaskWithPhases, Phase, SubPhase
from pyEDAA.OutputFilter.Xilinx.Common2     import MAJOR, MAJOR_MINOR, MAJOR_MINOR_MICRO
from pyEDAA.OutputFilter.Xilinx.PlaceDesign import SubSubPhase


@export
class Phase_BuildRTDesign(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Build RT Design")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Build RT Design \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_FixTopologyConstraints(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Fix Topology Constraints")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Fix Topology Constraints \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PreRouteCleanup(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Pre Route Cleanup")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Pre Route Cleanup \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_GlobalClockNetRouting(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Clock Net Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Clock Net Routing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_UpdateTiming(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Update Timing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Update Timing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_SoftConstraintPins_FastBudgeting(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Soft Constraint Pins - Fast Budgeting")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Soft Constraint Pins - Fast Budgeting \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class SubSubPhase_UpdateTiming(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR_MICRO} Update Timing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex}.{subSubPhaseIndex} Update Timing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_UpdateTimingForBusSkew(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Update Timing for Bus Skew")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Update Timing for Bus Skew \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		SubSubPhase_UpdateTiming,
	)

	_subsubphases: Dict[Type[SubSubPhase], SubSubPhase]

	def __init__(self, subphase: SubPhase):
		super().__init__(subphase)

		self._subsubphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SubPhaseStart(line)

		activeParsers: List[Phase] = list(self._subsubphases.values())

		START_PREFIX = f"Phase {self._phaseIndex}.{self._subPhaseIndex}."

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith(START_PREFIX):
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
class Phase_RouterInitialization(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Router Initialization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Router Initialization \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[SubPhase], ...]]] = {
		VersionRange(YearReleaseVersion(2019, 1), YearReleaseVersion(2023, 2), RangeBoundHandling.UpperBoundExclusive): (
			Phase_FixTopologyConstraints,
			Phase_PreRouteCleanup,
			Phase_GlobalClockNetRouting,
			Phase_UpdateTiming,
			Phase_UpdateTimingForBusSkew
		),
		VersionRange(YearReleaseVersion(2023, 2), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase_FixTopologyConstraints,
			Phase_PreRouteCleanup,
			Phase_GlobalClockNetRouting,
			Phase_UpdateTiming,
			Phase_UpdateTimingForBusSkew,
			Phase_SoftConstraintPins_FastBudgeting
		)
	}

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, task: TaskWithPhases):
		super().__init__(task)

		processor: "Processor" = task._command._processor
		toolVersion: YearReleaseVersion = processor.Preamble.ToolVersion

		for versionRange in self._PARSERS:
			if toolVersion in versionRange:
				parsers = self._PARSERS[versionRange]
				break
		else:
			ex = OutputFilterException(f"Tool version {toolVersion} is not supported for '{self.__class__.__name__}'.")
			ex.add_note(f"Supported tool versions: {', '.join(str(vr) for vr in self._PARSERS)}")
			raise ex

		self._subphases = {p: p(self) for p in parsers}

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
					for parser in activeParsers:  # type: SubPhase
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
class SubPhase_GlobalRouting(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Routing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

@export
class Phase_InitialNetRouting(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Initial Net Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Initial Net Routing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

@export
class Phase_Initial_Routing(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Initial Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Initial Routing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		SubPhase_GlobalRouting,
		Phase_InitialNetRouting
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

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
					for parser in activeParsers:  # type: SubPhase
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
class Phase_GlobalRouting(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Global Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Global Routing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_GlobalIteration0(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Iteration 0")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Iteration 0 \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_GlobalIteration1(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Iteration 1")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Iteration 1 \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_GlobalIteration2(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Iteration 2")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Iteration 2 \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_RipUpAndReroute(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Rip-up And Reroute")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Rip-up And Reroute \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_GlobalIteration0,
		Phase_GlobalIteration1,
		Phase_GlobalIteration2
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

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
					for parser in activeParsers:  # type: SubPhase
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
class Phase_InitialNetRoutingPass(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Initial Net Routing Pass")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Initial Net Routing Pass \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_InitialRouting(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Initial Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Initial Routing | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_InitialNetRoutingPass,
		SubPhase_GlobalRouting,
		Phase_InitialNetRouting
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		START_PREFIX = f"Phase {self._phaseIndex}."
		FINISH_START = self._FINISH.format(phaseIndex=self._phaseIndex)

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith(START_PREFIX):
					for parser in activeParsers:  # type: SubPhase
						print(parser._START.pattern)
						if (match := parser._START.match(line._message)) is not None:
							line = yield next(phase := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown subphase: {line!r}")
					break
				elif line.StartsWith(FINISH_START):
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
class Phase_DelayCleanUp(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Delay CleanUp")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Delay CleanUp \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_ClockSkewOptimization(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Clock Skew Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Clock Skew Optimization \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_DelayAndSkewOptimization(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Delay and Skew Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Delay and Skew Optimization \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_DelayCleanUp,
		Phase_ClockSkewOptimization
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

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
					for parser in activeParsers:  # type: SubPhase
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
class Phase_GlobalIteration0(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Iteration 0")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Iteration 0 \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_GlobalIteration1(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Global Iteration 1")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Global Iteration 1 \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_RipUpAndReroute(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Rip-up And Reroute")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Rip-up And Reroute \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_GlobalIteration0,
		Phase_GlobalIteration1
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

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
					for parser in activeParsers:  # type: SubPhase
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

# 6.1.1 Update Timing

@export
class Phase_HoldFixIter(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Hold Fix Iter")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Hold Fix Iter \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PostHoldFix(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Hold Fix")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Hold Fix \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_HoldFixIter,
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

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
					for parser in activeParsers:  # type: SubPhase
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
class Phase_DelayCleanUp(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Delay CleanUp")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Delay CleanUp \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_ClockSkewOptimization(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Clock Skew Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Clock Skew Optimization \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_DelayAndSkewOptimization(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Delay and Skew Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Delay and Skew Optimization \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_DelayCleanUp,
		Phase_ClockSkewOptimization
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

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
					for parser in activeParsers:  # type: SubPhase
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
class Phase_RouteFinalize_1(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Route finalize")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Route finalize \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_RouteFinalize_2(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Route finalize")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Route finalize \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_HoldFixIter(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Hold Fix Iter")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Hold Fix Iter \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PostHoldFix(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Hold Fix")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Hold Fix \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_HoldFixIter,
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

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
					for parser in activeParsers:  # type: SubPhase
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
class Phase_VerifyingRoutedNets(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Verifying routed nets")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Verifying routed nets \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_DepositingRoutes(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Depositing Routes")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Depositing Routes \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_VerifyingRoutedNets(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Verifying routed nets")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Verifying routed nets \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_ResolveXTalk(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Resolve XTalk")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Resolve XTalk \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_DepositingRoutes(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Depositing Routes")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Depositing Routes \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PostProcessRouting(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Process Routing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Process Routing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PostRouterTiming(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Router Timing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Router Timing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"

@export
class Phase_PostRouterTiming(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post Router Timing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post Router Timing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_PostRouteEventProcessing(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Post-Route Event Processing")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Post-Route Event Processing \| Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class RoutingTask(TaskWithPhases):
	_START:  ClassVar[str] = "Starting Routing Task"
	_FINISH: ClassVar[str] = "Ending Routing Task"

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[Phase], ...]]] = {
		VersionRange(YearReleaseVersion(2019, 1), YearReleaseVersion(2023, 2), RangeBoundHandling.UpperBoundExclusive): (
			Phase_BuildRTDesign,
			Phase_RouterInitialization,
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
			Phase_PostRouteEventProcessing
		),
		VersionRange(YearReleaseVersion(2023, 2), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
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
			Phase_PostRouterTiming,
			Phase_PostRouteEventProcessing
		)
	}
