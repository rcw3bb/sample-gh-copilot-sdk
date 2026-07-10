"""
Session hook handler functions for the GitHub Copilot SDK agent plugins demo.

Demonstrates pre/post tool-use hooks and a session-start hook.  Each handler
follows the SDK contract: it receives an ``input`` dict and an ``invocation``
dict, and returns a dict with the appropriate response keys.

:author: Ron Webb
:since: 0.1.0
"""

import logging

_LOG = logging.getLogger(__name__)


async def on_pre_tool_use(input_data: dict, invocation: dict) -> dict:
    """Intercept a tool call before execution.

    Logs the tool name and approves the call unconditionally.

    :param input_data: SDK-provided dict containing at least ``toolName``.
    :param invocation: Raw invocation context from the SDK.
    :return: Dict with ``permissionDecision`` set to ``"allow"``.
    :author: Ron Webb
    :since: 0.1.0
    """
    _ = invocation
    tool_name = input_data.get("toolName", "<unknown>")
    _LOG.debug("pre_tool_use: %s", tool_name)
    return {
        "permissionDecision": "allow",
        "additionalContext": f"Approved tool '{tool_name}' via pre-use hook.",
    }


async def on_post_tool_use(input_data: dict, invocation: dict) -> dict:
    """Process a successful tool result after execution.

    Logs the completed tool name and injects a brief audit note.

    :param input_data: SDK-provided dict containing at least ``toolName``.
    :param invocation: Raw invocation context from the SDK.
    :return: Dict with ``additionalContext`` for the model.
    :author: Ron Webb
    :since: 0.1.0
    """
    _ = invocation
    tool_name = input_data.get("toolName", "<unknown>")
    _LOG.debug("post_tool_use: %s completed", tool_name)
    return {"additionalContext": f"Tool '{tool_name}' completed successfully."}


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
            "Session initialised with custom agents and plugin directory. "
            "Use the 'analyze_code' or 'summarize_project' tools for code insights."
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
