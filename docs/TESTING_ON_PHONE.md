# Testing Guide: Running `claude-phone` on a Real Android Phone

This guide is for **manually testing this project on a device** — not just
installing Claude Code, but verifying that the `claude-phone` planner/executor and
its 24 Termux actions actually behave as designed. It deliberately walks through
the items that could **not** be verified without hardware (see
`docs/UNCERTAINTIES.md` and `docs/UNCERTAINTIES_VERIFICATION.md`).

> **Why a separate guide?** `SETUP.md` is the plain "install Claude Code" path.
> This file is a **test plan**: each step has an *expected result* and a box to
> record what actually happened, so the open uncertainties get resolved.

Target device: Samsung Galaxy S22+ (any modern Android works; paths may vary).

---

## 0. Before you start — what we're trying to confirm

The pure-Python logic is already verified by the test suite. On-device testing
exists to confirm the **device-dependent** assumptions. Keep this short list in
mind — these are the things most likely to differ from expectation:

| ID | Thing to watch | Expected | Known risk |
|----|----------------|----------|------------|
| A1 | `claude-phone probe` detecting Termux | `termux_ready` ✓ | `echo $TERMUX_VERSION` always exits 0 → may be a false ✓ |
| A2 | Termux:API commands | work after installing the **app + package** | package alone is not enough |
| A3 | `has_internet` (ICMP ping) | ✓ when online | some networks block ICMP → false ✗ |
| B3 | `termux-setup-storage` | creates `~/storage` | **interactive** — needs a manual tap |
| B5 | `termux-*` flags | each action exits 0 | a wrong flag fails that action |
| — | `claude` global CLI | `command -v claude` succeeds | npm package may **not** install a global `claude` on Termux (needs alias) |

---

## 1. Install Termux and Termux:API (the apps)

1. Install **F-Droid** from https://f-droid.org/ (do **not** use the Play Store
   build — it is outdated).
2. From F-Droid install **both**:
   - **Termux** (the terminal)
   - **Termux:API** (the hardware bridge app — APK)

> ⚠️ The `termux-api` *package* you install later (step 3) is only the CLI shims.
> The Termux:API **app** above must also be installed or sensor/battery/wifi
> commands hang or fail. (This is uncertainty **A2**.)

---

## 2. Get the code onto the phone

Open Termux and run:

```bash
pkg install -y git
git clone https://github.com/supersfera-online/18676.git
cd 18676
```

---

## 3. Install the Python toolchain and the package

```bash
pkg update -y && pkg upgrade -y
pkg install -y python nodejs-lts git termux-api
pip install -e .
```

**Expected:** `claude-phone --help` prints usage.

```
[ ] PASS / [ ] FAIL  — claude-phone is on PATH and prints help
```

> If `pip install -e .` complains, you can still run the tool with
> `python -m claude_phone ...` from inside the repo.

---

## 4. Grant storage access (interactive!)

```bash
termux-setup-storage
```

**Expected:** an Android permission dialog appears — **tap "Allow"**. This
creates `~/storage/...`. (Uncertainty **B3**: this step cannot be automated.)

```bash
ls ~/storage/
```

```
[ ] PASS / [ ] FAIL  — ~/storage exists; note which subdirs are present:
     ____________________________________________   (B4: dcim/downloads/shared?)
```

---

## 5. Test the planner WITHOUT touching the device (safe, first)

These commands are read-only / simulation and are the safest first checks.

```bash
# Show the action catalogue
claude-phone list

# Show the dependency graph
claude-phone graph

# Simulate the full plan to fully_configured (no commands are executed)
claude-phone plan --skip-probe --dry-run
```

**Expected:** `--dry-run` prints a 9-step plan ending in `fully_configured`, with
a critical path `Update Termux → Install Node.js → Install Claude Code →
Fully ready` (complexity 8.1). No real installation happens.

```
[ ] PASS / [ ] FAIL  — dry-run plan looks correct, nothing was installed
```

---

## 6. Probe reality (this DOES run real probe commands)

```bash
claude-phone probe
```

**Expected:** a checklist of facts with ✓/✗. Record anything surprising:

```
[ ] termux_ready        ✓/✗   (A1: is it ✓ even though it can't really tell?)
[ ] termux_api_ready    ✓/✗   (needs the Termux:API app from step 1)
[ ] has_internet        ✓/✗   (A3: ✗ here while online ⇒ ICMP blocked)
[ ] nodejs_ready        ✓/✗
[ ] python_ready        ✓/✗
[ ] git_ready           ✓/✗
[ ] claude_installed    ✓/✗   (likely ✗ until step 8)
```

**A3 check:** if `has_internet` is ✗ but you can browse, run
`curl -sI https://example.com | head -1`. If curl works but ping fails, the ICMP
assumption is wrong on this network — note it.

---

## 7. Run the real plan (this installs things)

```bash
claude-phone plan
```

**Expected:** it probes, then executes only the missing steps, ending at
`fully_configured`, and the **process exit code is 0** on success:

```bash
claude-phone plan ; echo "exit=$?"
```

```
[ ] PASS / [ ] FAIL  — plan completed, exit=0
[ ] If it stopped early, record the step + message:
     ____________________________________________
```

---

## 8. The Claude Code CLI — the highest-risk check

After the plan installs `@anthropic-ai/claude-code`, check whether a **global
`claude` command** actually exists:

```bash
command -v claude && claude --version
```

**Expected (per the code):** `claude` is found.

**Known risk:** recent reports say the npm package **no longer ships a global
`claude` binary** on Termux, so this may fail even though install "succeeded". If
so, set up the documented alias:

```bash
# Find the installed cli.js
ls $PREFIX/lib/node_modules/@anthropic-ai/claude-code/cli.js
# Add an alias
echo "alias claude='node \$PREFIX/lib/node_modules/@anthropic-ai/claude-code/cli.js'" >> ~/.bashrc
source ~/.bashrc
claude --version
```

```
[ ] PASS — `claude` worked directly (assumption holds)
[ ] PASS — only worked after alias (assumption WRONG ⇒ claude_installed probe
            and the fully_configured goal need fixing; see UNCERTAINTIES)
[ ] FAIL — neither worked, record error: __________________________________
```

---

## 9. Exercise individual Termux:API actions (flag check, B5)

Each should exit 0 and print something. Tick the ones that work:

```bash
claude-phone plan --target battery_known    # termux-battery-status
claude-phone plan --target wifi_scanned     # termux-wifi-scaninfo
claude-phone plan --target sensors_listed   # termux-sensor -l
claude-phone plan --target torch_on         # termux-torch on  (light comes on!)
claude-phone plan --target torch_off        # termux-torch off
claude-phone plan --target vibrated         # termux-vibrate -d 500
claude-phone plan --target notification_sent
claude-phone plan --target location_known   # termux-location -p gps (can be slow)
```

```
[ ] battery_known   [ ] wifi_scanned   [ ] sensors_listed
[ ] torch_on/off    [ ] vibrated       [ ] notification_sent
[ ] location_known  (note: GPS has a 120s timeout; outdoors works best)
Any action that FAILED — record command + error:
     ____________________________________________
```

---

## 10. Report back

If you want the findings folded into the docs, capture:

1. The full output of `claude-phone probe` and `claude-phone plan ; echo exit=$?`.
2. Which `~/storage` subdirs exist (step 4).
3. Whether `claude` worked directly or needed an alias (step 8) — **most
   important**.
4. Any action from step 9 that failed, with its error.

Run with `-v` for debug output if anything misbehaves:

```bash
claude-phone -v plan --dry-run
```

These five answers resolve the bulk of `docs/UNCERTAINTIES.md`. Anything that
turns out to differ from "Expected" above is a real finding, not a hallucination
— and now it's measured rather than assumed.

---

## Quick troubleshooting

| Symptom | Fix |
|---------|-----|
| `claude-phone: command not found` | use `python -m claude_phone ...`, or re-run `pip install -e .` |
| Sensor/battery commands hang | install the **Termux:API app** (step 1), not just the package |
| `has_internet` ✗ while online | network blocks ICMP; functionally fine for browsing/npm |
| `Permission denied` on `~/storage` | re-run `termux-setup-storage`, tap Allow |
| `npm`/`node` missing | `pkg install -y nodejs-lts` |
| Low space during `npm i -g` | `npm cache clean --force`, check `df -h` |
