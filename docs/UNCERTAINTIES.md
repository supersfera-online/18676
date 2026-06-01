# Uncertainties & Unverified Assumptions

This document lists every definition, rule, and piece of logic in this project
that I (the AI assistant doing the production-readiness work) am **not 100%
certain is correct**. It exists because the user correctly pointed out that code
having a clean git history says nothing about whether its *content* is sound —
the original code was AI-generated, and AI-generated code can contain
plausible-looking but wrong logic ("hallucinations").

Nothing here is asserted to be broken. Each item is something that **could not be
verified in this environment** (no Android/Termux device is available; Termux
commands are not present) or that relies on a **heuristic or assumption** rather
than a proven guarantee.

Legend:
- **Severity**: how much it matters if the assumption is wrong.
- **Confidence**: my rough confidence that the current behaviour is correct.
- **How to verify**: the concrete check that would settle it.

---

## A. Probe logic (state detection) — `src/claude_phone/actions.py`

### A1. `termux_ready` probe likely always returns True — ✓ FIXED
- **What it did:** `probe("echo $TERMUX_VERSION")` → fact `termux_ready`.
- **Concern:** `echo` exits 0 regardless of whether `$TERMUX_VERSION` is set or
  empty. The probe checks the **exit code**, not the output, so it reported
  `True` even on a non-Termux system; it did not actually detect Termux.
- **Severity:** Low–Medium · **Confidence it was correct as a detector:** ~10%
- **✓ Fixed:** the probe is now `probe('test -n "$TERMUX_VERSION"')`, which exits
  non-zero when the variable is empty/unset and therefore genuinely detects
  Termux. Covered by `tests/test_actions.py`
  (`test_termux_ready_probe_is_false_outside_termux` /
  `..._is_true_inside_termux`). The `plan`/`prompt` commands no longer assert the
  fact blindly: `plan` warns when not in Termux (still injecting it as the
  planner's bootstrap root so dry-run previews work), and `prompt` lets the probe
  decide so the generated prompt mirrors reality.

### A2. `termux_api_ready` detects the CLI, not the Termux:API app
- **What it does:** `probe("command -v termux-battery-status")`.
- **Concern:** This confirms the `termux-api` *package* (CLI shims) is installed,
  but **not** that the companion **Termux:API Android app (APK)** is installed
  and permitted. If the APK is missing, the CLI commands can hang or fail at
  runtime even though this probe says the fact holds.
- **Severity:** Medium · **Confidence:** ~50%
- **How to verify:** On a device with the `termux-api` package but without the
  Termux:API app, run `termux-battery-status` and observe hang/failure.

### A3. `has_internet` relies on ICMP ping to 8.8.8.8
- **What it does:** `ping -c 1 -W 2 8.8.8.8`.
- **Concern:** Some mobile networks / Android configurations block ICMP, and
  `ping` flag semantics (`-W` timeout units) can differ. A blocked-ICMP network
  with working HTTP would be falsely reported as offline.
- **Severity:** Low–Medium · **Confidence:** ~70%
- **How to verify:** Test on a network that blocks ICMP; compare with an
  HTTP-based check (e.g. `curl -sI https://example.com`).

### A4. `wifi_connected` / `battery_known` probes parse command output
- **What they do:** pipe `termux-*` output through `grep -q ssid` / `grep -q
  percentage`.
- **Concern:** Depends on the exact JSON/text field names emitted by the current
  Termux:API version. If the output schema differs (key casing, field rename),
  the grep silently fails and the fact is reported absent.
- **Severity:** Low · **Confidence:** ~95% (raised after doc verification)
- **How to verify:** Run `termux-wifi-connectioninfo` and
  `termux-battery-status` on-device and confirm the literal substrings `ssid`
  and `percentage` appear.
- **✓ Verified (docs):** the exact field names `percentage` and `ssid` are
  confirmed in current Termux:API JSON output — see
  `docs/UNCERTAINTIES_VERIFICATION.md` (A4). Only the version pin is unconfirmed.

---

## B. Termux command catalogue — `src/claude_phone/actions.py`

I have **not** been able to confirm against a live device or current Termux
documentation that each command name, flag, and path below is exactly correct.
They look right, but "looks right" is precisely the property of a hallucination.

### B1. `pkg install -y nodejs-lts`
- **Concern:** Termux ships both `nodejs` and `nodejs-lts`; package availability
  and naming change over time. If `nodejs-lts` is unavailable in the active
  repo, the install fails.
- **Severity:** Medium (it's on the critical path to `claude_installed`) ·
  **Confidence:** ~75%
- **How to verify:** `pkg show nodejs-lts` on-device.

### B2. `pkg update -y && pkg upgrade -y` is non-interactive
- **Concern:** `pkg upgrade` can prompt on config-file conflicts; `-y` may not
  suppress every prompt. Could block automation.
- **Severity:** Low–Medium · **Confidence:** ~70%
- **How to verify:** Run on a device with pending upgrades and observe whether
  any interactive prompt appears.

### B3. `termux-setup-storage` is interactive (Android permission dialog)
- **Concern:** It triggers a system permission popup that the **user must tap**.
  It cannot complete headlessly, so any "fully automated" claim for the storage
  step is wrong; the run will pause for human interaction the first time.
- **Severity:** Medium · **Confidence it's interactive:** ~90%
- **How to verify:** First-run on a fresh Termux install.

### B4. Storage paths `$HOME/storage/{shared,dcim,downloads}`
- **Concern:** These symlinks are created by `termux-setup-storage`. Their exact
  presence/names depend on Android version and storage layout. The camera action
  writes to `$HOME/storage/dcim/claude_photo.jpg`, assuming `dcim` exists and is
  writable.
- **Severity:** Low · **Confidence:** ~95% (raised after doc verification)
- **How to verify:** `ls -la $HOME/storage/` after setup.
- **✓ Verified (docs):** `shared`, `dcim`, and `downloads` are all part of the
  canonical symlink set created by `termux-setup-storage` — see
  `docs/UNCERTAINTIES_VERIFICATION.md` (B4).

### B5. The remaining `termux-*` commands and flags
- Commands assumed correct but unverified on-device:
  `termux-battery-status`, `termux-wifi-connectioninfo`, `termux-wifi-scaninfo`,
  `termux-telephony-deviceinfo`, `termux-location -p gps`, `termux-sensor -l`,
  `termux-torch on|off`, `termux-vibrate -d 500`, `termux-volume`,
  `termux-notification --title --content`, `termux-camera-photo`,
  `termux-clipboard-get`.
- **Severity:** Low (most are leaf/optional actions, not on the critical path) ·
  **Confidence:** ~95% (raised after doc verification)
- **How to verify:** Run each on-device; cross-check flags against the current
  Termux:API docs (https://wiki.termux.com/wiki/Termux:API).
- **✓ Verified (docs):** every command name and flag is confirmed against the
  official `termux-api-package` scripts — `-d <ms>` (vibrate), `-p gps`
  (location), `-l` (sensor), `--title/--content` (notification),
  `termux-torch [on|off]`, and the existence of `termux-wifi-scaninfo`,
  `termux-volume`, `termux-camera-photo`, `termux-clipboard-get`,
  `termux-telephony-deviceinfo`. See `docs/UNCERTAINTIES_VERIFICATION.md` (B5).

---

## C. Planner algorithm — `src/claude_phone/planner.py`

### C1. Greedy "cheapest producer" is NOT guaranteed globally optimal
- **What it does:** For each needed fact, `plan()` picks
  `min(producers, key=complexity)` — the locally cheapest action that produces
  it (`planner.py:91`).
- **Concern:** This is a **greedy heuristic**. It ignores the cost of the chosen
  producer's *own* preconditions. A "cheap" action with expensive prerequisites
  can yield a higher total cost than an "expensive" action with none. So the
  resulting plan is valid but **not necessarily minimum-cost**. The code and
  docs should not be read as claiming optimality.
- **Severity:** Low (in the current catalogue most facts have a single producer,
  so it rarely bites) · **Confidence the plan is *valid*:** ~95% ·
  **Confidence it's *optimal*:** ~20%
- **How to verify:** Construct a catalogue with two producers for one fact where
  greedy picks the worse total; observe suboptimal plan.

### C2. `critical_path` correctness depends on prior topological order
- **What it does:** Computes longest-cost chain with an O(n²) scan
  (`planner.py:122-154`), assuming `plan` is already topologically sorted.
- **Concern:** Correct **only because** `_topo_sort` runs first. If
  `critical_path` were ever called on an unordered list, `cost_to` lookups for
  not-yet-processed predecessors would be wrong. It's an implicit coupling, not
  an enforced one.
- **Severity:** Low · **Confidence given current call order:** ~90%
- **How to verify:** Unit test feeding a deliberately unordered plan.

### C3. Tie-breaking and determinism
- **Concern:** `_topo_sort` sorts each ready batch by complexity, but ties
  (equal complexity) resolve by pre-existing list order. Plan order among
  equal-cost actions is therefore stable but arbitrary, not semantically chosen.
- **Severity:** Very low · **Confidence:** ~85%
- **How to verify:** Inspect ordering of the many `0.1`-complexity actions.

### C4. Complexity weights are arbitrary
- **Concern:** The numbers (`3, 2, 1, 0.5, 0.1`) are guesses at relative
  cost/time, not measured. They drive both ordering and the critical path, so a
  mis-estimate changes the reported plan even if execution is fine.
- **Severity:** Very low (cosmetic/ordering) · **Confidence they're "reasonable":**
  ~60%
- **How to verify:** Time real `pkg`/`npm` operations on-device and compare.

---

## D. Executor semantics — `src/claude_phone/planner.py`

### D1. Asymmetry between "skipped" and "failed"
- **What it does:** In `execute_plan`, an action whose preconditions are unmet is
  **skipped** (`ok=False`, but the loop continues), whereas an action that raises
  during execution **stops the run** and returns `False` immediately
  (`planner.py:195-213`).
- **Concern:** This asymmetry is a deliberate-looking choice but I'm not certain
  it matches intended behaviour. "Skip and continue" can leave the run pressing
  on after a precondition gap, producing a partially-configured device while
  still surfacing `ok=False`.
- **Severity:** Low–Medium · **Confidence it's intended:** ~50%
- **How to verify:** Decide product intent: should an unmet precondition abort or
  continue? Add a test pinning the chosen behaviour.

### D2. Return-value contract (changed during hardening)
- **What it does:** `execute_plan` now returns `bool` (was previously the final
  state set). The CLI maps this to the process exit code.
- **Concern:** Any external caller relying on the old return type would break.
  Internal to this repo it's consistent, but I can't rule out undocumented
  consumers.
- **Severity:** Low · **Confidence:** ~85%
- **How to verify:** Grep for callers; confirmed only `cli.py` uses it here.

---

## E. Shell scripts — `scripts/setup-termux.sh`, `scripts/phone-settings.sh`

### E1. Not executed on a device
- **Concern:** They pass `shellcheck`, but static linting is not runtime proof.
  The actual `pkg`/`termux-*` sequences, ordering, and any prompts are
  unverified on Android.
- **Severity:** Medium · **Confidence:** ~70%
- **How to verify:** Run end-to-end in a real Termux session.

---

## F. Things I changed during hardening that are judgement calls

### F1. Timeout defaults (120 s actions, 60 s GPS)
- Chosen by intuition (`config.py`). Long `pkg`/`npm` operations on slow mobile
  networks could legitimately exceed 120 s and be killed as "timed out".
- **Severity:** Medium · **Confidence they're adequate:** ~60%
- **How to verify:** Measure worst-case real durations on-device/cellular.

### F2. `shellcheck-py` pre-commit rev pin (`v0.10.0.1`)
- Pinned to a specific tag for a Docker-free hook. Tag is assumed to exist on the
  mirror; if not, `pre-commit autoupdate` resolves it.
- **Severity:** Very low · **Confidence:** ~85%

### F3. Test coverage reflects mocked behaviour
- All tests mock the Termux/`subprocess` boundary. They prove the **Python
  logic** (planner, executor, CLI wiring) is correct; they prove **nothing**
  about real device behaviour. High coverage here is not evidence against any
  uncertainty in sections A, B, or E.
- **Severity:** (informational) · **Confidence in this statement:** ~99%

---

## What would move these from "uncertain" to "verified"

A single end-to-end run on the target device (Samsung Galaxy S22+, fresh Termux +
Termux:API installed) with verbose logging would resolve the large majority of
A, B, and E. The planner items (C, D) are resolvable purely by reasoning/unit
tests and do not need hardware.
