"""
Sample GitHub Copilot SDK package.

A sample GitHub Copilot SDK application using agent plugins is a small reference
project that shows how to extend Copilot with custom agents and plugin-based
capabilities so it can perform specialized tasks within a structured workflow.

:author: Ron Webb
:since: 0.1.0
"""

from env_dir_bootstrap import EnvDirBootstrap
from logenrich import setup_logger

__version__ = "0.1.0"

_bootstrapper = EnvDirBootstrap(
    env_var="SAMPLE_GH_COPILOT_SDK_CONFIG_DIR",
    resources=["logging.ini"],
    package="sample_gh_copilot_sdk",
)

_bootstrapper.setup()

CONF_DIR = str(_bootstrapper.get_dir())

setup_logger("sample_gh_copilot_sdk", conf_dir=CONF_DIR)
