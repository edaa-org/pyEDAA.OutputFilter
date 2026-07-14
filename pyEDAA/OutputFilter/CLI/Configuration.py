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
from enum     import StrEnum
from pathlib  import Path
from re       import compile as re_compile, Pattern
from typing   import Optional as Nullable, Dict, List, ClassVar, Set, Self, Any, TextIO, Callable

from pyTooling.Decorators       import export
from pyTooling.Exceptions       import addNoteWithItemList
from pyTooling.MetaClasses      import ExtendedType, abstractmethod
from pyTooling.Stopwatch        import Stopwatch
from pyTooling.TerminalUI       import TerminalBaseApplication
from pyTooling.Warning          import WarningCollector, Warning
from ruamel.yaml                import YAML, CommentedMap, CommentedSeq

from pyEDAA.OutputFilter        import OutputFilterException
from pyEDAA.OutputFilter.Xilinx import VivadoInfoMessage, VivadoWarningMessage, VivadoCriticalWarningMessage, VivadoErrorMessage, LineAction
from pyEDAA.OutputFilter.Xilinx import Synth_Design, Opt_Design, Link_Design, Place_Design, PhyOpt_Design, Route_Design, Write_Bitstream
from pyEDAA.OutputFilter.Xilinx import Command, LineKind, VivadoLine


@export
class ConfigurationException(OutputFilterException):
	pass


@export
class ConfigurationWarning(Warning):
	pass


@export
class OutputFormat(StrEnum):
	Plain =    "plain"
	JSON =     "json"
	JSONLine = "jsonl"

	@classmethod
	def Parse(cls, value: str) -> Self:
		if value not in cls._value2member_map_:
			ex = ValueError(f"'{value}' is not a valid OutputFormat.")
			ex.add_note(f"Allowed values: {', '.join([item.value for item in cls])}")
			raise ex

		return cls(value)


@export
class TimestampFormat(StrEnum):
	Undefined = "undefined"
	DateTime =  "datetime"
	TimeOnly =  "timeonly"
	Runtime = "deltatime"

	@classmethod
	def Parse(cls, value: str) -> Self:
		if value not in cls._value2member_map_:
			ex = ValueError(f"'{value}' is not a valid TimestampFormat.")
			ex.add_note(f"Allowed values: {', '.join([item.value for item in cls])}")
			raise ex

		return cls(value)


@export
class Action(StrEnum):
	Default = "default"
	Remove =  "remove"
	Keep =    "keep"
	Error =   "error"

	@classmethod
	def Parse(cls, value: str) -> Self:
		if value not in cls._value2member_map_:
			ex = ValueError(f"'{value}' is not a valid Action.")
			ex.add_note(f"Allowed values: {', '.join([item.value for item in cls])}")
			raise ex

		return cls(value)


@export
class Level(StrEnum):
	Unknown =         ""
	Info =            "info"
	Warning =         "warning"
	CriticalWarning = "critical warning"
	Error =           "error"

	@classmethod
	def Parse(cls, value: str) -> Self:
		if value not in cls._value2member_map_:
			ex = ValueError(f"'{value}' is not a valid Level.")
			ex.add_note(f"Allowed values: {', '.join([item.value for item in cls])}")
			raise ex

		return cls(value)


@export
class Rule(metaclass=ExtendedType, slots=True):
	_optional: bool
	_action:   Nullable[Action]
	_level:    Nullable[Level]

# todo: justification (whitelist/ blacklist / message)

	def __init__(self, action: Nullable[Action] = None, level: Nullable[Level] = None) -> None:
		self._action = action
		self._level =  level

	@abstractmethod
	def Match(self, line: VivadoLine) -> bool:
		pass

	def Process(self, line: VivadoLine) -> None:
		if self._action is Action.Remove:
			line._action = LineAction.Remove
		elif self._action is Action.Default or self._action is Action.Keep:
			line._action = LineAction.Default


@export
class AllRule(Rule):
	def __init__(self, action: Nullable[Action] = None) -> None:
		super().__init__(action)

	def Match(self, line: VivadoLine) -> bool:
		return True

	def __str__(self) -> str:
		return "Rule match all lines"


@export
class ClassificationRule(Rule):
	_lineKind: LineKind

	def __init__(self, lineKind: LineKind, action: Nullable[Action] = None, level: Nullable[Level] = None) -> None:
		super().__init__(action, level)

		self._lineKind = lineKind

	def Match(self, line: VivadoLine) -> bool:
		return self._lineKind == line._kind

	def __str__(self) -> str:
		if self._lineKind is LineKind.InfoMessage:
			kind = "info"
		elif self._lineKind is LineKind.Warning:
			kind = "warning"
		elif self._lineKind is LineKind.CriticalWarning:
			kind = "critical warning"
		elif self._lineKind is LineKind.Error:
			kind = "error"

		return f"Rule for all '{kind}' messages: Level={self._level}; Action={self._action}"


@export
class VivadoMessageRule(Rule):
	_toolID:        int
	_messageKindID: int

	def __init__(self, toolID: int, messageKindID: int, action: Nullable[Action] = None, level: Nullable[Level] = None) -> None:
		super().__init__(action, level)

		self._toolID = toolID
		self._messageKindID = messageKindID

	def Match(self, line: VivadoLine) -> bool:
		if isinstance(line, (VivadoInfoMessage, VivadoWarningMessage, VivadoCriticalWarningMessage, VivadoErrorMessage)):
			return line._toolID == self._toolID and line._messageKindID == self._messageKindID

		return False

	def __str__(self) -> str:
		return f"Rule for '{self._toolID}-{self._messageKindID}': Level={self._level}; Action={self._action}"


@export
class Output(metaclass=ExtendedType, slots=True):
	_parent:   "ProcessingPipeline"
	_file:     TextIO
	_format:   OutputFormat
	_commands: Nullable[List[Command]]
	_rules:    Nullable[List[Rule]]

	def __init__(
		self,
		parent:   "ProcessingPipeline",
		format:   OutputFormat,
		commands: Nullable[List[Command]],
		rules:    Nullable[List[Rule]]
	) -> None:
		self._parent =   parent
		self._format =   format
		self._commands = commands
		self._rules =    rules


@export
class StdOutOutput(Output):
	_coloring:        bool
	_colors:          Dict[str, str]
	_lineNumbers:     bool
	_timestampFormat: TimestampFormat

	def __init__(
		self,
		parent:   "ProcessingPipeline",
		coloring: bool,
		format:   OutputFormat,
		commands: Nullable[List[Command]],
		rules:    Nullable[List[Rule]]
	) -> None:
		super().__init__(parent, format, commands, rules)

		self._coloring =        coloring
		self._colors =          parent._parent._colors
		self._lineNumbers =     False
		self._timestampFormat = TimestampFormat.Undefined


@export
class FileOutput(Output):
	_path: Path

	def __init__(
		self,
		parent:   "ProcessingPipeline",
		file:     Path,
		format:   OutputFormat,
		commands: List[Command],
		rules:    List[Rule]
	) -> None:
		super().__init__(parent, format, commands, rules)

		self._path = file


@export
class ProcessingPipeline(metaclass=ExtendedType, slots=True):
	_ALLOWED_BOOL_VALUES: ClassVar[Dict[str, bool]] = {
		"false": False,
		"true":  True,
		"off":   False,
		"on":    True,
		"no":    False,
		"yes":   True
	}
	_ALLOWED_COMMANDS:    ClassVar[Dict[str, Command]] = {
		"synth_design":    Synth_Design,
		"link_design":     Link_Design,
		"opt_design":      Opt_Design,
		"place_design":    Place_Design,
		"phyopt_design":   PhyOpt_Design,
		"route_design":    Route_Design,
		"write_bitstream": Write_Bitstream
	}

	_parent:        "Vivado"
	_preprocessing: Nullable[List[Rule]]
	_outputs:       Dict[str, Output]

	def __init__(self, parent: "Vivado") -> None:
		self._parent =        parent
		self._preprocessing = None
		self._outputs =       {
			"stdout": StdOutOutput(self, True, OutputFormat.Plain, None, [])
		}

	def Parse(self, config: Any, key: str, configPath: str) -> None:
		if key not in config:
			return
		elif (ruleConfig := config[key]) is None:
			return
		elif not isinstance(ruleConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Is not a dictionary."))
			return

		# todo: preprocessing

		for outputName in ruleConfig:
			if outputName == "stdout":
				self._ParseStdOutOutput(ruleConfig, "stdout", f"{configPath}.{key}")
			elif outputName == "stderr":
				pass
			else:
				self._ParseOutput(ruleConfig, outputName, f"{configPath}.{key}")

	def _ParseStdOutOutput(self, config: Any, key: str, configPath: str) -> None:
		if key not in config:
			return
		elif (outputConfig := config[key]) is None:
			return
		elif not isinstance(outputConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Is not a dictionary."))
			return

		stdout: StdOutOutput = self._outputs["stdout"]

		stdout._coloring =        self._ParseBoolean(outputConfig,    "coloring",    False, "tools.vivado.outputs.stdout.coloring")
		stdout._lineNumbers =     self._ParseBoolean(outputConfig,    "lineNumbers", False, "tools.vivado.outputs.stdout.lineNumbers")
		stdout._timestampFormat = self._ParseTimestampFormat(outputConfig, "timestamps", "tools.vivado.outputs.stdout.timestamps")
		stdout._commands =        self._ParseCommands(outputConfig,   "commands",   "tools.vivado.outputs.stdout.commands")
		stdout._rules =           self._ParseRuleSets(outputConfig,   "rule-sets",  "tools.vivado.outputs.stdout.rule-sets")

	def _ParseOutput(self, config: Any, key: str, configPath: str) -> None:
		if key not in config:
			return
		elif (outputConfig := config[key]) is None:
			return
		elif not isinstance(outputConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Is not a dictionary."))
			return

		try:
			path = self._ParsePath(outputConfig, "path", f"{configPath}.{key}")
		except ConfigurationException as ex:
			WarningCollector.Raise(ConfigurationWarning(str(ex)))
			return

		self._outputs[key] = FileOutput(
			self,
			path,
			self._ParseOutputFormat(outputConfig, "format", f"{configPath}.{key}"),
			self._ParseCommands(outputConfig,"commands",   f"{configPath}.{key}"),
			self._ParseRuleSets(outputConfig,"rule-sets",  f"{configPath}.{key}")
		)

	def _ParseBoolean(self, config: CommentedMap, key: str, default: Nullable[bool], configPath: str) -> Nullable[bool]:
		if key not in config:
			return default
		elif isinstance((value := config[key]), bool):
			return value

		try:
			return self._ALLOWED_BOOL_VALUES[value]
		except KeyError:
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}: Unknown value '{value}'."))

	def _ParsePath(self, config: CommentedMap, key: str, configPath: str) -> Path:
		if key not in config:
			raise ConfigurationException(f"{configPath}: Doesn't exist. A filename is required.")
		elif (pathConfig := config[key]) is None:
			raise ConfigurationException(f"{configPath}: Is empty. A filename is required.")
		elif not isinstance(pathConfig, str):
			raise ConfigurationException(f"{configPath}: Unknown value '{pathConfig}'.")

		try:
			return Path(pathConfig)
		except ValueError as ex:
			raise ConfigurationException(f"{configPath}: Value '{pathConfig}' is not a path.") from ex

	def _ParseOutputFormat(self, config: CommentedMap, key: str, configPath: str) -> OutputFormat:
		if key not in config:
			return OutputFormat.Plain
		elif (formatConfig := config[key]) is None:
			return OutputFormat.Plain
		elif not isinstance(formatConfig, str):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}: Unknown settings."))
			return OutputFormat.Plain

		return OutputFormat.Parse(formatConfig)

	def _ParseTimestampFormat(self, config: CommentedMap, key: str, configPath: str) -> TimestampFormat:
		if key not in config:
			return TimestampFormat.Undefined
		elif (formatConfig := config[key]) is None:
			return TimestampFormat.Undefined
		elif not isinstance(formatConfig, str):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}: Unknown settings."))
			return TimestampFormat.Undefined

		return TimestampFormat.Parse(formatConfig)

	def _ParseCommands(self, config: CommentedMap, key: str, configPath: str) -> Nullable[List[Command]]:
		if key not in config:
			return None
		elif (commandsConfig := config[key]) is None:
			return None
		elif not isinstance(commandsConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}: Unknown settings."))
			return None

		commands: List[Command] = []
		for commandName in commandsConfig:
			try:
				commands.append(self._ALLOWED_COMMANDS[commandName])
			except KeyError:
				WarningCollector.Raise(ConfigurationWarning(f"{configPath}: Unknown Vivado TCL command '{commandName}'."))

		if len(commands) > 0:
			return commands

		return None

	def _ParseRuleSets(self, config: CommentedMap, key: str, configPath: str) -> Nullable[List[Rule]]:
		if key not in config:
			return None
		elif (ruleSetsConfig := config[key]) is None:
			return None
		elif not isinstance(ruleSetsConfig, CommentedSeq):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}: Unknown settings."))
			return None

		rules: List[Rule] = []
		for ruleSetName in ruleSetsConfig:
			try:
				rules.extend(self._parent._ruleSets[ruleSetName].values())
			except KeyError:
				warn = ConfigurationWarning(f"{configPath}: Unknown rule set '{ruleSetName}'.")
				warn.add_note(f"Rule set '{ruleSetName}' not found in tools.vivado.rule-sets.")
				WarningCollector.Raise(warn)

		if len(rules) > 0:
			return rules

		return None

	def __len__(self) -> int:
		return len(self._outputs)


@export
class Tool(metaclass=ExtendedType, slots=True):
	@abstractmethod
	def Parse(self, config: CommentedMap, key: str, configPath: str) -> None:
		pass


@export
class Vivado(Tool):
	_ALLOWED_COLORS:         ClassVar[Set[str]] = set(TerminalBaseApplication.Foreground.keys())  # FIXME: this set contains unwanted color names like ERROR or HEADLINE
	_SECTIONS:               ClassVar[Set[str]] = {"colors", "rule-sets", "outputs", "exports", "policies"}

	_VIVADO_MESSAGE_PATTERN: ClassVar[Pattern] = re_compile(r"^(?P<toolID>\d+)-(?P<messageID>\d+)$")

	_parent:             "Configuration"
	_colors:             Dict[str, str]
	_ruleSets:           Dict[str, Dict[str, Rule]]
	_processingPipeline: ProcessingPipeline
	_hasLatches:         Action

	def __init__(self, parent: "Configuration") -> None:
		self._parent =   parent

		self._colors =             self._InitializeColors()
		self._ruleSets =           {}
		self._processingPipeline = ProcessingPipeline(self)
		self._hasLatches =         Action.Default

	def _InitializeColors(self) -> Dict[str, str]:
		# FIXME: more colors
		#  - vivado exit -> dark green
		#  - datetimeline + finished -> green

		return {
			"normal":               "WHITE",
			"info":                 "DARK_BLUE",  # GRAY
			"warning":              "YELLOW",
			"critical":             "MAGENTA",
			"error":                "RED",
			"tcl":                  "CYAN",
			"success":              "GREEN",
			"failed":               "RED",
			"verbose":              "GRAY",
			"unprocessed":          "DARK_GRAY",
			"empty":                "NOCOLOR",
			"sectionDelimiter":     "DARK_GRAY",
			"sectionStart":         "DARK_CYAN",
			"sectionEnd":           "DARK_CYAN",
			"sectionTime":          "DARK_GREEN",
			"subsectionStart":      "DARK_CYAN",
			"subsectionEnd":        "DARK_CYAN",
			"subsectionTime":       "DARK_GREEN",
			"launchStart":          "CYAN",
			"launchWaiting":        "DARK_CYAN",
			"launchArguments":      "MAGENTA",
			"launchFinished":       "CYAN",
			"launchTime":           "DARK_GREEN",
			"taskStart":            "YELLOW",
			"taskEnd":              "YELLOW",
			"taskTime":             "DARK_GREEN",
			"phaseStart":           "BLUE",
			"phaseEnd":             "BLUE",
			"phaseTime":            "DARK_GREEN",
			"subphaseStart":        "DARK_CYAN",
			"subphaseEnd":          "DARK_CYAN",
			"subphaseTime":         "DARK_GREEN",
			"subsubphaseStart":     "DARK_CYAN",
			"subsubphaseEnd":       "DARK_CYAN",
			"subsubphaseTime":      "DARK_GREEN",
			"subsubsubphaseStart":  "DARK_CYAN",
			"subsubsubphaseEnd":    "DARK_CYAN",
			"subsubsubphaseTime":   "DARK_GREEN",
			"nestedTaskStart":      "DARK_CYAN",
			"nestedTaskEnd":        "DARK_CYAN",
			"nestedTaskTime":       "DARK_GREEN",
			"nestedPhaseStart":     "DARK_CYAN",
			"nestedPhaseEnd":       "DARK_CYAN",
			"nestedPhaseTime":      "DARK_GREEN",
			"paragraphHeadline":    "DARK_YELLOW",
			"hierarchyStart":       "DARK_CYAN",
			"hierarchyEnd":         "DARK_GRAY",
			"xdcStart":             "DARK_CYAN",
			"xdcEnd":               "DARK_GRAY",
			# "dateTimeLine":         "WHITE",
			"table":                "WHITE",
		}

	def Parse(self, config: CommentedMap, key: str, configPath: str) -> None:
		if config is None:
			return
		elif key not in config:
			return
		elif (toolConfig := config[key]) is None:
			return
		elif not isinstance(toolConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Is not a dictionary."))

		for name in toolConfig:
			if name not in self._SECTIONS:
				warn = ConfigurationWarning(f"{configPath}.{key}: Unknown configuration section '{name}'.")
				addNoteWithItemList(warn, "Supported configuration sections: ", self._SECTIONS)
				WarningCollector.Raise(warn)

		self._ParseColors(toolConfig, "colors", f"{configPath}.{key}")
		self._ParseRuleSets(toolConfig, "rule-sets", f"{configPath}.{key}")
		self._processingPipeline.Parse(toolConfig, "outputs", f"{configPath}.{key}")

		if "exports" in toolConfig:
			if "cellUsage" in (exportConfig := toolConfig["exports"]):
				pass
				# self._ParseCellUsage(exportConfig["cellUsage"])

		if "policies" in toolConfig:
			self._ParsePolicies(toolConfig["policies"])

	def _ParseColors(self, config: CommentedMap, key: str, configPath: str) -> None:
		if key not in config:
			return
		elif (colorsConfig := config[key]) is None:
			return
		elif not isinstance(colorsConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Is not a dictionary."))
			return

		for lineKind, color in colorsConfig.items():
			if not isinstance(lineKind, str):
				WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: LineKind '{lineKind}' is not a string.'."))
			elif lineKind not in self._colors:
				warn = ConfigurationWarning(f"{configPath}.{key}: LineKind '{lineKind}' not supported for coloring.")
				addNoteWithItemList(warn, "Supported LineKinds for coloring: ", self._colors)
				WarningCollector.Raise(warn)
			elif not isinstance(color, str):
				WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}.{lineKind}: Color '{color}' is not a string.'."))
			elif (col := color.upper()) not in self._ALLOWED_COLORS:
				WarningCollector.Raise(
					ConfigurationWarning(f"{configPath}.{key}.{lineKind}: Color '{color}' is not supported."),
					notes=f"Supported colors: {', '.join(self._ALLOWED_COLORS)}"
				)
			else:
				self._colors[lineKind] = col

	def _ParseRuleSets(self, config: CommentedMap, key: str, configPath: str) -> None:
		if key not in config:
			return
		elif (ruleSetsConfig := config[key]) is None:
			return
		elif not isinstance(ruleSetsConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Is not a dictionary."))
			return

		for ruleSetName in ruleSetsConfig:
			self._ParseRuleSet(ruleSetsConfig, ruleSetName, f"{configPath}.{key}")

	def _ParseRuleSet(self, config: CommentedMap, key: str, configPath: str) -> None:
		if key not in config:
			return
		elif (ruleSetConfig := config[key]) is None:
			return
		elif not isinstance(ruleSetConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Is not a dictionary."))
			return

		self._ruleSets[key] = (ruleSet := {})

		for ruleName in ruleSetConfig:
			if ruleName == "all":
				self._ParseAllRule(ruleSet, ruleSetConfig, "all", f"{configPath}.{key}")
			elif ruleName in ("info", "warning", "criticalWarning", "error"):
				self._ParseVivadoMessageClassRule(ruleSet, ruleSetConfig, ruleName, f"{configPath}.{key}")
			elif (match := self._VIVADO_MESSAGE_PATTERN.match(ruleName)) is not None:
				toolID =    int(match.group("toolID"))
				messageID = int(match.group("messageID"))
				self._ParseVivadoMessageRule(ruleSet, toolID, messageID, ruleSetConfig, ruleName, f"{configPath}.{key}")
			else:
				WarningCollector.Raise(ConfigurationWarning(f"tools.vivado.rule-sets.{key}: Unknown rule '{ruleName}'."))

	def _ParseAllRule(self, ruleSet: Dict[str, Rule], config: Any, key: str, configPath: str) -> None:
		if key not in config:
			return
		elif (ruleConfig := config[key]) is None:
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Catch-all rule without action."))
			return
		elif not isinstance(ruleConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Is not a dictionary."))
			return

		action = self._ParseAction(ruleConfig, "action", f"{configPath}.{key}")

		ruleSet[key] = AllRule(action)

	def _ParseVivadoMessageClassRule(self, ruleSet: Dict[str, Rule], config: Any, key: str, configPath: str) -> None:
		if key not in config:
			return
		elif (ruleConfig := config[key]) is None:
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Vivado message class rule without action."))
			return
		elif not isinstance(ruleConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Is not a dictionary."))
			return

		if key == "info":
			lineKind = LineKind.InfoMessage
		elif key == "warning":
			lineKind = LineKind.WarningMessage
		elif key == "criticalWarning":
			lineKind = LineKind.CriticalWarning
		elif key == "error":
			lineKind = LineKind.ErrorMessage

		action = self._ParseAction(ruleConfig, "action", f"{configPath}.{key}")

		ruleSet[key] = ClassificationRule(lineKind, action)

	def _ParseVivadoMessageRule(self, ruleSet: Dict[str, Rule], toolID: int, messageID: int, config: Any, key: str, configPath: str) -> None:
		if key not in config:
			return
		elif (ruleConfig := config[key]) is None:
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Vivado message rule without action."))
			return
		elif not isinstance(ruleConfig, CommentedMap):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: Is not a dictionary."))
			return

		action = self._ParseAction(ruleConfig, "action", f"{configPath}.{key}")

		ruleSet[key] = VivadoMessageRule(toolID, messageID, action)

	def _ParseAction(self, config: Any, key: str, configPath: str) -> Action:
		if key not in config:
			return Action.Default
		elif (actionConfig := config[key]) is None:
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}.{key}: No defined action."))
			return Action.Default
		elif not isinstance(actionConfig, str):
			warn = ConfigurationWarning(f"{configPath}.{key}: Is not an Action.")
			addNoteWithItemList(warn, "Supported actions: ", Action)
			WarningCollector.Raise(warn)
			return Action.Default

		try:
			return Action.Parse(actionConfig)
		except ValueError as ex:
			warn = ConfigurationWarning(f"{configPath}.{key}: Unknown Action '{actionConfig}'.")
			addNoteWithItemList(warn, "Supported actions: ", Action)
			WarningCollector.Raise(warn, ex)
			return Action.Default

	def _ParsePolicies(self, policies: CommentedMap) -> None:
		if "hasLatches" in policies:

			if policies["hasLatches"] == "error":
				self._hasLatches = Action.Error
			else:
				WarningCollector.Raise(
					ConfigurationWarning(f"tools.vivado.policies.hasLatches: Unknown value '{policies["hasLatches"]}'."))

	def _ParseRuleSetAction(self, actionConfig: Any) -> LineAction:
		if not isinstance(actionConfig, str):
			WarningCollector.Raise(ConfigurationWarning(f"tools.vivado.rule-sets.<ruleset>.<rule>.action: Unsupported value '{actionConfig}'."))
		try:
			return Action(actionConfig)
		except ValueError:
			WarningCollector.Raise(ConfigurationWarning(f"tools.vivado.rule-sets.<ruleset>.<rule>.action: Unknown value '{actionConfig}'."))


@export
class Configuration(metaclass=ExtendedType, slots=True):
	_file:         Nullable[Path]
	_yamlDocument: Nullable[YAML]
	_yamlLoadTime: Nullable[float]

	_tools:        Dict[str, Tool]

	def __init__(self, file: Nullable[Path] = None) -> None:
		self._file =  None
		self._yamlDocument = None
		self._yamlLoadTime = None
		self._tools = {
			"vivado": Vivado(self)
		}

		if file is not None:
			self.Load(file)

	def Load(self, file: Path) -> None:
		self._file = file

		with Stopwatch() as sw:
			try:
				yamlReader = YAML()
				self._yamlDocument = yamlReader.load(file)
			except Exception as ex:
				raise ConfigurationException(f"Couldn't open '{file}'.") from ex

		self._yamlLoadTime = sw.Duration

		if self._yamlDocument is None:
			ex = ConfigurationException(f"Configuration file is empty.")
			raise ex
		elif not isinstance(self._yamlDocument, CommentedMap):
			ex = ConfigurationException(f"Configuration file is not a dictionary.")
			raise ex

		self.Parse()

	def Parse(self) ->None:
		if "version" not in self._yamlDocument:
			ex = ConfigurationException(f"Configuration file has no 'version'.")
			addNoteWithItemList(ex, "Supported versions: ", self._VERSIONS)
			raise ex
		elif not isinstance(version := self._yamlDocument["version"], str):
			ex = ConfigurationException(f"version: is not a string.")
			addNoteWithItemList(ex, "Supported versions: ", self._VERSIONS)
			raise ex
		elif version not in self._VERSIONS:
			ex = ConfigurationException(f"Configuration file version '{version}' is not supported.")
			addNoteWithItemList(ex, "Supported versions: ", self._VERSIONS)
			raise ex

		self._VERSIONS[version](self)

	def _Parse_v0_1(self) -> None:
		if "tools" not in self._yamlDocument:
			WarningCollector.Raise(ConfigurationWarning(f"Configuration doesn't contain tool configurations."))
			return
		elif (toolsConfig := self._yamlDocument["tools"]) is None:
			WarningCollector.Raise(
				ConfigurationWarning(f"tools: Configuration doesn't contain tool specific configurations."),
				notes=f"Supported keys: vivado"
			)
			return
		elif not isinstance(toolsConfig, CommentedMap):
			WarningCollector.Raise(
				ConfigurationWarning(f"tools: Is not a dictionary."),
				notes=f"Supported keys: vivado"
			)
			return

		for toolName in toolsConfig:
			try:
				tool = self._tools[toolName]
			except KeyError:
				WarningCollector.Raise(ConfigurationWarning(f"tools: Unknown tool '{toolName}'."))
				continue

			tool.Parse(toolsConfig, "vivado", "tools")

	_VERSIONS: ClassVar[Dict[str, Callable[[Self], None]]] = {
		"0.1": _Parse_v0_1
	}
