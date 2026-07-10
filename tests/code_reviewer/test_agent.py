"""
Tests for sample_gh_copilot_sdk.code_reviewer.agent.

:author: Ron Webb
:since: 0.1.0
"""

from sample_gh_copilot_sdk.code_reviewer.agent import build_code_reviewer_config


class TestBuildCodeReviewerConfig:
    """Tests for build_code_reviewer_config().

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_has_required_fields(self) -> None:
        """The config must contain 'name' and 'prompt'.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_code_reviewer_config()
        assert "name" in config
        assert "prompt" in config

    def test_name_is_code_reviewer(self) -> None:
        """The agent name must be 'code-reviewer'.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_code_reviewer_config()
        assert config["name"] == "code-reviewer"

    def test_tools_are_read_only(self) -> None:
        """The code-reviewer must only have access to read-only tools.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_code_reviewer_config()
        tools = config.get("tools") or []
        write_tools = {"edit_file", "bash", "insert_edit_into_file"}
        assert not set(tools) & write_tools

    def test_tools_include_view_grep_glob(self) -> None:
        """The agent must be configured with the view, grep, and glob tools.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_code_reviewer_config()
        tools = set(config.get("tools") or [])
        assert {"view", "grep", "glob"} <= tools

    def test_prompt_mentions_owasp(self) -> None:
        """The inline prompt must reference OWASP security guidance.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_code_reviewer_config()
        assert "OWASP" in config["prompt"]

    def test_infer_is_true(self) -> None:
        """The code-reviewer agent must be available for automatic selection.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_code_reviewer_config()
        assert config.get("infer") is True

    def test_description_is_non_empty(self) -> None:
        """The description field must be a non-empty string.

        :author: Ron Webb
        :since: 0.1.0
        """
        config = build_code_reviewer_config()
        assert config.get("description")
