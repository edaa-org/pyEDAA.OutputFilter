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
from re       import compile as re_compile
from typing   import Optional as Nullable, Dict, List, ClassVar, Set, Self, Any, TextIO, Callable

from pyTooling.Decorators       import export
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
	def parse(cls, value: str) -> Self:
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
	def parse(cls, value: str) -> Self:
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
	def parse(cls, value: str) -> Self:
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
	def parse(cls, value: str) -> Self:
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

	def Parse(self, outputsConfig: CommentedMap) -> None:
		if "preprocessing" in outputsConfig and (preprocessing := outputsConfig["preprocessing"]) is not None:
			try:
				self._preprocessing = list(self._parent._ruleSets[preprocessing].values())
			except KeyError:
				warn = ConfigurationWarning(f"tools.vivado.outputs.preprocessing: Unknown rule set '{preprocessing}'.")
				warn.add_note(f"Rule set '{preprocessing}' not found in tools.vivado.rule-sets.")
				WarningCollector.Raise(warn)

		for outputName, outputConfig in outputsConfig.items():
			if outputName == "preprocessing":
				continue
			elif outputName == "stdout":
				self._ParseStdOutOutput(outputConfig)
			elif outputName == "stderr":
				pass
			# self._ParseStdErrOutput(outputConfig)
			else:
				self._ParseOutput(outputName, outputConfig)

	def _ParseStdOutOutput(self, outputConfig: CommentedMap) -> None:
		stdout: StdOutOutput = self._outputs["stdout"]

		stdout._coloring =        self._ParseBoolean(outputConfig,    "coloring",    False, "tools.vivado.outputs.stdout.coloring")
		stdout._lineNumbers =     self._ParseBoolean(outputConfig,    "lineNumbers", False, "tools.vivado.outputs.stdout.lineNumbers")
		stdout._timestampFormat = self._ParseTimestampFormat(outputConfig, "timestamps", "tools.vivado.outputs.stdout.timestamps")
		stdout._commands =        self._ParseCommands(outputConfig,   "commands",   "tools.vivado.outputs.stdout.commands")
		stdout._rules =           self._ParseRuleSets(outputConfig,   "rule-sets",  "tools.vivado.outputs.stdout.rule-sets")

	def _ParseOutput(self, outputName: str, outputConfig: CommentedMap) -> None:
		try:
			path = self._ParsePath(outputConfig, "path", f"tools.vivado.outputs.{outputName}.path")
		except ConfigurationException as ex:
			WarningCollector.Raise(ConfigurationWarning(str(ex)))
			return

		self._outputs[outputName] = FileOutput(
			self,
			path,
			self._ParseOutputFormat(outputConfig, "format", f"tools.vivado.outputs.{outputName}.format"),
			self._ParseCommands(outputConfig,"commands",   f"tools.vivado.outputs.{outputName}.commands"),
			self._ParseRuleSets(outputConfig,"rule-sets",  f"tools.vivado.outputs.{outputName}.rule-sets")
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

		return OutputFormat.parse(formatConfig)

	def _ParseTimestampFormat(self, config: CommentedMap, key: str, configPath: str) -> TimestampFormat:
		if key not in config:
			return TimestampFormat.Undefined
		elif (formatConfig := config[key]) is None:
			return TimestampFormat.Undefined
		elif not isinstance(formatConfig, str):
			WarningCollector.Raise(ConfigurationWarning(f"{configPath}: Unknown settings."))
			return TimestampFormat.Undefined

		return TimestampFormat.parse(formatConfig)

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
	pass


@export
class Vivado(Tool):
	_ALLOWED_COLORS:   ClassVar[Set[str]] = set(TerminalBaseApplication.Foreground.keys())

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
		return {
			"normal":               "WHITE",
			"info":                 "GRAY", # "DARK_BLUE",
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
			"table":                "GRAY",
		}

	def Parse(self, toolConfig: CommentedMap) -> None:
		if "colors" in toolConfig:
			self._ParseColors(toolConfig["colors"])

		if "rule-sets" in toolConfig:
			for ruleSetName, ruleSetConfig in toolConfig["rule-sets"].items():
				if len(ruleSetConfig) > 0:
					self._ParseRuleSet(ruleSetName, ruleSetConfig)

		if "outputs" in toolConfig:
			self._processingPipeline.Parse(toolConfig["outputs"])

		if "exports" in toolConfig:
			if "cellUsage" in (exportConfig := toolConfig["exports"]):
				pass
				# self._ParseCellUsage(exportConfig["cellUsage"])

		if "policies" in toolConfig:
			self._ParsePolicies(toolConfig["policies"])

	def _ParseColors(self, colors: CommentedMap) -> None:
		for lineKind, color in colors.items():
			if lineKind not in self._colors:
				WarningCollector.Raise(ConfigurationWarning(f"tools.vivado.colors: Item '{lineKind}' not supported for coloring."))
				continue
			elif (col := color.upper()) not in self._ALLOWED_COLORS:
				WarningCollector.Raise(ConfigurationWarning(f"tools.vivado.colors.{lineKind}: Color '{color}' is not supported."))
				continue

			self._colors[lineKind] = col

	def _ParseRuleSet(self, ruleSetName: str, ruleSetConfig: CommentedMap) -> None:
		self._ruleSets[ruleSetName] = (ruleSet := {})

		pattern = re_compile(r"^(?P<toolID>\d+)-(?P<messageID>\d+)$")

		for ruleName, ruleConfig in ruleSetConfig.items():
			if ruleName == "all":
				ruleSet[ruleName] = AllRule(self._ParseRuleSetAction(ruleConfig["action"]))
			elif ruleName == "info":
				ruleSet[ruleName] = ClassificationRule(LineKind.InfoMessage, self._ParseRuleSetAction(ruleConfig["action"]))
			elif ruleName == "criticalWarning":
				ruleSet[ruleName] = ClassificationRule(LineKind.WarningMessage, self._ParseRuleSetAction(ruleConfig["action"]))
			elif ruleName == "warning":
				ruleSet[ruleName] = ClassificationRule(LineKind.CriticalWarningMessage, self._ParseRuleSetAction(ruleConfig["action"]))
			elif ruleName == "error":
				ruleSet[ruleName] = ClassificationRule(LineKind.ErrorMessage, self._ParseRuleSetAction(ruleConfig["action"]))
			elif (match := pattern.match(ruleName)) is not None:
					toolID =    int(match.group("toolID"))
					messageID = int(match.group("messageID"))
					ruleSet[ruleName] = VivadoMessageRule(toolID, messageID, self._ParseRuleSetAction(ruleConfig["action"]))
			else:
				WarningCollector.Raise(ConfigurationWarning(f"tools.vivado.rule-sets.{ruleSetName}: Unknown rule '{ruleName}'."))

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
	_file:         Path
	_yamlDocument: YAML
	_yamlLoadTime: float

	_tools:        Dict[str, Tool]

	def __init__(self, file: Path) -> None:
		self._file =  file
		self._tools = {}

		with Stopwatch() as sw:
			try:
				yamlReader = YAML()
				self._yamlDocument = yamlReader.load(self._file)
			except Exception as ex:
				raise ConfigurationException(f"Couldn't open '{self._file}'.") from ex

		self._yamlLoadTime = sw.Duration

		self.Parse()

	def Parse(self) ->None:
		if (version := self._yamlDocument["version"]) != "0.1":
			ex = ConfigurationException(f"Configuration file version {version} is not supported.")
			ex.add_note("Supported versions: 0.1")
			raise ex

		self._Parse_v0_1()

	def _Parse_v0_1(self) -> None:
		for toolName, toolConfig in self._yamlDocument["tools"].items():
			if toolName == "vivado":
				self._tools["vivado"] = (vivado := Vivado(self))
				vivado.Parse(toolConfig)
