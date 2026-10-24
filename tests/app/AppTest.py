# ==================================================================================================================== #
#             _____           _ _                  _        _   _                                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _     / \   ___| |_(_) ___  _ __  ___                                      #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |   / _ \ / __| __| |/ _ \| '_ \/ __|                                     #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_ / ___ \ (__| |_| | (_) | | | \__ \                                     #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_/   \_\___|\__|_|\___/|_| |_|___/                                     #
# |_|    |___/                          |___/                                                                          #
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
from pathlib import Path
from typing  import ClassVar

from pyTooling.Testing import ApplicationTestcase, stripANSIColorCodes


def escape(input: str) -> str:
	return input.replace("{", "{{").replace("}", "}}")


class Testcase(ApplicationTestcase):
	"""Base-class naming the program under test; pyTooling resolves the console script and runs it."""

	_CONSOLE_SCRIPT:  ClassVar[str] = "pyedaa-outputfilter"
	_RUNNABLE_MODULE: ClassVar[str] = "pyEDAA.OutputFilter.CLI"


class Commands(Testcase):
	def test_NoArguments(self) -> None:
		print()
		completedProcess = self.RunEntrypoint()
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_WrongCommand(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("dummy")
		print(completedProcess.stdout)
		print("STDERR: " + "-" * 112)
		print(completedProcess.stderr)

		self.assertExitCode(completedProcess, 1)
		self.assertEqual("", completedProcess.stdout)

	def test_HelpCommand(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("help")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_ShortHelpOption(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("-h")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_LongHelpOption(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("--help")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_VersionCommand(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("version")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_HelpCommand_VersionCommand(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("help", "version")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_LongHelpOption_VersionCommand(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("--help", "version")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_VivadoCommand(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("vivado")
		print(completedProcess.stdout)
		print("STDERR: " + "-" * 112)
		print(completedProcess.stderr)

		stderr = stripANSIColorCodes(completedProcess.stderr)
		self.assertExitCode(completedProcess, 2)
		self.assertTrue(stderr.startswith("[ERROR]"), f"STDERR doesn't start with '[ERROR]': {stderr[:80]!r}")


class Vivado(Testcase):
	def test_Help(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("help", "vivado")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_StdIn(self) -> None:
		print()
		with Path("tests/data/Stopwatch/toplevel.vds").open("r") as file:
			content = file.read()

		completedProcess = self.RunEntrypoint("--quiet", "vivado", "--stdin", stdInput=content)
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_SynthesisLogFile(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("--quiet", "vivado", "--file=tests/data/Stopwatch/toplevel.vds")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_ImplementationLogFile(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("--quiet", "vivado", "--file=tests/data/Stopwatch/toplevel.vdi")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)


class Issues(Testcase):
	def test_Issue_87_Log(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("-q", "vivado", "--file=tests/data/Issues/87/vivado.log")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		self.assertEqual("", completedProcess.stderr)

	def test_Issue_87_Interface(self) -> None:
		print()
		completedProcess = self.RunEntrypoint("--quiet", "vivado", "--file=tests/data/Issues/87/en_axi_rb_interface.log")
		print(completedProcess.stdout)

		self.assertExitCode(completedProcess, 0)
		# self.assertEqual("", completedProcess.stderr)
