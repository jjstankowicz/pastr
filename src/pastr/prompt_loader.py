"""Prompt loading and template substitution utilities."""

from __future__ import annotations

import re
from pathlib import Path

_prompt_directory_override: Path | None = None
_PROMPT_INCLUDE_PATTERN = re.compile(r"\{\{FROM_PROMPT:([^}]+)\}\}")
_CODE_PLACEHOLDER_PATTERN = re.compile(r"\{\{FROM_CODE:([^}]+)\}\}")


def set_prompt_directory(path: Path | str | None) -> None:
    """Set global prompt directory override used by ``load_prompt``.

    Passing ``None`` clears the override.
    """
    global _prompt_directory_override
    if path is None:
        _prompt_directory_override = None
        return
    _prompt_directory_override = Path(path).expanduser()


def load_prompt_structure(tag: str, *, prompt_root: Path) -> str:
    """Load prompt template text and expand ``FROM_PROMPT`` inclusions."""
    return _load_prompt_structure_recursive(
        tag=tag,
        prompt_root=prompt_root,
        active_tags=(),
    )


def substitute_code_placeholders(prompt: str, code_replacements: dict[str, str]) -> str:
    """Replace ``FROM_CODE`` placeholders with caller-provided values."""

    def replacement(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        if key not in code_replacements:
            raise KeyError(f"Missing code replacement for key '{key}'")
        return code_replacements[key]

    return _CODE_PLACEHOLDER_PATTERN.sub(replacement, prompt)


def load_prompt(
    tag: str,
    code_replacements: dict[str, str] = {},
    *,
    prompt_root: Path | str | None = None,
) -> str:
    """Load a prompt template and apply ``FROM_PROMPT`` and ``FROM_CODE`` expansions."""
    resolved_prompt_root = _resolve_prompt_root(prompt_root)
    prompt_structure = load_prompt_structure(tag, prompt_root=resolved_prompt_root)
    return substitute_code_placeholders(prompt_structure, dict(code_replacements))


def _load_prompt_structure_recursive(
    *,
    tag: str,
    prompt_root: Path,
    active_tags: tuple[str, ...],
) -> str:
    if tag in active_tags:
        cycle = " -> ".join((*active_tags, tag))
        raise ValueError(f"Circular prompt reference detected: {cycle}")

    prompt_path = _resolve_prompt_path(prompt_root, tag)
    prompt_text = prompt_path.read_text(encoding="utf-8")

    def include_replacement(match: re.Match[str]) -> str:
        nested_tag = match.group(1).strip()
        return _load_prompt_structure_recursive(
            tag=nested_tag,
            prompt_root=prompt_root,
            active_tags=(*active_tags, tag),
        )

    return _PROMPT_INCLUDE_PATTERN.sub(include_replacement, prompt_text)


def _resolve_prompt_root(prompt_root: Path | str | None) -> Path:
    if prompt_root is not None:
        candidate = Path(prompt_root).expanduser()
        return _require_existing_directory(candidate, "prompt_root argument")

    if _prompt_directory_override is not None:
        return _require_existing_directory(_prompt_directory_override, "set_prompt_directory override")

    repo_root = _discover_repo_root(Path.cwd())
    default_prompts = repo_root / "prompts"
    if default_prompts.is_dir():
        return default_prompts

    fallback_prompts = repo_root / "pastr"
    if fallback_prompts.is_dir():
        return fallback_prompts

    raise FileNotFoundError(
        "Prompt root not found. Expected '<repo_root>/prompts' or '<repo_root>/pastr'."
    )


def _discover_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise FileNotFoundError(
        "Could not auto-discover repository root. No parent directory contains '.git'."
    )


def _require_existing_directory(path: Path, context: str) -> Path:
    if path.is_dir():
        return path
    raise FileNotFoundError(f"Prompt root from {context} does not exist: {path}")


def _resolve_prompt_path(prompt_root: Path, tag: str) -> Path:
    direct = prompt_root / tag
    if direct.is_file():
        return direct

    txt = prompt_root / f"{tag}.txt"
    if txt.is_file():
        return txt

    raise FileNotFoundError(
        f"Prompt file not found for tag '{tag}' under root '{prompt_root}'. "
        f"Tried '{direct}' and '{txt}'."
    )
