"""
Tests for sample_gh_copilot_sdk.agent_plugins.hooks.

:author: Ron Webb
:since: 0.1.0
"""

import asyncio

from sample_gh_copilot_sdk.agent_plugins.hooks import (
    build_hooks,
    on_post_tool_use,
    on_pre_tool_use,
    on_session_start,
)


class TestOnPreToolUse:
    """Tests for the on_pre_tool_use hook handler.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_allow_decision(self) -> None:
        """The handler must return a dict with permissionDecision set to 'allow'.

        :author: Ron Webb
        :since: 0.1.0
        """
        result = asyncio.run(on_pre_tool_use({"toolName": "bash"}, {}))
        assert result["permissionDecision"] == "allow"

    def test_includes_additional_context(self) -> None:
        """The handler must include an additionalContext key in its response.

        :author: Ron Webb
        :since: 0.1.0
        """
        result = asyncio.run(on_pre_tool_use({"toolName": "view"}, {}))
        assert "additionalContext" in result

    def test_handles_missing_tool_name(self) -> None:
        """Missing toolName in input_data must not raise an exception.

        :author: Ron Webb
        :since: 0.1.0
        """
        result = asyncio.run(on_pre_tool_use({}, {}))
        assert result["permissionDecision"] == "allow"


class TestOnPostToolUse:
    """Tests for the on_post_tool_use hook handler.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_additional_context(self) -> None:
        """The handler must return a dict with an additionalContext key.

        :author: Ron Webb
        :since: 0.1.0
        """
        result = asyncio.run(on_post_tool_use({"toolName": "view"}, {}))
        assert "additionalContext" in result

    def test_context_mentions_tool_name(self) -> None:
        """The additionalContext value should reference the tool that completed.

        :author: Ron Webb
        :since: 0.1.0
        """
        result = asyncio.run(on_post_tool_use({"toolName": "grep"}, {}))
        assert "grep" in result["additionalContext"]

    def test_handles_missing_tool_name(self) -> None:
        """Missing toolName must not raise an exception.

        :author: Ron Webb
        :since: 0.1.0
        """
        result = asyncio.run(on_post_tool_use({}, {}))
        assert "additionalContext" in result


class TestOnSessionStart:
    """Tests for the on_session_start hook handler.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_additional_context(self) -> None:
        """The handler must return a dict with an additionalContext key.

        :author: Ron Webb
        :since: 0.1.0
        """
        result = asyncio.run(on_session_start({"source": "startup"}, {}))
        assert "additionalContext" in result

    def test_handles_missing_source(self) -> None:
        """Missing source key must not raise an exception.

        :author: Ron Webb
        :since: 0.1.0
        """
        result = asyncio.run(on_session_start({}, {}))
        assert "additionalContext" in result


class TestBuildHooks:
    """Tests for the build_hooks convenience function.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_dict_with_three_keys(self) -> None:
        """build_hooks() must return a dict containing exactly three hook entries.

        :author: Ron Webb
        :since: 0.1.0
        """
        hooks = build_hooks()
        assert len(hooks) == 3

    def test_contains_expected_hook_names(self) -> None:
        """The returned dict must contain all three expected hook-name keys.

        :author: Ron Webb
        :since: 0.1.0
        """
        hooks = build_hooks()
        assert "on_pre_tool_use" in hooks
        assert "on_post_tool_use" in hooks
        assert "on_session_start" in hooks

    def test_hook_values_are_callable(self) -> None:
        """Each value in the hooks dict must be callable (async functions).

        :author: Ron Webb
        :since: 0.1.0
        """
        for handler in build_hooks().values():
            assert callable(handler)
