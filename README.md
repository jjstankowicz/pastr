# pastr

Prompt loading utilities.

## Install

After the first PyPI release:

```bash
uv add pastr
```

Fallback before a package release is published:

```bash
uv add "pastr @ git+https://github.com/jjstankowicz/pastr.git@v0.1.0"
```

Release steps are documented in `docs/pypi-release.md`.

## Quick Start

```python
from pathlib import Path

from pastr import load_prompt, set_prompt_directory

# Optional global override.
set_prompt_directory(Path("prompts"))

# Load by tag from prompts/simple.txt
prompt = load_prompt("simple")

# Or pass an explicit root per call.
prompt = load_prompt("simple", prompt_root=Path("prompts"))

# Replace code placeholders like {{FROM_CODE:answer}}.
prompt = load_prompt(
    "simple",
    code_replacements={"answer": "42"},
    prompt_root=Path("prompts"),
)
```
