## Purpose

This repo is `sample-gh-copilot-sdk`, a Python reference application demonstrating how to extend
GitHub Copilot with custom agents and plugin-based capabilities so it can perform specialized tasks
within a structured workflow.

**Stack:** Python `>=3.14`, Poetry 2.x (PEP 621), `logenrich` for logging, `env-dir-bootstrap`
for configuration directory bootstrapping.

**Dev tooling:** Black (formatting), Pylint (linting, must score 10/10), Pytest + Pytest-Cov
(tests, minimum 80% coverage).

**Key commands:**
- `poetry install` — install all dependencies
- `poetry run black sample_gh_copilot_sdk; poetry run pylint sample_gh_copilot_sdk` — format and lint
- `poetry run pytest --cov=sample_gh_copilot_sdk tests --cov-report html` — run tests with coverage

## Tree

- `sample_gh_copilot_sdk/` — main package
- `sample_gh_copilot_sdk/__init__.py` — package init: version, env-dir-bootstrap setup, logenrich logger init
- `sample_gh_copilot_sdk/logging.ini` — logging config bundled as a package resource
- `sample_gh_copilot_sdk/agent_plugins/` — agent plugins demo sub-package (run: `python -m sample_gh_copilot_sdk.agent_plugins`)
- `sample_gh_copilot_sdk/agent_plugins/__init__.py` — sub-package init; re-exports public symbols
- `sample_gh_copilot_sdk/agent_plugins/__main__.py` — interactive chat loop entry point
- `sample_gh_copilot_sdk/agent_plugins/agents.py` — `AgentConfig` TypedDict + researcher/editor config builders
- `sample_gh_copilot_sdk/agent_plugins/hooks.py` — pre/post tool-use and session-start hook handlers + `build_hooks()`
- `sample_gh_copilot_sdk/agent_plugins/session.py` — `AgentPluginSession` class: plugin-dir loading, custom agents, tools, hooks
- `sample_gh_copilot_sdk/agent_plugins/tools.py` — `@define_tool` custom tools (`analyze_code`, `summarize_project`) + `get_tools()`
- `sample_gh_copilot_sdk/agent_plugins/plugins/code_reviewer/` — bundled sample plugin directory
- `sample_gh_copilot_sdk/agent_plugins/plugins/code_reviewer/plugin.json` — plugin manifest
- `sample_gh_copilot_sdk/agent_plugins/plugins/code_reviewer/agents/code-reviewer.md` — code-reviewer agent definition
- `tests/` — test suite (mirrors main package structure)
- `tests/agent_plugins/` — tests for the agent_plugins sub-package
- `tests/agent_plugins/test_agents.py` — tests for agents.py
- `tests/agent_plugins/test_hooks.py` — tests for hooks.py
- `tests/agent_plugins/test_session.py` — tests for session.py (uses mocked CopilotClient)
- `tests/agent_plugins/test_tools.py` — tests for tools.py
- `.pylintrc` — Pylint configuration (10/10 enforced)
- `pyproject.toml` — PEP 621 project metadata and Poetry configuration
- `poetry.lock` — locked dependency versions (not ignored by git)
- `CHANGELOG.md` — Keep a Changelog format
- `README.md` — project overview and usage instructions
- `LICENSE` — MIT License
- `.gitignore` — excludes `.venv/`, `__pycache__/`, `.env`, `*.log`, IDE files
- `.gitattributes` — enforces LF line endings for non-Windows files

## Rules

- Before adding a dependency, use `poetry add` (main) or `poetry add --group dev` (dev); never edit `pyproject.toml` manually for dependencies.
- All new modules go inside `sample_gh_copilot_sdk/`; all tests go in `tests/` mirroring the package structure.
- Name test files `test_*.py`.
- Follow SOLID principles — each class has a single responsibility, depend on abstractions not concretions.
- Follow DRY — extract shared logic into utilities; never duplicate business logic.
- Prefer composition over inheritance; use dependency injection where applicable.
- Use snake_case for functions and variables, PascalCase for classes, UPPER_CASE for constants.
- Use type hints for all method arguments and return types; use `collections.abc` instead of deprecated `typing` types.
- Prefix private/protected members with `_`.
- Always add docstrings with `:author: Ron Webb` and `:since: <version>` to all modules, classes, and methods.
- Pylint must score 10/10 after every change — run `poetry run pylint sample_gh_copilot_sdk` to verify.
- Maintain minimum 80% test coverage — run `poetry run pytest --cov=sample_gh_copilot_sdk tests`.
- Never modify `poetry.lock` directly; let Poetry manage it.
- Never commit `.env` files or `*.log` files.
- When you create or discover new files, update the Tree above.

## Note-taking

- After each task, log any correction, preference, or pattern learned.
- Write to the matching docs file's "Session learnings" section;
  if none fits, add to Rules above. One dated line, plain language.
  e.g. "Prefer `from logenrich import setup_logger` over importing the module (learned 2026-07-10)"
- 3+ related notes → create a new `docs/` file, move the notes there, and update the Tree.
  Keep this file under 100 lines.
