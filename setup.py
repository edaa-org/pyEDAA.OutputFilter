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
# Copyright 2017-2024 Patrick Lehmann - Boetzingen, Germany                                                            #
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
"""Package installer for 'Post-processing of EDA Tool outputs (log files)'."""
from pathlib             import Path
from setuptools          import setup
from pyTooling.Packaging import DescribePythonPackageHostedOnGitHub, DEFAULT_CLASSIFIERS

gitHubNamespace =        "edaa-org"
packageName =            "pyEDAA.OutputFilter"
packageDirectory =       packageName.replace(".", "/")
packageInformationFile = Path(f"{packageDirectory}/__init__.py")

setup(
	**DescribePythonPackageHostedOnGitHub(
		packageName=packageName,
		description="Post-processing of EDA Tool outputs (log files).",
		gitHubNamespace=gitHubNamespace,
		keywords="Python3 CLI Output Filter PostProcessing",
		sourceFileWithVersion=packageInformationFile,
		developmentStatus="alpha",
		pythonVersions=("3.11", "3.12", "3.13"),
		classifiers=list(DEFAULT_CLASSIFIERS) + [
			"Intended Audience :: Developers",
			"Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
			"Topic :: Utilities"
	],
	dataFiles={
		packageName: ["py.typed"]
	},
		consoleScripts={
			"pyedaa-outputfilter": "pyEDAA.OutputFilter.CLI:main"
		},
	debug=True
	)
)
