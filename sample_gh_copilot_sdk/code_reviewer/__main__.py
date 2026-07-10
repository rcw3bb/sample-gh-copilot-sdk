"""
Interactive entry point for the GitHub Copilot SDK code-reviewer demo.

Run with::

    python -m sample_gh_copilot_sdk.code_reviewer

The script registers the code-reviewer agent inline (no plugin directory),
opens an interactive chat loop backed by the GitHub Copilot SDK, and outputs
structured Markdown code-review reports.  Press **Ctrl+C** or **Ctrl+D** (EOF)
to exit.

:author: Ron Webb
:since: 0.1.0
"""

import asyncio

from sample_gh_copilot_sdk._chat_loop import run_chat_loop
from sample_gh_copilot_sdk.code_reviewer.session import CodeReviewerSession

_BANNER = """\
╔══════════════════════════════════════════════════════╗
║   GitHub Copilot — Code Reviewer Demo (Inline)       ║
║   Agent:  code-reviewer (inline, no plugin dir)      ║
║   Tools:  view · grep · glob                         ║
╚══════════════════════════════════════════════════════╝
Model  : {model}
Type your prompts below.  Ctrl+C or Ctrl+D to exit.
"""


async def main() -> None:
    """Run the interactive Copilot code-reviewer demo chat loop.

    Creates a :class:`~sample_gh_copilot_sdk.code_reviewer.CodeReviewerSession`
    with the code-reviewer agent registered inline, then delegates to
    :func:`~sample_gh_copilot_sdk._chat_loop.run_chat_loop` until the user
    signals EOF or interrupt.

    :author: Ron Webb
    :since: 0.1.0
    """
    model = "gpt-5-mini"
    timeout = 600.0

    print(_BANNER.format(model=model))
    await run_chat_loop(CodeReviewerSession(model=model, timeout=timeout))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye!")
