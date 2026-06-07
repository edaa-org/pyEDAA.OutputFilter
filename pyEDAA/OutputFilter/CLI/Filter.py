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
from itertools import tee
from typing    import Optional as Nullable, List, Generator, Tuple

from pyTooling.Decorators                  import export

from pyEDAA.OutputFilter.CLI.Configuration import Rule
from pyEDAA.OutputFilter.Xilinx            import VivadoLine


@export
def preprocessing(gen: Generator[VivadoLine, None, None], rules: Nullable[List[Rule]]) -> Generator[VivadoLine, None, None]:
	if rules is None:
		return gen

	def filter(gen: Generator[VivadoLine, None, None]) -> Generator[VivadoLine, None, None]:
		for line in gen:
			for rule in rules:
				if rule.Match(line):
					rule.Process(line)

			yield line

	return filter(gen)


@export
def doublyLinkedList(gen: Generator[VivadoLine, None, None]) -> Generator[VivadoLine, None, None]:
	previousLine: VivadoLine = None
	for line in gen:
		previousLine = (newLine := line.FromItem(line, previousLine))
		yield newLine


@export
def mirror(gen: Generator[VivadoLine, None, None], count: int) -> Tuple[Generator[VivadoLine, None, None], ...]:
	if count == 1:
		return gen,
	else:
		return tuple(doublyLinkedList(source) for source in tee(gen, count))


@export
def postprocessing(gen: Generator[VivadoLine, None, None], rules: Nullable[List[Rule]]) -> Generator[VivadoLine, None, None]:
	if rules is None:
		return gen

	def filter(gen: Generator[VivadoLine, None, None]) -> Generator[VivadoLine, None, None]:
		try:
			for line in gen:
				for rule in rules:
					if rule.Match(line):
						rule.Process(line)

				yield line
		except RuntimeError:
			pass

	return filter(gen)
