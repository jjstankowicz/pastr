# Project Instructions

User preferences and shared cross-project workflow conventions are maintained in `~/.codex/AGENTS.md`.
This file contains `pastr` project context and workflow overrides.

# Project Context

## Goal

`pastr` provides a small standalone Python package named `pastr` ("Prompts Are STRings") for reusable prompt-loading utilities.

## MVP Scope (Phase 1)

Implement and stabilize prompt utilities only:

- `load_prompt_structure`
- `substitute_code_placeholders`
- `load_prompt`
- `set_prompt_directory` (optional global prompt root override)

Do not include phase-2 functionality in this repository yet:

- XML parsing helpers (for example `extract_xml_tags`)
- LiteLLM wrappers (for example `LLMClient`)
- Web search wrappers and task-specific research loops
- Project-specific agent logic that is outside prompt-loading utilities

# Package Design Constraints

- Use `src/` layout and explicit exports from `pastr.__init__`.
- Keep external dependencies minimal for phase 1.
- Maintain strict typing and deterministic path resolution behavior.
- Package ships no prompt files; consuming repositories provide prompt directories.

# Prompt Resolution Contract

`load_prompt` must keep this signature for compatibility:

```python
load_prompt(
    tag: str,
    code_replacements: dict[str, str] = {},
    *,
    prompt_root: Path | str | None = None,
) -> str
```

Resolution order:

1. If `prompt_root` is passed to `load_prompt`, use it.
2. Else if `set_prompt_directory(...)` override exists, use it.
3. Else auto-discover repository root by walking upward from current working directory to first parent containing `.git`, then use `<repo_root>/prompts`.
4. Optional fallback: `<repo_root>/pastr` when `<repo_root>/prompts` is absent.

Error handling requirements:

- Raise clear `FileNotFoundError` when prompt root or prompt file is missing.
- Detect and fail clearly on circular prompt references.
- Preserve nested `FROM_PROMPT` and `FROM_CODE` behavior across existing call sites.

# Development Guidelines

## Code Quality

- Treat this package as shared infrastructure: APIs must be stable, typed, and documented.
- Production code should include accurate type hints and concise docstrings.
- Keep behavior explicit. Hidden global behavior should be limited to `set_prompt_directory`.

## Testing And Typing

- Use pytest function tests and fixtures only.
- Keep unit tests in `tests/unit/`.
- Keep integration tests in `tests/integration/`.
- Mark integration tests with `@pytest.mark.integration`.
- Keep unit tests deterministic and offline by default.
- Keep pyright clean at configured strictness.
- Minimum release gate: test suite passes on Python 3.12.
- Cover at least:
  - nested `FROM_PROMPT` references
  - `FROM_CODE` substitutions
  - missing prompt files
  - circular references
- Include integration coverage for end-to-end prompt loading across real prompt files and resolution precedence.

# Planning Workflow

Planning is markdown-first and git-tracked.

- Canonical queue file: `plans/next-steps.md`
- Maintain ordered `Priority Queue` for execution order.
- Maintain checklist-style `Backlog` grouped by backlog tags.
- Each backlog tag maps to exactly one pull request.

# Pull Request Feedback Monitor

Use one script for review monitoring:

- `scripts/monitor_pr_feedback.sh`

Behavior:

- Watches a pull request for new commits and actionable feedback.
- Filters out self-comments and Copilot issue-comment noise.
- Exits on first detected update so follow-up actions can start immediately.

Usage:

```bash
scripts/monitor_pr_feedback.sh 3 2>&1 | tee -a ~/claude.log
```

or, for the current checkout's pull request:

```bash
POLL_SECONDS=10 scripts/monitor_pr_feedback.sh 2>&1 | tee -a ~/claude.log
```

# Integration Notes

- Consumers should depend on tagged releases of this repository (Git URL pin first, then Python Package Index later if desired).
- Compatibility shims are a release decision; default conservative path is one release cycle before removal.
