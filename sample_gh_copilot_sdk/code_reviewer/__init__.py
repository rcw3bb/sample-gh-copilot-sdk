"""
Code-reviewer demonstration package for the GitHub Copilot SDK.

Demonstrates how to define a custom agent inline (without a plugin directory)
and run a focused code-review session using the ``github-copilot-sdk`` Python SDK.

:author: Ron Webb
:since: 0.1.0
"""

from sample_gh_copilot_sdk.agent_plugins.agents import AgentConfig
from sample_gh_copilot_sdk.code_reviewer.agent import build_code_reviewer_config
from sample_gh_copilot_sdk.code_reviewer.hooks import build_hooks
from sample_gh_copilot_sdk.code_reviewer.session import CodeReviewerSession
from sample_gh_copilot_sdk.code_reviewer.tools import get_tools

__all__ = [
    "AgentConfig",
    "build_code_reviewer_config",
    "build_hooks",
    "CodeReviewerSession",
    "get_tools",
]
