"""Unit tests for prompt loader behavior."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from pastr import load_prompt, set_prompt_directory


@pytest.fixture(autouse=True)
def clear_prompt_directory_override() -> Iterator[None]:
    """Reset global prompt directory state before and after each test."""
    set_prompt_directory(None)
    yield
    set_prompt_directory(None)


def test_load_prompt_reads_file_from_explicit_root(tmp_path: Path) -> None:
    """load_prompt should resolve prompt files from explicit prompt_root."""
    prompt_path = tmp_path / "simple.txt"
    prompt_path.write_text("hello world", encoding="utf-8")

    result = load_prompt("simple", prompt_root=tmp_path)

    assert result == "hello world"


def test_load_prompt_uses_global_override(tmp_path: Path) -> None:
    """Global prompt root override should apply when prompt_root is omitted."""
    prompt_path = tmp_path / "global.txt"
    prompt_path.write_text("global root", encoding="utf-8")
    set_prompt_directory(tmp_path)

    result = load_prompt("global")

    assert result == "global root"


def test_missing_prompt_file_raises_file_not_found(tmp_path: Path) -> None:
    """Missing prompt files should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_prompt("missing", prompt_root=tmp_path)


def test_nested_prompt_inclusion_and_code_substitution(tmp_path: Path) -> None:
    """Nested prompt includes and code placeholders should resolve fully."""
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    (nested_dir / "part.txt").write_text("inner", encoding="utf-8")
    (tmp_path / "main.txt").write_text(
        "before {{FROM_PROMPT:nested/part}} after {{FROM_CODE:value}}",
        encoding="utf-8",
    )

    result = load_prompt(
        "main",
        code_replacements={"value": "42"},
        prompt_root=tmp_path,
    )

    assert result == "before inner after 42"


def test_missing_code_replacement_raises_key_error(tmp_path: Path) -> None:
    """Missing FROM_CODE replacements should raise KeyError."""
    (tmp_path / "code.txt").write_text("value={{FROM_CODE:missing_key}}", encoding="utf-8")

    with pytest.raises(KeyError, match="missing_key"):
        load_prompt("code", prompt_root=tmp_path)


def test_prompt_root_argument_overrides_global_root(tmp_path: Path) -> None:
    """Explicit prompt_root should take precedence over global override."""
    global_root = tmp_path / "global"
    explicit_root = tmp_path / "explicit"
    global_root.mkdir()
    explicit_root.mkdir()
    (global_root / "target.txt").write_text("global", encoding="utf-8")
    (explicit_root / "target.txt").write_text("explicit", encoding="utf-8")

    set_prompt_directory(global_root)
    result = load_prompt("target", prompt_root=explicit_root)

    assert result == "explicit"


def test_circular_prompt_reference_raises_value_error(tmp_path: Path) -> None:
    """Circular FROM_PROMPT references should raise ValueError."""
    (tmp_path / "a.txt").write_text("{{FROM_PROMPT:b}}", encoding="utf-8")
    (tmp_path / "b.txt").write_text("{{FROM_PROMPT:a}}", encoding="utf-8")

    with pytest.raises(ValueError, match="Circular prompt reference detected"):
        load_prompt("a", prompt_root=tmp_path)


def test_rejects_parent_traversal_tag(tmp_path: Path) -> None:
    """Top-level tags should reject parent-directory traversal."""
    with pytest.raises(ValueError, match="Invalid prompt tag"):
        load_prompt("../secrets", prompt_root=tmp_path)


def test_rejects_absolute_tag(tmp_path: Path) -> None:
    """Top-level tags should reject absolute filesystem paths."""
    with pytest.raises(ValueError, match="Invalid prompt tag"):
        load_prompt("/etc/passwd", prompt_root=tmp_path)


def test_rejects_parent_traversal_in_nested_prompt_reference(tmp_path: Path) -> None:
    """FROM_PROMPT should reject parent-directory traversal tags."""
    (tmp_path / "main.txt").write_text("{{FROM_PROMPT:../secrets}}", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid prompt tag"):
        load_prompt("main", prompt_root=tmp_path)
