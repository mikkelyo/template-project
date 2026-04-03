# CLAUDE.md

## Project
Python template project using `uv` for dependency management.

## Stack
- Python 3.11+
- Pydantic / pydantic-settings for config and validation
- dynaconf for settings
- dependency-injector for DI
- pytest for tests

## Commands
`uv` is used for all tooling — running scripts, tests, linters, and formatters.

```bash
uv run pytest          # run tests
uv run ruff check .    # lint
uv run black .         # format
uv run mypy .          # type check
```

## Conventions

### 1. Keep It Simple
- Line length: 88 (black/ruff)
- Write straightforward, readable code that solves the problem at hand.
- Prefer clarity over cleverness. If a simple solution works, use it. THIS IS IMPORTANT.
- Handle edge cases gracefully, but don't add complexity for hypothetical scenarios.
- Only introduce patterns or structures when they provide clear benefits.
- Leave the code better and more simple than you found it.
- Don't add comments unless the logic isn't self-evident.
- *No defensive coding.* Don't add `if x is None` fallbacks, `Optional` wrappers, or lazy-import defaults to "be safe". If something is required, make it required and let it fail clearly.
- *No redundant fallback logic.* If a value is already set earlier in a function, don't add fallback code to set it again in an `except` block. Trust the existing code flow.
- *No wrapping DI-provided dependencies.* Services from the DI container are always available. Don't add `try/except` or `None` checks around `container.infrastructure.x()` calls — if infrastructure is broken, the app should fail clearly at startup.
- Don't change docstrings or comments unless directly relevant for the change you are working on.
- *Don't ever commit to main* — let the user merge the PR.

### 2. Document Inline
- Keep documentation close to the code it describes — makes it easy to follow and maintain.

### 3. Verify Changes Carefully
- Read through all changes carefully before considering the task complete.
- Review the associated parts of the codebase that your changes touch or depend on.
- Ensure no functionality is broken and the implementation works correctly.

### 4. Use Subagents for Complex Evaluations
- When a change touches multiple systems or has non-obvious side effects, spawn a subagent to evaluate the changes.
- Give the subagent clear instructions on what to check and what context to review.
- Create multiple subagents for different aspects of the change if needed (e.g., one for logic review, one for integration points).
- Wait for subagent findings before finalizing.

### 5. Async-Safe External Calls
- External API calls (HTTP, database, etc.) used during async tool/agent execution must not block the event loop.
- Either use async libraries, or wrap sync calls with `asyncio.to_thread()`.
- Pre-load/cache data at startup where possible.
- Blocking calls inside `asyncio.gather()` will serialize execution and cause severe delays.
