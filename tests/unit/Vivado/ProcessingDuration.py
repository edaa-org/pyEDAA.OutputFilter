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
# Copyright 2026-2026 Electronic Design Automation Abstraction (EDA²)                                                  #
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
"""Unit tests for the processing duration of Vivado log output processors."""
from datetime                   import datetime, timedelta
from pathlib                    import Path
from time                       import sleep
from typing                     import ClassVar

from pyTooling.Testing          import Testcase

from pyEDAA.OutputFilter.Xilinx import Document, Processor, timestampIterator

if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ProcessingDuration(Testcase):
	_LOGFILE: ClassVar[Path] = Path("tests/data/Stopwatch/toplevel.vds")

	def test_NotStarted(self) -> None:
		processor = Processor()

		self.assertEqual(timedelta(), processor.ProcessingDuration)

	def test_Processing(self) -> None:
		processor = Processor()

		with self._LOGFILE.open("r", encoding="utf-8") as file:
			lines = processor.LineClassification(timestampIterator(file, datetime.now()))
			for _ in range(10):
				next(lines)

			first = processor.ProcessingDuration
			sleep(0.01)
			second = processor.ProcessingDuration

			self.assertGreater(first, timedelta())
			self.assertGreaterEqual(second - first, timedelta(seconds=0.01))

			for _ in lines:
				pass

		final = processor.ProcessingDuration
		sleep(0.01)

		self.assertGreater(final, second)
		self.assertEqual(final, processor.ProcessingDuration)

	def test_Parsed(self) -> None:
		document = Document(self._LOGFILE)
		document.Parse()

		final = document.ProcessingDuration
		sleep(0.01)

		self.assertGreater(final, timedelta())
		self.assertEqual(final, document.ProcessingDuration)
