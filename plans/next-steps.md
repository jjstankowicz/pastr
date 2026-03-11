# Next Steps

Checklist-style queue tracked in version control.

Rules:

- Each backlog tag maps to exactly one pull request.
- `Priority Queue` defines execution order.
- `Backlog` defines scope and completion gates for each pull request.

## Priority Queue

- [ ] `bootstrap-package-foundation`
- [ ] `implement-prompt-api-core`
- [ ] `harden-prompt-resolution`
- [ ] `prepare-first-release`
- [ ] `design-xml-and-llm-utilities` (deferred)

## Backlog

### `bootstrap-package-foundation`

Deliverables:

- [ ] Create package skeleton with `pyproject.toml` and `src/pastr/`.
- [ ] Add explicit public exports in `pastr.__init__`.
- [ ] Configure strict pyright and pytest for Python 3.12.
- [ ] Add README quick start for `load_prompt` and prompt directory configuration.

Gates:

- [ ] `uv run pyright` passes.
- [ ] `uv run pytest -q` passes with at least one smoke test.
- [ ] Package imports succeed from editable install.

Data flow:

```text
(project metadata, src/pastr/*, tests/*) -> [uv run pyright and uv run pytest -q] -> (validated package baseline)
```

### `implement-prompt-api-core`

Deliverables:

- [ ] Ship package namespace as `pastr`.
- [ ] Implement `load_prompt_structure`.
- [ ] Implement `substitute_code_placeholders`.
- [ ] Implement `load_prompt`.
- [ ] Implement `set_prompt_directory`.
- [ ] Keep `load_prompt` signature: `load_prompt(tag: str, code_replacements: dict[str, str] = {}, *, prompt_root: Path | str | None = None) -> str`.
- [ ] Preserve nested `FROM_PROMPT` and `FROM_CODE` behavior.
- [ ] Keep dependencies minimal and prompt-focused.

Gates:

- [ ] Prompt-loading APIs are exported from `pastr.__init__`.
- [ ] Unit tests pass for nested prompt expansion and code substitution.
- [ ] Public API signatures match the project contract.
- [ ] Prompt API behavior is stable.

Data flow:

```text
(tag, code_replacements, optional prompt_root) -> [load_prompt] -> (resolved prompt text)
(prompt text with FROM_PROMPT markers) -> [load_prompt_structure recursion] -> (fully expanded prompt text)
(prompt text with FROM_CODE markers, code_replacements) -> [substitute_code_placeholders] -> (final prompt text)
```

### `harden-prompt-resolution`

Deliverables:

- [ ] Implement deterministic prompt root resolution order.
- [ ] Enforce `prompt_root` argument precedence.
- [ ] Enforce `set_prompt_directory` precedence when no `prompt_root` argument is provided.
- [ ] Enforce auto-discovery fallback by walking upward to first parent containing `.git` when no explicit path is provided.
- [ ] Resolve default prompt root to `<repo_root>/prompts`.
- [ ] Support optional fallback `<repo_root>/pastr` when `<repo_root>/prompts` is absent.
- [ ] Add clear failures for missing prompt root and missing prompt files.
- [ ] Add cycle detection for circular prompt references.
- [ ] Add explicit tests for resolution precedence and error behavior.

Gates:

- [ ] Tests verify `prompt_root` argument precedence over global override.
- [ ] Tests verify global override precedence over auto-discovery.
- [ ] Circular references fail with clear error messaging.
- [ ] Missing prompt assets raise `FileNotFoundError`.

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
