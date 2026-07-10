"""
AgentPluginSession: orchestrates a GitHub Copilot session with custom agents,
registered tools, session hooks, and optional plugin-directory loading.

:author: Ron Webb
:since: 0.1.0
"""

import collections.abc
from types import TracebackType
from typing import Any

from copilot import CopilotClient, RuntimeConnection
from copilot.session import PermissionHandler
from copilot.session_events import AssistantMessageData

from sample_gh_copilot_sdk.agent_plugins.agents import build_agents_config
from sample_gh_copilot_sdk.agent_plugins.hooks import build_hooks
from sample_gh_copilot_sdk.agent_plugins.tools import get_tools


class AgentPluginSession:
    """Manages a Copilot session with custom agents and optional plugin directories.

    Wraps :class:`copilot.CopilotClient` with plugin-dir support and exposes an
    async context-manager interface so client and session resources are always
    released cleanly.

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
        self._plugin_dirs: list[str] = plugin_dirs or []
        self._model: str = model
        self._timeout: float = timeout
        self._client_factory = client_factory
        self._client: CopilotClient | None = None
        self._session: Any = None

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

    def _extract_content(self, reply: Any) -> str:
        """Extract the assistant message text from a ``send_and_wait`` reply event.

        :param reply: The event object returned by ``session.send_and_wait``, or
            ``None`` if no reply was produced.
        :return: The assistant's message content, or an empty string when the reply
            does not contain an :class:`~copilot.session_events.AssistantMessageData`
            payload.
        :author: Ron Webb
        :since: 0.1.0
        """
        if reply is None:
            return ""
        data = getattr(reply, "data", None)
        if isinstance(data, AssistantMessageData):
            return data.content
        return ""

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "AgentPluginSession":
        """Start the Copilot client and open a session with custom agents and tools.

        :return: This :class:`AgentPluginSession` instance.
        :author: Ron Webb
        :since: 0.1.0
        """
        self._client = self._build_client()
        await self._client.start()
        self._session = await self._client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model=self._model,
            tools=get_tools(),
            custom_agents=build_agents_config(),
            hooks=build_hooks(),
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Disconnect the session and stop the Copilot client.

        :param exc_type: Exception type, if an exception is propagating.
        :param exc_val: Exception value, if an exception is propagating.
        :param exc_tb: Exception traceback, if an exception is propagating.
        :author: Ron Webb
        :since: 0.1.0
        """
        if self._session is not None:
            await self._session.disconnect()
        if self._client is not None:
            await self._client.stop()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(self, prompt: str) -> str:
        """Send *prompt* to the active session and return the assistant's response.

        :param prompt: The user's input text.
        :return: The assistant's reply text.
        :raises RuntimeError: If called before entering the async context manager.
        :author: Ron Webb
        :since: 0.1.0
        """
        if self._session is None:
            raise RuntimeError(
                "Session not started — use 'async with AgentPluginSession() as s:'."
            )
        reply = await self._session.send_and_wait(prompt, timeout=self._timeout)
        return self._extract_content(reply)

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
