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
from typing import Generator, ClassVar

from pyTooling.Decorators  import export
from pyTooling.MetaClasses import ExtendedType, abstractmethod

from pyEDAA.OutputFilter.Xilinx import Line, VivadoMessage, LineKind
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

		line._kind = LineKind.TaskEnd
		line = yield line
		while self._FINAL is not None:
			if line.StartsWith(self._FINAL):
				break

			line = yield line

		line._kind = LineKind.PhaseEnd
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

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._TaskStart(line)

		while True:
			if line.StartsWith("Phase "):
				break
			elif line.StartsWith("Ending"):
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
class Phase1_Initialization(Phase):
	pass


@export
class Phase11_CoreGenerationAndDesignSetup(Phase):
	pass


@export
class Phase12_SetupConstraintsAndSortNetlist(Phase):
	pass


@export
class Phase2_TimerUpdateAndTimingDataCollection(Phase):
	pass


@export
class Phase21_TimerUpdate(Phase):
	pass


@export
class Phase22_TimingDataCollection(Phase):
	pass


@export
class Phase3_Retarget(Phase):
	pass


@export
class Phase4_ConstantPropagation(Phase):
	pass


@export
class Phase5_Sweep(Phase):
	pass


@export
class Phase6_BUFGOptimization(Phase):
	pass


@export
class Phase7_ShiftRegisterOptimization(Phase):
	pass


@export
class Phase8_PostProcessingNetlist(Phase):
	pass


@export
class Phase9_Finalization(Phase):
	pass


@export
class Phase91_FinalizingDesignCoresAndUpdatingShapes(Phase):
	pass


@export
class Phase92_VerifyingNetlistConnectivity(Phase):
	pass


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
