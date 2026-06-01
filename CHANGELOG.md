# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `src/claude_phone/` package layout with `claude-phone` console entry point.
- `prompt` subcommand that generates a context-aware Claude system prompt
  (integrates the former standalone `claude_prompt_builder.py`).
- Test suite (`pytest`) covering the planner, executor, runner, action catalogue,
  CLI, and prompt builder; coverage gate in CI.
- GitHub Actions CI: ruff, mypy (strict), bandit, pytest+coverage across
  Python 3.10–3.12, shellcheck, and a tag-triggered release job.
- Tooling: `pyproject.toml`, `pre-commit`, `.editorconfig`, `Makefile`.
- Documentation: real `README`, `docs/ARCHITECTURE.md`, and this changelog.

### Changed
- The `prompt` subcommand now builds the system prompt from the device's **actual
  probed state** and the live action catalogue instead of a static demo profile:
  it lists only the capabilities currently available and the remaining setup
  steps, and regenerates as the device changes. Removed the unused `--user` flag
  and the hard-coded integration profiles.
- Replaced `print`-based output with the `logging` module; added `-v`/`-q` flags.
- `subprocess` calls now have timeouts; a hung command is a soft failure instead
  of blocking the run.
- CLI now returns a non-zero exit code when planning or execution fails.
- Hardened shell scripts (`set -euo pipefail`, quoting, input validation for
  volume/vibration in `phone-settings.sh`).
- Fixed the broken clone URL in `SETUP.md`.

### Security
- Documented and annotated the `shell=True` trust boundary (trusted literal
  commands only); `bandit` runs in CI.
