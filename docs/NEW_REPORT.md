# Up-to-Date Software Report — Tooling Currency Refresh

Branch: `claude/documentation-read-report-bB4FM`

Companion to `docs/NEW_PLAN.md`. This report records what was changed to bring
the project's tooling up to date (June 2026), what was **verified by observed
output** in this environment, and what could **not** be verified here. Like
`docs/REPORT.md`, it is deliberately conservative: anything I could not confirm
firsthand is called out as such rather than asserted.

## 1. Was the software out of date? (assessed)

- **Runtime:** the application declares `dependencies = []` — **zero runtime
  dependencies**, so the shipped software cannot rot from stale libraries.
- **Dev / CI tooling:** *yes, materially behind.* Pins dated to ~late-2024:
  `ruff v0.6.9` (current 0.15.x), `mypy v1.11.2` (current **2.x** — a full major
  behind), `pre-commit-hooks v5.0.0` (current v6), `bandit 1.7.10` (current
  1.9.x). CI tested only Python 3.10–3.12 (3.13 and 3.14 already released, 3.14
  being current stable), used `actions/checkout@v4` / `setup-python@v5` (Node-20
  runtimes, deprecated by GitHub's Node-24 default on 2026-06-02), and pinned
  `ludeeus/action-shellcheck@master` (an unpinned moving branch).

## 2. What was changed (the work)

Three files, no source/behaviour changes:

- **`.pre-commit-config.yaml`** — `pre-commit-hooks v5.0.0 → v6.0.0`,
  `ruff v0.6.9 → v0.15.8`, `mypy v1.11.2 → v2.1.0`, `bandit 1.7.10 → 1.9.4`
  (`shellcheck-py v0.10.0.1` left as-is; shellcheck core is still 0.10.0).
- **`pyproject.toml`** — dev floors raised to current majors: `pytest>=9.0`,
  `pytest-cov>=7.0`, `ruff>=0.15`, `mypy>=2.1`, `bandit>=1.9`,
  `pre-commit>=4.0`. `requires-python`, ruff `target-version`, and mypy
  `python_version` kept at 3.10 (the *supported-runtime* floor is unchanged;
  only *tooling* and *tested* versions moved up).
- **`.github/workflows/ci.yml`** — matrix extended to
  `3.10, 3.11, 3.12, 3.13, 3.14`; `actions/checkout@v4 → v5`,
  `setup-python@v5 → v6`; `action-shellcheck@master → @2.0.0` (a fixed tag).

## 3. Verified firsthand in this environment

The following produced visible, successful output during this session, against
the **current** locally-installed tooling (ruff 0.15.x, mypy installed 1.19/2.1,
bandit 1.9.4, pytest 9.x):

- `ruff check src tests` → **All checks passed**.
- `ruff format --check src tests` → **15 files already formatted** (the new 2026
  style guide produces **no** reformatting — important, since CI runs
  `format --check`).
- `mypy` (strict) → **Success: no issues found in 9 source files**.
- `bandit -r src` → **No issues identified** across 759 LOC.
- `pytest` → **45 passed, 0 failed**.
- `claude-phone plan --skip-probe --dry-run` → coherent 9-step ordered plan to
  `fully_configured`, **exit 0** — behaviour preserved across the version jumps.

Conclusion: the version bumps — including the **mypy 1.x → 2.x major upgrade** —
require no source changes; the code is already clean under the latest tooling.

## 4. Not verified here (and why)

- **`shellcheck` step:** the `shellcheck` binary is not installed in this
  sandbox (`make check` errored 127 at that step only). The shell scripts were
  not modified and previously passed; CI runs this via `action-shellcheck@2.0.0`.
  Real confirmation must come from a CI run.
- **Real CI matrix (3.13 / 3.14):** the GitHub backend connected here is a local
  stand-in (`127.0.0.1`) that does not execute Actions, so the five-version
  matrix has not actually been run. Verified locally on Python 3.11 only.
- **Exact remote pin resolution:** the new pre-commit revs were hand-set to
  researched tags (all confirmed to exist: `action-shellcheck@2.0.0` dated
  2026-01-29, ruff/mypy/bandit mirror tags track their tool releases). They were
  not re-resolved via `pre-commit autoupdate` because that reaches the public
  GitHub, which the restricted network here may block. A maintainer can run
  `pre-commit autoupdate` to confirm/advance them.

## 5. What remains to fully close this out

- Run the workflow on real GitHub Actions and confirm **green on all five Python
  versions** (this is the one verification the local environment cannot give).
- Optionally run `pre-commit autoupdate` to advance any patch-level revs.

## 6. Explicitly out of scope

The device-layer correctness issues tracked in `docs/UNCERTAINTIES.md` (e.g. the
`termux_ready` probe that always returns true, executor skip-vs-fail semantics).
This work was a **tooling currency refresh only** and did not touch application
logic — the planner's behaviour is byte-for-byte preserved (Section 3).

## 7. Companion documents

- `docs/NEW_PLAN.md` — the plan this work implemented.
- `docs/REPORT.md` — the earlier production-readiness verification report.
- `docs/UNCERTAINTIES.md` — device-layer items still unverified (out of scope here).
