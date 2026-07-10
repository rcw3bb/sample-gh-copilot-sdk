"""
BaseSession: shared Copilot session lifecycle for the GitHub Copilot SDK demos.

Provides common client construction, content extraction, context manager teardown,
and prompt dispatching.  Subclasses implement :meth:`_session_kwargs` to supply
the agent, tool, and hook configuration specific to their use case.

:author: Ron Webb
:since: 0.1.0
"""

import collections.abc
from types import TracebackType
from typing import Any

from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.session_events import AssistantMessageData


class BaseSession:
    """Shared lifecycle manager for GitHub Copilot SDK session wrappers.

    Handles client construction, content extraction, context-manager teardown,
    and prompt dispatching.  Concrete subclasses provide session-specific
    configuration by implementing :meth:`_session_kwargs`.

    :author: Ron Webb
    :since: 0.1.0
    """

    def __init__(
        self,
        model: str = "gpt-5-mini",
        timeout: float = 300.0,
        client_factory: collections.abc.Callable[[], CopilotClient] | None = None,
    ) -> None:
        """Initialise common session parameters.

        :param model: Model identifier forwarded to ``create_session``.
        :param timeout: Seconds to wait for a reply.  Defaults to ``300.0``.
        :param client_factory: Optional callable returning a
            :class:`~copilot.CopilotClient`; used for dependency injection in tests.
        :author: Ron Webb
        :since: 0.1.0
        """
        self._model: str = model
        self._timeout: float = timeout
        self._client_factory = client_factory
        self._client: CopilotClient | None = None
        self._session: Any = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_client(self) -> CopilotClient:
        """Construct a :class:`~copilot.CopilotClient` for this session.

        If a *client_factory* was supplied it is called and its return value used
        directly; otherwise a plain default client is returned.  Subclasses may
        override this to pass additional constructor arguments.

        :return: A configured :class:`~copilot.CopilotClient` instance.
        :author: Ron Webb
        :since: 0.1.0
        """
        if self._client_factory is not None:
            return self._client_factory()
        return CopilotClient()

    def _extract_content(self, reply: Any) -> str:
        """Extract the assistant message text from a ``send_and_wait`` reply.

        :param reply: The event object returned by ``session.send_and_wait``, or
            ``None`` if no reply was produced.
        :return: The assistant's message content, or an empty string.
        :author: Ron Webb
        :since: 0.1.0
        """
        if reply is None:
            return ""
        data = getattr(reply, "data", None)
        if isinstance(data, AssistantMessageData):
            return data.content
        return ""

    def _session_kwargs(self) -> dict:
        """Return keyword arguments for ``client.create_session``.

        Subclasses must override this to provide their specific agents, tools,
        and hooks.

        :return: Dict of keyword arguments.
        :raises NotImplementedError: When called on the base class directly.
        :author: Ron Webb
        :since: 0.1.0
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement _session_kwargs()"
        )

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "BaseSession":
        """Start the Copilot client and open a session using :meth:`_session_kwargs`.

        :return: This session instance.
        :author: Ron Webb
        :since: 0.1.0
        """
        self._client = self._build_client()
        await self._client.start()
        self._session = await self._client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model=self._model,
            **self._session_kwargs(),
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
                f"Session not started — use "
                f"'async with {type(self).__name__}() as s:'."
            )
        reply = await self._session.send_and_wait(prompt, timeout=self._timeout)
        return self._extract_content(reply)
