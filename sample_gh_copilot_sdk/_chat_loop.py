"""
Shared interactive chat loop for GitHub Copilot SDK session demos.

Provides a single ``run_chat_loop`` coroutine used by all demo entry points so
the input/output logic is not duplicated across packages.

:author: Ron Webb
:since: 0.1.0
"""

from typing import Any


async def run_chat_loop(session: Any) -> None:
    """Run an interactive prompt loop against *session*.

    Enters the *session* context manager, reads user input from stdin in a loop,
    forwards each non-empty prompt to the session, and prints the assistant's
    reply.  The loop ends on EOF (Ctrl+D) or an empty read.

    :param session: A session object that supports ``async with`` and exposes
        an async ``run(prompt: str) -> str`` method.
    :author: Ron Webb
    :since: 0.1.0
    """
    async with session as active_session:
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                break
            if not user_input:
                continue
            print()
            response = await active_session.run(user_input)
            print(f"Assistant: {response}\n")

    print("Session closed.")
