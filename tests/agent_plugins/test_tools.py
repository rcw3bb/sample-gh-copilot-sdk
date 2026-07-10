"""
Tests for sample_gh_copilot_sdk.agent_plugins.tools.

:author: Ron Webb
:since: 0.1.0
"""

import os
import asyncio
import tempfile

import pytest

from sample_gh_copilot_sdk.agent_plugins.tools import (
    CodeAnalysisParams,
    GlobParams,
    GrepParams,
    ProjectSummaryParams,
    ViewParams,
    _analyze_code_impl,
    _glob_impl,
    _grep_impl,
    _summarize_project_impl,
    _view_impl,
    get_tools,
)


class TestCodeAnalysisParams:
    """Tests for the CodeAnalysisParams Pydantic model.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_valid_params_are_accepted(self) -> None:
        """Valid keyword arguments should create the model without error.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = CodeAnalysisParams(file_path="main.py", language="python")
        assert params.file_path == "main.py"
        assert params.language == "python"

    def test_missing_language_raises_validation_error(self) -> None:
        """Omitting the required *language* field must raise a ValidationError.

        :author: Ron Webb
        :since: 0.1.0
        """
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CodeAnalysisParams(file_path="main.py")  # type: ignore[call-arg]

    def test_missing_file_path_raises_validation_error(self) -> None:
        """Omitting the required *file_path* field must raise a ValidationError.

        :author: Ron Webb
        :since: 0.1.0
        """
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CodeAnalysisParams(language="python")  # type: ignore[call-arg]


class TestProjectSummaryParams:
    """Tests for the ProjectSummaryParams Pydantic model.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_valid_param_is_accepted(self) -> None:
        """A valid *directory* value should be accepted.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = ProjectSummaryParams(directory="/some/dir")
        assert params.directory == "/some/dir"

    def test_missing_directory_raises_validation_error(self) -> None:
        """Omitting *directory* must raise a ValidationError.

        :author: Ron Webb
        :since: 0.1.0
        """
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ProjectSummaryParams()  # type: ignore[call-arg]


class TestAnalyzeCodeImpl:
    """Tests for the _analyze_code_impl async function.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_not_found_for_missing_file(self) -> None:
        """A non-existent path should return a 'not found' message.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = CodeAnalysisParams(file_path="/no/such/file.py", language="python")
        result = asyncio.run(_analyze_code_impl(params))
        assert "File not found" in result

    def test_returns_summary_for_existing_file(self) -> None:
        """A real file should produce a multi-line summary with line count and size.

        :author: Ron Webb
        :since: 0.1.0
        """
        content = "x = 1\ny = 2\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            params = CodeAnalysisParams(file_path=tmp_path, language="python")
            result = asyncio.run(_analyze_code_impl(params))
            assert "Lines: 3" in result
            assert "Language: python" in result
        finally:
            os.unlink(tmp_path)


class TestSummarizeProjectImpl:
    """Tests for the _summarize_project_impl async function.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_not_found_for_missing_dir(self) -> None:
        """A non-existent directory should return a 'not found' message.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = ProjectSummaryParams(directory="/no/such/directory")
        result = asyncio.run(_summarize_project_impl(params))
        assert "Directory not found" in result

    def test_returns_summary_for_existing_dir(self) -> None:
        """An existing directory should produce file and sub-directory counts.

        :author: Ron Webb
        :since: 0.1.0
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create one file and one sub-directory
            with open(os.path.join(tmp_dir, "readme.txt"), "w", encoding="utf-8") as fh:
                fh.write("hi")
            os.makedirs(os.path.join(tmp_dir, "src"))
            params = ProjectSummaryParams(directory=tmp_dir)
            result = asyncio.run(_summarize_project_impl(params))
        assert "Files: 1" in result
        assert "Subdirectories: 1" in result


class TestGetTools:
    """Tests for the get_tools factory function.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_five_tools(self) -> None:
        """get_tools() must return exactly five tool objects.

        :author: Ron Webb
        :since: 0.1.0
        """
        tools = get_tools()
        assert len(tools) == 5

    def test_returns_new_instances_each_call(self) -> None:
        """Each invocation of get_tools() should produce fresh instances.

        :author: Ron Webb
        :since: 0.1.0
        """
        assert get_tools() is not get_tools()


class TestViewParams:
    """Tests for the ViewParams Pydantic model.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_defaults_are_applied(self) -> None:
        """start_line should default to 1 and end_line to None.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = ViewParams(file_path="main.py")
        assert params.start_line == 1
        assert params.end_line is None

    def test_custom_range_is_stored(self) -> None:
        """Explicit start_line and end_line values must be stored correctly.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = ViewParams(file_path="main.py", start_line=5, end_line=10)
        assert params.start_line == 5
        assert params.end_line == 10


class TestViewImpl:
    """Tests for the _view_impl async function.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_not_found_for_missing_file(self) -> None:
        """A non-existent path should return a 'not found' message.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = ViewParams(file_path="/no/such/file.txt")
        result = asyncio.run(_view_impl(params))
        assert "File not found" in result

    def test_returns_numbered_lines(self) -> None:
        """Lines must be prefixed with their 1-based line number.

        :author: Ron Webb
        :since: 0.1.0
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write("alpha\nbeta\ngamma\n")
            tmp_path = tmp.name
        try:
            params = ViewParams(file_path=tmp_path)
            result = asyncio.run(_view_impl(params))
            assert "1: alpha" in result
            assert "3: gamma" in result
        finally:
            os.unlink(tmp_path)

    def test_respects_line_range(self) -> None:
        """Only lines within [start_line, end_line] should be returned.

        :author: Ron Webb
        :since: 0.1.0
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write("one\ntwo\nthree\nfour\n")
            tmp_path = tmp.name
        try:
            params = ViewParams(file_path=tmp_path, start_line=2, end_line=3)
            result = asyncio.run(_view_impl(params))
            assert "two" in result
            assert "three" in result
            assert "one" not in result
            assert "four" not in result
        finally:
            os.unlink(tmp_path)


class TestGrepParams:
    """Tests for the GrepParams Pydantic model.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_valid_params_are_accepted(self) -> None:
        """Valid keyword arguments should create the model without error.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = GrepParams(pattern="def ", path="/src")
        assert params.pattern == "def "
        assert params.recursive is True


class TestGrepImpl:
    """Tests for the _grep_impl async function.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_invalid_pattern_message(self) -> None:
        """An invalid regex should return an error message.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = GrepParams(pattern="[invalid", path=".")
        result = asyncio.run(_grep_impl(params))
        assert "Invalid pattern" in result

    def test_returns_no_matches_message(self) -> None:
        """When no lines match the pattern, a 'no matches' message is returned.

        :author: Ron Webb
        :since: 0.1.0
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write("hello world\n")
            tmp_path = tmp.name
        try:
            params = GrepParams(pattern="NOMATCH", path=tmp_path)
            result = asyncio.run(_grep_impl(params))
            assert "No matches found" in result
        finally:
            os.unlink(tmp_path)

    def test_returns_matching_lines_with_annotation(self) -> None:
        """Matching lines must include filepath and line number prefix.

        :author: Ron Webb
        :since: 0.1.0
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write("def foo():\n    pass\n")
            tmp_path = tmp.name
        try:
            params = GrepParams(pattern=r"def \w+", path=tmp_path)
            result = asyncio.run(_grep_impl(params))
            assert "def foo" in result
            assert ":1:" in result
        finally:
            os.unlink(tmp_path)

    def test_returns_not_found_for_missing_path(self) -> None:
        """A non-existent path should return a 'not found' message.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = GrepParams(pattern="x", path="/no/such/path")
        result = asyncio.run(_grep_impl(params))
        assert "Path not found" in result


class TestGlobParams:
    """Tests for the GlobParams Pydantic model.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_defaults_are_applied(self) -> None:
        """root should default to '.'.

        :author: Ron Webb
        :since: 0.1.0
        """
        params = GlobParams(pattern="**/*.py")
        assert params.root == "."


class TestGlobImpl:
    """Tests for the _glob_impl async function.

    :author: Ron Webb
    :since: 0.1.0
    """

    def test_returns_no_files_matched_when_empty(self) -> None:
        """A pattern that matches nothing should return a 'no files matched' message.

        :author: Ron Webb
        :since: 0.1.0
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            params = GlobParams(pattern="*.xyz", root=tmp_dir)
            result = asyncio.run(_glob_impl(params))
        assert "No files matched" in result

    def test_returns_matching_files(self) -> None:
        """Files matching the pattern must appear in the result.

        :author: Ron Webb
        :since: 0.1.0
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            py_file = os.path.join(tmp_dir, "script.py")
            with open(py_file, "w", encoding="utf-8") as file_handle:
                file_handle.write("")
            params = GlobParams(pattern="*.py", root=tmp_dir)
            result = asyncio.run(_glob_impl(params))
        assert "script.py" in result
