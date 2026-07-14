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
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2014-2016 Technische Universitaet Dresden - Germany, Chair of VLSI-Design, Diagnostics and Architecture    #
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
"""An abstraction layer of EDA tool output filters."""
__author__ =            "Patrick Lehmann"
__email__ =             "Paebbels@gmail.com"
__copyright__ =         "2014-2026, Patrick Lehmann"
__license__ =           "Apache License, Version 2.0"
__version__ =           "0.14.2"
__keywords__ =          ["cli", "abstraction layer", "eda", "filter", "classification"]
__project_url__ =       "https://github.com/edaa-org/pyEDAA.OutputFilter"
__documentation_url__ = "https://edaa-org.github.io/pyEDAA.OutputFilter"
__issue_tracker_url__ = "https://GitHub.com/edaa-org/pyEDAA.OutputFilter/issues"

from datetime              import datetime
from enum                  import Flag
from typing                import Any, Generator, Callable, Tuple, Union, Optional as Nullable, Generic, TypeVar

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import ExceptionBase
from pyTooling.MetaClasses import ExtendedType


@export
class OutputFilterException(ExceptionBase):
	"""Base-class for all pyEDAA.OutputFilter specific exceptions."""


LineClassification =   TypeVar("LineClassification",   bound=Flag)
LineProcessingAction = TypeVar("LineProcessingAction", bound=Flag)

@export
class Line(Generic[LineClassification, LineProcessingAction], metaclass=ExtendedType, slots=True):
	"""
	This class represents any line in a log file.

	A line has a line number (:attr:`_lineNumber`), a message (:attr:`__message`) and a message kind (:attr:`__kind`). In
	addition, all line objects in a log file form a doubly
	linked list.
	"""
	_lineNumber:    int
	_timestamp:     Nullable[datetime]
	_document:      "Document"
	_kind:          LineClassification
	_action:        LineProcessingAction
	_message:       str
	_previousLine:  Nullable["Line"]
	_nextLine:      Nullable["Line"]

	def __init__(
		self,
		lineNumber:   int,
		kind:         LineClassification,
		action:       LineProcessingAction,
		message:      str,
		previousLine: Nullable["Line"] = None
	) -> None:
		self._lineNumber =   lineNumber
		self._kind =         kind
		self._action =       action
		self._message =      message
		self._previousLine = previousLine
		self._nextLine =     None

		if previousLine is not None:
			previousLine._nextLine = self

		if not isinstance(message, str):
			pass

	@readonly
	def LineNumber(self) -> int:
		return self._lineNumber

	@readonly
	def Kind(self) -> LineClassification:
		return self._kind

	@readonly
	def Action(self) -> LineProcessingAction:
		return self._action

	@readonly
	def Message(self) -> str:
		return self._message

	@property
	def PreviousLine(self) -> Nullable["Line"]:
		return self._previousLine

	@PreviousLine.setter
	def PreviousLine(self, line: "Line") -> None:
		self._previousLine = line
		if line is not None:
			line._nextLine = self

	@readonly
	def NextLine(self) -> Nullable["Line"]:
		return self._nextLine

	def StartsWith(self, prefix: Union[str, Tuple[str, ...]]):
		return self._message.startswith(prefix)

	def Partition(self, separator: str) -> Tuple[str, str, str]:
		return self._message.partition(separator)

	def GetIterator(
		self,
		stopPredicate: Nullable[Callable[["Line"], bool]] = None,
		*,
		reverse:   bool = False,
		inclusive: bool = True,
		maxLines:  Nullable[int] = None,
	) -> Generator["Line", None, None]:
		"""
		Iterate consecutive lines starting from next line towards the end of the log.

		If the order is reversed, iterate starting at the previous line towards the beginning of the log. The iteration ends
		either at the bounds of the log, by specifying a stop predicate or a maximum number of lines to return. When stopped
		this line is usually included in the iteration, but can be excluded.

		:param stopPredicate: Optional, a callable receiving a :class:`Line` and returning ``True`` when iteration should
		                      stop at that line.
		:param reverse:       Optional, reverse the iteration from previous line to the beginning of the log.
		:param inclusive:     Optional, when ``True`` the line where ``stopPredicate`` or ``maxLines`` triggers, is
		                      included in the iteration, otherwise it's excluded.
		:param maxLines:      Optional, maximum number of lines to yield.
 		:returns:             A generator yielding :class:`Line` in the requested direction, stopping at the log boundary,
 		                      the predicate match, or the line limit — whichever comes first.
		:raises TypeError:    When ``stopPredicate`` is not callable.
		:raises ValueError:   When ``maxLines`` is not a positive integer.
		"""
		if stopPredicate is not None and not callable(stopPredicate):
			ex = TypeError("Parameter 'stopPredicate' is not a callable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(stopPredicate)}'.")
			raise ex
		if not isinstance(reverse, bool):
			ex = TypeError("Parameter 'reverse' is not a boolean.")
			ex.add_note(f"Got type '{getFullyQualifiedName(reverse)}'.")
			raise ex
		if not isinstance(inclusive, bool):
			ex = TypeError("Parameter 'inclusive' is not a boolean.")
			ex.add_note(f"Got type '{getFullyQualifiedName(inclusive)}'.")
			raise ex
		if maxLines is not None:
			if not isinstance(maxLines, int):
				ex = TypeError("Parameter 'maxLines' is not a integer.")
				ex.add_note(f"Got type '{getFullyQualifiedName(maxLines)}'.")
				raise ex
			elif maxLines <= 0:
				ex = ValueError("Parameter 'maxLines' must be a positive integer.")
				ex.add_note(f"Got {maxLines!r}.")
				raise ex

		current = self._previousLine if reverse else self._nextLine

		if maxLines is None:
			if stopPredicate is None:
				if reverse:
					while current is not None:
						yield current
						current = current._previousLine
				else:
					while current is not None:
						yield current
						current = current._nextLine
			else:
				if reverse:
					while current is not None:
						if stopPredicate(current):
							if inclusive:
								yield current
							return
						yield current
						current = current._previousLine
				else:
					while current is not None:
						if stopPredicate(current):
							if inclusive:
								yield current
							return
						yield current
						current = current._nextLine

		elif stopPredicate is None:
			remaining = maxLines
			if reverse:
				while current is not None and remaining > 0:
					yield current
					current = current._previousLine
					remaining -= 1
			else:
				while current is not None and remaining > 0:
					yield current
					current = current._nextLine
					remaining -= 1

		else:
			remaining = maxLines
			if reverse:
				while current is not None and remaining > 0:
					if stopPredicate(current):
						if inclusive:
							yield current
						return
					yield current
					current = current._previousLine
					remaining -= 1
			else:
				while current is not None and remaining > 0:
					if stopPredicate(current):
						if inclusive:
							yield current
						return
					yield current
					current = current._nextLine
					remaining -= 1

	def __getitem__(self, item: slice) -> str:
		return self._message[item]

	def __eq__(self, other: Any):
		return self._message == other

	def __ne__(self, other: Any):
		return self._message != other

	def __str__(self) -> str:
		return self._message

	def __repr__(self) -> str:
		return f"{self._lineNumber}: {self._message}"


@export
class InfoMessage(metaclass=ExtendedType, mixin=True):
	pass


@export
class WarningMessage(metaclass=ExtendedType, mixin=True):
	pass


@export
class CriticalWarningMessage(metaclass=ExtendedType, mixin=True):
	pass


@export
class ErrorMessage(metaclass=ExtendedType, mixin=True):
	pass
