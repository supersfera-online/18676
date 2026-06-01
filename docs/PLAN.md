# Production-Readiness Plan

This is the plan I worked from to take the project from an AI-generated prototype
to a packaged, tested, documented state. It is recorded here after the fact for
transparency; the work described is already implemented on branch
`claude/production-readiness-plan-vFAtx`.

## Starting point (as uploaded)

The repository contained a working prototype, originally AI-generated and then
uploaded to the server:

- `main.py` — argparse CLI / entry point
- `remnant.py` — STRIPS-style `Planner`, `Executor`, `InformationRemnant`,
  plus `shell()`/`probe()` helpers
- `phone_remnants.py` — catalogue of 24 actions + 10 probes for Termux
- `setup-termux.sh`, `phone-settings.sh` — shell setup scripts
- `claude_prompt_builder.py` — standalone system-prompt generator
- `SETUP.md`, `README.md`, `LICENSE`

Maturity assessed at roughly 2/10 for production use: it ran, but had no tests,
no packaging, no CI, no tooling, weak error handling, and some safety gaps.

## Goals

Make the project production-ready **without changing its core behaviour or the
planner's design**: package it, test it, lint/type/scan it in CI, harden the
risky bits, and document it — while being explicit about what cannot be verified
in this environment (no Android device).

## Workstreams

1. **Restructure into an installable package**
   - Move code into `src/claude_phone/` (`planner.py`, `runner.py`,
     `actions.py`, `cli.py`, `config.py`, `logging_config.py`,
     `prompt_builder.py`, `__main__.py`).
   - Add `pyproject.toml` with a `claude-phone` console entry point.
   - Move shell scripts to `scripts/`.

2. **Safety / correctness hardening**
   - Add timeouts to every `subprocess.run` (`shell`/`probe`) so actions like
     GPS can't hang forever.
   - Document and contain the `shell=True` trust boundary (commands are static
     literals; user input never reaches a shell). Record the invariant for
     Bandit with scoped `# nosec`.
   - Fix the success-but-nonzero-exit bug: propagate real exit codes.
   - Remove dead code (`shlex`, unused `field`), fix the mutable/incorrect
     `__init__` default.

3. **Tests**
   - `pytest` suite covering planner, executor, runner, actions, CLI, and the
     prompt builder, mocking the Termux/`subprocess` boundary.
   - Target meaningful coverage of the core logic.

4. **CI/CD**
   - GitHub Actions running ruff, mypy (strict), bandit, pytest, and shellcheck.
   - A release job for packaging.

5. **Logging & error handling**
   - Replace `print` with the `logging` module; add `-v`/`-q` verbosity and
     correct exit codes; no silently swallowed exceptions.

6. **Integrate `claude_prompt_builder`**
   - Fold it into the package as a `prompt` subcommand.

7. **Documentation**
   - `README`, `docs/ARCHITECTURE.md`, `CHANGELOG.md`; fix the broken link in
     `SETUP.md`; add issue/PR templates.

## Definition of Done

- Package builds and installs; `claude-phone` CLI works from a clean venv.
- `make check` (lint + type + security + tests + shellcheck) passes locally.
- `pre-commit run --all-files` passes (Docker-free).
- Behaviour preserved: planner still produces a valid, dependency-ordered plan
  to `fully_configured`.

## Verified results

Measured firsthand:

- **Tests:** `pytest` → **45 passed, 0 failed**, branch coverage **91%**
  (`runner.py`/`actions.py`/`prompt_builder.py`/`config.py` 100%, `planner.py`
  98%, `cli.py` 83%, `logging_config.py` 75%). Python logic only — the
  Termux/`subprocess` boundary is mocked.

## Explicitly out of scope / not verifiable here

- Real execution on the Samsung Galaxy S22+ (no device; Termux mocked).
- CI status on the real GitHub Actions backend (the connected GitHub here is a
  local stand-in that does not report Actions runs).
- Correctness of individual Termux command names/flags against a live device —
  tracked separately in `docs/UNCERTAINTIES.md`.
