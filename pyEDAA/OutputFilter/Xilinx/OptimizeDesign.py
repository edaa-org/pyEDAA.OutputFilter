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
from typing import Generator, ClassVar, List, Type, Dict

from pyTooling.Decorators  import export
from pyTooling.MetaClasses import ExtendedType, abstractmethod

from pyEDAA.OutputFilter.Xilinx           import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Exception import ProcessorException
from pyEDAA.OutputFilter.Xilinx.Common2   import BaseParser, VivadoMessagesMixin


@export
class Task(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]
	_FINAL:  ClassVar[str] = "Time (s):"

	_command:  "Command"
	_duration: float

	def __init__(self, command: "Command"):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._command = command

	def _TaskStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException()

		line._kind = LineKind.TaskStart
		nextLine = yield line
		return nextLine

	def _TaskFinish(self, line: Line) -> Generator[Line, Line, None]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException()

		line._kind = LineKind.TaskEnd
		line = yield line
		while self._FINAL is not None:
			if line.StartsWith(self._FINAL):
				break

			line = yield line

		line._kind = LineKind.TaskTime
		line = yield line
		return line

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._TaskStart(line)

		while True:
			if line.StartsWith("Ending"):
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			elif line.StartsWith(self._FINAL):
				line._kind = LineKind.TaskTime
				nextLine = yield line
				return nextLine

			line = yield line

		nextLine = yield from self._TaskFinish(line)
		return nextLine


@export
class Phase(BaseParser, VivadoMessagesMixin, metaclass=ExtendedType, slots=True):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]

	_task:     Task
	_duration: float

	def __init__(self, task: Task):
		super().__init__()
		VivadoMessagesMixin.__init__(self)

		self._task = task

	def _PhaseStart(self, line: Line) -> Generator[Line, Line, Line]:
		if not line.StartsWith(self._START):
			raise ProcessorException()

		line._kind = LineKind.PhaseStart
		nextLine = yield line
		return nextLine

	def _PhaseFinish(self, line: Line) -> Generator[Line, Line, None]:
		if not line.StartsWith(self._FINISH):
			raise ProcessorException()

		line._kind = LineKind.PhaseEnd
		line = yield line

		while self._TIME is not None:
			if line.StartsWith(self._TIME):
				line._kind = LineKind.PhaseTime
				break

			line = yield line

		line = yield line
		while self._FINAL is not None:
			if line.StartsWith(self._FINAL):
				line._kind = LineKind.PhaseFinal
				break

			line = yield line

		nextLine = yield line
		return nextLine

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._PhaseStart(line)

		while True:
			if line.StartsWith(self._FINISH):
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)

			line = yield line

		nextLine = yield from self._PhaseFinish(line)
		return nextLine


@export
class Phase1_Initialization(Phase):
	_START:  ClassVar[str] = "Phase 1 Initialization"
	_FINISH: ClassVar[str] = "Phase 1 Initialization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None


@export
class Phase11_CoreGenerationAndDesignSetup(Phase):
	pass


@export
class Phase12_SetupConstraintsAndSortNetlist(Phase):
	pass


@export
class Phase2_TimerUpdateAndTimingDataCollection(Phase):
	_START:  ClassVar[str] = "Phase 2 Timer Update And Timing Data Collection"
	_FINISH: ClassVar[str] = "Phase 2 Timer Update And Timing Data Collection | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None


@export
class Phase21_TimerUpdate(Phase):
	pass


@export
class Phase22_TimingDataCollection(Phase):
	pass


@export
class Phase3_Retarget(Phase):
	_START:  ClassVar[str] = "Phase 3 Retarget"
	_FINISH: ClassVar[str] = "Phase 3 Retarget | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Retarget | Checksum:"


@export
class Phase4_ConstantPropagation(Phase):
	_START:  ClassVar[str] = "Phase 4 Constant propagation"
	_FINISH: ClassVar[str] = "Phase 4 Constant propagation | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Constant propagation | Checksum:"


@export
class Phase5_Sweep(Phase):
	_START:  ClassVar[str] = "Phase 5 Sweep"
	_FINISH: ClassVar[str] = "Phase 5 Sweep | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = "Sweep | Checksum:"


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
class Phase9_Finalization(Phase):
	_START:  ClassVar[str] = "Phase 9 Finalization"
	_FINISH: ClassVar[str] = "Phase 9 Finalization | Checksum:"
	_TIME:   ClassVar[str] = "Time (s):"
	_FINAL:  ClassVar[str] = None


@export
class Phase91_FinalizingDesignCoresAndUpdatingShapes(Phase):
	pass


@export
class Phase92_VerifyingNetlistConnectivity(Phase):
	pass


@export
class DRCTask(Task):
	_START:  ClassVar[str] = "Starting DRC Task"
	_FINISH: ClassVar[str] = "Time (s):"


@export
class CacheTimingInformationTask(Task):
	_START:  ClassVar[str] = "Starting Cache Timing Information Task"
	_FINISH: ClassVar[str] = "Ending Cache Timing Information Task"


@export
class LogicOptimizationTask(Task):
	_START:  ClassVar[str] = "Starting Logic Optimization Task"
	_FINISH: ClassVar[str] = "Ending Logic Optimization Task"

	_PARSERS: ClassVar[List[Type[Phase]]] = (
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

	_phases: Dict[Type[Phase], Phase]

	def __init__(self, command: "Command"):
		super().__init__(command)

		self._phases = {t: t(self) for t in self._PARSERS}

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
						raise Exception(f"Unknown phase: {line}")
					break
				elif line.StartsWith("Ending"):
					nextLine = yield from self._TaskFinish(line)
					return nextLine
				elif line.StartsWith(self._FINAL):
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
