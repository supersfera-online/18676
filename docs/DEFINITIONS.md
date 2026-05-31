# Definitions I Am Confident About

Companion to `docs/UNCERTAINTIES.md`. That file lists everything I am **not**
100% sure of (chiefly device-dependent Termux behaviour). This file lists the
definitions, rules, and logic I **am** confident are correct, with what each
thing is and how it works.

**Why I'm confident about these:** they are pure Python whose behaviour is
fully determined by the code in this repository — not by an absent Android
device. They are exercised by the test suite (45 tests passing, 91% branch
coverage; planner 98%, runner 100%, actions 100%) and by direct execution
observed in this environment. Confidence here is about **the Python mechanics**,
not about whether a given Termux command is the right thing to run on a real
phone (that is what `UNCERTAINTIES.md` covers).

Scope note: this lists *what the code does and why it is internally correct*. It
deliberately excludes the domain question "is this the right command for the
device", which lives in `UNCERTAINTIES.md`.

---

## 1. Data model — `planner.py`

### 1.1 `InformationRemnant` (the unit of "an action")
- **What it is:** a `@dataclass` describing one action with six fields:
  `name`, `preconditions` (facts required before it can run), `effects` (facts it
  makes true), `complexity` (a cost weight, default `1.0`), `action` (an optional
  zero-arg callable returning `bool | None`), and `description`.
- **The world model:** state is a **set of string facts**. A fact is either
  present (true) or absent (unknown/false). There is no negation and no fact
  deletion — actions only ever *add* facts. This is a monotonic STRIPS model.
- **Why I'm confident:** it's a plain dataclass with no hidden behaviour; the
  field types and defaults are explicit.

### 1.2 `InformationRemnant.can_execute(state)`
- **What it does:** returns `True` iff **every** precondition is in `state`
  (`all(p in state for p in self.preconditions)`).
- **Logic:** an action with no preconditions is always runnable (`all([])` is
  `True`). This is correct and intended.

### 1.3 `InformationRemnant.execute(state)`
- **What it does:** runs the action and returns the **new** state, or raises.
- **Logic, step by step:**
  1. If preconditions aren't met → raise `RuntimeError` listing what's missing.
     (Guard against being called out of order.)
  2. If there is an `action` callable, call it; otherwise treat as success.
  3. **Success rule:** `True` *or* `None` counts as success → return
     `state | set(effects)` (a new set; the input is not mutated).
  4. Only an explicit falsy return (`False`) is failure → raise `RuntimeError`.
- **Why `None` == success:** lets an action that has no meaningful boolean result
  still succeed. This is a deliberate, documented rule.

---

## 2. The planner — `planner.py::Planner`

### 2.1 Producer index (`__init__`)
- **What it is:** `_producers` maps each fact → list of remnants that have it in
  their `effects`. Built once at construction.
- **Why:** lets `plan()` answer "what action produces fact X?" in O(1).

### 2.2 `plan(initial, target)` — backward chaining
- **What it does:** returns an ordered, runnable list of remnants that takes the
  world from `initial` to a state containing all of `target`.
- **Logic, step by step:**
  1. `needed = target - initial` (don't plan for facts already true).
  2. BFS-style queue over needed facts, with a `visited` set so each fact is
     expanded once.
  3. For each fact, look up producers. **If none exist → raise** "Cannot reach
     'X': no action produces it." (This is the correct, explicit failure for an
     unreachable goal.)
  4. Pick the **cheapest** producer (`min(..., key=complexity)`), add it to the
     plan set (keyed by name so each action appears once), and enqueue *its*
     preconditions that aren't already in `initial`.
  5. Hand the collected actions to `_topo_sort` for ordering.
- **Confidence boundary:** I'm confident the produced plan is **valid** (every
  action's preconditions are satisfiable and it reaches the target, or it raises
  cleanly). I'm *not* claiming it's **cost-optimal** — the greedy choice in
  step 4 is a heuristic; that caveat lives in `UNCERTAINTIES.md` (C1).

### 2.3 `_topo_sort(remnants, initial)` — ordering
- **What it does:** orders the selected actions so each runs only after its
  preconditions are available.
- **Logic:** repeatedly take all actions whose preconditions are currently
  satisfied ("ready"), sorted by complexity (cheapest first within a layer),
  append them, and add their effects to the available set. **If a pass finds no
  ready action but actions remain → raise "Deadlock!"** — this correctly detects
  an unorderable selection (a dependency cycle).
- **Why I'm confident:** this is textbook Kahn-style layered topological sort;
  the deadlock branch is covered by tests.

### 2.4 `critical_path(plan, initial)` — longest dependency chain
- **What it does:** returns the chain of actions with the greatest cumulative
  complexity, plus that total. This is the "this is the part that gates total
  time" path.
- **Logic:** for each action in (topologically ordered) `plan`, `cost_to[action]
  = own complexity + max cost_to over its non-initial predecessors`; it tracks
  `prev` to reconstruct the path, then walks back from the maximum.
- **Confidence boundary:** correct **given** `plan` is already topologically
  ordered (which `plan()` guarantees, since it calls `_topo_sort` first). The
  empty-plan case returns `([], 0.0)`. The dependency on prior ordering is noted
  in `UNCERTAINTIES.md` (C2); the math itself I'm confident in.
- **Verified by execution:** on the default catalogue it reports
  `Update Termux → Install Node.js → Install Claude Code → Fully ready`,
  cost `8.1` — which I confirmed by hand against the action weights.

---

## 3. The executor — `planner.py::Executor`

### 3.1 `__init__(initial=None)`
- **What it does:** holds mutable `state` (a copy of `initial`, or empty) and a
  `history` list. Using `None` as the default and copying inside avoids the
  classic shared-mutable-default bug.

### 3.2 `probe_state(probes)`
- **What it does:** runs each probe callable; adds the fact on success, discards
  it on failure. Returns the updated state. Pure set bookkeeping over whatever
  the probes report.

### 3.3 `execute_plan(plan, dry_run=False)` → `bool`
- **What it does:** runs the plan in order; returns `True` if everything
  completed (or was simulated), `False` otherwise.
- **Logic, the rules I'm confident about:**
  - **Return contract:** the boolean result is what the CLI turns into the
    process exit code (`0` for `True`, `1` for `False`). This is the fix for the
    original "success but non-zero exit" bug.
  - **`dry_run`:** simulates by unioning effects into state and printing the
    plan, without calling any action. Useful and side-effect-free.
  - **Hard failure:** if an action *raises* during real execution, the loop
    **stops immediately** and returns `False`.
  - **Soft skip:** if an action's preconditions are unexpectedly unmet at run
    time, it is **skipped**, `ok` is set to `False`, and the loop continues.
  - (Whether "skip and continue" is the *desired product behaviour* is the only
    open question here — recorded in `UNCERTAINTIES.md` D1. The *mechanics* above
    are what the code does, and I'm confident of them.)

---

## 4. Execution helpers — `runner.py`

### 4.1 The `shell=True` trust boundary (security invariant)
- **What it is:** both `shell()` and `probe()` run their command via
  `subprocess.run(..., shell=True)`. This is **safe in this codebase** because
  every command string is a **static literal** defined in `actions.py`; no
  user-supplied input is ever interpolated into a command. The CLI's `--target`
  is used only as a planner *fact name* and never reaches a shell.
- **Why I'm confident:** I can see all call sites; the `# nosec` annotations
  record the invariant and bandit reports no issues. (This is an invariant about
  *this repo's* code, not a claim that `shell=True` is generally safe.)

### 4.2 `shell(cmd, timeout=DEFAULT_TIMEOUT)`
- **What it does:** returns a zero-arg callable that runs `cmd`, captures output,
  logs it, and returns `True` on exit code 0, `False` on non-zero **or timeout**.
- **Key rule:** `subprocess.TimeoutExpired` is caught and converted to a logged
  `False` — so a hanging command can no longer block the run forever. This is the
  timeout hardening; I'm confident it works because it's covered by a test that
  mocks a timeout.

### 4.3 `probe(cmd, timeout=DEFAULT_TIMEOUT)`
- **What it does:** returns a zero-arg callable that returns `True` iff `cmd`
  exits 0, `False` otherwise (including timeout). Same timeout-safety rule.
- **Confidence boundary:** I'm confident about *the wrapper mechanics* (exit-code
  → bool, timeout → False). Whether a *specific* probe command actually detects
  what its fact name claims is a separate matter in `UNCERTAINTIES.md` (A1–A4).

---

## 5. CLI — `cli.py`

### 5.1 Subcommand resolution
- **What it does:** commands are `plan` (default), `probe`, `list`, `graph`,
  `prompt`. Legacy flags `--probe/--list/--graph` are mapped onto the new
  subcommands by `_resolve_command` for backward compatibility.
- **Why I'm confident:** simple, deterministic mapping; covered by CLI tests.

### 5.2 `main(argv)` → `int`
- **What it does:** parses args, configures logging, dispatches to the chosen
  command, and **returns an int exit code**; `__main__` / the console entry
  point pass it to `sys.exit`. Correct exit-code propagation end-to-end.

### 5.3 `_run_plan` semantics I'm confident about
- `--skip-probe` starts from empty state; otherwise it probes reality first.
- `termux_ready` is **always** added to the initial state (so the planner has its
  universal precondition). *(Side effect: it makes the `termux_ready` probe
  redundant — flagged in `UNCERTAINTIES.md` A1.)*
- Facts already satisfied are subtracted from the target; if nothing remains it
  reports "Goal already achieved" and returns `0`.
- A `RuntimeError` from `plan()` (unreachable goal / deadlock) is caught and
  turned into a logged error + exit `1`.

### 5.4 `probe_reality()` resilience
- **Rule I'm confident about:** if an individual probe **raises**, it is caught,
  logged as `? fact (check error)`, and the loop **keeps probing** the rest. One
  bad probe can't abort state detection.

---

## 6. Logging — `logging_config.py`

### 6.1 `configure_logging(verbose, quiet)`
- **What it does:** sets the package logger level — `WARNING` if `quiet`,
  `DEBUG` if `-v` given, else `INFO`. Installs a single `StreamHandler` with a
  bare `%(message)s` formatter (preserving the original console look), removes any
  pre-existing handlers (idempotent across calls/tests), and sets
  `propagate = False` so messages aren't double-emitted by the root logger.
- **Why I'm confident:** standard logging setup; the idempotency and
  no-propagation rules are deliberate and verifiable by reading the code.

---

## 7. Prompt builder — `prompt_builder.py`

### 7.1 Data-driven profiles
- **What it is:** `INTEGRATION_PROFILES` (keyed by user id) and `DEFAULT_PROFILE`
  hold the session context as **data**; unknown users fall back to the default.
  Adding a profile requires no logic changes.

### 7.2 `get_session_context(user_id, now=None)`
- **What it does:** merges the matching (or default) profile with a
  `session_start_time` and the `user_id`. `now` is **injectable** so tests get
  deterministic output. Confident — pure dict construction.

### 7.3 `build_system_prompt(context)`
- **What it does:** renders a fixed system-prompt template, substituting context
  fields with safe fallbacks (e.g. missing location → "Not specified", empty
  integrations → "None"). Pure string formatting; no side effects.
- **Confidence boundary:** I'm confident it renders deterministically from its
  input. I'm **not** making any claim about whether the prompt's *content* is
  desirable — that's a product/wording judgement, not code correctness.

---

## 8. Package wiring — `__init__.py`, `__main__.py`

- `__init__.py` exports `Planner`, `Executor`, `InformationRemnant`,
  `__version__` (`"0.1.0"`) — the stable public API.
- `__main__.py` enables `python -m claude_phone` by calling `cli.main` and
  exiting with its return code. Confident — trivial, and the wheel/CLI install
  was observed working in a clean venv.

---

## 9. Configuration constants — `config.py`

- **What they are:** `PHONE_MODEL` (banner text only), `PING_TARGET` (`8.8.8.8`,
  a literal IP so the connectivity check doesn't depend on DNS),
  `DEFAULT_TARGET` (`"fully_configured"`), and the timeouts
  `DEFAULT_TIMEOUT = 60.0` / `LOCATION_TIMEOUT = 120.0`.
- **What I'm confident about:** these are the single source of truth for those
  values and are wired through correctly. Whether the timeout *numbers* are large
  enough for real mobile networks is a tuning judgement, noted in
  `UNCERTAINTIES.md` (F1).

---

## One-line summary of the confidence split

- **This file:** the Python logic is internally correct and behaves as described
  — verified by tests and execution.
- **`UNCERTAINTIES.md`:** whether the Termux commands/probes are the right thing
  to do on a real device — not verifiable here.
