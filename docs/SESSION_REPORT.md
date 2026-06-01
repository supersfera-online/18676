# Session Report

Honest record of everything done in this session, what was verified, and what
was **not**. Date: 2026-06-01.

## What was merged into `main`

| PR | Title | Status |
| --- | --- | --- |
| #4 | `chore: refresh dev/CI tooling to current versions` | merged |
| #5 | `feat(prompt): build system prompt from real device state` | merged |
| #6 | `fix(probe): make termux_ready actually detect Termux` | closed (tangled history, superseded by #7) |
| #7 | `feat: one-click phone install + fix termux_ready probe` | merged |
| #8 | `feat(android): one-tap APK installer for Claude Code` | merged |

## 1. Read the docs and reported (the original request)

Read `docs/` (PLAN, REPORT, ARCHITECTURE, DEFINITIONS, UNCERTAINTIES, …) and
summarised the project: a STRIPS-style planner-executor (`claude-phone`) that
bootstraps Claude Code on an Android phone via Termux, tuned for the Galaxy S22+.

## 2. Production-readiness assessment

- Verdict: solid as a Python package (tests, lint, types, CI), **not** proven as
  a phone configurator — the entire device layer is mocked and never run on real
  hardware.

## 3. Tooling currency refresh (PR #4)

- Pins were ~18 months behind. Bumped pre-commit hooks (ruff `0.6.9→0.15.x`,
  mypy `1.11→2.1` — a major jump, bandit, pre-commit-hooks `v5→v6`), raised
  `pyproject` dev floors, extended CI matrix to Python **3.10–3.14**, bumped
  `actions/checkout@v5` / `setup-python@v6` (Node-24 runtime), pinned
  `action-shellcheck@2.0.0`.
- **Verified:** CI green on all five Python versions; ruff/mypy/bandit clean.
- Docs: `docs/NEW_PLAN.md`, `docs/NEW_REPORT.md`.

## 4. System-prompt builder — real integration (PR #5)

- **Problem found:** the `prompt` subcommand was only mechanically folded in; it
  emitted a static, generic web-assistant prompt (Gmail/Drive) with **zero**
  coupling to the planner.
- **Fix:** `get_device_context(state, remnants)` now derives the prompt from the
  probed facts + the live action catalogue; it lists only currently-available
  capabilities and the remaining setup steps, and **regenerates** as the device
  changes. Removed the dead `--user` flag and the static profiles.
- **Verified:** 46 tests pass (incl. a rebuild test); CI green.

## 5. Fixed the `termux_ready` probe (PR #7, originally #6)

- **Bug (UNCERTAINTIES A1):** the probe ran `echo $TERMUX_VERSION`, which exits 0
  everywhere, so it reported `True` even off-device — it never detected Termux.
- **Fix:** `test -n "$TERMUX_VERSION"`. `plan` now warns when not in Termux;
  `prompt` lets the probe govern.
- **Verified:** 48 tests pass; CI green. UNCERTAINTIES A1 marked fixed.

## 6. One-command phone install (PR #7)

- `scripts/bootstrap.sh`: a single `curl … | bash` paste that clones/updates the
  repo, runs `setup-termux.sh`, and installs **Termux:Widget** shortcuts
  (`Claude Code` / `Update Claude Code`).
- **Verified:** shellcheck + tests green. **Not run on a device.**

## 7. One-tap APK installer (PR #8)

- `android/`: a minimal Kotlin app that drives Termux via the `RUN_COMMAND`
  service to run the bootstrap; CI builds a downloadable debug APK
  (`.github/workflows/android.yml`).
- **Bugs I caught by actually reviewing my own work:**
  - `startForegroundService` is API 26+ → would have crashed; switched to
    `ContextCompat.startForegroundService`.
  - `minSdk` was a thoughtless `24` (Android 7) on a tool tuned for the **S22+**,
    which shipped on Android 12 → raised to `31`.
- **Verified:** Gradle build green, APK artifact produced.

## What is NOT done / NOT verified (the honest part)

- **Nothing has been run on a real phone.** No Android/Termux device was
  available; every device interaction (`pkg`, `termux-*`, the APK, the bootstrap)
  is unverified at runtime. CI proves the code compiles/builds and the Python
  logic passes — nothing more.
- **It is not a true "one click."** The APK needs Termux already installed and,
  for auto-run, `allow-external-apps=true` in `termux.properties`; otherwise it
  falls back to copy-command-and-paste. Two taps are unavoidable on Android (the
  storage-permission popup and the API key on first launch).
- Other `docs/UNCERTAINTIES.md` items (greedy planner optimality, executor
  skip-vs-fail, timeout defaults, real Termux command/flag correctness) remain
  open and out of scope for this session.

## Process mistakes made this session (owned, not deflected)

- Reused one branch for three sequential squash-merges, which tangled the history
  and caused a needless merge conflict (cleaned up via PR #7 on a fresh branch).
- Over-narrated status instead of just delivering.
- Set an Android `minSdk` without thinking about the actual target device.

## The one open item to call this "ready"

Install the CI-built APK on the physical Galaxy S22+ and walk the flow
(tap → install → `claude` launches). On-device behaviour is the only thing that
turns "builds" into "works".
