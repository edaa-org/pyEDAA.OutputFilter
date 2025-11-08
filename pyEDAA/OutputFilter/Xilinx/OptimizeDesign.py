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

from pyTooling.Decorators  import export
from pyTooling.Versioning  import VersionRange, YearReleaseVersion, RangeBoundHandling

from pyEDAA.OutputFilter.Xilinx         import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Common2 import Task, Phase, SubPhase, TaskWithPhases, TaskWithSubTasks, SubTask
from pyEDAA.OutputFilter.Xilinx.Common2 import MAJOR, MAJOR_MINOR


@export
class Phase_Retarget(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Retarget")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Retarget | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Retarget | Checksum:"


@export
class Phase_CoreGenerationAndDesignSetup(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Core Generation And Design Setup")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Core Generation And Design Setup | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_SetupConstraintsAndSortNetlist(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Setup Constraints And Sort Netlist")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Setup Constraints And Sort Netlist | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_Initialization(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Initialization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Initialization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_CoreGenerationAndDesignSetup,
		Phase_SetupConstraintsAndSortNetlist
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		START_PREFIX = f"Phase {self._phaseIndex}."
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex)

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
						raise Exception(f"Unknown subphase: {line!r}")
					break
				elif line.StartsWith(FINISH):
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
class Phase_ConstantPropagation(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Constant propagation")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Constant propagation | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = "Constant propagation | Checksum:"


@export
class Phase_TimerUpdate(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Timer Update")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Timer Update | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_TimingDataCollection(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Timing Data Collection")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Timing Data Collection | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_TimerUpdateAndTimingDataCollection(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Timer Update And Timing Data Collection")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Timer Update And Timing Data Collection | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_TimerUpdate,
		Phase_TimingDataCollection
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		START_PREFIX = f"Phase {self._phaseIndex}."
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex)

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
						raise Exception(f"Unknown subphase: {line!r}")
					break
				elif line.StartsWith(FINISH):
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
class Phase_FinalizingDesignCoresAndUpdatingShapes(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Finalizing Design Cores and Updating Shapes")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Finalizing Design Cores and Updating Shapes | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_VerifyingNetlistConnectivity(SubPhase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR_MINOR} Verifying Netlist Connectivity")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex}.{subPhaseIndex} Verifying Netlist Connectivity | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"


@export
class Phase_Finalization(Phase):
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Finalization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Finalization | Checksum:"
	_TIME:   ClassVar[str]     = "Time (s):"
	_FINAL:  ClassVar[str] = None

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_FinalizingDesignCoresAndUpdatingShapes,
		Phase_VerifyingNetlistConnectivity
	)

	_subphases: Dict[Type[SubPhase], SubPhase]

	def __init__(self, phase: Phase):
		super().__init__(phase)

		self._subphases = {p: p(self) for p in self._PARSERS}

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		activeParsers: List[Phase] = list(self._subphases.values())

		START_PREFIX = f"Phase {self._phaseIndex}."
		FINISH = self._FINISH.format(phaseIndex=self._phaseIndex)

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
						raise Exception(f"Unknown subphase: {line!r}")
					break
				elif line.StartsWith(FINISH):
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
			Phase_Retarget,
			Phase_ConstantPropagation,
			Phase_Sweep,
			Phase_BUFGOptimization,
			Phase_ShiftRegisterOptimization,
			Phase_PostProcessingNetlist
		),
		VersionRange(YearReleaseVersion(2023, 2), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
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
						if (match := parser._START.match(line._message)) is not None:
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
class PowerOptPatchEnablesTask(SubTask):
	_START:  ClassVar[str] = "Starting PowerOpt Patch Enables Task"
	_FINISH: ClassVar[str] = "Ending PowerOpt Patch Enables Task"


@export
class PowerOptimizationTask(TaskWithSubTasks):
	_START:  ClassVar[str] = "Starting Power Optimization Task"
	_FINISH: ClassVar[str] = "Ending Power Optimization Task"

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[SubTask], ...]]] = {
		VersionRange(YearReleaseVersion(2019, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			PowerOptPatchEnablesTask,
		)
	}


@export
class LogicOptimizationTask(SubTask):
	_START:  ClassVar[str] = "Starting Logic Optimization Task"
	_FINISH: ClassVar[str] = "Ending Logic Optimization Task"


@export
class FinalCleanupTask(TaskWithSubTasks):
	_START:  ClassVar[str] = "Starting Final Cleanup Task"
	_FINISH: ClassVar[str] = "Ending Final Cleanup Task"

	_PARSERS: ClassVar[Dict[VersionRange[YearReleaseVersion], Tuple[Type[SubTask], ...]]] = {
		VersionRange(YearReleaseVersion(2019, 1), YearReleaseVersion(2030, 1), RangeBoundHandling.UpperBoundExclusive): (
			LogicOptimizationTask,
		)
	}


@export
class NetlistObfuscationTask(Task):
	_START:  ClassVar[str] = "Starting Netlist Obfuscation Task"
	_FINISH: ClassVar[str] = "Ending Netlist Obfuscation Task"
