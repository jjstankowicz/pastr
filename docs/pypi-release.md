# PyPI Release

This repository publishes releases to PyPI from GitHub Actions.

## One-time repository setup

1. In PyPI, add a Trusted Publisher for this repository:
   - owner: `jjstankowicz`
   - repository: `pastr`
   - workflow: `publish-pypi.yml`
   - environment: `pypi`
2. For first publish of a new project name, create a pending publisher entry in PyPI with the same fields.
3. Keep the GitHub workflow environment name as `pypi` (used in `.github/workflows/publish-pypi.yml`).

## Release commands

Run from repository root:

```bash
VERSION="0.1.0"
TAG="v${VERSION}"

uv run pytest -q tests/unit tests/integration
uv run pyright
uv build
git checkout main
git pull --ff-only
git tag -a "${TAG}" -m "Release ${TAG}."
git push origin main
git push origin "${TAG}"
```

Pushing `"${TAG}"` triggers the `Publish to PyPI` workflow.

## Post-publish verification

```bash
tmp_dir="$(mktemp -d)"
cd "${tmp_dir}"
uv init --name pastr-pypi-install-check
uv add "pastr==${VERSION}"
uv run python -c "from pastr import load_prompt, set_prompt_directory; assert load_prompt and set_prompt_directory"
```
