# Changelog

## [0.1.0] - 2026-03-12

### Added

- Initial release of `pastr`.
- Prompt loader API:
  - `load_prompt`
  - `load_prompt_structure`
  - `substitute_code_placeholders`
  - `set_prompt_directory`
- Recursive includes via `FROM_PROMPT` and code substitution via `FROM_CODE`.
- Prompt root precedence handling, cycle detection, and prompt tag path-safety validation.
- Unit and integration test coverage for prompt loading and resolution behavior.
