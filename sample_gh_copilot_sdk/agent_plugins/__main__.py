"""
Interactive entry point for the GitHub Copilot agent plugins demonstration.

Run with::

    python -m sample_gh_copilot_sdk.agent_plugins

The script loads the bundled ``code_reviewer`` plugin directory, registers the
researcher and editor custom agents, and opens an interactive chat loop backed
by the GitHub Copilot SDK.  Press **Ctrl+C** or **Ctrl+D** (EOF) to exit.

:author: Ron Webb
:since: 0.1.0
"""

import asyncio
import pathlib

from sample_gh_copilot_sdk._chat_loop import run_chat_loop
from sample_gh_copilot_sdk.agent_plugins.session import AgentPluginSession

_BANNER = """\
╔══════════════════════════════════════════════════════╗
║   GitHub Copilot — Agent Plugins Demo                ║
║   Custom agents: researcher · editor                 ║
║   Custom tools:  analyze_code · summarize_project    ║
╚══════════════════════════════════════════════════════╝
Plugin : {plugin}
Model  : {model}
Type your prompts below.  Ctrl+C or Ctrl+D to exit.
"""


async def main() -> None:
    """Run the interactive Copilot agent-plugins demo chat loop.

    Resolves the bundled ``code_reviewer`` plugin directory relative to this
    file, creates an :class:`~sample_gh_copilot_sdk.agent_plugins.AgentPluginSession`
    with that plugin loaded, then delegates to
    :func:`~sample_gh_copilot_sdk._chat_loop.run_chat_loop` until the user
    signals EOF or interrupt.

    :author: Ron Webb
    :since: 0.1.0
    """
    plugin_path = pathlib.Path(__file__).parent / "plugins" / "code_reviewer"
    model = "gpt-5-mini"
    timeout = 600.0

    print(_BANNER.format(plugin=plugin_path, model=model))
    await run_chat_loop(
        AgentPluginSession(plugin_dirs=[str(plugin_path)], model=model, timeout=timeout)
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye!")
