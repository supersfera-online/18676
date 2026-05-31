# Internet Verification of Confident Definitions

Each definition from `docs/DEFINITIONS.md` that rests on a general, named
concept (a language rule, an algorithm, a convention) was checked against an
internet primary/authoritative source. Marking scheme requested by the user:

- **QQ** + source link — the logic in the code is a **full match** with the
  primary source.
- **Zuddd** + (no source) — there is **no external primary source**; the rule is
  project-specific (a design decision local to this repo), so the source cell is
  left empty.
- **jpjjjjj** — the concept matches the source **but not completely** (the code
  adapts, narrows, or deviates from the canonical definition in some respect).
- *(blank)* — no match at all; no source recorded.

| # | Definition (from DEFINITIONS.md) | The logic / rule as coded | Mark | Source |
|---|----------------------------------|---------------------------|------|--------|
| 1.1a | `InformationRemnant` is a `@dataclass`; fields are class vars with type annotations, `__init__`/`__repr__` auto-generated | `@dataclass` generates `__init__` from annotated fields | QQ | https://docs.python.org/3/library/dataclasses.html |
| 1.1b | World = **set of string facts**; actions only **add** facts, never delete (monotonic) | STRIPS models actions with pre/add/**del** effects | jpjjjjj | https://en.wikipedia.org/wiki/Stanford_Research_Institute_Problem_Solver |
| 1.2 | `can_execute` → `all(p in state for p in preconditions)`; no preconditions ⇒ always runnable because `all([])` is `True` | `all()` returns `True` for an empty iterable | QQ | https://docs.python.org/3/library/functions.html#all |
| 1.3a | `execute` returns `state | set(effects)` — a **new** set, input not mutated | `|` / `union()` returns a new set, operands unchanged | QQ | https://docs.python.org/3/library/stdtypes.html#frozenset.union |
| 1.3b | Action return `True` **or `None`** counts as success; only `False` is failure | (project-specific success convention) | Zuddd | |
| 2.1 | `_producers`: fact → list of remnants producing it, for O(1) lookup | (project-specific index structure) | Zuddd | |
| 2.2a | `plan()` chains **backward** from goal facts to subgoals via producers' preconditions | Backward/regression planning: regress goal over actions into subgoals | QQ | https://aima.cs.berkeley.edu/newchap11.pdf |
| 2.2b | `needed = target - initial`; unreachable fact (no producer) ⇒ raise | (project-specific guard) | Zuddd | |
| 2.2c | Pick **cheapest** producer `min(..., key=complexity)` — greedy, not optimal | (greedy heuristic; see UNCERTAINTIES C1) | Zuddd | |
| 2.3 | `_topo_sort`: repeatedly take precondition-satisfied actions in layers; none ready + remaining ⇒ "Deadlock" (cycle) | Kahn's algorithm, layered topological sort; remaining nodes ⇒ cycle | jpjjjjj | https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm |
| 2.4 | `critical_path`: `cost_to[a] = complexity + max(cost_to[predecessors])` over topo order; walk back from max | Longest path in DAG via DP in topological order = critical path | QQ | https://en.wikipedia.org/wiki/Longest_path_problem#Acyclic_graphs |
| 3.1 | `Executor.__init__(initial=None)` copies inside ⇒ avoids shared-mutable-default bug | `None` default + copy-inside is the canonical fix for mutable defaults | QQ | https://docs.python.org/3/library/dataclasses.html#mutable-default-values |
| 3.3a | `execute_plan` returns `bool`; CLI maps to exit code | (project-specific contract) | Zuddd | |
| 3.3b | Action that **raises** ⇒ stop immediately; precondition unmet ⇒ **skip + continue**, `ok=False` | (project-specific execution policy; see UNCERTAINTIES D1) | Zuddd | |
| 4.1 | `shell=True` safe **only** because commands are static literals, no user input interpolated | Bandit B602: static string ⇒ low severity; computed string ⇒ injection risk | QQ | https://bandit.readthedocs.io/en/latest/plugins/b602_subprocess_popen_with_shell_equals_true.html |
| 4.2 | `shell()` catches `subprocess.TimeoutExpired` ⇒ returns `False` instead of hanging | `run(..., timeout=)` raises `TimeoutExpired` when it expires | QQ | https://docs.python.org/3/library/subprocess.html#subprocess.TimeoutExpired |
| 5.1 | Subcommands with `plan` as default when omitted; legacy flags mapped | argparse has no built-in default subcommand; custom logic needed | jpjjjjj | https://docs.python.org/3/library/argparse.html#sub-commands |
| 5.2 | `main()` returns `int`; `sys.exit(main())` ⇒ 0 success / non-zero failure | Unix convention: 0 = success, non-zero = failure | QQ | https://en.wikipedia.org/wiki/Exit_status |
| 5.4 | `probe_reality`: a probe that raises is caught, logged, loop **keeps going** | (project-specific resilience policy) | Zuddd | |
| 6.1a | `configure_logging` sets `propagate = False` to prevent duplicate emission via ancestors | `propagate=False` stops records passing to ancestor handlers ⇒ no duplicates | QQ | https://docs.python.org/3/library/logging.html#logging.Logger.propagate |
| 6.1b | Removes pre-existing handlers first ⇒ idempotent across calls | Clearing handlers prevents duplicate-handler log doubling | QQ | https://docs.python.org/3/library/logging.html#logging.Logger.handlers |
| 9 | `PING_TARGET = 8.8.8.8` is a literal IP so the check doesn't depend on DNS | 8.8.8.8 is Google Public DNS; pinging the literal IP bypasses DNS resolution | QQ | https://developers.google.com/speed/public-dns/docs/using |

## Notes on the partial / no-source marks

- **1.1b `jpjjjjj`** — The canonical STRIPS model has **add *and* delete**
  effects (`s' = (s ∪ add) \ del`). This code implements add-only (monotonic),
  with no delete list. Concept matches, but not completely.
- **2.3 `jpjjjjj`** — Canonical Kahn's algorithm tracks **in-degree counts** and
  uses a queue; this code re-scans for precondition-satisfied actions each pass
  (layered variant). Same result and cycle-detection idea, different bookkeeping.
- **5.1 `jpjjjjj`** — argparse documents subcommands but has **no built-in
  default-subcommand** feature; the "default to `plan`" behaviour is custom code
  on top of the documented mechanism, so it's a partial match.
- **Zuddd rows** — these are deliberate design decisions local to this project
  (success-as-None convention, the producer index, the greedy choice, the
  skip-vs-raise policy, the bool/exit-code contract, the probe-resilience loop).
  They have no external canonical primary source to match against, so the source
  cell is intentionally empty.

## Sources

- [Python `dataclasses`](https://docs.python.org/3/library/dataclasses.html)
- [STRIPS — Wikipedia](https://en.wikipedia.org/wiki/Stanford_Research_Institute_Problem_Solver)
- [Python built-in `all()`](https://docs.python.org/3/library/functions.html#all)
- [Python set `union()` / `|`](https://docs.python.org/3/library/stdtypes.html#frozenset.union)
- [AIMA Ch. 11, Planning (backward/regression search)](https://aima.cs.berkeley.edu/newchap11.pdf)
- [Topological sorting — Kahn's algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm)
- [Longest path in a DAG (Wikipedia)](https://en.wikipedia.org/wiki/Longest_path_problem#Acyclic_graphs)
- [Mutable default values in dataclasses (Python docs)](https://docs.python.org/3/library/dataclasses.html#mutable-default-values)
- [Bandit B602 — subprocess with shell=True](https://bandit.readthedocs.io/en/latest/plugins/b602_subprocess_popen_with_shell_equals_true.html)
- [Python `subprocess.TimeoutExpired`](https://docs.python.org/3/library/subprocess.html#subprocess.TimeoutExpired)
- [Python `argparse` sub-commands](https://docs.python.org/3/library/argparse.html#sub-commands)
- [Exit status — Wikipedia](https://en.wikipedia.org/wiki/Exit_status)
- [Python logging `propagate`](https://docs.python.org/3/library/logging.html#logging.Logger.propagate)
- [Python logging handlers](https://docs.python.org/3/library/logging.html#logging.Logger.handlers)
- [Google Public DNS (8.8.8.8)](https://developers.google.com/speed/public-dns/docs/using)
