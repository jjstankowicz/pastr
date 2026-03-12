"""Integration tests for prompt root auto-discovery."""

from pathlib import Path

import pytest

from pastr import load_prompt, set_prompt_directory

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def clear_prompt_directory_override() -> None:
    """Reset global prompt directory state between tests."""
    set_prompt_directory(None)


def test_auto_discovers_git_root_for_prompts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """load_prompt should find <repo_root>/prompts when no root is provided."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    prompts_dir = repo_root / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "auto.txt").write_text("auto discovery", encoding="utf-8")

    nested_dir = repo_root / "a" / "b" / "c"
    nested_dir.mkdir(parents=True)
    monkeypatch.chdir(nested_dir)

    result = load_prompt("auto")

    assert result == "auto discovery"


def test_global_override_precedence_over_auto_discovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Global override should win when both override and auto-discovery are available."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    prompts_dir = repo_root / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "target.txt").write_text("auto discovery root", encoding="utf-8")

    override_root = tmp_path / "override"
    override_root.mkdir()
    (override_root / "target.txt").write_text("global override root", encoding="utf-8")

    nested_dir = repo_root / "nested"
    nested_dir.mkdir()
    monkeypatch.chdir(nested_dir)
    set_prompt_directory(override_root)

    result = load_prompt("target")

    assert result == "global override root"


def test_falls_back_to_repo_root_pastr_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Auto-discovery should use <repo_root>/pastr when prompts directory is absent."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    fallback_dir = repo_root / "pastr"
    fallback_dir.mkdir()
    (fallback_dir / "fallback.txt").write_text("pastr fallback", encoding="utf-8")

    nested_dir = repo_root / "nested" / "dir"
    nested_dir.mkdir(parents=True)
    monkeypatch.chdir(nested_dir)

    result = load_prompt("fallback")

    assert result == "pastr fallback"


def test_set_prompt_directory_relative_path_is_stable_across_cwd_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Relative set_prompt_directory paths should resolve to an absolute root immediately."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    prompts_dir = repo_root / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "stable.txt").write_text("stable", encoding="utf-8")

    monkeypatch.chdir(repo_root)
    set_prompt_directory("prompts")

    other_dir = tmp_path / "other"
    other_dir.mkdir()
    monkeypatch.chdir(other_dir)

    result = load_prompt("stable")

    assert result == "stable"
