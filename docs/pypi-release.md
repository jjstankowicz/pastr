# PyPI Release

This repository publishes releases to PyPI from GitHub Actions.

## One-time repository setup

1. Create repository secret `PYPI_API_TOKEN` with a PyPI token that has publish permission for `pastr`.
2. Keep the workflow environment name as `pypi` (used in `.github/workflows/publish-pypi.yml`).

## Release commands

Run from repository root:

```bash
uv run pytest -q tests/unit tests/integration
uv run pyright
uv build
git checkout main
git pull --ff-only
git tag -a v0.1.0 -m "Release v0.1.0."
git push origin main
git push origin v0.1.0
```

Pushing `v0.1.0` triggers the `Publish to PyPI` workflow.

## Post-publish verification

```bash
tmp_dir="$(mktemp -d)"
cd "${tmp_dir}"
uv init --name pastr-pypi-install-check
uv add pastr==0.1.0
uv run python -c "from pastr import load_prompt, set_prompt_directory; assert load_prompt and set_prompt_directory"
```
