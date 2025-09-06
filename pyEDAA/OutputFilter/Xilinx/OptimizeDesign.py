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
from pyTooling.Versioning  import VersionRange, YearReleaseVersion, RangeBoundHandling

from pyEDAA.OutputFilter.Xilinx         import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Common2 import Task, Phase, SubPhase, TaskWithPhases


@export
class Phase1_Retarget(Phase):
	_START:  ClassVar[str] = "Phase 1 Retarget"
	_FINISH: ClassVar[str] = "Phase 1 Retarget | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Retarget | Checksum:"


@export
class Phase11_CoreGenerationAndDesignSetup(SubPhase):
	_START:  ClassVar[str] = "Phase 1.1 Core Generation And Design Setup"
	_FINISH: ClassVar[str] = "Phase 1.1 Core Generation And Design Setup | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase12_SetupConstraintsAndSortNetlist(SubPhase):
	_START:  ClassVar[str] = "Phase 1.2 Setup Constraints And Sort Netlist"
	_FINISH: ClassVar[str] = "Phase 1.2 Setup Constraints And Sort Netlist | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase1_Initialization(Phase):
	_START:  ClassVar[str] = "Phase 1 Initialization"
	_FINISH: ClassVar[str] = "Phase 1 Initialization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase11_CoreGenerationAndDesignSetup,
		Phase12_SetupConstraintsAndSortNetlist
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
				elif line.StartsWith("Phase 1."):
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
class Phase2_ConstantPropagation(Phase):
	_START:  ClassVar[str] = "Phase 2 Constant propagation"
	_FINISH: ClassVar[str] = "Phase 2 Constant propagation | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Constant propagation | Checksum:"


@export
class Phase21_TimerUpdate(SubPhase):
	_START:  ClassVar[str] = "Phase 2.1 Timer Update"
	_FINISH: ClassVar[str] = "Phase 2.1 Timer Update | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase22_TimingDataCollection(SubPhase):
	_START:  ClassVar[str] = "Phase 2.2 Timing Data Collection"
	_FINISH: ClassVar[str] = "Phase 2.2 Timing Data Collection | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase2_TimerUpdateAndTimingDataCollection(Phase):
	_START:  ClassVar[str] = "Phase 2 Timer Update And Timing Data Collection"
	_FINISH: ClassVar[str] = "Phase 2 Timer Update And Timing Data Collection | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase21_TimerUpdate,
		Phase22_TimingDataCollection
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
class Phase3_Sweep(Phase):
	_START:  ClassVar[str] = "Phase 3 Sweep"
	_FINISH: ClassVar[str] = "Phase 3 Sweep | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Sweep | Checksum:"


@export
class Phase3_Retarget(Phase):
	_START:  ClassVar[str] = "Phase 3 Retarget"
	_FINISH: ClassVar[str] = "Phase 3 Retarget | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Retarget | Checksum:"


@export
class Phase4_BUFGOptimization(Phase):
	_START:  ClassVar[str] = "Phase 4 BUFG optimization"
	_FINISH: ClassVar[str] = "Phase 4 BUFG optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "BUFG optimization | Checksum:"


@export
class Phase4_ConstantPropagation(Phase):
	_START:  ClassVar[str] = "Phase 4 Constant propagation"
	_FINISH: ClassVar[str] = "Phase 4 Constant propagation | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Constant propagation | Checksum:"


@export
class Phase5_ShiftRegisterOptimization(Phase):
	_START:  ClassVar[str] = "Phase 5 Shift Register Optimization"
	_FINISH: ClassVar[str] = "Phase 5 Shift Register Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Shift Register Optimization | Checksum:"


@export
class Phase5_Sweep(Phase):
	_START:  ClassVar[str] = "Phase 5 Sweep"
	_FINISH: ClassVar[str] = "Phase 5 Sweep | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Sweep | Checksum:"


@export
class Phase6_PostProcessingNetlist(Phase):
	_START:  ClassVar[str] = "Phase 6 Post Processing Netlist"
	_FINISH: ClassVar[str] = "Phase 6 Post Processing Netlist | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Post Processing Netlist | Checksum:"


@export
class Phase6_BUFGOptimization(Phase):
	_START:  ClassVar[str] = "Phase 6 BUFG optimization"
	_FINISH: ClassVar[str] = "Phase 6 BUFG optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "BUFG optimization | Checksum:"


@export
class Phase7_ShiftRegisterOptimization(Phase):
	_START:  ClassVar[str] = "Phase 7 Shift Register Optimization"
	_FINISH: ClassVar[str] = "Phase 7 Shift Register Optimization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Shift Register Optimization | Checksum:"


@export
class Phase8_PostProcessingNetlist(Phase):
	_START:  ClassVar[str] = "Phase 8 Post Processing Netlist"
	_FINISH: ClassVar[str] = "Phase 8 Post Processing Netlist | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Post Processing Netlist | Checksum:"


@export
class Phase91_FinalizingDesignCoresAndUpdatingShapes(SubPhase):
	_START:  ClassVar[str] = "Phase 9.1 Finalizing Design Cores and Updating Shapes"
	_FINISH: ClassVar[str] = "Phase 9.1 Finalizing Design Cores and Updating Shapes | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase92_VerifyingNetlistConnectivity(SubPhase):
	_START:  ClassVar[str] = "Phase 9.2 Verifying Netlist Connectivity"
	_FINISH: ClassVar[str] = "Phase 9.2 Verifying Netlist Connectivity | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"


@export
class Phase9_Finalization(Phase):
	_START:  ClassVar[str] = "Phase 9 Finalization"
	_FINISH: ClassVar[str] = "Phase 9 Finalization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase91_FinalizingDesignCoresAndUpdatingShapes,
		Phase92_VerifyingNetlistConnectivity
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
				elif line.StartsWith("Phase 9."):
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

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[Phase], ...]]] = {
		VersionRange(YearReleaseVersion(2019, 1), YearReleaseVersion(2023, 2), RangeBoundHandling.UpperBoundExclusive): (
			Phase1_Retarget,
			Phase2_ConstantPropagation,
			Phase3_Sweep,
			Phase4_BUFGOptimization,
			Phase5_ShiftRegisterOptimization,
			Phase6_PostProcessingNetlist
		),
		VersionRange(YearReleaseVersion(2023, 2), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			Phase1_Initialization,
			Phase2_TimerUpdateAndTimingDataCollection,
			Phase3_Retarget,
			Phase4_ConstantPropagation,
			Phase5_Sweep,
			Phase6_BUFGOptimization,
			Phase7_ShiftRegisterOptimization,
			Phase8_PostProcessingNetlist,
			Phase9_Finalization
		)
	}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._TaskStart(line)

		activeParsers: List[Phase] = list(self._phases.values())

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif isinstance(line, VivadoMessage):
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

# @export
# class ConnectivityCheckTask(Task):
# 	pass


@export
class PowerOptimizationTask(Task):
	_START:  ClassVar[str] = "Starting Power Optimization Task"
	_FINISH: ClassVar[str] = "Ending Power Optimization Task"


@export
class FinalCleanupTask(Task):
	_START:  ClassVar[str] = "Starting Final Cleanup Task"
	_FINISH: ClassVar[str] = "Ending Final Cleanup Task"


@export
class NetlistObfuscationTask(Task):
	_START:  ClassVar[str] = "Starting Netlist Obfuscation Task"
	_FINISH: ClassVar[str] = "Ending Netlist Obfuscation Task"
