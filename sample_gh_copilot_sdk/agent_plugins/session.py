"""
AgentPluginSession: orchestrates a GitHub Copilot session with custom agents,
registered tools, session hooks, and optional plugin-directory loading.

:author: Ron Webb
:since: 0.1.0
"""

import collections.abc

from copilot import CopilotClient, RuntimeConnection

from sample_gh_copilot_sdk._base_session import BaseSession
from sample_gh_copilot_sdk.agent_plugins.agents import build_agents_config
from sample_gh_copilot_sdk.agent_plugins.hooks import build_hooks
from sample_gh_copilot_sdk.agent_plugins.tools import get_tools


class AgentPluginSession(BaseSession):
    """Manages a Copilot session with custom agents and optional plugin directories.

    Extends :class:`~sample_gh_copilot_sdk._base_session.BaseSession` with
    plugin-directory support and a researcher/editor agent configuration.

    Usage::

        async with AgentPluginSession(plugin_dirs=["./plugins/my_plugin"]) as sess:
            response = await sess.run("Explain this codebase")
            print(response)

    :author: Ron Webb
    :since: 0.1.0
    """

    def __init__(
        self,
        plugin_dirs: list[str] | None = None,
        model: str = "gpt-5-mini",
        timeout: float = 300.0,
        client_factory: collections.abc.Callable[[], CopilotClient] | None = None,
    ) -> None:
        """Initialise session configuration.

        :param plugin_dirs: Optional list of plugin-directory paths.  Each path is
            forwarded to the CLI as ``--plugin-dir <path>``.
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
        self._plugin_dirs: list[str] = plugin_dirs or []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_client(self) -> CopilotClient:
        """Construct a :class:`~copilot.CopilotClient` appropriate for this config.

        If a *client_factory* was supplied it is called and its return value used
        directly.  Otherwise a new client is constructed: when *plugin_dirs* is
        non-empty the CLI is spawned with ``--plugin-dir`` args; otherwise a plain
        default client is returned.

        :return: A configured :class:`~copilot.CopilotClient` instance.
        :author: Ron Webb
        :since: 0.1.0
        """
        if self._client_factory is not None:
            return self._client_factory()
        if self._plugin_dirs:
            cli_args: list[str] = []
            for plugin_dir in self._plugin_dirs:
                cli_args.extend(["--plugin-dir", plugin_dir])
            return CopilotClient(connection=RuntimeConnection.for_stdio(args=cli_args))
        return CopilotClient()

    def _session_kwargs(self) -> dict:
        """Return agents, tools, and hooks for the agent-plugins session.

        :return: Dict with ``tools``, ``custom_agents``, and ``hooks`` keys.
        :author: Ron Webb
        :since: 0.1.0
        """
        return {
            "tools": get_tools(),
            "custom_agents": build_agents_config(),
            "hooks": build_hooks(),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def list_plugins(self) -> list[dict]:
        """Return metadata for every plugin loaded by the current session.

        Calls ``session.rpc.plugins.list()`` and normalises the result into plain
        dicts for easy consumption.

        :return: A list of dicts, each containing ``name`` (str) and ``enabled``
            (bool) keys.
        :raises RuntimeError: If called before entering the async context manager.
        :author: Ron Webb
        :since: 0.1.0
        """
        if self._session is None:
            raise RuntimeError(
                "Session not started — use 'async with AgentPluginSession() as s:'."
            )
        result = await self._session.rpc.plugins.list()
        return [{"name": plug.name, "enabled": plug.enabled} for plug in result.plugins]
