"""
Tests for sample_gh_copilot_sdk.code_reviewer.session.

:author: Ron Webb
:since: 0.1.0
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from copilot.session_events import AssistantMessageData
from sample_gh_copilot_sdk.code_reviewer.session import CodeReviewerSession


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


def _make_mock_session(
    content: str = "No issues found. The code looks good!",
) -> MagicMock:
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
    return session


class TestBuildClient:
    """Tests for CodeReviewerSession._build_client.

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
        reviewer = CodeReviewerSession(client_factory=factory)
        result = reviewer._build_client()
        factory.assert_called_once()
        assert result is fake_client

    def test_uses_plain_client_without_factory(self) -> None:
        """Without a factory, a plain CopilotClient should be created.

        :author: Ron Webb
        :since: 0.1.0
        """
        reviewer = CodeReviewerSession()
        with patch("sample_gh_copilot_sdk._base_session.CopilotClient") as mock_cls:
            mock_cls.return_value = MagicMock()
            result = reviewer._build_client()
            mock_cls.assert_called_once_with()
            assert result is mock_cls.return_value


class TestExtractContent:
    """Tests for CodeReviewerSession._extract_content.

    :author: Ron Webb
    :since: 0.1.0
    """

    def _make_session(self) -> CodeReviewerSession:
        """Return a bare CodeReviewerSession for testing internal helpers.

        :author: Ron Webb
        :since: 0.1.0
        """
        return CodeReviewerSession()

    def test_returns_empty_string_for_none_reply(self) -> None:
        """None reply must produce an empty string.

        :author: Ron Webb
        :since: 0.1.0
        """
        reviewer = self._make_session()
        assert reviewer._extract_content(None) == ""

    def test_returns_content_from_assistant_message_data(self) -> None:
        """An AssistantMessageData payload must yield its content string.

        :author: Ron Webb
        :since: 0.1.0
        """
        mock_data = AssistantMessageData(
            content="### Warning\n- Missing types", message_id="m1"
        )
        mock_reply = MagicMock()
        mock_reply.data = mock_data
        reviewer = self._make_session()
        assert reviewer._extract_content(mock_reply) == "### Warning\n- Missing types"

    def test_returns_empty_string_when_data_is_not_assistant_message(self) -> None:
        """A reply with non-AssistantMessageData payload must yield empty string.

        :author: Ron Webb
        :since: 0.1.0
        """
        mock_reply = MagicMock()
        mock_reply.data = "unexpected_type"
        reviewer = self._make_session()
        assert reviewer._extract_content(mock_reply) == ""


class TestContextManager:
    """Tests for CodeReviewerSession async context-manager lifecycle.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_session_is_none_before_enter(self) -> None:
        """_session must be None before the context manager is entered.

        :author: Ron Webb
        :since: 0.1.0
        """
        reviewer = CodeReviewerSession()
        assert reviewer._session is None

    def test_run_raises_before_enter(self) -> None:
        """Calling run() before entering the context must raise RuntimeError.

        :author: Ron Webb
        :since: 0.1.0
        """
        reviewer = CodeReviewerSession()
        with pytest.raises(RuntimeError):
            asyncio.run(reviewer.run("Review auth.py"))

    def test_enter_and_exit_manage_client_lifecycle(self) -> None:
        """__aenter__ must start the client; __aexit__ must stop it.

        :author: Ron Webb
        :since: 0.1.0
        """
        mock_session = _make_mock_session()
        mock_client = _make_mock_client(mock_session)

        async def _run() -> None:
            async with CodeReviewerSession(
                client_factory=lambda: mock_client
            ) as reviewer:
                assert reviewer._session is mock_session
            mock_client.start.assert_called_once()
            mock_client.stop.assert_called_once()

        asyncio.run(_run())

    def test_run_returns_assistant_content(self) -> None:
        """run() must return the assistant's message content.

        :author: Ron Webb
        :since: 0.1.0
        """
        content = "### Warning\n- Missing docstring on line 5"
        mock_session = _make_mock_session(content=content)
        mock_client = _make_mock_client(mock_session)

        async def _run() -> str:
            async with CodeReviewerSession(
                client_factory=lambda: mock_client
            ) as reviewer:
                return await reviewer.run("Review auth.py")

        result = asyncio.run(_run())
        assert result == content

    def test_no_plugin_dir_used(self) -> None:
        """The session must not forward any plugin-dir args to CopilotClient.

        :author: Ron Webb
        :since: 0.1.0
        """
        mock_session = _make_mock_session()
        mock_client = _make_mock_client(mock_session)

        async def _run() -> None:
            async with CodeReviewerSession(client_factory=lambda: mock_client):
                pass

        with patch(
            "sample_gh_copilot_sdk.code_reviewer.session.CopilotClient"
        ) as mock_cls:
            mock_cls.return_value = mock_client
            asyncio.run(_run())
            # CopilotClient() is never called because the factory is supplied;
            # the factory itself is a plain lambda — no RuntimeConnection involved.
            mock_cls.assert_not_called()
