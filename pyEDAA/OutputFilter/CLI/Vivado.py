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
from argparse import Namespace
from pathlib  import Path
from sys      import stdin
from typing   import NoReturn

from pyTooling.Decorators                     import readonly
from pyTooling.MetaClasses                    import ExtendedType
from pyTooling.Common                         import count
from pyTooling.Attributes.ArgParse            import CommandHandler
from pyTooling.Attributes.ArgParse.Flag       import LongFlag
from pyTooling.Attributes.ArgParse.ValuedFlag import LongValuedFlag
from pyTooling.Stopwatch                      import Stopwatch

from pyEDAA.OutputFilter.Xilinx.Synthesis import Processor, Preamble, WritingSynthesisReport


class Proto(metaclass=ExtendedType, mixin=True):
	@readonly
	def Verbose(self) -> bool:
		...

	@readonly
	def Width(self) -> int:
		...

	def _PrintHeadline(self):
		...

	def WriteDebug(self, a: str, appendLinebreak: bool = True):
		...

	def WriteVerbose(self, a: str, appendLinebreak: bool = True):
		...

	def WriteNormal(self, a: str, appendLinebreak: bool = True):
		...

	def WriteWarning(self, a: str, appendLinebreak: bool = True):
		...

	def WriteCritical(self, a: str, appendLinebreak: bool = True):
		...

	def WriteError(self, a: str, appendLinebreak: bool = True):
		...

	def WriteFatal(self, a: str, appendLinebreak: bool = True, immediateExit: bool = True):
		...

	def Exit(self, i: int = 0) -> NoReturn:
		...


class VivadoHandlers(Proto, metaclass=ExtendedType, mixin=True):
	@CommandHandler("vivado-synth", help="Parse AMD/Xilinx Vivado Synthesis log files.", description="Parse AMD/Xilinx Vivado Synthesis log files.")
	@LongValuedFlag("--file", dest="logfile", metaName='Synthesis Log', help="Synthesis log file (*.vds).")
	@LongFlag("--info", dest="info", help="Print info messages.")
	@LongFlag("--warning", dest="warning", help="Print warning messages.")
	@LongFlag("--critical", dest="critical", help="Print critical warning messages.")
	@LongFlag("--error", dest="error", help="Print error messages.")
	@LongFlag("--influxdb", dest="influxdb", help="Write statistics as InfluxDB line protocol file (*.line).")
	# @LongValuedFlag("--file", dest="logfile", metaName='Synthesis Log', help="Synthesis log file (*.vds).")
	def HandleVivadoSynthesis(self, args: Namespace) -> None:
		"""Handle program calls with command ``vivado-synth``."""
		self._PrintHeadline()

		returnCode = 0
		if args.logfile is None:
			self.WriteError(f"Option '--file=<VDS file>' is missing.")
			returnCode = 3

		logfile = Path(args.logfile)
		if not logfile.exists():
			self.WriteError(f"Vivado synthesis log file '{logfile}' doesn't exist.")
			returnCode = 4

		if returnCode != 0:
			self.Exit(returnCode)

		processor = Processor(logfile)
		processor.Parse()

		if args.info:
			self.WriteNormal(f"INFO messages: {len(processor.InfoMessages)}")
			for message in processor.InfoMessages:
				self.WriteNormal(f"  {message}")
		if args.warning:
			self.WriteNormal(f"WARNING messages: {len(processor.WarningMessages)}")
			for message in processor.WarningMessages:
				self.WriteNormal(f"  {message}")
		if args.critical:
			self.WriteNormal(f"CRITICAL WARNING: messages {len(processor.CriticalWarningMessages)}")
			for message in processor.CriticalWarningMessages:
				self.WriteNormal(f"  {message}")
		if args.error:
			self.WriteNormal(f"ERROR messages: {len(processor.ErrorMessages)}")
			for message in processor.ErrorMessages:
				self.WriteNormal(f"  {message}")

		if args.influxdb:
			influxString  =  "vivado_synthesis_overview"
			influxString += f",version={processor[Preamble].ToolVersion}"
			influxString += f",branch=main"
			influxString += f",design=Stopwatch"
			influxString += " "
			influxString += f"processing_duration={processor.Duration:.3f}"
			influxString += f",synthesis_duration={processor[WritingSynthesisReport].Duration:.1f}"
			influxString += f",info_count={len(processor.InfoMessages)}u"
			influxString += f",warning_count={len(processor.WarningMessages)}u"
			influxString += f",critical_count={len(processor.CriticalWarningMessages)}u"
			influxString += f",error_count={len(processor.ErrorMessages)}u"
			influxString += f",blackbox_count={len(processor[WritingSynthesisReport].Blackboxes)}u"
			influxString +=  "\n"
			influxString +=  "vivado_synthesis_cells"
			influxString += f",version={processor[Preamble].ToolVersion}"
			influxString += f",branch=main"
			influxString += f",design=Stopwatch"
			influxString += " "
			influxString += ",".join(f"{cellName}={cellCount}" for cellName, cellCount in processor[WritingSynthesisReport].Cells.items() if not cellName.endswith("_bbox"))

			self.WriteNormal(influxString)

		self.WriteNormal("Summary:")
		self.WriteNormal(f"  Processing duration: {processor.Duration:.3f} s")
		self.WriteNormal(f"  Info: {len(processor.InfoMessages)}  Warning: {len(processor.WarningMessages)}  Critical Warning: {len(processor.CriticalWarningMessages)}  Error: {len(processor.ErrorMessages)}")

		self.ExitOnPreviousErrors()

	@CommandHandler("vivado-impl", help="Parse AMD/Xilinx Vivado Implementation log files.", description="Parse AMD/Xilinx Vivado Implementation log files.")
	@LongValuedFlag("--file", dest="logfile", metaName='Implementation Log', help="Implementation log file (*.vdi).")
	@LongFlag("--info", dest="info", help="Print info messages.")
	@LongFlag("--warning", dest="warning", help="Print warning messages.")
	@LongFlag("--critical", dest="critical", help="Print critical warning messages.")
	@LongFlag("--error", dest="error", help="Print error messages.")
	def HandleVivadoImplementation(self, args: Namespace) -> None:
		"""Handle program calls with command ``vivado-impl``."""
		self._PrintHeadline()
