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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from pathlib            import Path
from re                 import compile as re_compile
from shutil             import which
from subprocess         import CompletedProcess, run as subprocess_run
from sys                import executable as PYTHON_EXECUTABLE
from typing             import ClassVar, Optional as Nullable
from unittest           import TestCase

RUNABLE_MODULE: ClassVar[str] = "pyEDAA.OutputFilter.CLI"
CONSOLE_SCRIPT: ClassVar[str] = "pyedaa-outputfilter"

class Testcase(TestCase):
	"""
	Shared base class: resolves the installed console_scripts executable once per test class and provides a
	subprocess-invocation helper.
	"""

	_executable: str

	@classmethod
	def setUpClass(cls) -> None:
		if (resolved := which(CONSOLE_SCRIPT)) is None:
			raise RuntimeError(
				f"'{CONSOLE_SCRIPT}' not found on PATH. Verify the wheel was installed in this environment and that setup.py's "
				f"entry_points {{'console_scripts': ['{CONSOLE_SCRIPT}={RUNABLE_MODULE}:main']}} was picked up correctly."
			)
		print(f"Found {CONSOLE_SCRIPT} at '{resolved}'.")
		cls._executable = resolved

	def RunEntrypoint(
		self,
		*arguments:       str,
		timeout:          float = 10.0,
		stdInput:         Nullable[str] = None,
		environment:      Nullable[dict[str, str]] = None,
		workingDirectory: Nullable[Path] = None,
	) -> CompletedProcess:
		return subprocess_run(
			[self._executable, *arguments],
			capture_output=True,
			text=True,
			timeout=timeout,
			input=stdInput,
			env=environment,
			cwd=workingDirectory
		)

	def RunModule(
		self,
		*arguments:       str,
		timeout:          float = 10.0,
		stdInput:         Nullable[str] = None,
		environment:      Nullable[dict[str, str]] = None,
		workingDirectory: Nullable[Path] = None,
	) -> CompletedProcess:
		"""
		Invokes `python -m myPackage.CLI` directly, bypassing the console_scripts shim. Use to isolate whether a failure
		originates in the entry-point wiring vs. the CLI logic itself.
		"""
		return subprocess_run(
			[PYTHON_EXECUTABLE, "-m", RUNABLE_MODULE, *arguments],
			capture_output=True,
			text=True,
			timeout=timeout,
			input=stdInput,
			env=environment,
			cwd=workingDirectory
		)

	def assertExitCode(self, result: CompletedProcess, expected: int) -> None:
		self.assertEqual(
			expected,
			result.returncode,
			msg=(
				f"args={result.args!r}\n"
				f"--- stdout ---\n{result.stdout}\n"
				f"--- stderr ---\n{result.stderr}"
			),
		)




_ANSI_COLOR_CODES = re_compile(r"\x1B\[[0-9;]*m")

def stripANSIColorCodes(text: str) -> str:
	return _ANSI_COLOR_CODES.sub('', text)

def escape(input: str) -> str:
	return input.replace("{", "{{").replace("}", "}}")


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
		self.assertStartsWith(stderr, "[ERROR]")
