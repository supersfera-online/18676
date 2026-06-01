# Architecture

`claude-phone` is a tiny automatic planner inspired by
[STRIPS](https://en.wikipedia.org/wiki/Stanford_Research_Institute_Problem_Solver).
It turns "make the phone ready for Claude Code" into a search problem over a set
of boolean facts.

## Core concepts

- **Fact** — a string describing something true about the world, e.g.
  `nodejs_ready`, `storage_accessible`, `fully_configured`.
- **State** — the set of facts currently true.
- **Action** (`InformationRemnant`) — has `preconditions` (facts required to
  run), `effects` (facts it makes true), a `complexity` cost, and a callable
  that performs the work. See `src/claude_phone/planner.py`.

## Modules

| Module | Responsibility |
| --- | --- |
| `planner.py` | `InformationRemnant`, `Planner`, `Executor` — the engine. |
| `runner.py` | `shell()` / `probe()` — safe subprocess wrappers with timeouts. |
| `actions.py` | The catalogue of phone actions and `PROBES`. |
| `prompt_builder.py` | Context-aware Claude system-prompt generation. |
| `config.py` | Tunable constants (ping target, device name, timeouts). |
| `cli.py` | Argument parsing, subcommands, presentation, exit codes. |

## How a run works

1. **Probe reality** (`cli.probe_reality`): each entry in `actions.PROBES` is a
   read-only check that reports whether a fact already holds. The results form
   the *initial state*. (`--skip-probe` starts from an empty state.)
2. **Plan** (`Planner.plan`): starting from the target facts, the planner walks
   *backwards*. For each needed fact it picks the **cheapest** producing action
   (`min` by `complexity`) and enqueues that action's unmet preconditions. This
   yields the set of actions required.
3. **Order** (`Planner._topo_sort`): the chosen actions are topologically sorted
   so every action runs only after its preconditions are satisfied. If no action
   is ever runnable, a `Deadlock!` error is raised (dependency cycle).
4. **Critical path** (`Planner.critical_path`): the longest-cost dependency
   chain is computed and reported, giving a sense of the minimum sequential cost.
5. **Execute** (`Executor.execute_plan`): actions run in order, updating state
   and recording history. On failure it stops and returns `False`; the CLI maps
   that to a non-zero exit code. `--dry-run` simulates effects without running
   any command.

## Security model

`runner.shell()` / `runner.probe()` execute commands with `shell=True`. This is
safe **only** because every command string is a trusted literal defined in
`actions.py`; nothing from user input is ever interpolated into a command. The
CLI's `--target` is used purely as a *fact name* for the planner. These
invariants are annotated with `# nosec` and enforced by review. All subprocess
calls have timeouts so a hung command (e.g. an unreachable `ping` or a GPS fix)
cannot block the run indefinitely.

## Extending

Add a new capability by appending an `InformationRemnant` to
`actions.phone_remnants()` (and, if it can be detected, a probe to `PROBES`).
The planner picks it up automatically — no changes to the engine are needed.
`tests/test_actions.py` guards that every precondition remains reachable.
