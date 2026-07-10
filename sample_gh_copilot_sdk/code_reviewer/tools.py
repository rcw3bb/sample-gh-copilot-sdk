"""
Tool definitions for the GitHub Copilot SDK code-reviewer demo.

Registers the read-only ``view``, ``grep``, and ``glob`` tools required by the
inline code-reviewer agent.  Tool creation is delegated to
:func:`~sample_gh_copilot_sdk.agent_plugins.tools.build_review_tools` so the
definitions live in a single place.

:author: Ron Webb
:since: 0.1.0
"""

from typing import Any

from sample_gh_copilot_sdk.agent_plugins.tools import build_review_tools


def get_tools() -> list[Any]:
    """Create and return the list of SDK tool instances for the code-reviewer session.

    Each call produces fresh tool objects so sessions remain independent.
    Only the read-only ``view``, ``grep``, and ``glob`` tools are registered —
    write-capable tools are intentionally excluded.

    :return: A list containing the ``view``, ``grep``, and ``glob`` tools.
    :author: Ron Webb
    :since: 0.1.0
    """
    return build_review_tools()
