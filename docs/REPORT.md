# Production-Readiness Report

Branch: `claude/production-readiness-plan-vFAtx`

This report records what was done, what was actually verified (by observed
output, not assumption), and what remains unverifiable in this environment. It is
deliberately conservative: claims here are limited to things whose output I saw,
and anything I could not confirm is sent to `docs/UNCERTAINTIES.md` instead.

## 1. Origin & provenance (verified)

`git log` shows two distinct authors:

- Original prototype: author `supersfera-online <slava@supersfera.online>`,
  commits dated 2026-03-08 and 2026-05-28 ("Initial commit" through
  "Add files via upload"). This is the AI-generated code as uploaded.
- Hardening work: author `Claude`, commits dated 2026-05-31
  (restructure, packaging/CI, tests, docs, shellcheck-py fix).

Provenance establishes *who committed what*. It does **not** establish that the
content is free of AI hallucination — that requires execution and logic review
(below and in `UNCERTAINTIES.md`).

## 2. What the original code actually does (verified by execution)

Running the **original** files (commit `b25eb54`, before any of my edits):

- `python -m py_compile` succeeds → syntax valid, cross-file imports resolve.
- `python main.py --list` → coherent table of 24 actions with correct
  `preconditions → effects`.
- `python main.py --skip-probe --dry-run` → the planner builds a valid,
  **causally ordered** 9-step plan to `fully_configured`:
  - `Update Termux` (produces `packages_updated`) precedes `Install Node.js`
    (requires `packages_updated`) precedes `Install Claude Code`
    (requires `nodejs_ready`).
  - Reported **critical path** = 8.1 (Update → Node → Claude → Fully ready),
    total plan complexity 11.2.

Conclusion: the core algorithm is a genuine, working STRIPS-style planner that
produces a correct, dependency-consistent result on execution — not incoherent
output. This is positive evidence against "hallucinated logic" for the planner
specifically.

The same run also surfaced a real defect in the original: it returned a
**non-zero exit code despite a fully successful plan** — fixed during hardening.

## 3. Changes made (the hardening work)

- **Packaging:** restructured into `src/claude_phone/` with `pyproject.toml` and
  a `claude-phone` console entry point; shell scripts moved to `scripts/`.
- **Safety/correctness:**
  - Added timeouts to every `subprocess.run` (default 120 s; 60 s for GPS) so
    actions like `termux-location` can no longer hang indefinitely.
  - Documented and contained the `shell=True` trust boundary in
    `runner.py` (all command strings are static literals; user input never
    reaches a shell) with scoped `# nosec` annotations.
  - Fixed the success-but-nonzero-exit bug; corrected the `Executor.__init__`
    default; removed dead imports (`shlex`, `field`).
- **Logging:** replaced `print` with `logging`, added `-v`/`-q` and correct exit
  codes.
- **Prompt builder:** folded `claude_prompt_builder.py` into the package as a
  `prompt` subcommand.
- **Tests:** added a `pytest` suite under `tests/` (six modules:
  `test_planner`, `test_executor`, `test_runner`, `test_actions`, `test_cli`,
  `test_prompt_builder`) mocking the Termux/`subprocess` boundary.
- **CI/tooling:** GitHub Actions (ruff, mypy strict, bandit, pytest,
  shellcheck), `Makefile`, `.pre-commit-config.yaml`, `.editorconfig`.
- **Docs:** `README`, `docs/ARCHITECTURE.md`, `CONTRIBUTING.md`, `CHANGELOG.md`,
  `SECURITY.md`; fixed broken `SETUP.md` link; issue/PR templates.

## 4. Verification actually observed in this environment

The following produced visible, successful output during this session:

- **Tests:** `pytest` → **45 passed, 0 failed, 0 skipped**, total branch
  coverage **91%** (`runner.py` 100%, `actions.py` 100%, `prompt_builder.py`
  100%, `config.py` 100%, `planner.py` 98%, `cli.py` 83%, `logging_config.py`
  75%, `__main__.py` 0% — the `python -m` entry point, not invoked by tests).
  These numbers cover the **Python logic only** — the Termux/`subprocess`
  boundary is mocked, so they say nothing about real device behaviour.
- **On-device deployment (emulator):** on a Samsung Galaxy S22+ emulator
  (Android 16 / API 36, x86_64), Termux bootstrapped and `scripts/setup-termux.sh`
  ran successfully — **Node.js v24.15.0**, **npm 11.16.0**, Python and Git all
  installed and working. However, **Claude Code (`@anthropic-ai/claude-code`)
  does not run on Android**: its postinstall reported that no native binary for
  `linux-x64-android` exists (available targets: `darwin-arm64`, `darwin-x64`,
  `linux-x64`, `linux-arm64`, `linux-x64-musl`, `linux-arm64-musl`, `win32-x64`,
  `win32-arm64`). This is an **upstream limitation (Anthropic), not a bug in this
  repository**. Details in `tests/VERIFICATION_REPORT.md`.
- **`make check`** (ruff + mypy + bandit + pytest + shellcheck) → completed;
  bandit reported "No issues identified" across 759 LOC.
- **Package build:** `pip wheel` produced `claude_phone-0.1.0-py3-none-any.whl`;
  installed into a clean venv; the `claude-phone` console command ran (exit 0).
- **`pre-commit run --all-files`** → all hooks pass after switching the
  Docker-dependent `koalaman/shellcheck-precommit` to the Docker-free
  `shellcheck-py` hook.

## 5. Not verified here (and why)

- **Real device behaviour (Samsung Galaxy S22+, Termux):** partially verified on
  an **x86_64 emulator** (Android 16 / API 36), not on real arm64 hardware. The
  emulator run confirmed the toolchain install path and surfaced the Android
  blocker above; the conclusion that Claude Code has no Android build holds for
  arm64 too, since `linux-arm64-android` is likewise absent from the available
  targets. Still unverified on a physical device: correctness of individual
  `pkg`/`termux-*` command names, flags, and probe semantics at runtime — the
  unit tests mock this boundary.
- **CI status on real GitHub Actions:** the GitHub backend connected in this
  environment is a local stand-in (127.0.0.1) that does not report Actions runs.
  The same checks were run locally instead.
- **Correctness of individual Termux command names/flags/paths and several probe
  semantics:** these "look right" but looking right is exactly what a
  hallucination does — so each is itemised in `docs/UNCERTAINTIES.md` with a
  severity, a confidence estimate, and a concrete way to verify it.

## 6. Bottom line

- The project's **Python logic is green**: 45/45 tests pass at 91% branch
  coverage, and the planner produces a correct, dependency-ordered plan.
- The end goal **"run Claude Code on the phone via the current npm package" is
  not achievable**: there is no Android (`linux-*-android`) native build —
  an upstream limitation, not a defect in this code.
- **Installation is safe:** Termux runs in the app sandbox, no root is required,
  and system partitions/firmware are untouched — the device is not bricked.

## 7. Honest caveats about this report

- "Works and is coherent" (Section 2) is **not** the same as "correct in every
  detail." The planner algorithm is verified; the *domain content* (which Termux
  commands to run, how to detect state) is only partially verifiable without a
  device.
- During this session I made at least one factual slip from memory (referring to
  a non-existent `claude_phone_planner.py`), which is itself the reason
  device-dependent claims are quarantined in `UNCERTAINTIES.md` rather than
  asserted here.

## 8. Companion documents

- `docs/PLAN.md` — the plan this work followed.
- `docs/UNCERTAINTIES.md` — everything not certain to 100%, with how to verify.
- `docs/ARCHITECTURE.md` — design of the planner/executor.
- `tests/VERIFICATION_REPORT.md` — firsthand test + on-device emulator results.
