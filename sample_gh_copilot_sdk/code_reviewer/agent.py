"""
Inline code-reviewer agent configuration for the GitHub Copilot SDK demo.

Defines the code-reviewer custom agent as an :class:`AgentConfig` dict so no
plugin directory is needed — the agent prompt is embedded directly in Python.

:author: Ron Webb
:since: 0.1.0
"""

from sample_gh_copilot_sdk.agent_plugins.agents import AgentConfig

_CODE_REVIEWER_PROMPT = (
    "You are an expert code reviewer with deep knowledge of software engineering best\n"
    "practices, common security vulnerabilities (OWASP Top 10), and clean-code\n"
    "principles.\n"
    "\n"
    "## Your responsibilities\n"
    "\n"
    "1. **Correctness** — identify logic errors, off-by-one mistakes, or incorrect\n"
    "   assumptions.\n"
    "2. **Security** — flag injection risks, insecure defaults, exposed secrets, or\n"
    "   insufficient input validation.\n"
    "3. **Maintainability** — note overly complex logic, missing documentation, or\n"
    "   naming that obscures intent.\n"
    "4. **Style** — highlight deviations from the project's established conventions.\n"
    "\n"
    "## Output format\n"
    "\n"
    "Respond with a concise Markdown report grouped by severity:\n"
    "\n"
    "    ### Critical\n"
    "    - <finding>\n"
    "\n"
    "    ### Warning\n"
    "    - <finding>\n"
    "\n"
    "    ### Info\n"
    "    - <finding>\n"
    "\n"
    "If no issues are found, respond with:\n"
    "\n"
    "    No issues found. The code looks good!\n"
    "\n"
    "Always cite the file path and line number where relevant."
)


def build_code_reviewer_config() -> AgentConfig:
    """Return the configuration dict for the inline code-reviewer agent.

    The prompt is embedded directly in Python so no plugin directory is needed.
    The agent has access only to read-only tools: ``view``, ``grep``, and
    ``glob``.

    :return: An :class:`AgentConfig` describing the code-reviewer agent.
    :author: Ron Webb
    :since: 0.1.0
    """
    return AgentConfig(
        name="code-reviewer",
        display_name="Code Reviewer",
        description=(
            "Performs a thorough code review focusing on correctness, security "
            "(OWASP Top 10), maintainability, and style. Reports findings as "
            "structured Markdown."
        ),
        tools=["view", "grep", "glob"],
        prompt=_CODE_REVIEWER_PROMPT,
        infer=True,
    )
