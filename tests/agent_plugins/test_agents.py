"""
Tests for sample_gh_copilot_sdk.agent_plugins.agents.

:author: Ron Webb
:since: 0.1.0
"""

from sample_gh_copilot_sdk.agent_plugins.agents import (
    build_agents_config,
    build_editor_config,
    build_researcher_config,
)


class TestBuildResearcherConfig:
    """Tests for build_researcher_config().

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_has_required_fields(self) -> None:
        """The config must contain 'name' and 'prompt'.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_researcher_config()
        assert "name" in config
        assert "prompt" in config

    def test_name_is_researcher(self) -> None:
        """The agent name must be 'researcher'.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_researcher_config()
        assert config["name"] == "researcher"

    def test_tools_are_read_only(self) -> None:
        """The researcher must be restricted to non-modifying tools only.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_researcher_config()
        tools = config.get("tools") or []
        write_tools = {"edit_file", "bash", "insert_edit_into_file"}
        assert not set(tools) & write_tools

    def test_infer_is_true(self) -> None:
        """The researcher agent must be available for automatic selection.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_researcher_config()
        assert config.get("infer") is True


class TestBuildEditorConfig:
    """Tests for build_editor_config().

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_has_required_fields(self) -> None:
        """The config must contain 'name' and 'prompt'.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_editor_config()
        assert "name" in config
        assert "prompt" in config

    def test_name_is_editor(self) -> None:
        """The agent name must be 'editor'.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_editor_config()
        assert config["name"] == "editor"

    def test_tools_include_edit_capability(self) -> None:
        """The editor must have access to at least one file-editing tool.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_editor_config()
        tools = config.get("tools") or []
        assert "edit_file" in tools

    def test_description_is_non_empty(self) -> None:
        """The description field must be a non-empty string.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_editor_config()
        assert isinstance(config.get("description"), str)
        assert len(config["description"]) > 0  # type: ignore[arg-type]


class TestBuildAgentsConfig:
    """Tests for build_agents_config().

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_two_agents(self) -> None:
        """build_agents_config() must return exactly two agent configurations.

        :author: Ron Webb
        :since: 0.1.0
        """
        configs = build_agents_config()
        assert len(configs) == 2

    def test_contains_researcher_and_editor(self) -> None:
        """The list must contain agents named 'researcher' and 'editor'.

        :author: Ron Webb
        :since: 0.1.0
        """
        names = {cfg["name"] for cfg in build_agents_config()}
        assert "researcher" in names
        assert "editor" in names

    def test_returns_new_list_each_call(self) -> None:
        """Each invocation must return a distinct list object.

        :author: Ron Webb
        :since: 0.1.0
        """
        assert build_agents_config() is not build_agents_config()
