# Next Steps

Checklist-style queue tracked in version control.

Rules:

- Each backlog tag maps to exactly one pull request.
- `Priority Queue` defines execution order.
- `Backlog` defines scope and completion gates for each pull request.

## Priority Queue

- [x] `bootstrap-package-foundation`
- [x] `implement-prompt-api-core`
- [x] `harden-prompt-resolution`
- [ ] `prepare-first-release`
- [ ] `design-xml-and-llm-utilities` (deferred)

## Backlog

### `bootstrap-package-foundation`

Deliverables:

- [x] Create package skeleton with `pyproject.toml` and `src/pastr/`.
- [x] Add explicit public exports in `pastr.__init__`.
- [x] Configure strict pyright and pytest for Python 3.12.
- [x] Configure pytest `integration` marker and split test directories (`tests/unit`, `tests/integration`).
- [x] Add README quick start for `load_prompt` and prompt directory configuration.

Gates:

- [x] `uv run pyright` passes.
- [x] `uv run pytest -q tests/unit` passes.
- [x] `uv run pytest -q -m integration tests/integration` passes.
- [x] Package imports succeed from editable install.

Data flow:

```text
(project metadata, src/pastr/*, tests/*) -> [uv run pyright and uv run pytest -q] -> (validated package baseline)
```

### `implement-prompt-api-core`

Deliverables:

- [x] Ship package namespace as `pastr`.
- [x] Implement `load_prompt_structure`.
- [x] Implement `substitute_code_placeholders`.
- [x] Implement `load_prompt`.
- [x] Implement `set_prompt_directory`.
- [x] Keep `load_prompt` signature: `load_prompt(tag: str, code_replacements: dict[str, str] = {}, *, prompt_root: Path | str | None = None) -> str`.
- [x] Preserve nested `FROM_PROMPT` and `FROM_CODE` behavior.
- [x] Keep dependencies minimal and prompt-focused.

Gates:

- [x] Prompt-loading APIs are exported from `pastr.__init__`.
- [x] Unit tests pass for nested prompt expansion and code substitution.
- [x] Integration tests pass for end-to-end prompt loading from real prompt files.
- [x] Public API signatures match the project contract.
- [x] Prompt API behavior is stable.

Data flow:

```text
(tag, code_replacements, optional prompt_root) -> [load_prompt] -> (resolved prompt text)
(prompt text with FROM_PROMPT markers) -> [load_prompt_structure recursion] -> (fully expanded prompt text)
(prompt text with FROM_CODE markers, code_replacements) -> [substitute_code_placeholders] -> (final prompt text)
```

### `harden-prompt-resolution`

Deliverables:

- [x] Implement deterministic prompt root resolution order.
- [x] Enforce `prompt_root` argument precedence.
- [x] Enforce `set_prompt_directory` precedence when no `prompt_root` argument is provided.
- [x] Enforce auto-discovery fallback by walking upward to first parent containing `.git` when no explicit path is provided.
- [x] Resolve default prompt root to `<repo_root>/prompts`.
- [x] Support optional fallback `<repo_root>/pastr` when `<repo_root>/prompts` is absent.
- [x] Add clear failures for missing prompt root and missing prompt files.
- [x] Add cycle detection for circular prompt references.
- [x] Add explicit tests for resolution precedence and error behavior.

Gates:

- [x] Tests verify `prompt_root` argument precedence over global override.
- [x] Tests verify global override precedence over auto-discovery.
- [x] Circular references fail with clear error messaging.
- [x] Missing prompt assets raise `FileNotFoundError`.
- [x] Integration tests verify resolver behavior with real filesystem layouts.

Data flow:

```text
(prompt_root arg, global override, cwd) -> [prompt root resolver] -> (resolved root path or FileNotFoundError)
(prompt graph) -> [cycle detector] -> (safe expansion order or circular reference error)
```

### `prepare-first-release`

Deliverables:

- [ ] Prepare `v0.1.0` changelog and version metadata.
- [ ] Validate installation from pinned Git tag.
- [ ] Document upgrade procedure for consumers.
- [ ] Record release checklist in repository docs.

Gates:

- [ ] Tagged installation succeeds in a clean environment.
- [ ] Release notes cover API surface and known constraints.
- [ ] Versioned installation instructions are reproducible.

Data flow:

```text
(main branch release commit) -> [git tag v0.1.0] -> (versioned source snapshot)
(versioned source snapshot) -> [uv add git+...@v0.1.0] -> (consumer environment with pinned dependency)
```

### `design-xml-and-llm-utilities`

Deliverables:

- [ ] Define API proposal for XML parsing helpers.
- [ ] Define API proposal for LLM wrapper surface.
- [ ] Decide dependency policy and isolation boundaries.

Gates:

- [ ] Prompt API work is complete before implementation starts.
- [ ] Item is promoted in `Priority Queue` before coding starts.
