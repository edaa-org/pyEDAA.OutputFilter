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
from datetime import datetime
from enum     import Flag
from pathlib  import Path
from re       import compile as re_compile, Pattern
from typing   import ClassVar, List, Optional as Nullable, Callable, Dict, Type

from pyTooling.Decorators import export, readonly
from pyTooling.MetaClasses import ExtendedType, abstractmethod, mustoverride
from pyTooling.Common      import firstValue
from pyTooling.Stopwatch import Stopwatch
from pyTooling.Versioning  import YearReleaseVersion

from pyEDAA.OutputFilter.Xilinx import VivadoMessage, VivadoInfoMessage, VivadoWarningMessage, VivadoCriticalWarningMessage, VivadoErrorMessage


@export
class ProcessingState(Flag):
	Processed =        1
	Skipped =          2
	EmptyLine =        4
	CommentLine =      8
	DelimiterLine =   16
	TableLine =       32
	TableHeader =     64
	Reprocess =      512
	Last =          1024


TIME_MEMORY_PATTERN = re_compile(r"""Time \(s\): cpu = (\d{2}:\d{2}:\d{2}) ; elapsed = (\d{2}:\d{2}:\d{2}) . Memory \(MB\): peak = (\d+\.\d+) ; gain = (\d+\.\d+)""")

@export
class Parser(metaclass=ExtendedType, slots=True):
	_processor: "Processor"

	def __init__(self, processor: "Processor"):
		self._processor = processor

	@readonly
	def Processor(self) -> "Processor":
		return self._processor

	@abstractmethod
	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		pass


@export
class Preamble(Parser):
	_toolVersion:   Nullable[YearReleaseVersion]
	_startDatetime: Nullable[datetime]

	_VERSION:   ClassVar[Pattern] = re_compile(r"""# Vivado v(\d+\.\d(\.\d)?) \(64-bit\)""")
	_STARTTIME: ClassVar[Pattern] = re_compile(r"""# Start of session at: Thu (\w+) (\d+) (\d+):(\d+):(\d+) (\d+)""")

	def __init__(self, processor: "Processor"):
		super().__init__(processor)

		self._toolVersion =   None
		self._startDatetime = None

	@readonly
	def ToolVersion(self) -> YearReleaseVersion:
		return self._toolVersion

	@readonly
	def StartDatetime(self) -> datetime:
		return self._startDatetime

	def ParseLine(self, lineNumber: int, line: str) -> ProcessingState:
		if self._toolVersion is not None and line.startswith("#----"):
			return ProcessingState.DelimiterLine | ProcessingState.Last
		elif (match := self._VERSION.match(line)) is not None:
			self._toolVersion = YearReleaseVersion.Parse(match[1])
			return ProcessingState.Processed
		elif (match := self._VERSION.match(line)) is not None:
			self._startDatetime = datetime(int(match[6]), int(match[1]), int(match[2]), int(match[3]), int(match[4]), int(match[5]))
			return ProcessingState.Processed

		return ProcessingState.Skipped


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

@export
class Processor(metaclass=ExtendedType, slots=True):
	_logfile:  Path
	_parsers:  Dict[Type[Parser], Parser]
	_state:    Callable[[int, str], bool]
	_duration: float

	_infoMessages:            List[VivadoInfoMessage]
	_warningMessages:         List[VivadoWarningMessage]
	_criticalWarningMessages: List[VivadoCriticalWarningMessage]
	_errorMessages:           List[VivadoErrorMessage]
	_toolIDs:                 Dict[int, str]
	_toolNames:               Dict[str, int]
	_messagesByID:            Dict[int, Dict[int, List[VivadoMessage]]]

	def __init__(self, synthesisLogfile: Path):
		self._logfile =  synthesisLogfile
		self._parsers =  {p: p(self) for p in PARSERS}
		self._state =    firstValue(self._parsers).ParseLine
		self._duration = 0.0

		self._infoMessages =            []
		self._warningMessages =         []
		self._criticalWarningMessages = []
		self._errorMessages =           []
		self._toolIDs =                 {}
		self._toolNames =               {}
		self._messagesByID =            {}

	@readonly
	def Duration(self) -> float:
		return self._duration

	@readonly
	def InfoMessages(self) -> List[VivadoInfoMessage]:
		return self._infoMessages

	@readonly
	def WarningMessages(self) -> List[VivadoWarningMessage]:
		return self._warningMessages

	@readonly
	def CriticalWarningMessages(self) -> List[VivadoCriticalWarningMessage]:
		return self._criticalWarningMessages

	@readonly
	def ErrorMessages(self) -> List[VivadoErrorMessage]:
		return self._errorMessages

	def __getitem__(self, item: Type[Parser]) -> Parser:
		return self._parsers[item]

	def Parse(self):
		with Stopwatch() as sw:
			with self._logfile.open("r", encoding="utf-8") as f:
				content = f.read()

			activeParsers = list(self._parsers.values())

			lines = content.splitlines()
			for lineNumber, line in enumerate(l.rstrip() for l in lines):
				prefix = line[:4]
				if prefix == "INFO":
					if (message := VivadoInfoMessage.Parse(line, lineNumber)) is None:
						print(f"pattern not detected\n{line}")
						continue

					self._infoMessages.append(message)
				elif prefix == "WARN":
					if (message := VivadoWarningMessage.Parse(line, lineNumber)) is None:
						print(f"pattern not detected\n{line}")
						continue

					self._warningMessages.append(message)
				elif prefix == "CRIT":
					if (message := VivadoCriticalWarningMessage.Parse(line, lineNumber)) is None:
						print(f"pattern not detected\n{line}")
						continue

					self._criticalWarningMessages.append(message)
				elif prefix == "ERRO":
					if (message := VivadoErrorMessage.Parse(line, lineNumber)) is None:
						print(f"pattern not detected\n{line}")
						continue

					self._errorMessages.append(message)
				else:
					if self._state is not None:
						result = self._state(lineNumber, line)
						if ProcessingState.Last in result:
							obj: Section = self._state.__self__
							activeParsers.remove(obj)
							self._state = None

							print(f" DONE: {obj.__class__.__name__}")
					else:
						if line.startswith("Start") or line.startswith("Starting"):
							for parser in activeParsers:   # type: Section
								if line.startswith(parser._START):
									print(f"BEGIN: {parser.__class__.__name__}")
									self._state = parser.ParseLine
									_ = self._state(lineNumber, line)
									break
							else:
								print(f"Unknown section\n  {line}")

					continue

				if message._toolID in self._messagesByID:
					sub = self._messagesByID[message._toolID]
					if message._messageKindID in sub:
						sub[message._messageKindID].append(message)
					else:
						sub[message._messageKindID] = [message]
				else:
					self._toolIDs[message._toolID] = message._toolName
					self._toolNames[message._toolName] = message._toolID
					self._messagesByID[message._toolID] = {message._messageKindID: [message]}

		self._duration = sw.Duration


def main():
	logfile = Path("tests/data/Stopwatch/toplevel.vds")
	logfile = Path("tests/data/ADL-1000/toplevel.vds")
	processor = Processor(logfile)
	processor.Parse()

	print()
	print(f"Vivado version: {processor._parsers[Preamble]._toolVersion}")


	#
	# print("%" * 80)
	# for toolID, messageGroups in processor._messagesByID.items():
	# 	print(f"{toolID} ({len(messageGroups)}):")
	# 	for messageID, messages in messageGroups.items():
	# 		print(f"  {messageID} ({len(messages)}):")
	# 		for message in messages:
	# 			print(f"    {message}")
	#
	# print("%" * 80)
	# for tool, toolID in processor._toolNames.items():
	# 	messages = list(chain(*processor._messagesByID[toolID].values()))
	# 	print(f"{tool} ({len(messages)}):")
	# 	for message in messages:
	# 		print(f"  {message}")

	# print(f"Cells Statistics")
	# for cellName, cellCount in processor._parsers[WritingSynthesisReport]._cells.items():
	# 	print(f"  {cellName:16}: {cellCount}")

if __name__ == '__main__':
	main()


# latches
# unused
# used but not set
# statemachine encodings
# resources
#  * RTL
#	 * Mapped
