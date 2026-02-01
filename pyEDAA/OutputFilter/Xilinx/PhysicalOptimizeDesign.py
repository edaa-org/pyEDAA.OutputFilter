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
from typing import ClassVar, Type, Tuple, Dict

from pyTooling.Decorators import export

from pyEDAA.OutputFilter.Xilinx.Common2 import Task, TaskWithPhases, Phase
from pyEDAA.OutputFilter.Xilinx.Common2 import MAJOR, MAJOR_MINOR, MAJOR_MINOR_MICRO, MAJOR_MINOR_MICRO_NANO


@export
class InitialUpdateTimingTask(Task):
	_NAME:   ClassVar[str] = "Initial Update Timing Task"
	_START:  ClassVar[str] = "Starting Initial Update Timing Task"
	_FINISH: ClassVar[str] = None


@export
class Phase_PlacerInitialization(Phase):
	"""
	*Physical Synthesis Initialization* phase.

	Used by task :class:`PhysicalSynthesisTask`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Physical Synthesis Initialization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Physical Synthesis Initialization | Checksum:"


@export
class Phase_DSPRegisterOptimization(Phase):
	"""
	*DSP Register Optimization* phase.

	Used by task :class:`PhysicalSynthesisTask`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} DSP Register Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} DSP Register Optimization | Checksum:"


@export
class Phase_CriticalPathOptimization_1(Phase):
	"""
	*Critical Path Optimization* phase.

	Used by task :class:`PhysicalSynthesisTask`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Critical Path Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Critical Path Optimization | Checksum:"


@export
class Phase_CriticalPathOptimization_2(Phase):
	"""
	*Critical Path Optimization* phase.

	Used by task :class:`PhysicalSynthesisTask`.
	"""
	_START:  ClassVar[Pattern] = compile(f"^Phase {MAJOR} Critical Path Optimization")
	_FINISH: ClassVar[str]     = "Phase {phaseIndex} Critical Path Optimization | Checksum:"


@export
class PhysicalSynthesisTask(TaskWithPhases):
	"""
	Parses *Physical Synthesis* task's outputs.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.PhysicalOptimizeDesign`.
	"""
	_NAME:   ClassVar[str] = "Physical Synthesis Task"
	_START:  ClassVar[str] = "Starting Physical Synthesis Task"
	_FINISH: ClassVar[str] = "Ending Physical Synthesis Task"

	_PARSERS: ClassVar[Tuple[Type[Phase], ...]] = (
		Phase_PlacerInitialization,
		Phase_DSPRegisterOptimization,
		Phase_CriticalPathOptimization_1,
		Phase_CriticalPathOptimization_2
	)
