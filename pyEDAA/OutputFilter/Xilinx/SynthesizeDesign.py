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
from re     import compile as re_compile
from typing import ClassVar, Dict, Generator, Optional as Nullable

from pyTooling.Decorators  import export, readonly

from pyEDAA.OutputFilter.Xilinx import Section, SubSection, SectionWithChildren
from pyEDAA.OutputFilter.Xilinx import VHDLAssertionMessage, VivadoLine, LineKind, VivadoInfoMessage, VHDLReportMessage, VivadoMessage


__all__ = ["TIME_MEMORY_PATTERN"]

TIME_MEMORY_PATTERN = re_compile(r"""Time \(s\): cpu = (\d{2}:\d{2}:\d{2}) ; elapsed = (\d{2}:\d{2}:\d{2}) . Memory \(MB\): peak = (\d+\.\d+) ; gain = (\d+\.\d+)""")


@export
class RTLElaboration(Section):
	"""
	*RTL Elaboration* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "RTL Elaboration"
	_START:      ClassVar[str] = "Starting RTL Elaboration : "
	_FINISH:     ClassVar[str] = "Finished RTL Elaboration : "
	_DUPLICATES: ClassVar[bool] = False

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._SectionStart(line)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif isinstance(line, VivadoInfoMessage):
				if line._toolID == 8:
					if line._messageKindID == 63:    # VHDL assert statement
						newLine = VHDLAssertionMessage.Convert(line)
						if newLine is None:
							pass
						else:
							line = newLine
					elif line._messageKindID == 6031:  # VHDL report statement
						newLine = VHDLReportMessage.Convert(line)
						if newLine is None:
							pass
						else:
							line = newLine

			if line.StartsWith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			else:
				line._kind = LineKind.Verbose

			line = yield line

		# line = yield line
		nextLine = yield from self._SectionFinish(line)
		return nextLine


@export
class HandlingCustomAttributes(Section):
	"""
	*Handling Custom Attributes* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Handling Custom Attributes"
	_START:      ClassVar[str] = "Start Handling Custom Attributes"
	_FINISH:     ClassVar[str] = "Finished Handling Custom Attributes : "
	_DUPLICATES: ClassVar[bool] = True


@export
class ConstraintValidation(Section):
	"""
	*Constraint Validation* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Constraint Validation"
	_START:      ClassVar[str] = "Finished RTL Optimization Phase 1"
	_FINISH:     ClassVar[str] = "Finished Constraint Validation : "
	_DUPLICATES: ClassVar[bool] = False


@export
class LoadingPart(Section):
	"""
	*Loading Part and Timing Information* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Loading Part and Timing Information"
	_START:      ClassVar[str] = "Start Loading Part and Timing Information"
	_FINISH:     ClassVar[str] = "Finished Loading Part and Timing Information : "
	_DUPLICATES: ClassVar[bool] = False

	_part:   Nullable[str]  #: Part name of the device this design was synthesized for.

	def __init__(self, command: "Command") -> None:
		"""
		Initializes the section for loading the device information.

		:param command: Reference to the TCL command.
		"""
		super().__init__(command)

		self._part = None

	@readonly
	def Part(self) -> Nullable[str]:
		"""
		Read-only property to access the used device's part name.

		:returns: Part name of the device this design was synthesized for.
		"""
		return self._part

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._SectionStart(line)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith("Loading part: "):
				line._kind = LineKind.Normal
				self._part = line._message[14:].strip()
			elif line.StartsWith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			else:
				line._kind = LineKind.Verbose

			line = yield line

		nextLine = yield from self._SectionFinish(line)
		return nextLine


@export
class ApplySetPropertyXDCConstraints(Section):
	"""
	*Applying 'set_property' XDC Constraints* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Applying 'set_property' XDC Constraints"
	_START:      ClassVar[str] = "Start Applying 'set_property' XDC Constraints"
	_FINISH:     ClassVar[str] = "Finished applying 'set_property' XDC Constraints : "
	_DUPLICATES: ClassVar[bool] = False


@export
class RTLComponentStatistics(Section):
	"""
	*RTL Component Statistics* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "RTL Component Statistics"
	_START:      ClassVar[str] = "Start RTL Component Statistics"
	_FINISH:     ClassVar[str] = "Finished RTL Component Statistics"
	_DUPLICATES: ClassVar[bool] = False

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._SectionStart(line)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			else:
				line._kind = LineKind.Verbose

			line = yield line

		nextLine = yield from self._SectionFinish(line)
		return nextLine


@export
class RTLHierarchicalComponentStatistics(Section):
	"""
	*RTL Hierarchical Component Statistics* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "RTL Hierarchical Component Statistics"
	_START:      ClassVar[str] = "Start RTL Hierarchical Component Statistics"
	_FINISH:     ClassVar[str] = "Finished RTL Hierarchical Component Statistics"
	_DUPLICATES: ClassVar[bool] = False


@export
class PartResourceSummary(Section):
	"""
	*Part Resource Summary* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Part Resource Summary"
	_START:      ClassVar[str] = "Start Part Resource Summary"
	_FINISH:     ClassVar[str] = "Finished Part Resource Summary"
	_DUPLICATES: ClassVar[bool] = False


@export
class CrossBoundaryAndAreaOptimization(Section):
	"""
	*Cross Boundary and Area Optimization* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Cross Boundary and Area Optimization"
	_START:      ClassVar[str] = "Start Cross Boundary and Area Optimization"
	_FINISH:     ClassVar[str] = "Finished Cross Boundary and Area Optimization : "
	_DUPLICATES: ClassVar[bool] = False


@export
class ROM_RAM_DSP_SR_Retiming(Section):
	"""
	*ROM, RAM, DSP, Shift Register and Retiming Reporting* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "ROM, RAM, DSP, Shift Register and Retiming Reporting"
	_START:      ClassVar[str] = "Start ROM, RAM, DSP, Shift Register and Retiming Reporting"
	_FINISH:     ClassVar[str] = "Finished ROM, RAM, DSP, Shift Register and Retiming Reporting"
	_DUPLICATES: ClassVar[bool] = True


@export
class ApplyingXDCTimingConstraints(Section):
	"""
	*Applying XDC Timing Constraints* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Applying XDC Timing Constraints"
	_START:      ClassVar[str] = "Start Applying XDC Timing Constraints"
	_FINISH:     ClassVar[str] = "Finished Applying XDC Timing Constraints : "
	_DUPLICATES: ClassVar[bool] = False


@export
class TimingOptimization(Section):
	"""
	*Timing Optimization* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Timing Optimization"
	_START:      ClassVar[str] = "Start Timing Optimization"
	_FINISH:     ClassVar[str] = "Finished Timing Optimization : "
	_DUPLICATES: ClassVar[bool] = False


@export
class TechnologyMapping(Section):
	"""
	*Technology Mapping* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Technology Mapping"
	_START:      ClassVar[str] = "Start Technology Mapping"
	_FINISH:     ClassVar[str] = "Finished Technology Mapping : "
	_DUPLICATES: ClassVar[bool] = False


@export
class FlatteningBeforeIOInsertion(SubSection):
	"""
	*Flattening Before IO Insertion* subsection.

	Used by section :class:`IOInsertion`.
	"""
	_NAME:   ClassVar[str] = "Flattening Before IO Insertion"
	_START:  ClassVar[str] = "Start Flattening Before IO Insertion"
	_FINISH: ClassVar[str] = "Finished Flattening Before IO Insertion"
	_DUPLICATES: ClassVar[bool] = False


@export
class FinalNetlistCleanup(SubSection):
	"""
	*Final Netlist Cleanup* subsection.

	Used by section :class:`IOInsertion`.
	"""
	_NAME:   ClassVar[str] = "Final Netlist Cleanup"
	_START:  ClassVar[str] = "Start Final Netlist Cleanup"
	_FINISH: ClassVar[str] = "Finished Final Netlist Cleanup"
	_DUPLICATES: ClassVar[bool] = False


@export
class IOInsertion(SectionWithChildren):
	"""
	*IO Insertion* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "IO Insertion"
	_START:      ClassVar[str] = "Start IO Insertion"
	_FINISH:     ClassVar[str] = "Finished IO Insertion : "
	_DUPLICATES: ClassVar[bool] = False

	# TODO: generalize, use _PARSERS and move to SectionWithChildren
	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._SectionStart(line)

		while True:
			while True:
				if line._kind is LineKind.Empty:
					line = yield line
					continue
				elif line.StartsWith("----"):
					line._kind = LineKind.SubSectionStart | LineKind.SubSectionDelimiter
				elif line.StartsWith("Start "):
					if line == FlatteningBeforeIOInsertion._START:
						self._subsections[FlatteningBeforeIOInsertion] = (subsection := FlatteningBeforeIOInsertion(self))
						line = yield next(parser := subsection.Generator(line))
						break
					elif line == FinalNetlistCleanup._START:
						self._subsections[FinalNetlistCleanup] = (subsection := FinalNetlistCleanup(self))
						line = yield next(parser := subsection.Generator(line))
						break
				elif isinstance(line, VivadoMessage):
					self._AddMessage(line)
				elif line.StartsWith("Finished "):
					break
				else:
					line._kind |= LineKind.ProcessorError

				line = yield line

			if line.StartsWith(self._FINISH):
				break

			while True:
				if line.StartsWith(subsection._FINISH):
					line = yield parser.send(line)
					line = yield parser.send(line)

					subsection = None
					parser = None
					break

				line = parser.send(line)
				if isinstance(line, VivadoMessage):
					self._AddMessage(line)

				line = yield line

		nextLine = yield from self._SectionFinish(line, True)
		return nextLine


@export
class RenamingGeneratedInstances(Section):
	"""
	*Renaming Generated Instances* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Renaming Generated Instances"
	_START:      ClassVar[str] = "Start Renaming Generated Instances"
	_FINISH:     ClassVar[str] = "Finished Renaming Generated Instances : "
	_DUPLICATES: ClassVar[bool] = False


@export
class RebuildingUserHierarchy(Section):
	"""
	*Rebuilding User Hierarchy* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Rebuilding User Hierarchy"
	_START:      ClassVar[str] = "Start Rebuilding User Hierarchy"
	_FINISH:     ClassVar[str] = "Finished Rebuilding User Hierarchy : "
	_DUPLICATES: ClassVar[bool] = False


@export
class RenamingGeneratedPorts(Section):
	"""
	*Renaming Generated Ports* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Renaming Generated Ports"
	_START:      ClassVar[str] = "Start Renaming Generated Ports"
	_FINISH:     ClassVar[str] = "Finished Renaming Generated Ports : "
	_DUPLICATES: ClassVar[bool] = False


@export
class RenamingGeneratedNets(Section):
	"""
	*Renaming Generated Nets* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Renaming Generated Nets"
	_START:      ClassVar[str] = "Start Renaming Generated Nets"
	_FINISH:     ClassVar[str] = "Finished Renaming Generated Nets : "
	_DUPLICATES: ClassVar[bool] = False


@export
class WritingSynthesisReport(Section):
	"""
	*Writing Synthesis Report* section.

	Used by Vivado command :class:`~pyEDAA.OutputFilter.Xilinx.Commands.SynthesizeDesign`.
	"""
	_NAME:       ClassVar[str] = "Writing Synthesis Report"
	_START:      ClassVar[str] = "Start Writing Synthesis Report"
	_FINISH:     ClassVar[str] = "Finished Writing Synthesis Report : "
	_DUPLICATES: ClassVar[bool] = False

	_blackboxes: Dict[str, int]  #: Blackbox statistics: blackbox name -> count
	_cells:      Dict[str, int]  #: Cell statistics: cell name -> count

	def __init__(self, command: "Command") -> None:
		super().__init__(command)

		self._blackboxes = {}
		self._cells =      {}

	@readonly
	def Cells(self) -> Dict[str, int]:
		"""
		Read-only property to access the dictionary of synthesized cell statistics.

		:returns: The dictionary of used cell statistics.
		"""
		return self._cells

	@readonly
	def Blackboxes(self) -> Dict[str, int]:
		"""
		Read-only property to access the dictionary of found blackbox statistics.

		:returns: The dictionary of found blackbox statistics.
		"""
		return self._blackboxes

	def _BlackboxesGenerator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		"""
		A parser parsing the blackboxes table.

		:param line: First line to process.
		:returns:    A generator to process multiple lines containing a table of blackboxes.

		.. rubric:: Example

		.. code-block::

		   Report BlackBoxes:
		   +------+----------------------------------+----------+
		   |      |BlackBox name                     |Instances |
		   +------+----------------------------------+----------+
		   |1     |name                              |         1|
		   |[...] |[...]                             |     [...]|
		   +------+----------------------------------+----------+
		"""
		if line.StartsWith("+-"):
			line._kind = LineKind.TableFrame
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		if line.StartsWith("| "):
			line._kind = LineKind.TableHeader
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		if line.StartsWith("+-"):
			line._kind = LineKind.TableFrame
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		while True:
			if line.StartsWith("|"):
				line._kind = LineKind.TableRow

				columns = line._message.strip("|").split("|")
				self._blackboxes[columns[1].strip()] = int(columns[2].strip())
			elif line.StartsWith("+-"):
				line._kind = LineKind.TableFrame
				break
			else:
				line._kind = LineKind.ProcessorError

			line = yield line

		nextLine = yield line
		return nextLine

	def _CellGenerator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		"""
		A parser parsing the cell statistic table.

		:param line: First line to process.
		:returns:    A generator to process multiple lines containing a table of cell statistics.

		.. rubric:: Example

		.. code-block::

		   Report Cell Usage:
		   +------+----------------------------------+------+
		   |      |Cell                              |Count |
		   +------+----------------------------------+------+
		   |1     |name                              |     1|
		   |[...] |[...]                             | [...]|
		   +------+----------------------------------+------+
		"""
		if line.StartsWith("+-"):
			line._kind = LineKind.TableFrame
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		if line.StartsWith("| "):
			line._kind = LineKind.TableHeader
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		if line.StartsWith("+-"):
			line._kind = LineKind.TableFrame
		else:
			line._kind = LineKind.ProcessorError

		line = yield line
		while True:
			if line.StartsWith("|"):
				line._kind = LineKind.TableRow

				columns = line._message.strip("|").split("|")
				self._cells[columns[1].strip()] = int(columns[2].strip())
			elif line.StartsWith("+-"):
				line._kind = LineKind.TableFrame
				break
			else:
				line._kind = LineKind.ProcessorError

			line = yield line

		nextLine = yield line
		return nextLine

	def Generator(self, line: VivadoLine) -> Generator[VivadoLine, VivadoLine, VivadoLine]:
		line = yield from self._SectionStart(line)

		while True:
			if line._kind is LineKind.Empty:
				line = yield line
				continue
			elif line.StartsWith("Report BlackBoxes:"):
				line._kind = LineKind.ParagraphHeadline
				line = yield line
				line = yield from self._BlackboxesGenerator(line)
			elif line.StartsWith("Report Cell Usage:"):
				line._kind = LineKind.ParagraphHeadline
				line = yield line
				line = yield from self._CellGenerator(line)
			elif line.StartsWith("----"):
				line._kind = LineKind.SectionEnd | LineKind.SectionDelimiter
				break
			elif isinstance(line, VivadoMessage):
				self._AddMessage(line)
			else:
				line._kind = LineKind.Verbose
				line = yield line

		nextLine = yield from self._SectionFinish(line)
		return nextLine
