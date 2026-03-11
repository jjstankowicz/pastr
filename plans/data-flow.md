# Data Flow

Prompt files -> loader functions -> prompt strings. Update as the graph evolves.

## Directory Structure

```text
src/
  pastr/
    __init__.py
    prompt_loader.py

prompts/
  *.txt
  */*.txt

tests/
  unit/
    test_prompt_loader.py
```

## Pipeline

```text
Legend:
(data)
[function]

(tag, code_replacements, optional prompt_root)
                    ->
              [load_prompt]
                    ->
       [resolve_prompt_root_path]
                    ->
         [load_prompt_structure]
                    ->
    [substitute_code_placeholders]
                    ->
           (final prompt string)
```

## Prompt Root Resolution Contract

- If `prompt_root` is passed to `load_prompt`, use it.
- Else if `set_prompt_directory` has been called, use that path.
- Else walk upward from current working directory to first parent with `.git`.
- Resolve prompt root to `<repo_root>/prompts`.
- Optional fallback: `<repo_root>/pastr` when `<repo_root>/prompts` is absent.
- Missing root or prompt file must raise `FileNotFoundError`.

## Expansion And Substitution Contract

- `FROM_PROMPT` supports nested references by tag.
- `FROM_CODE` supports placeholder replacement from `code_replacements`.
- Circular prompt references must fail with a clear error.
