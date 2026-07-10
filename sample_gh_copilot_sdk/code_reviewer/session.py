"""
CodeReviewerSession: runs a GitHub Copilot session with the inline code-reviewer
agent, read-only tools, and session hooks — no plugin directory required.

:author: Ron Webb
:since: 0.1.0
"""

import collections.abc

from copilot import CopilotClient

from sample_gh_copilot_sdk._base_session import BaseSession
from sample_gh_copilot_sdk.code_reviewer.agent import build_code_reviewer_config
from sample_gh_copilot_sdk.code_reviewer.hooks import build_hooks
from sample_gh_copilot_sdk.code_reviewer.tools import get_tools


class CodeReviewerSession(BaseSession):
    """Manages a Copilot session with the inline code-reviewer agent.

    Unlike :class:`~sample_gh_copilot_sdk.agent_plugins.AgentPluginSession`,
    no plugin directory is required -- the agent is defined entirely in Python
    via :func:`~sample_gh_copilot_sdk.code_reviewer.agent.build_code_reviewer_config`.

    Usage::

        async with CodeReviewerSession() as session:
            report = await session.run("Review the authentication module")
            print(report)

    :author: Ron Webb
    :since: 0.1.0
    """

    def __init__(
        self,
        model: str = "gpt-5-mini",
        timeout: float = 300.0,
        client_factory: collections.abc.Callable[[], CopilotClient] | None = None,
    ) -> None:
        """Initialise session configuration.

        :param model: Model identifier forwarded to ``create_session``.
        :param timeout: Seconds to wait for the session to become idle after sending
            a prompt.  Defaults to ``300.0``.
        :param client_factory: Optional zero-argument callable that returns a
            :class:`~copilot.CopilotClient`; primarily used for dependency injection
            in tests.
        :author: Ron Webb
        :since: 0.1.0
        """
        super().__init__(model=model, timeout=timeout, client_factory=client_factory)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _session_kwargs(self) -> dict:
        """Return the code-reviewer agent, tools, and hooks for this session.

        :return: Dict with ``tools``, ``custom_agents``, and ``hooks`` keys.
        :author: Ron Webb
        :since: 0.1.0
        """
        return {
            "tools": get_tools(),
            "custom_agents": [build_code_reviewer_config()],
            "hooks": build_hooks(),
            "agent": "code-reviewer",
        }
