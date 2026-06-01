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

_This report is limited to what was observed in this session; anything not verified on hardware is not counted as verified._
