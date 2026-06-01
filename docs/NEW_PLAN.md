# New Plan — Dependency & Tooling Currency Refresh

> **Status: implemented** on branch `claude/documentation-read-report-bB4FM`
> (commit `06a39e0`). See `docs/NEW_REPORT.md` for what was actually done and
> verified.

## Context

The shipped application has **zero runtime dependencies**, so the software
*itself* cannot go stale. The problem is the **dev/CI tooling**, which is pinned
to releases from roughly late-2024 and has drifted a long way behind current
(June 2026):

- `ruff` pinned `v0.6.9` while current is **0.15.x** (many minors behind).
- `mypy` pinned `v1.11.2` while current is **2.1.0** — a *full major version*
  behind (mypy 2.0/2.1 added parallel checking).
- `pre-commit-hooks` `v5.0.0` → **v6.0.0**; `bandit` `1.7.10` → **1.9.4**.
- CI test matrix tops out at **Python 3.12**, missing **3.13 and 3.14** (3.14 is
  the current stable release; 3.10 reaches EOL Oct 2026).
- CI uses **`actions/checkout@v4`** and **`actions/setup-python@v5`**, and
  **`ludeeus/action-shellcheck@master`** (an unpinned moving branch). GitHub
  forces the **Node.js 24 runtime as the default on 2026-06-02**, which
  deprecates the Node-20-based v4/v5 action runtimes — so this bump is
  *time-sensitive*, not cosmetic.

**Why now / intended outcome:** bring pre-commit, CI, and dev-dependency floors
up to current releases so local `pre-commit` matches what CI runs, CI exercises
the Python versions people actually deploy on, and the GitHub Actions keep
working past the Node 24 cutover. **Validated as low-risk:** the code already
passes clean against the latest tooling installed locally — `ruff 0.15`
(`ruff check` **and** `ruff format --check` → "15 files already formatted") and
`mypy 2.1` (`Success: no issues found in 9 source files`). No code changes are
required to adopt the new versions.

**Out of scope:** the device-layer correctness issues (e.g. the broken
`termux_ready` probe, executor skip-vs-fail semantics) tracked in
`docs/UNCERTAINTIES.md`. This plan is purely a tooling/version refresh.

## Changes

### 1. `.pre-commit-config.yaml` — bump pinned hook revs to current

| Repo | From | To (June 2026) |
| --- | --- | --- |
| `pre-commit/pre-commit-hooks` | `v5.0.0` | `v6.0.0` |
| `astral-sh/ruff-pre-commit` | `v0.6.9` | `v0.15.x` (latest 0.15) |
| `pre-commit/mirrors-mypy` | `v1.11.2` | `v2.1.0` |
| `PyCQA/bandit` | `1.7.10` | `1.9.4` |
| `shellcheck-py/shellcheck-py` | `v0.10.0.1` | latest (`autoupdate`; likely unchanged — shellcheck core still 0.10.0) |

Implement by running `pre-commit autoupdate` (resolves each repo to its latest
tag automatically), then `pre-commit run --all-files` to confirm a clean pass.
Do **not** hand-edit revs to guessed tags — let `autoupdate` pin the exact ones.

### 2. `pyproject.toml` — raise dev-dependency floors

In `[project.optional-dependencies].dev`, lift the `>=` floors to the current
majors so a fresh `pip install -e ".[dev]"` and CI both land on modern tools:

- `pytest>=8.0` → `pytest>=9.0`
- `pytest-cov>=5.0` → `pytest-cov>=7.0`
- `ruff>=0.6` → `ruff>=0.15`
- `mypy>=1.11` → `mypy>=2.1`
- `bandit>=1.7` → `bandit>=1.9`
- `pre-commit>=3.8` → `pre-commit>=4.0`

Leave `requires-python = ">=3.10"`, `[tool.ruff].target-version = "py310"`, and
`[tool.mypy].python_version = "3.10"` **unchanged** — the floor of *supported*
runtimes stays 3.10; only the *tooling* and *tested* versions move up. (Optional
follow-up once 3.10 hits EOL in Oct 2026: raise the floor to 3.11.)

### 3. `.github/workflows/ci.yml` — modernize matrix and actions

- **Python matrix:** `["3.10", "3.11", "3.12"]` →
  `["3.10", "3.11", "3.12", "3.13", "3.14"]`.
- **Action versions (Node 24 deadline):**
  - `actions/checkout@v4` → `@v5` (latest major is v6; v5 is the safe
    Node-24-compatible choice — bump to v6 if preferred).
  - `actions/setup-python@v5` → `@v6`.
  - `softprops/action-gh-release@v2` — already current, leave as-is.
- **Pin the floating action:** `ludeeus/action-shellcheck@master` → a fixed
  release tag (verify the exact latest, e.g. `@2.0.0`) to remove the
  unpinned-`master` supply-chain risk.

## Critical files

- `.pre-commit-config.yaml` — hook revs (§1).
- `pyproject.toml` — `[project.optional-dependencies].dev` (§2).
- `.github/workflows/ci.yml` — `strategy.matrix.python-version` and the
  `uses:` action versions (§3).
- `Makefile` — read only; `make check` (ruff + mypy + bandit + pytest +
  shellcheck) is the existing local gate and needs no change.

## Verification (end-to-end)

1. `pre-commit autoupdate` then `pre-commit run --all-files` → all hooks pass
   Docker-free.
2. `pip install -e ".[dev]"` into a clean venv → resolves the new floors.
3. `make check` → ruff (check + `format --check`), mypy strict, bandit, pytest,
   shellcheck all green. Expected from local validation: `ruff` clean,
   `mypy` "no issues", `bandit` "No issues identified",
   `pytest` **45 passed**.
4. `claude-phone plan --skip-probe --dry-run` → still produces the coherent
   9-step ordered plan to `fully_configured`, exit 0 (behaviour preserved).
5. Push the branch and confirm the **CI matrix runs green on all five Python
   versions (3.10–3.14)** on the real GitHub Actions backend.

## Risk

Low. The latest `ruff` and `mypy` were run against this code during planning and
reported no findings and no reformatting, so the version jumps — including the
mypy 1.x → 2.x major bump — require no source changes. The only items needing a
live check are the exact `shellcheck-py`/action tags (resolved by `autoupdate`
and a quick releases-page lookup) and confirming 3.13/3.14 pass in real CI.

## Sources

- [ruff releases (astral-sh/ruff)](https://github.com/astral-sh/ruff/releases) ·
  [Ruff v0.15.0 blog](https://astral.sh/blog/ruff-v0.15.0)
- [mypy 2.0 release notes](https://mypy-lang.blogspot.com/2026/05/mypy-20-relased.html) ·
  [mypy on PyPI](https://pypi.org/project/mypy/)
- [Status of Python versions](https://devguide.python.org/versions/) ·
  [What's new in Python 3.14](https://docs.python.org/3/whatsnew/3.14.html)
- [actions/checkout releases](https://github.com/actions/checkout/releases) ·
  [actions/setup-python releases](https://github.com/actions/setup-python/releases)
- [pre-commit/pre-commit-hooks releases](https://github.com/pre-commit/pre-commit-hooks/releases)
