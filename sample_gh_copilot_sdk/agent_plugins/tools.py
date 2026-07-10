"""
Custom tool definitions for the GitHub Copilot SDK agent plugins demo.

Demonstrates how to define custom tools using the :func:`copilot.define_tool`
factory with Pydantic models for parameter validation and automatic JSON-schema
generation.

:author: Ron Webb
:since: 0.1.0
"""

import glob as glob_module
import os
import re
from typing import Any

from pydantic import BaseModel, Field

from copilot import define_tool


class CodeAnalysisParams(BaseModel):
    """Parameters accepted by the ``analyze_code`` tool.

    :author: Ron Webb
    :since: 0.1.0
    """

    file_path: str = Field(
        description="Absolute or relative path to the source file to analyse"
    )
    language: str = Field(
        description="Programming language of the source file, e.g. 'python' or 'typescript'"
    )


class ProjectSummaryParams(BaseModel):
    """Parameters accepted by the ``summarize_project`` tool.

    :author: Ron Webb
    :since: 0.1.0
    """

    directory: str = Field(
        description="Path to the project root directory to summarise"
    )


async def _analyze_code_impl(params: CodeAnalysisParams) -> str:
    """Return a brief structural summary of the specified source file.

    :param params: Validated tool parameters.
    :return: A multi-line summary string describing the file.
    :author: Ron Webb
    :since: 0.1.0
    """
    if not os.path.isfile(params.file_path):
        return f"File not found: {params.file_path}"
    with open(params.file_path, encoding="utf-8") as source_file:
        content = source_file.read()
    line_count = content.count("\n") + 1
    return (
        f"File: {params.file_path}\n"
        f"Language: {params.language}\n"
        f"Lines: {line_count}\n"
        f"Size: {len(content)} bytes"
    )


async def _summarize_project_impl(params: ProjectSummaryParams) -> str:
    """Return a top-level directory listing with file and sub-directory counts.

    :param params: Validated tool parameters.
    :return: A multi-line summary string describing the directory.
    :author: Ron Webb
    :since: 0.1.0
    """
    if not os.path.isdir(params.directory):
        return f"Directory not found: {params.directory}"
    entries = os.listdir(params.directory)
    file_count = sum(
        1 for entry in entries if os.path.isfile(os.path.join(params.directory, entry))
    )
    dir_count = sum(
        1 for entry in entries if os.path.isdir(os.path.join(params.directory, entry))
    )
    visible = sorted(entries)[:10]
    return (
        f"Directory: {params.directory}\n"
        f"Files: {file_count}\n"
        f"Subdirectories: {dir_count}\n"
        f"Top entries: {', '.join(visible)}"
    )


# ---------------------------------------------------------------------------
# view / grep / glob — required by the bundled code-reviewer plugin agent
# ---------------------------------------------------------------------------


class ViewParams(BaseModel):
    """Parameters accepted by the ``view`` tool.

    :author: Ron Webb
    :since: 0.1.0
    """

    file_path: str = Field(description="Path to the file to view")
    start_line: int = Field(default=1, description="First line to display (1-based)")
    end_line: int | None = Field(
        default=None,
        description="Last line to display (inclusive); omit for end of file",
    )


class GrepParams(BaseModel):
    """Parameters accepted by the ``grep`` tool.

    :author: Ron Webb
    :since: 0.1.0
    """

    pattern: str = Field(description="Regular expression to search for")
    path: str = Field(description="File or directory path to search in")
    recursive: bool = Field(
        default=True, description="Search recursively in subdirectories"
    )


class GlobParams(BaseModel):
    """Parameters accepted by the ``glob`` tool.

    :author: Ron Webb
    :since: 0.1.0
    """

    pattern: str = Field(description="Glob pattern to match files, e.g. '**/*.py'")
    root: str = Field(
        default=".", description="Root directory from which to expand the pattern"
    )


async def _view_impl(params: ViewParams) -> str:
    """Return the content of a file, optionally restricted to a line range.

    :param params: Validated tool parameters.
    :return: Numbered lines of the file, or an error message.
    :author: Ron Webb
    :since: 0.1.0
    """
    if not os.path.isfile(params.file_path):
        return f"File not found: {params.file_path}"
    with open(params.file_path, encoding="utf-8", errors="replace") as file_handle:
        lines = file_handle.readlines()
    start = max(params.start_line - 1, 0)
    end = len(lines) if params.end_line is None else params.end_line
    selected = lines[start:end]
    return "".join(f"{start + idx + 1}: {line}" for idx, line in enumerate(selected))


async def _grep_impl(params: GrepParams) -> str:
    """Search *path* for lines matching *pattern* and return annotated matches.

    :param params: Validated tool parameters.
    :return: Matching lines prefixed with ``filepath:lineno:``, or a message when
        nothing matched.
    :author: Ron Webb
    :since: 0.1.0
    """
    try:
        compiled = re.compile(params.pattern)
    except re.error as exc:
        return f"Invalid pattern: {exc}"

    if os.path.isfile(params.path):
        file_list = [params.path]
    elif os.path.isdir(params.path):
        if params.recursive:
            file_list = [
                os.path.join(root, fname)
                for root, _dirs, fnames in os.walk(params.path)
                for fname in fnames
            ]
        else:
            file_list = [
                os.path.join(params.path, entry)
                for entry in os.listdir(params.path)
                if os.path.isfile(os.path.join(params.path, entry))
            ]
    else:
        return f"Path not found: {params.path}"

    results: list[str] = []
    for filepath in sorted(file_list):
        try:
            with open(filepath, encoding="utf-8", errors="replace") as file_handle:
                for lineno, line in enumerate(file_handle, start=1):
                    if compiled.search(line):
                        results.append(f"{filepath}:{lineno}: {line.rstrip()}")
        except OSError:
            pass

    return "\n".join(results) if results else "No matches found."


async def _glob_impl(params: GlobParams) -> str:
    """Return a newline-separated list of paths matching *pattern* under *root*.

    :param params: Validated tool parameters.
    :return: Matching paths, one per line, or a message when nothing matched.
    :author: Ron Webb
    :since: 0.1.0
    """
    full_pattern = os.path.join(params.root, params.pattern)
    matches = sorted(glob_module.glob(full_pattern, recursive=True))
    return "\n".join(matches) if matches else "No files matched."


def get_tools() -> list[Any]:
    """Create and return the list of SDK tool instances for session registration.

    Each call produces fresh tool objects so sessions remain independent.

    :return: A list containing the ``analyze_code``, ``summarize_project``,
        ``view``, ``grep``, and ``glob`` tools.
    :author: Ron Webb
    :since: 0.1.0
    """
    analyze_code = define_tool(
        name="analyze_code",
        description="Analyse a source file for structure and size. Read-only — no changes.",
        skip_permission=True,
    )(_analyze_code_impl)

    summarize_project = define_tool(
        name="summarize_project",
        description="List top-level contents of a project directory and count files.",
        skip_permission=True,
    )(_summarize_project_impl)

    view_tool = define_tool(
        name="view",
        description="Read a file and return its content with line numbers.",
        overrides_built_in_tool=True,
        skip_permission=True,
    )(_view_impl)

    grep_tool = define_tool(
        name="grep",
        description="Search files for lines matching a regular expression.",
        overrides_built_in_tool=True,
        skip_permission=True,
    )(_grep_impl)

    glob_tool = define_tool(
        name="glob",
        description="List files matching a glob pattern under a root directory.",
        overrides_built_in_tool=True,
        skip_permission=True,
    )(_glob_impl)

    return [analyze_code, summarize_project, view_tool, grep_tool, glob_tool]
