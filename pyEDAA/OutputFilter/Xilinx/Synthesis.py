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
from typing   import ClassVar, List, Callable, Dict, Type, Iterator, Union

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import mustoverride
from pyTooling.Common      import firstValue

from pyEDAA.OutputFilter.Xilinx import VivadoMessage, ProcessingState, Parser, Preamble, BaseProcessor

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

	@mustoverride
	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		if len(line) == 0:
			return ProcessingState.EmptyLine
		elif line.startswith("----"):
			return ProcessingState.DelimiterLine
		elif line.startswith(self._START):
			return ProcessingState.Skipped
		elif line.startswith(self._FINISH):
			l = line[len(self._FINISH):]
			if (match := TIME_MEMORY_PATTERN.match(l)) is not None:
				# cpuParts = match[1].split(":")
				elapsedParts = match[2].split(":")
				# peakMemory = float(match[3])
				# gainMemory = float(match[4])
				self._duration = int(elapsedParts[0]) * 3600 + int(elapsedParts[1]) * 60 + int(elapsedParts[2])

			return ProcessingState.Skipped | ProcessingState.Last
		elif line.startswith("Start") or line.startswith("Starting"):
			print(f"ERROR: didn't find finish\n  {line}")
			return ProcessingState.Reprocess

		return ProcessingState.Skipped


@export
class RTLElaboration(Section):
	_START:  ClassVar[str] = "Starting RTL Elaboration : "
	_FINISH: ClassVar[str] = "Finished RTL Elaboration : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class HandlingCustomAttributes1(Section):
	_START: ClassVar[str] =  "Start Handling Custom Attributes"
	_FINISH: ClassVar[str] = "Finished Handling Custom Attributes : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class LoadingPart(Section):
	_START: ClassVar[str] =  "Start Loading Part and Timing Information"
	_FINISH: ClassVar[str] = "Finished Loading Part and Timing Information : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class ApplySetProperty(Section):
	_START: ClassVar[str] =  "Start Applying 'set_property' XDC Constraints"
	_FINISH: ClassVar[str] = "Finished applying 'set_property' XDC Constraints : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class RTLComponentStatistics(Section):
	_START: ClassVar[str] =  "Start RTL Component Statistics"
	_FINISH: ClassVar[str] = "Finished RTL Component Statistics"

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class PartResourceSummary(Section):
	_START: ClassVar[str] =  "Start Part Resource Summary"
	_FINISH: ClassVar[str] = "Finished Part Resource Summary"

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class CrossBoundaryAndAreaOptimization(Section):
	_START: ClassVar[str] =  "Start Cross Boundary and Area Optimization"
	_FINISH: ClassVar[str] = "Finished Cross Boundary and Area Optimization : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class ApplyingXDCTimingConstraints(Section):
	_START: ClassVar[str] =  "Start Applying XDC Timing Constraints"
	_FINISH: ClassVar[str] = "Finished Applying XDC Timing Constraints : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class TimingOptimization(Section):
	_START: ClassVar[str] =  "Start Timing Optimization"
	_FINISH: ClassVar[str] = "Finished Timing Optimization : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class TechnologyMapping(Section):
	_START: ClassVar[str] =  "Start Technology Mapping"
	_FINISH: ClassVar[str] = "Finished Technology Mapping : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class IOInsertion(Section):
	_START: ClassVar[str] =  "Start IO Insertion"
	_FINISH: ClassVar[str] = "Finished IO Insertion : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class FlatteningBeforeIOInsertion(Section):
	_START: ClassVar[str] =  "Start Flattening Before IO Insertion"
	_FINISH: ClassVar[str] = "Finished Flattening Before IO Insertion"

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class FinalNetlistCleanup(Section):
	_START: ClassVar[str] =  "Start Final Netlist Cleanup"
	_FINISH: ClassVar[str] = "Finished Final Netlist Cleanup"

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class RenamingGeneratedInstances(Section):
	_START: ClassVar[str] =  "Start Renaming Generated Instances"
	_FINISH: ClassVar[str] = "Finished Renaming Generated Instances : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class RebuildingUserHierarchy(Section):
	_START: ClassVar[str] =  "Start Rebuilding User Hierarchy"
	_FINISH: ClassVar[str] = "Finished Rebuilding User Hierarchy : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class RenamingGeneratedPorts(Section):
	_START: ClassVar[str] =  "Start Renaming Generated Ports"
	_FINISH: ClassVar[str] = "Finished Renaming Generated Ports : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class HandlingCustomAttributes2(Section):
	_START: ClassVar[str] =  "Start Handling Custom Attributes"
	_FINISH: ClassVar[str] = "Finished Handling Custom Attributes : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class RenamingGeneratedNets(Section):
	_START: ClassVar[str] =  "Start Renaming Generated Nets"
	_FINISH: ClassVar[str] = "Finished Renaming Generated Nets : "

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		return super().ParseLine(lineNumber, line)


@export
class WritingSynthesisReport(Section):
	_START:  ClassVar[str] = "Start Writing Synthesis Report"
	_FINISH: ClassVar[str] = "Finished Writing Synthesis Report : "

	_state:      int
	_blackboxes: Dict[str, int]
	_cells:      Dict[str, int]

	def __init__(self, processor: "Processor"):
		super().__init__(processor)

		self._state =      0
		self._blackboxes = {}
		self._cells =      {}

	@readonly
	def Cells(self) -> Dict[str, int]:
		return self._cells

	@readonly
	def Blackboxes(self) -> Dict[str, int]:
		return self._blackboxes

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		if self._state == 0:
			if line.startswith("Report BlackBoxes:"):
				self._state = 10
				return ProcessingState.Processed
			elif line.startswith("Report Cell Usage:"):
				self._state = 20
				return ProcessingState.Processed
		elif 10 <= self._state < 20:
			if self._state == 10 or self._state == 12 and line.startswith("+-"):
				self._state += 1
				return ProcessingState.TableLine
			elif self._state == 11 and line.startswith("| "):
				self._state += 1
				return ProcessingState.TableHeader
			elif self._state == 13:
				if line.startswith("+-"):
					self._state = 0
					return ProcessingState.TableLine
				else:
					columns = line.strip("|").split("|")
					self._blackboxes[columns[1].strip()] = int(columns[2].strip())
		elif 20 <= self._state < 30:
			if self._state == 20 or self._state == 22 and line.startswith("+-"):
				self._state += 1
				return ProcessingState.TableLine
			elif self._state == 21 and line.startswith("| "):
				self._state += 1
				return ProcessingState.TableHeader
			elif self._state == 23:
				if line.startswith("+-"):
					self._state = 0
					return ProcessingState.TableLine
				else:
					columns = line.strip("|").split("|")
					self._cells[columns[1].strip()] = int(columns[2].strip())

		return super().ParseLine(lineNumber, line)


PARSERS = (
	Preamble,
	RTLElaboration,
	HandlingCustomAttributes1,
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
class Processor(BaseProcessor):
	_logfile:  Path
	_parsers:  Dict[Type[Parser], Parsers]
	_state:    Callable[[int, str], bool]

	_activeParsers: List[Parsers]

	def __init__(self, synthesisLogfile: Path):
		super().__init__()

		self._logfile =  synthesisLogfile
		self._parsers =  {p: p(self) for p in PARSERS}
		self._state =    firstValue(self._parsers).ParseLine

		self._activeParsers = list(self._parsers.values())

	@readonly
	def HasLatches(self) -> bool:
		try:
			synth = self._messagesByID[8]
			if 327 in synth:
				return True
		except KeyError:
			pass

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

	def _Parse(self, lineNumber: int, line: str):
		if self._state is not None:
			result = self._state(lineNumber, line)
			if ProcessingState.Last in result:
				obj: Section = self._state.__self__
				self._activeParsers.remove(obj)
				self._state = None

				print(f" DONE: {obj.__class__.__name__}")
		else:
			if line.startswith("Start") or line.startswith("Starting"):
				for parser in self._activeParsers:   # type: Section
					if line.startswith(parser._START):
						print(f"BEGIN: {parser.__class__.__name__}")
						self._state = parser.ParseLine
						_ = self._state(lineNumber, line)
						break
				else:
					print(f"Unknown section\n  {line}")

# unused
# used but not set
# statemachine encodings
# resources
#  * RTL
#	 * Mapped
