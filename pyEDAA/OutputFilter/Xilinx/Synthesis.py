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
from pathlib  import Path
from re       import compile as re_compile
from typing   import ClassVar, List, Callable, Dict, Type, Iterator, Union, Generator

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import mustoverride
from pyTooling.Common      import firstValue

from pyEDAA.OutputFilter.Xilinx import VivadoMessage, ProcessingState, Parser, Preamble, BaseProcessor, BaseDocument, \
	Line, ProcessorException, LineKind, VivadoInfoMessage, VHDLAssertionMessage, VHDLReportMessage

TIME_MEMORY_PATTERN = re_compile(r"""Time \(s\): cpu = (\d{2}:\d{2}:\d{2}) ; elapsed = (\d{2}:\d{2}:\d{2}) . Memory \(MB\): peak = (\d+\.\d+) ; gain = (\d+\.\d+)""")


@export
class Initialize(Parser):
	_command: str
	_license: VivadoMessage

	def ParseLine(self, lineNumber: int, line: str) -> bool:
		pass


@export
class Section(Parser):
	# _START:  ClassVar[str]
	# _FINISH: ClassVar[str]

	_duration: float

	def __init__(self, processor: "Processor"):
		super().__init__(processor)

		self._duration = 0.0

	@readonly
	def Duration(self) -> float:
		return self._duration

	def _SectionStart(self, line: Line) -> Generator[Line, Line, Line]:
		line._kind = LineKind.SectionStart

		line = yield line
		if line._message.startswith("----"):
			line._kind = LineKind.SectionStart | LineKind.SectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		nextLine = yield line
		return nextLine

	def _SectionFinish(self, line: Line) -> Generator[Line, Line, None]:
		if line._message.startswith(self._FINISH):
			line._kind = LineKind.SectionEnd
		else:
			line._kind |= LineKind.ProcessorError

		line = yield line
		if line._message.startswith("----"):
			line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter | LineKind.Last
		else:
			line._kind |= LineKind.ProcessorError

		check = yield line
		if check is not None:
			raise Exception()

	# @mustoverride
	# def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
	# 	if len(line) == 0:
	# 		return ProcessingState.EmptyLine
	# 	elif line.startswith("----"):
	# 		return ProcessingState.DelimiterLine
	# 	elif line.startswith(self._START):
	# 		return ProcessingState.Skipped
	# 	elif line.startswith(self._FINISH):
	# 		l = line[len(self._FINISH):]
	# 		if (match := TIME_MEMORY_PATTERN.match(l)) is not None:
	# 			# cpuParts = match[1].split(":")
	# 			elapsedParts = match[2].split(":")
	# 			# peakMemory = float(match[3])
	# 			# gainMemory = float(match[4])
	# 			self._duration = int(elapsedParts[0]) * 3600 + int(elapsedParts[1]) * 60 + int(elapsedParts[2])
	#
	# 		return ProcessingState.Skipped | ProcessingState.Last
	# 	elif line.startswith("Start") or line.startswith("Starting"):
	# 		print(f"ERROR: didn't find finish\n  {line}")
	# 		return ProcessingState.Reprocess
	#
	# 	return ProcessingState.Skipped

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SectionStart(line)

		while line is not None:
			rawMessage = line._message

			if rawMessage.startswith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
				break
			else:
				line._kind = LineKind.Verbose

			line = yield line

		line = yield line
		nextLine = yield from self._SectionFinish(line)
		return nextLine


@export
class SubSection(Section):
	def _SectionStart(self, line: Line) -> Generator[Line, Line, Line]:
		line._kind = LineKind.SubSectionStart

		line = yield line
		if line._message.startswith("----"):
			line._kind = LineKind.SubSectionStart | LineKind.SubSectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		nextLine = yield line
		return nextLine

	def _SectionFinish(self, line: Line) -> Generator[Line, Line, None]:
		if line._message.startswith(self._FINISH):
			line._kind = LineKind.SubSectionEnd
		else:
			line._kind |= LineKind.ProcessorError

		line = yield line
		if line._message.startswith("----"):
			line._kind = LineKind.SubSectionEnd | LineKind.SubSectionDelimiter | LineKind.Last
		else:
			line._kind |= LineKind.ProcessorError

		nextLine = yield line
		return nextLine

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SectionStart(line)

		while line is not None:
			rawMessage = line._message

			if rawMessage.startswith("----"):
				line._kind = LineKind.SubSectionEnd | LineKind.SubSectionDelimiter
				break
			else:
				line._kind = LineKind.Verbose

			line = yield line

		line = yield line
		nextLine = yield from self._SectionFinish(line)

		return nextLine


@export
class RTLElaboration(Section):
	_START:  ClassVar[str] = "Starting RTL Elaboration : "
	_FINISH: ClassVar[str] = "Finished RTL Elaboration : "

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SectionStart(line)

		while line is not None:
			rawMessage = line._message

			if isinstance(line, VivadoInfoMessage):
				if line._toolID == 8:
					if line._messageKindID == 63:    # VHDL assert statement
						newLine = VHDLAssertionMessage.Convert(line)
						if newLine is None:
							print(f"Convert error at: {line}")
						else:
							line = newLine
					elif line._messageKindID == 6031:  # VHDL report statement
						newLine = VHDLReportMessage.Convert(line)
						if newLine is None:
							print(f"Convert error at: {line}")
						else:
							line = newLine

			if rawMessage.startswith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
				break
			elif not isinstance(line, VivadoMessage):
				line._kind = LineKind.Verbose

			line = yield line

		line = yield line
		nextLine = yield from self._SectionFinish(line)
		return nextLine


@export
class HandlingCustomAttributes1(Section):
	_START:  ClassVar[str] = "Start Handling Custom Attributes"
	_FINISH: ClassVar[str] = "Finished Handling Custom Attributes : "


@export
class ConstraintValidation(Section):
	_START:  ClassVar[str] = "Finished RTL Optimization Phase 1"
	_FINISH: ClassVar[str] = "Finished Constraint Validation : "


@export
class LoadingPart(Section):
	_START:  ClassVar[str] = "Start Loading Part and Timing Information"
	_FINISH: ClassVar[str] = "Finished Loading Part and Timing Information : "

	_part: str

	def __init__(self, processor: "Processor"):
		super().__init__(processor)

		self._part = None

	@readonly
	def Part(self) -> str:
		return self._part

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SectionStart(line)

		while line is not None:
			rawMessage = line._message

			if line._message.startswith("Loading part: "):
				line._kind = LineKind.Normal
				self._part = line._message[14:].strip()

			if rawMessage.startswith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
				break

			line = yield line

		line = yield line
		nextLine = yield from self._SectionFinish(line)
		return nextLine

@export
class ApplySetProperty(Section):
	_START:  ClassVar[str] = "Start Applying 'set_property' XDC Constraints"
	_FINISH: ClassVar[str] = "Finished applying 'set_property' XDC Constraints : "


@export
class RTLComponentStatistics(Section):
	_START:  ClassVar[str] = "Start RTL Component Statistics"
	_FINISH: ClassVar[str] = "Finished RTL Component Statistics"

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SectionStart(line)

		while line is not None:
			rawMessage = line._message

			if rawMessage.startswith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
				break
			else:
				line._kind = LineKind.Verbose

			line = yield line

		line = yield line
		nextLine = yield from self._SectionFinish(line)
		return nextLine


@export
class PartResourceSummary(Section):
	_START:  ClassVar[str] = "Start Part Resource Summary"
	_FINISH: ClassVar[str] = "Finished Part Resource Summary"


@export
class CrossBoundaryAndAreaOptimization(Section):
	_START:  ClassVar[str] = "Start Cross Boundary and Area Optimization"
	_FINISH: ClassVar[str] = "Finished Cross Boundary and Area Optimization : "


@export
class ApplyingXDCTimingConstraints(Section):
	_START:  ClassVar[str] = "Start Applying XDC Timing Constraints"
	_FINISH: ClassVar[str] = "Finished Applying XDC Timing Constraints : "


@export
class TimingOptimization(Section):
	_START:  ClassVar[str] = "Start Timing Optimization"
	_FINISH: ClassVar[str] = "Finished Timing Optimization : "


@export
class TechnologyMapping(Section):
	_START:  ClassVar[str] = "Start Technology Mapping"
	_FINISH: ClassVar[str] = "Finished Technology Mapping : "


@export
class FlatteningBeforeIOInsertion(SubSection):
	_START:  ClassVar[str] = "Start Flattening Before IO Insertion"
	_FINISH: ClassVar[str] = "Finished Flattening Before IO Insertion"


@export
class FinalNetlistCleanup(SubSection):
	_START:  ClassVar[str] = "Start Final Netlist Cleanup"
	_FINISH: ClassVar[str] = "Finished Final Netlist Cleanup"


@export
class IOInsertion(Section):
	_START:  ClassVar[str] = "Start IO Insertion"
	_FINISH: ClassVar[str] = "Finished IO Insertion : "

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		flattening = FlatteningBeforeIOInsertion(None)
		netlist = FinalNetlistCleanup(None)

		line = yield from self._SectionStart(line)
		if line._message.startswith("----"):
			line._kind = LineKind.SectionStart | LineKind.SectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		line = yield line
		if line._message.startswith("Start "):
			line = yield from flattening.Generator(line)

		if line._message.startswith("----"):
			line._kind = LineKind.SubSectionStart | LineKind.SectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		line = yield line
		if line._message.startswith("Start "):
			line = yield from netlist.Generator(line)

		if line._message.startswith("----"):
			line._kind = LineKind.SubSectionEnd | LineKind.SectionDelimiter
		else:
			line._kind |= LineKind.ProcessorError

		line = yield line
		nextLine = yield from self._SectionFinish(line)
		return nextLine

@export
class RenamingGeneratedInstances(Section):
	_START:  ClassVar[str] = "Start Renaming Generated Instances"
	_FINISH: ClassVar[str] = "Finished Renaming Generated Instances : "


@export
class RebuildingUserHierarchy(Section):
	_START:  ClassVar[str] = "Start Rebuilding User Hierarchy"
	_FINISH: ClassVar[str] = "Finished Rebuilding User Hierarchy : "


@export
class RenamingGeneratedPorts(Section):
	_START:  ClassVar[str] = "Start Renaming Generated Ports"
	_FINISH: ClassVar[str] = "Finished Renaming Generated Ports : "


@export
class HandlingCustomAttributes2(Section):
	_START:  ClassVar[str] = "Start Handling Custom Attributes"
	_FINISH: ClassVar[str] = "Finished Handling Custom Attributes : "


@export
class RenamingGeneratedNets(Section):
	_START:  ClassVar[str] = "Start Renaming Generated Nets"
	_FINISH: ClassVar[str] = "Finished Renaming Generated Nets : "


@export
class WritingSynthesisReport(Section):
	_START:  ClassVar[str] = "Start Writing Synthesis Report"
	_FINISH: ClassVar[str] = "Finished Writing Synthesis Report : "

	_blackboxes: Dict[str, int]
	_cells:      Dict[str, int]

	def __init__(self, processor: "Processor"):
		super().__init__(processor)

		self._blackboxes = {}
		self._cells =      {}

	@readonly
	def Cells(self) -> Dict[str, int]:
		return self._cells

	@readonly
	def Blackboxes(self) -> Dict[str, int]:
		return self._blackboxes

	def _BlackboxesGenerator(self, line: Line) -> Generator[Line, Line, Line]:
		if line._message.startswith("+-"):
			line._kind = LineKind.TableFrame
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		if line._message.startswith("| "):
			line._kind = LineKind.TableHeader
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		if line._message.startswith("+-"):
			line._kind = LineKind.TableFrame
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		while line is not None:
			if line._message.startswith("| "):
				line._kind = LineKind.TableRow

				columns = line._message.strip("|").split("|")
				self._blackboxes[columns[1].strip()] = int(columns[2].strip())
			elif line._message.startswith("+-"):
				line._kind = LineKind.TableFrame
				break
			else:
				line._kind = LineKind.ProcessorError

			line = yield line

		nextLine = yield line
		return nextLine

	def _CellGenerator(self, line: Line) -> Generator[Line, Line, Line]:
		if line._message.startswith("+-"):
			line._kind = LineKind.TableFrame
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		if line._message.startswith("| "):
			line._kind = LineKind.TableHeader
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		if line._message.startswith("+-"):
			line._kind = LineKind.TableFrame
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		while line is not None:
			if line._message.startswith("|"):
				line._kind = LineKind.TableRow

				columns = line._message.strip("|").split("|")
				self._cells[columns[1].strip()] = int(columns[2].strip())
			elif line._message.startswith("+-"):
				line._kind = LineKind.TableFrame
				break
			else:
				line._kind = LineKind.ProcessorError

			line = yield line

		nextLine = yield line
		return nextLine

	def Generator(self, line: Line) -> Generator[Line, Line, Line]:
		line = yield from self._SectionStart(line)

		while line is not None:
			rawMessage = line._message

			if rawMessage.startswith("Report BlackBoxes:"):
				line._kind = LineKind.ParagraphHeadline
				line = yield line
				line = yield from self._BlackboxesGenerator(line)
			elif rawMessage.startswith("Report Cell Usage:"):
				line._kind = LineKind.ParagraphHeadline
				line = yield line
				line = yield from self._CellGenerator(line)
			elif rawMessage.startswith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
				break
			elif not isinstance(line, VivadoMessage):
				line._kind = LineKind.Verbose
				line = yield line
			elif line._kind is LineKind.Empty:
				line = yield line

		line = yield line
		nextLine = yield from self._SectionFinish(line)
		return nextLine


PARSERS = (
	Preamble,
	RTLElaboration,
	HandlingCustomAttributes1,
	ConstraintValidation,
	LoadingPart,
	ApplySetProperty,
	RTLComponentStatistics,
	PartResourceSummary,
	CrossBoundaryAndAreaOptimization,
	ApplyingXDCTimingConstraints,
	TimingOptimization,
	TechnologyMapping,
	IOInsertion,
	FlatteningBeforeIOInsertion,
	FinalNetlistCleanup,
	RenamingGeneratedInstances,
	RebuildingUserHierarchy,
	RenamingGeneratedPorts,
	HandlingCustomAttributes2,
	RenamingGeneratedNets,
	WritingSynthesisReport,
)


Parsers = Union[*PARSERS]


@export
class Processor(BaseDocument):
	_parsers:  Dict[Type[Parser], Parsers]

	def __init__(self, synthesisLogfile: Path):
		super().__init__(synthesisLogfile)

		self._parsers =  {p: p(self) for p in PARSERS}

	@readonly
	def HasLatches(self) -> bool:
		if (8 in self._messagesByID) and (327 in self._messagesByID[8]):
			return True

		return "LD" in self._parsers[WritingSynthesisReport]._cells

	@readonly
	def Latches(self) -> Iterator[VivadoMessage]:
		try:
			yield from iter(self._messagesByID[8][327])
		except KeyError:
			yield from ()

	@readonly
	def HasBlackboxes(self) -> bool:
		return len(self._parsers[WritingSynthesisReport]._blackboxes) > 0

	@readonly
	def Cells(self) -> Dict[str, int]:
		return self._parsers[WritingSynthesisReport]._cells

	def __getitem__(self, item: Type[Parser]) -> Parsers:
		return self._parsers[item]

	def DocumentSlicer(self) -> Generator[Union[Line, ProcessorException], Line, None]:
		parser:        Section       = firstValue(self._parsers)
		activeParsers: List[Parsers] = list(self._parsers.values())

		rtlElaboration = self._parsers[RTLElaboration]
		constraintValidation = self._parsers[ConstraintValidation]

		# get first line and send to preamble filter
		line = yield
		line = next(filter := parser.Generator(line))

		# return first line and get the second line
		line = yield line

		while line is not None:
			if filter is not None:
				line = filter.send(line)

				if (LineKind.Last in line._kind) and (LineKind.SectionDelimiter in line._kind):
					activeParsers.remove(parser)
					filter = None
			else:
				if line._message.startswith("Start "):
					for parser in activeParsers:  # type: Section
						if line._message.startswith(parser._START):
							line = next(filter := parser.Generator(line))
							break
					else:
						raise Exception(f"Unknown section: {line}")
				elif line._message.startswith("Starting "):
					if line._message[9:].startswith("synth_design"):
						line._kind = LineKind.Verbose
					elif line._message.startswith(rtlElaboration._START):
						parser = rtlElaboration
						line = next(filter := parser.Generator(line))
				elif line._message.startswith("Finished "):
					if line._message.startswith(constraintValidation._START):
						parser = constraintValidation
						line = next(filter := parser.Generator(line))

			if line._kind is LineKind.Unprocessed:
				line._kind = LineKind.Normal

			line = yield line

		pass

# unused
# used but not set
# statemachine encodings
# resources
#  * RTL
#	 * Mapped

# Design hierarchy + generics per hierarchy
# read XDC files
