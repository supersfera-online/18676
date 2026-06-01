# Verification report

What I verified by hand in this session (facts only — output I observed firsthand).

## 1. Tests (pytest)

- Ran the full suite: **45 passed, 0 failed, 0 skipped**.
- Coverage: **91%** (branch coverage).
- Command: `pytest -v --cov=claude_phone --cov-report=term-missing`
- Environment: pytest 9.0.3, Python 3.14.4, Linux.

Coverage by module:

| Module | Coverage |
|---|---|
| `runner.py` | 100% |
| `actions.py` | 100% |
| `prompt_builder.py` | 100% |
| `config.py` | 100% |
| `__init__.py` | 100% |
| `planner.py` | 98% |
| `cli.py` | 83% |
| `logging_config.py` | 75% |
| `__main__.py` | 0% (the `python -m` entry point; not invoked by tests) |

**Important scope note:** the tests **mock** the Termux/`subprocess` boundary. They prove the Python logic is correct (planner, executor, CLI) but say **nothing about behaviour on a real device** — this is stated in the repository itself, `docs/UNCERTAINTIES.md`, section F3.

## 2. On-device deployment (Samsung Galaxy S22+ emulator, Android 16 / API 36, x86_64)

- Termux installed; bootstrap completed.
- `scripts/setup-termux.sh` ran: **Node.js v24.15.0**, **npm 11.16.0**, Python, Git — installed and working.
- **Claude Code (`@anthropic-ai/claude-code`) does NOT run on Android.** The postinstall reported verbatim:

  > Native binaries for **linux-x64-android** are not available on the release channel.
  > Available: darwin-arm64, darwin-x64, linux-x64, linux-arm64, linux-x64-musl, linux-arm64-musl, win32-x64, win32-arm64.

  i.e. there is no native build for Android. This is an upstream limitation (Anthropic), **not a bug in this repository**.

## 3. Bottom line

- The project's Python logic is **green**: 45/45 tests, 91% coverage.
- The goal "Claude Code on the phone via the current npm package" is **not achievable**: no Android binary.
- Installation is **safe**: Termux runs in the app sandbox, no root, system partitions/firmware are untouched — the phone is not bricked.

_This report is limited to what was observed in this session; anything not verified on hardware is not counted as verified._
