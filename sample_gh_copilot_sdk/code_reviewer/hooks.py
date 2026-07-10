"""
Session hook handler functions for the GitHub Copilot SDK code-reviewer demo.

``on_pre_tool_use`` and ``on_post_tool_use`` are shared with
:mod:`sample_gh_copilot_sdk.agent_plugins.hooks`; only ``on_session_start``
is specific to this package.

:author: Ron Webb
:since: 0.1.0
"""

import logging

from sample_gh_copilot_sdk.agent_plugins.hooks import on_post_tool_use, on_pre_tool_use

_LOG = logging.getLogger(__name__)


async def on_session_start(input_data: dict, invocation: dict) -> dict:
    """Run custom initialisation logic when the session starts.

    Logs the startup source and injects a context note for the model.

    :param input_data: SDK-provided dict containing at least ``source``.
    :param invocation: Raw invocation context from the SDK.
    :return: Dict with ``additionalContext`` for the model.
    :author: Ron Webb
    :since: 0.1.0
    """
    _ = invocation
    source = input_data.get("source", "<unknown>")
    _LOG.info("session_start: source=%s", source)
    return {
        "additionalContext": (
            "Code-reviewer session initialised with the inline agent. "
            "Use 'view', 'grep', or 'glob' to inspect files."
        )
    }


def build_hooks() -> dict:
    """Assemble the session-hooks dict ready to pass to ``create_session``.

    :return: A dict mapping SDK hook names to their async handler functions.
    :author: Ron Webb
    :since: 0.1.0
    """
    return {
        "on_pre_tool_use": on_pre_tool_use,
        "on_post_tool_use": on_post_tool_use,
        "on_session_start": on_session_start,
    }
