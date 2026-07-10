"""
Tests for sample_gh_copilot_sdk.agent_plugins.session.

:author: Ron Webb
:since: 0.1.0
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from copilot.session_events import AssistantMessageData
from sample_gh_copilot_sdk.agent_plugins.session import AgentPluginSession


def _make_mock_client(mock_session: MagicMock) -> MagicMock:
    """Return a mock CopilotClient whose create_session resolves to *mock_session*.

    :param mock_session: The mock session object to return from ``create_session``.
    :return: A configured mock client.
    :author: Ron Webb
    :since: 0.1.0
    """
    client = MagicMock()
    client.start = AsyncMock()
    client.stop = AsyncMock()
    client.create_session = AsyncMock(return_value=mock_session)
    return client


def _make_mock_session(content: str = "Hello from assistant") -> MagicMock:
    """Return a mock session whose send_and_wait yields an AssistantMessageData reply.

    :param content: The assistant message content to include in the fake reply.
    :return: A configured mock session object.
    :author: Ron Webb
    :since: 0.1.0
    """
    mock_data = AssistantMessageData(content=content, message_id="msg-001")
    mock_reply = MagicMock()
    mock_reply.data = mock_data

    session = MagicMock()
    session.send_and_wait = AsyncMock(return_value=mock_reply)
    session.disconnect = AsyncMock()
    session.rpc = MagicMock()
    return session


class TestBuildClient:
    """Tests for AgentPluginSession._build_client.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_uses_factory_when_provided(self) -> None:
        """When client_factory is set, _build_client must delegate to it.

        :author: Ron Webb
        :since: 0.1.0
        """
        fake_client = MagicMock()
        factory = MagicMock(return_value=fake_client)
        agent = AgentPluginSession(client_factory=factory)
        result = agent._build_client()
        factory.assert_called_once()
        assert result is fake_client

    def test_uses_plain_client_without_plugins(self) -> None:
        """Without plugin_dirs or a factory, a plain CopilotClient should be created.

        :author: Ron Webb
        :since: 0.1.0
        """
        agent = AgentPluginSession()
        with patch(
            "sample_gh_copilot_sdk.agent_plugins.session.CopilotClient"
        ) as mock_cls:
            mock_cls.return_value = MagicMock()
            result = agent._build_client()
            mock_cls.assert_called_once_with()
            assert result is mock_cls.return_value

    def test_passes_plugin_dir_args_to_runtime_connection(self) -> None:
        """With plugin_dirs set, --plugin-dir flags must be forwarded to the CLI.

        :author: Ron Webb
        :since: 0.1.0
        """
        agent = AgentPluginSession(plugin_dirs=["/plugins/reviewer"])
        with (
            patch(
                "sample_gh_copilot_sdk.agent_plugins.session.RuntimeConnection"
            ) as mock_rtc,
            patch(
                "sample_gh_copilot_sdk.agent_plugins.session.CopilotClient"
            ) as mock_cls,
        ):
            mock_rtc.for_stdio.return_value = MagicMock()
            mock_cls.return_value = MagicMock()
            agent._build_client()
            mock_rtc.for_stdio.assert_called_once_with(
                args=["--plugin-dir", "/plugins/reviewer"]
            )


class TestExtractContent:
    """Tests for AgentPluginSession._extract_content.

    :author: Ron Webb
    :since: 0.1.0
    """

    def _make_agent(self) -> AgentPluginSession:
        """Return a bare AgentPluginSession for calling internal helpers directly.

        :author: Ron Webb
        :since: 0.1.0
        """
        return AgentPluginSession(client_factory=lambda: MagicMock())

    def test_returns_empty_string_for_none_reply(self) -> None:
        """A None reply must produce an empty string.

        :author: Ron Webb
        :since: 0.1.0
        """
        agent = self._make_agent()
        assert agent._extract_content(None) == ""

    def test_returns_empty_string_when_data_is_none(self) -> None:
        """A reply with data=None must produce an empty string.

        :author: Ron Webb
        :since: 0.1.0
        """
        agent = self._make_agent()
        reply = MagicMock()
        reply.data = None
        assert agent._extract_content(reply) == ""

    def test_returns_empty_string_for_non_assistant_data(self) -> None:
        """A reply with an unrecognised data type must produce an empty string.

        :author: Ron Webb
        :since: 0.1.0
        """
        agent = self._make_agent()
        reply = MagicMock()
        reply.data = MagicMock()  # not AssistantMessageData
        assert agent._extract_content(reply) == ""

    def test_returns_content_for_assistant_message(self) -> None:
        """A valid AssistantMessageData payload must return its content string.

        :author: Ron Webb
        :since: 0.1.0
        """
        agent = self._make_agent()
        data = AssistantMessageData(content="Test response", message_id="m1")
        reply = MagicMock()
        reply.data = data
        assert agent._extract_content(reply) == "Test response"


class TestAsyncContextManager:
    """Tests for the async context-manager protocol of AgentPluginSession.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_run_returns_assistant_content(self) -> None:
        """run() must return the assistant's message text from the session reply.

        :author: Ron Webb
        :since: 0.1.0
        """
        mock_session = _make_mock_session("Hi there!")
        mock_client = _make_mock_client(mock_session)

        agent = AgentPluginSession(client_factory=lambda: mock_client)

        async def _run() -> str:
            async with agent as sess:
                return await sess.run("Hello")

        result = asyncio.run(_run())
        assert result == "Hi there!"
        mock_session.send_and_wait.assert_called_once_with("Hello", timeout=300.0)

    def test_run_passes_custom_timeout_to_send_and_wait(self) -> None:
        """run() must forward the configured timeout to send_and_wait.

        :author: Ron Webb
        :since: 0.1.0
        """
        mock_session = _make_mock_session("ok")
        mock_client = _make_mock_client(mock_session)

        agent = AgentPluginSession(timeout=120.0, client_factory=lambda: mock_client)

        async def _run() -> str:
            async with agent as sess:
                return await sess.run("Hello")

        asyncio.run(_run())
        mock_session.send_and_wait.assert_called_once_with("Hello", timeout=120.0)

    def test_run_raises_when_session_not_started(self) -> None:
        """run() must raise RuntimeError when called outside the context manager.

        :author: Ron Webb
        :since: 0.1.0
        """
        agent = AgentPluginSession(client_factory=lambda: MagicMock())
        with pytest.raises(RuntimeError):
            asyncio.run(agent.run("Hello"))

    def test_list_plugins_raises_when_session_not_started(self) -> None:
        """list_plugins() must raise RuntimeError when the session is not started.

        :author: Ron Webb
        :since: 0.1.0
        """
        agent = AgentPluginSession(client_factory=lambda: MagicMock())
        with pytest.raises(RuntimeError):
            asyncio.run(agent.list_plugins())

    def test_exit_calls_disconnect_and_stop(self) -> None:
        """Leaving the context manager must disconnect the session and stop the client.

        :author: Ron Webb
        :since: 0.1.0
        """
        mock_session = _make_mock_session()
        mock_client = _make_mock_client(mock_session)

        agent = AgentPluginSession(client_factory=lambda: mock_client)

        async def _run() -> None:
            async with agent:
                pass

        asyncio.run(_run())
        mock_session.disconnect.assert_called_once()
        mock_client.stop.assert_called_once()

    def test_list_plugins_returns_plugin_dicts(self) -> None:
        """list_plugins() must normalise plugin data into a list of dicts.

        :author: Ron Webb
        :since: 0.1.0
        """
        fake_plugin = MagicMock()
        fake_plugin.name = "code-reviewer"
        fake_plugin.enabled = True

        plugin_result = MagicMock()
        plugin_result.plugins = [fake_plugin]

        mock_session = _make_mock_session()
        mock_session.rpc.plugins.list = AsyncMock(return_value=plugin_result)
        mock_client = _make_mock_client(mock_session)

        agent = AgentPluginSession(client_factory=lambda: mock_client)

        async def _run() -> list[dict]:
            async with agent as sess:
                return await sess.list_plugins()

        plugins = asyncio.run(_run())
        assert plugins == [{"name": "code-reviewer", "enabled": True}]
