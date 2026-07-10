# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-11

### Added

- Initial project scaffold with Poetry and PEP 621 configuration.
- Main package `sample_gh_copilot_sdk` with `env-dir-bootstrap` configuration directory bootstrapping.
- Logging support via `logenrich` with `logging.ini` bundled as a package resource.
- Development tooling: `black`, `pylint`, `pytest`, `pytest-cov`.
- MIT License.
- `agent_plugins` sub-package demonstrating the GitHub Copilot SDK agent-plugins feature set:
  - `AgentPluginSession` — async context manager that wires custom agents, tools, and session
    hooks, and loads plugin directories via `--plugin-dir` CLI flags.
  - Custom tools `analyze_code` and `summarize_project` defined with `@define_tool` and
    Pydantic parameter models; exposed through `get_tools()`.
  - Researcher (read-only) and editor (write-capable) custom-agent configurations with scoped
    tool access; composed via `build_agents_config()`.
  - Session hook handlers for pre/post tool-use and session-start events; assembled via
    `build_hooks()`.
  - Interactive chat entry point runnable as `python -m sample_gh_copilot_sdk.agent_plugins`.
  - Bundled `code_reviewer` plugin directory (`plugin.json` + `agents/code-reviewer.md`).
  - Test suite: 45 tests, 83 % coverage.
- `github-copilot-sdk` and `pydantic` added as main dependencies.
- README updated with prerequisites, usage, architecture diagram, and configuration reference.
