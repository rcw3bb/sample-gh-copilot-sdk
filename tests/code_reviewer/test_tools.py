"""
Tests for sample_gh_copilot_sdk.code_reviewer.tools.

:author: Ron Webb
:since: 0.1.0
"""

from sample_gh_copilot_sdk.code_reviewer.tools import get_tools


class TestGetTools:
    """Tests for the get_tools factory function.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_three_tools(self) -> None:
        """get_tools() must return exactly three tool objects (view, grep, glob).

        :author: Ron Webb
        :since: 0.1.0
        """
        tools = get_tools()
        assert len(tools) == 3

    def test_returns_new_instances_each_call(self) -> None:
        """Each invocation of get_tools() should produce fresh instances.

        :author: Ron Webb
        :since: 0.1.0
        """
        assert get_tools() is not get_tools()

    def test_all_tools_are_non_none(self) -> None:
        """All returned tool objects must be non-None.

        :author: Ron Webb
        :since: 0.1.0
        """
        for tool in get_tools():
            assert tool is not None
