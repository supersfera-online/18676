# jpjjjjj Rows — Does the Divergence Change the Logic?

This table collects every `jpjjjjj` (partial-match) row from **both** verification
files and asks one question per row, independently:

> Does the gap between the **assumption** (what the code does) and the
> **reality** (what the source says) actually **change the logic** — i.e. would
> the program behave differently / need different code — or not?

This is *not* about who is right or wrong. It only records whether the
divergence has a logical consequence.

- **Changes logic = YES** → the partial mismatch implies the code would behave
  differently, produce a wrong result, or require a code change to be correct.
- **Changes logic = NO** → the mismatch is conceptual/cosmetic/terminological;
  the code's actual behaviour is unaffected.

| Source list | # | Assumption (code) | Reality (source) | Changes logic? | Why |
|-------------|---|-------------------|------------------|----------------|-----|
| DEFINITIONS | 1.1b | World is a set of facts; actions only **add** facts (monotonic) | Canonical STRIPS has add **and delete** effects | **NO** | This codebase never needs to retract a fact (installs are monotonic). Dropping delete-effects is a *modeling simplification*, not a bug. The planner/executor logic works correctly as-is for this domain. Logic unaffected. |
| DEFINITIONS | 2.3 | `_topo_sort` re-scans for ready actions each pass (layered) | Canonical Kahn uses in-degree counters + queue | **NO** | Different bookkeeping, identical result: same valid topological order and the same cycle detection ("Deadlock"). Only performance differs (O(n²) vs O(V+E)), not behaviour. Logic unaffected. |
| DEFINITIONS | 5.1 | "default to `plan`" subcommand built on top of argparse | argparse has no built-in default subcommand | **NO** | The code already *implements* the missing feature with custom logic (`_resolve_command`, `nargs="?"`, `default="plan"`). The gap is only "argparse doesn't give this for free" — which the code handles. Behaviour is exactly as intended. Logic unaffected. |
| UNCERTAINTIES | A4 | grep for literal `ssid` / `percentage` in command output | Commands emit JSON with those fields, but schema is **version-dependent** | **YES** | If a Termux:API version renames/recases those fields, the grep silently fails and the fact is reported absent. The branch taken (`wifi_connected` / `battery_known` true vs false) depends on the exact output → real behavioural impact. |
| UNCERTAINTIES | B4 | Uses `$HOME/storage/{shared,dcim,downloads}` | Setup creates `$HOME/storage`; **subdir names are Android-version-dependent** | **YES** | If `dcim`/`downloads` don't exist or differ, the camera/list actions write/read the wrong path or fail. The action's success/failure depends on the path being real → behavioural impact (for those specific actions). |
| UNCERTAINTIES | B5 | Specific `termux-*` names + flags (`-p gps`, `-l`, …) | Command names/basic forms confirmed; **exact flags not version-pinned** | **YES** | If any flag is wrong for the installed version, that action fails at runtime (non-zero exit → `shell()` returns False). The per-action result depends on flag correctness → behavioural impact (per affected action). |
| UNCERTAINTIES | (claude) | `npm i -g …` yields a global `claude`; probe `command -v claude` | Package may **no longer install a global `claude` CLI** on Termux (needs alias) | **YES** | If true, `command -v claude` never succeeds → `claude_installed` never becomes true → `fully_configured` is **unreachable**, and the install action's effect is never realised. This is the highest-impact logic change of all the rows. |

## Summary

| Source list | Rows | Changes logic = YES | Changes logic = NO |
|-------------|------|---------------------|--------------------|
| DEFINITIONS (confident) | 3 | 0 | 3 |
| UNCERTAINTIES (uncertain) | 4 | 4 | 0 |
| **Total** | **7** | **4** | **3** |

## The pattern

The split is clean and, in hindsight, expected:

- **All 3 `jpjjjjj` rows from the *confident* list → NO.** The partial mismatches
  there are purely about *terminology / canonical form / how a feature is
  obtained* (STRIPS delete-effects, Kahn bookkeeping, argparse defaults). The
  code's actual behaviour is correct regardless. This is consistent with these
  having been in the "confident" bucket.

- **All 4 `jpjjjjj` rows from the *uncertain* list → YES.** Each is a
  device/version-dependent fact (output schema, storage paths, command flags,
  whether a global `claude` CLI exists). In every case the *branch the program
  takes* or *whether an action succeeds* depends on the reality matching the
  assumption. This is consistent with these having been in the "uncertain"
  bucket — and the `claude_installed` one can make the default goal unreachable.

So: of the 7 partial matches, **4 change the logic, 3 do not**, and they separate
exactly along the confident/uncertain line.
