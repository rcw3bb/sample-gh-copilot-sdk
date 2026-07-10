"""
Custom agent configuration builders for the GitHub Copilot SDK agent plugins demo.

Demonstrates how to define specialised sub-agents with scoped tool access so
that the Copilot runtime can delegate tasks automatically via intent matching.

:author: Ron Webb
:since: 0.1.0
"""

from typing import NotRequired, Required, TypedDict


class AgentConfig(TypedDict, total=False):
    """Typed structure for a single custom-agent configuration dict.

    Only ``name`` and ``prompt`` are required; all other fields are optional.

    :author: Ron Webb
    :since: 0.1.0
    """

    name: Required[str]
    prompt: Required[str]
    display_name: NotRequired[str]
    description: NotRequired[str]
    tools: NotRequired[list[str] | None]
    infer: NotRequired[bool]


def build_researcher_config() -> AgentConfig:
    """Return the configuration dict for the read-only researcher agent.

    The researcher can explore code using ``grep``, ``glob``, and ``view``
    but cannot modify any files, keeping its impact strictly read-only.

    :return: An :class:`AgentConfig` describing the researcher agent.
    :author: Ron Webb
    :since: 0.1.0
    """
    return AgentConfig(
        name="researcher",
        display_name="Research Agent",
        description=(
            "Explores codebases, answers questions about code structure, "
            "and gathers context using read-only tools."
        ),
        tools=["grep", "glob", "view"],
        prompt=(
            "You are a research assistant specialised in code exploration. "
            "Analyse the codebase and answer questions accurately. "
            "Do NOT modify any files."
        ),
        infer=True,
    )


def build_editor_config() -> AgentConfig:
    """Return the configuration dict for the write-capable editor agent.

    The editor can read and modify files and run shell commands, making it
    suitable for targeted code changes requested by the user.

    :return: An :class:`AgentConfig` describing the editor agent.
    :author: Ron Webb
    :since: 0.1.0
    """
    return AgentConfig(
        name="editor",
        display_name="Editor Agent",
        description=(
            "Makes targeted, minimal code changes to files as instructed. "
            "Focuses on surgical edits and verifies correctness after each change."
        ),
        tools=["view", "edit_file", "bash"],
        prompt=(
            "You are a precise code editor. "
            "Make minimal, surgical changes as requested. "
            "Always verify that modified files are syntactically correct."
        ),
        infer=True,
    )


def build_agents_config() -> list[AgentConfig]:
    """Return the complete list of custom-agent configs for a session.

    :return: A list containing the researcher and editor agent configurations.
    :author: Ron Webb
    :since: 0.1.0
    """
    return [build_researcher_config(), build_editor_config()]
