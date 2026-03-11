# pastr

Prompt loading utilities.

## Install

```bash
uv add pastr
```

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
