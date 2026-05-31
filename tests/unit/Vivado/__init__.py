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
"""Unit tests for Vivado messages."""
from unittest  import TestCase as TestCase

from pyEDAA.OutputFilter.Xilinx import LineKind, VivadoInfoMessage, VivadoIrregularInfoMessage, VivadoStuntedInfoMessage
from pyEDAA.OutputFilter.Xilinx import VivadoWarningMessage, VivadoStuntedWarningMessage
from pyEDAA.OutputFilter.Xilinx import VivadoCriticalWarningMessage, VivadoErrorMessage

if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_Info(self) -> None:
		message = VivadoInfoMessage(1, LineKind.InfoMessage, "some message", "synth", 8, 25)

		self.assertEqual(1, message.LineNumber)
		self.assertEqual("synth", message.ToolName)
		self.assertEqual(8, message.ToolID)
		self.assertEqual(25, message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual("INFO: [synth 8-25] some message", str(message))

	def test_IrregularInfo(self) -> None:
		message = VivadoIrregularInfoMessage(1, LineKind.InfoMessage, "some message", "runtcl", messageKindID=4)

		self.assertEqual(1, message.LineNumber)
		self.assertEqual("runtcl", message.ToolName)
		self.assertIsNone(message.ToolID)
		self.assertEqual(4, message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual("INFO: [runtcl-4] some message", str(message))

	def test_StuntedInfo(self) -> None:
		message = VivadoStuntedInfoMessage(1, LineKind.InfoMessage, "some message")

		self.assertEqual(1, message.LineNumber)
		self.assertIsNone(message.ToolName)
		self.assertIsNone(message.ToolID)
		self.assertIsNone(message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual("INFO: some message", str(message))

	def test_Warning(self) -> None:
		message = VivadoWarningMessage(1, LineKind.WarningMessage, "some message", "synth", 8, 25)

		self.assertEqual(1, message.LineNumber)
		self.assertEqual("synth", message.ToolName)
		self.assertEqual(8, message.ToolID)
		self.assertEqual(25, message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual("WARNING: [synth 8-25] some message", str(message))

	def test_StuntedWarning(self) -> None:
		message = VivadoStuntedWarningMessage(1, LineKind.WarningMessage, "some message")

		self.assertEqual(1, message.LineNumber)
		self.assertIsNone(message.ToolName)
		self.assertIsNone(message.ToolID)
		self.assertIsNone(message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual("WARNING: some message", str(message))

	def test_CriticalWarning(self) -> None:
		message = VivadoCriticalWarningMessage(1, LineKind.CriticalWarningMessage, "some message", "synth", 8, 25)

		self.assertEqual(1, message.LineNumber)
		self.assertEqual("synth", message.ToolName)
		self.assertEqual(8, message.ToolID)
		self.assertEqual(25, message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual("CRITICAL WARNING: [synth 8-25] some message", str(message))

	def test_Error(self) -> None:
		message = VivadoErrorMessage(1, LineKind.ErrorMessage, "some message", "synth", 8, 25)

		self.assertEqual(1, message.LineNumber)
		self.assertEqual("synth", message.ToolName)
		self.assertEqual(8, message.ToolID)
		self.assertEqual(25, message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual("ERROR: [synth 8-25] some message", str(message))


class Parsing(TestCase):
	def test_Info(self) -> None:
		messageText = "INFO: [synth 8-25] some message"
		message = VivadoInfoMessage.Parse(1, messageText)

		self.assertEqual(1, message.LineNumber)
		self.assertEqual("synth", message.ToolName)
		self.assertEqual(8, message.ToolID)
		self.assertEqual(25, message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual(messageText, str(message))

	# todo: there are more info formats
	def test_Info_IrregularFormat(self) -> None:
		messageText = "INFO: [runctrl-25] some message"
		if (message := VivadoInfoMessage.Parse(1, messageText)) is None:
			message = VivadoIrregularInfoMessage.Parse(1, messageText)

		self.assertEqual(1, message.LineNumber)
		self.assertEqual("runctrl", message.ToolName)
		self.assertIsNone(message.ToolID)
		self.assertEqual(25, message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual(messageText, str(message))

	def test_Info_WrongFormat(self) -> None:
		messageText = "FOOBAR: [synth 8-25] some message"
		message = VivadoInfoMessage.Parse(1, messageText)

		self.assertIsNone(message)

	# todo: there are more warning formats
	def test_Warning(self) -> None:
		messageText = "WARNING: [synth 8-25] some message"
		message = VivadoWarningMessage.Parse(1, messageText)

		self.assertEqual(1, message.LineNumber)
		self.assertEqual("synth", message.ToolName)
		self.assertEqual(8, message.ToolID)
		self.assertEqual(25, message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual(messageText, str(message))

	def test_Warning_AbnormalFormat(self) -> None:
		messageText = "WARNING: some message"
		if (message := VivadoInfoMessage.Parse(1, messageText)) is None:
			message = VivadoStuntedWarningMessage.Parse(1, messageText)

		self.assertEqual(1, message.LineNumber)
		self.assertIsNone(message.ToolName)
		self.assertIsNone(message.ToolID)
		self.assertIsNone(message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual(messageText, str(message))

	def test_Warning_WrongFormat(self) -> None:
		messageText = "FOOBAR: [synth 8-25] some message"
		message = VivadoWarningMessage.Parse(1, messageText)

		self.assertIsNone(message)

	def test_CriticalWarning(self) -> None:
		messageText = "CRITICAL WARNING: [synth 8-25] some message"
		message = VivadoCriticalWarningMessage.Parse(1, messageText)

		self.assertEqual(1, message.LineNumber)
		self.assertEqual("synth", message.ToolName)
		self.assertEqual(8, message.ToolID)
		self.assertEqual(25, message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual(messageText, str(message))

	def test_CriticalWarning_WrongFormat(self) -> None:
		messageText = "FOOBAR: [synth 8-25] some message"
		message = VivadoCriticalWarningMessage.Parse(1, messageText)

		self.assertIsNone(message)

	def test_Error(self) -> None:
		messageText = "ERROR: [synth 8-25] some message"
		message = VivadoErrorMessage.Parse(1, messageText)

		self.assertEqual(1, message.LineNumber)
		self.assertEqual("synth", message.ToolName)
		self.assertEqual(8, message.ToolID)
		self.assertEqual(25, message.MessageKindID)
		self.assertEqual("some message", message.Message)

		self.assertEqual(messageText, str(message))

	def test_Error_WrongFormat(self) -> None:
		messageText = "FOOBAR: [synth 8-25] some message"
		message = VivadoErrorMessage.Parse(1, messageText)

		self.assertIsNone(message)
