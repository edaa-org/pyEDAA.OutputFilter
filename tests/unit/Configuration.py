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
"""Unit tests for the configuration of the Vivado output filter."""
from textwrap                              import dedent

from pyTooling.Warning                     import WarningCollector
from ruamel.yaml                           import YAML
from pyTooling.Testing                     import Testcase

from pyEDAA.OutputFilter.CLI.Configuration import Action, Configuration, ConfigurationWarning, Vivado


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ToolSection(Testcase):
	def test_NotADictionary_String(self) -> None:
		"""A tool section, which is a string, is reported once and not parsed further."""
		config = YAML().load(dedent("""\
			vivado: invalid
			"""))

		vivado = Vivado(Configuration())
		with WarningCollector() as warnings:
			vivado.Parse(config, "vivado", "tools")

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], ConfigurationWarning)
		self.assertEqual("tools.vivado: Is not a dictionary.", str(warnings[0]))

	def test_NotADictionary_Integer(self) -> None:
		"""A tool section, which is an integer, is reported once and not parsed further."""
		config = YAML().load(dedent("""\
			vivado: 5
			"""))

		vivado = Vivado(Configuration())
		with WarningCollector() as warnings:
			vivado.Parse(config, "vivado", "tools")

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], ConfigurationWarning)
		self.assertEqual("tools.vivado: Is not a dictionary.", str(warnings[0]))


class RuleSetAction(Testcase):
	def test_Valid(self) -> None:
		vivado = Vivado(Configuration())
		with WarningCollector() as warnings:
			action = vivado._ParseRuleSetAction("remove")

		self.assertIs(Action.Remove, action)
		self.assertEqual(0, len(warnings))

	def test_NotAString(self) -> None:
		"""An action, which is not a string, is reported once and falls back to the default action."""
		vivado = Vivado(Configuration())
		with WarningCollector() as warnings:
			action = vivado._ParseRuleSetAction(5)

		self.assertIs(Action.Default, action)
		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], ConfigurationWarning)
		self.assertEqual("tools.vivado.rule-sets.<ruleset>.<rule>.action: Unsupported value '5'.", str(warnings[0]))

	def test_UnknownValue(self) -> None:
		"""An unknown action is reported and falls back to the default action."""
		vivado = Vivado(Configuration())
		with WarningCollector() as warnings:
			action = vivado._ParseRuleSetAction("delete")

		self.assertIs(Action.Default, action)
		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], ConfigurationWarning)
		self.assertEqual("tools.vivado.rule-sets.<ruleset>.<rule>.action: Unknown value 'delete'.", str(warnings[0]))
