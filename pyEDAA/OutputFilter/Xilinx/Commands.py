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
"""Basic classes for outputs from AMD/Xilinx Vivado."""
from typing               import ClassVar, Generator, Union, List, Type, Dict, Iterator

from pyTooling.Decorators import export, readonly

from pyEDAA.OutputFilter.Xilinx           import VivadoTclCommand
from pyEDAA.OutputFilter.Xilinx.Exception import ProcessorException
from pyEDAA.OutputFilter.Xilinx.Common    import Line, LineKind, VivadoMessage, VHDLReportMessage
from pyEDAA.OutputFilter.Xilinx.Common2   import Parser
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import Section, RTLElaboration, HandlingCustomAttributes
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import ConstraintValidation, LoadingPart, ApplySetProperty
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import RTLComponentStatistics, PartResourceSummary
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import CrossBoundaryAndAreaOptimization, ROM_RAM_DSP_SR_Retiming
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import ApplyingXDCTimingConstraints, TimingOptimization
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import TechnologyMapping, IOInsertion, FlatteningBeforeIOInsertion
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import FinalNetlistCleanup, RenamingGeneratedInstances
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import RebuildingUserHierarchy, RenamingGeneratedPorts
from pyEDAA.OutputFilter.Xilinx.SynthesizeDesign import RenamingGeneratedNets, WritingSynthesisReport


@export
class NotPresentException(ProcessorException):
	pass


@export
class SectionNotPresentException(NotPresentException):
	pass


@export
class HandlingCustomAttributes1(HandlingCustomAttributes):
	pass


@export
class HandlingCustomAttributes2(HandlingCustomAttributes):
	pass


@export
class ROM_RAM_DSP_SR_Retiming1(ROM_RAM_DSP_SR_Retiming):
	pass


@export
class ROM_RAM_DSP_SR_Retiming2(ROM_RAM_DSP_SR_Retiming):
	pass


@export
class ROM_RAM_DSP_SR_Retiming3(ROM_RAM_DSP_SR_Retiming):
	pass


@export
class Command(Parser):
	# _TCL_COMMAND: ClassVar[str]
	pass


@export
class SynthesizeDesign(Command):
	_TCL_COMMAND: ClassVar[str] = "synth_design"
	_PARSERS:     ClassVar[List[Type[Section]]] = (
		RTLElaboration,
		HandlingCustomAttributes1,
		ConstraintValidation,
		LoadingPart,
		ApplySetProperty,
		RTLComponentStatistics,
		PartResourceSummary,
		CrossBoundaryAndAreaOptimization,
		ROM_RAM_DSP_SR_Retiming1,
		ApplyingXDCTimingConstraints,
		TimingOptimization,
		ROM_RAM_DSP_SR_Retiming2,
		TechnologyMapping,
		IOInsertion,
		FlatteningBeforeIOInsertion,
		FinalNetlistCleanup,
		RenamingGeneratedInstances,
		RebuildingUserHierarchy,
		RenamingGeneratedPorts,
		HandlingCustomAttributes2,
		RenamingGeneratedNets,
		ROM_RAM_DSP_SR_Retiming3,
		WritingSynthesisReport,
	)

	_sections:  Dict[Type[Section], Section]

	def __init__(self, processor: "Processor") -> None:
		super().__init__(processor)

		self._sections =  {p: p(self) for p in self._PARSERS}

	@readonly
	def HasLatches(self) -> bool:
		if (8 in self._messagesByID) and (327 in self._messagesByID[8]):
			return True

		return "LD" in self._sections[WritingSynthesisReport]._cells

	@readonly
	def Latches(self) -> Iterator[VivadoMessage]:
		try:
			yield from iter(self._messagesByID[8][327])
		except KeyError:
			yield from ()

	@readonly
	def HasBlackboxes(self) -> bool:
		return len(self._sections[WritingSynthesisReport]._blackboxes) > 0

	@readonly
	def Blackboxes(self) -> Dict[str, int]:
		return self._sections[WritingSynthesisReport]._blackboxes

	@readonly
	def Cells(self) -> Dict[str, int]:
		return self._sections[WritingSynthesisReport]._cells

	@readonly
	def VHDLReportMessages(self) -> List[VHDLReportMessage]:
		if 8 in self._messagesByID:
			if 6031 in (synthMessages := self._messagesByID[8]):
				return [message for message in synthMessages[6031]]

		return []

	@readonly
	def VHDLAssertMessages(self) -> List[VHDLReportMessage]:
		if 8 in self._messagesByID:
			if 63 in (synthMessages := self._messagesByID[8]):
				return [message for message in synthMessages[63]]

		return []

	def __getitem__(self, item: Type[Parser]) -> Union[_PARSERS]:
		try:
			return self._sections[item]
		except KeyError as ex:
			raise SectionNotPresentException(F"Section '{item._NAME}' not present in '{self._parent.logfile}'.") from ex

	def SectionDetector(self, line: Line) -> Generator[Union[Line, ProcessorException], Line, None]:
		# parser:        Section      = firstValue(self._sections)
		activeParsers: List[Parser] = list(self._sections.values())

		rtlElaboration = self._sections[RTLElaboration]
		# constraintValidation = self._sections[ConstraintValidation]

		if not (isinstance(line, VivadoTclCommand) and line._command == self._TCL_COMMAND):
			raise ProcessorException()

		line = yield line
		if line == "Starting synth_design":
			line._kind = LineKind.Verbose
		else:
			raise ProcessorException()

		line = yield line

		while True:
			while True:
				if line.StartsWith("Start "):
					for parser in activeParsers:  # type: Section
						if line.StartsWith(parser._START):
							line = next(section := parser.Generator(line))
							line._previousLine._kind = LineKind.SectionStart | LineKind.SectionDelimiter
							break
					else:
						raise Exception(f"Unknown section: {line}")
					break
				elif line.StartsWith("Starting "):
					if line.StartsWith(rtlElaboration._START):
						parser = rtlElaboration
						line = next(section := parser.Generator(line))
						line._previousLine._kind = LineKind.SectionStart | LineKind.SectionDelimiter
						break
				elif line.StartsWith(self._TCL_COMMAND):
					if line[len(self._TCL_COMMAND) + 1:].startswith("completed successfully"):
						line._kind |= LineKind.Success

						line = yield line
						if line.StartsWith(self._TCL_COMMAND + ":"):
							line._kind |= LineKind.Last
						else:
							pass

						lastLine = yield line
						return lastLine
				elif line.StartsWith("Finished RTL Optimization Phase"):
					line._kind = LineKind.PhaseEnd
					line._previousLine._kind = LineKind.PhaseEnd | LineKind.PhaseDelimiter
				elif line.StartsWith("----"):
					if LineKind.Phase in line._previousLine._kind:
						line._kind = LineKind.PhaseEnd | LineKind.PhaseDelimiter
				elif not isinstance(line, VivadoMessage):
					pass
					# line._kind = LineKind.Unprocessed

				line = yield line

			line = yield line

			while True:
				if line.StartsWith("Finished"):
					l = line[9:]
					if not (l.startswith("Flattening") or l.startswith("Final")):
						line = yield section.send(line)
						break

				line = yield section.send(line)

			line = yield section.send(line)

			activeParsers.remove(parser)


@export
class LinkDesign(Command):
	_TCL_COMMAND: ClassVar[str] = "link_design"


@export
class OptimizeDesign(Command):
	_TCL_COMMAND: ClassVar[str] = "opt_design"


@export
class PlaceDesign(Command):
	_TCL_COMMAND: ClassVar[str] = "place_design"


@export
class PhysicalOptimizationDesign(Command):
	_TCL_COMMAND: ClassVar[str] = "phys_opt_design"


@export
class PhysicalOptimizationDesign(Command):
	_TCL_COMMAND: ClassVar[str] = "route_design"


@export
class WriteBitstream(Command):
	_TCL_COMMAND: ClassVar[str] = "write_bitstream"

# report_drc
# report_methodology
# report_power
