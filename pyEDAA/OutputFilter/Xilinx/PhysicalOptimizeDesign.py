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
from typing import Generator, ClassVar, List, Type, Tuple

from pyTooling.Decorators import export

from pyEDAA.OutputFilter.Xilinx           import Line, VivadoMessage, LineKind
from pyEDAA.OutputFilter.Xilinx.Common2   import Task, Phase


@export
class InitialUpdateTimingTask(Task):
	_NAME:   ClassVar[str] = "Initial Update Timing Task"
	_START:  ClassVar[str] = "Starting Initial Update Timing Task"
	_FINISH: ClassVar[str] = None


@export
class Phase1_PlacerInitialization(Phase):
	_START:  ClassVar[str] = "Phase 1 Physical Synthesis Initialization"
	_FINISH: ClassVar[str] = "Phase 1 Physical Synthesis Initialization | Checksum:"


@export
class Phase2_DSPRegisterOptimization(Phase):
	_START:  ClassVar[str] = "Phase 2 DSP Register Optimization"
	_FINISH: ClassVar[str] = "Phase 2 DSP Register Optimization | Checksum:"


@export
class Phase3_CriticalPathOptimization(Phase):
	_START:  ClassVar[str] = "Phase 3 Critical Path Optimization"
	_FINISH: ClassVar[str] = "Phase 3 Critical Path Optimization | Checksum:"


@export
class Phase4_CriticalPathOptimization(Phase):
	_START:  ClassVar[str] = "Phase 4 Critical Path Optimization"
	_FINISH: ClassVar[str] = "Phase 4 Critical Path Optimization | Checksum:"


@export
class PhysicalSynthesisTask(Task):
	_NAME:   ClassVar[str] = "Physical Synthesis Task"
	_START:  ClassVar[str] = "Starting Physical Synthesis Task"
	_FINISH: ClassVar[str] = "Ending Physical Synthesis Task"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase1_PlacerInitialization,
		Phase2_DSPRegisterOptimization,
		Phase3_CriticalPathOptimization,
		Phase4_CriticalPathOptimization
	)

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
					for parser in activeParsers:  # type: Phase
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
