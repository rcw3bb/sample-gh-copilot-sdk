"""
Agent plugins demonstration package for the GitHub Copilot SDK.

Shows how to register custom tools, define multi-agent workflows, load plugin
directories via ``--plugin-dir``, and wire session hooks using the
``github-copilot-sdk`` Python SDK.

:author: Ron Webb
:since: 0.1.0
"""

from sample_gh_copilot_sdk.agent_plugins.agents import AgentConfig, build_agents_config
from sample_gh_copilot_sdk.agent_plugins.hooks import build_hooks
from sample_gh_copilot_sdk.agent_plugins.session import AgentPluginSession
from sample_gh_copilot_sdk.agent_plugins.tools import get_tools

__all__ = [
    "AgentConfig",
    "AgentPluginSession",
    "build_agents_config",
    "build_hooks",
    "get_tools",
]
