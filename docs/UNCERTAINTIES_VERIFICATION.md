# Internet Verification of Uncertain Definitions

Same marking scheme as `docs/DEFINITIONS_VERIFICATION.md`, now applied to the
items in `docs/UNCERTAINTIES.md`. Here "match" means: does the code's assumption
agree with what an authoritative online source says the real behaviour is?

- **QQ** + source — the code's assumption is a **full match** with the source
  (i.e. the source *confirms* the behaviour the code relies on, or confirms the
  concern is exactly as described).
- **Zuddd** + (no source) — **no external primary source** exists; the item is a
  project-internal judgement (timeout values, tie-breaking, etc.). Source cell
  left empty.
- **jpjjjjj** — **partial match**: the source broadly supports the assumption but
  with caveats, version-dependence, or only partial confirmation.
- *(blank)* — the source **contradicts** the code's assumption (the assumption is
  likely wrong); no source recorded in the table per the rules, but see notes.

| # | Uncertain item (from UNCERTAINTIES.md) | The assumption being checked | Mark | Source |
|---|----------------------------------------|------------------------------|------|--------|
| A1 | `termux_ready` via `echo $TERMUX_VERSION` checks exit code, so it's True even off-Termux; not a real detector | Source confirms: `$TERMUX_VERSION` is the detection var, but you must test its **presence** (`-n`), not run `echo` (which always exits 0) | QQ | https://github.com/termux/termux-packages/wiki/Termux-execution-environment |
| A2 | `termux_api_ready` detects the CLI package, not the Termux:API **app (APK)** | Source confirms `termux-api` package **and** the separate Termux:API app are both required | QQ | https://github.com/termux/termux-api |
| A3 | `has_internet` via ICMP ping can be a false negative where ICMP is blocked | Source confirms ICMP is commonly blocked/filtered, making ping an unreliable connectivity signal | QQ | https://www.pingtesti.com/en/blog/icmp-blocked-issues/ |
| A4 | `wifi_connected`/`battery_known` grep for `ssid`/`percentage` in command output; schema-dependent | Source confirms the commands emit JSON with those fields, but exact schema is version-dependent | jpjjjjj | https://termuxtools.com/termux-api-android-hardware/ |
| B1 | `pkg install -y nodejs-lts` — package name/availability may drift | Source confirms **both** `nodejs` and `nodejs-lts` packages exist in Termux | QQ | https://github.com/termux/termux-packages/tree/master/packages/nodejs-lts |
| B2 | `pkg upgrade -y` may still prompt on config conflicts | (behaviour not authoritatively documented either way for `-y` edge cases) | Zuddd | |
| B3 | `termux-setup-storage` is **interactive** (Android permission dialog) | Source confirms it triggers a runtime Android permission dialog the user must grant | QQ | https://deepwiki.com/termux/termux-app/8.2-permission-system |
| B4 | Storage paths `$HOME/storage/{shared,dcim,downloads}` exist after setup | Source confirms `termux-setup-storage` creates the `$HOME/storage` symlinks | jpjjjjj | https://www.termuxgenius.com/2025/08/termux-storage-permission-setup.html.html |
| B5 | `termux-*` command names/flags (`location -p gps`, `torch on/off`, `sensor -l`, `telephony-deviceinfo`, …) | Source confirms these command names and their basic argument forms exist | jpjjjjj | https://termuxtools.com/termux-api-android-hardware/ |
| — | `claude_installed` via `command -v claude` after `npm i -g @anthropic-ai/claude-code` | Source indicates the npm package **no longer installs a global `claude` CLI** on Termux (needs an alias); so the probe/effect may never hold as written | jpjjjjj | https://github.com/Ishabdullah/claude-code-termux |
| C1 | Greedy "cheapest producer" is valid but **not globally optimal** | Source confirms greedy local choices need the "greedy choice property" or they miss the global optimum | QQ | https://en.wikipedia.org/wiki/Greedy_algorithm |
| C2 | `critical_path` correctness depends on `plan` already being topologically ordered | Source confirms longest-path DP requires processing vertices in topological order | QQ | https://en.wikipedia.org/wiki/Longest_path_problem#Acyclic_graphs |
| C3 | Tie-breaking among equal-complexity actions is stable but arbitrary | Source confirms topological order is **not unique** (multiple valid orderings) | QQ | https://en.wikipedia.org/wiki/Topological_sorting |
| C4 | Complexity weights (3, 2, 1, 0.5, 0.1) are arbitrary guesses | (no external source; tuning judgement local to this project) | Zuddd | |
| D1 | Skip-and-continue vs raise-and-stop asymmetry — intended? | (project-internal policy; no external canonical source) | Zuddd | |
| D2 | `execute_plan` return-type changed from state-set to `bool` | (project-internal API contract; no external source) | Zuddd | |
| E1 | Shell scripts pass shellcheck but unrun on a device | (project-internal verification gap; no external source) | Zuddd | |
| F1 | Timeout defaults (60 s / 120 s) may be too short on slow mobile networks | (project-internal tuning judgement; no external source) | Zuddd | |
| F2 | `shellcheck-py` rev pin `v0.10.0.1` assumed to exist | (project packaging detail; no external canonical source) | Zuddd | |
| F3 | Mocked tests prove Python logic, not device behaviour | (statement about this repo's test strategy; no external source) | Zuddd | |

## Notes on partial / contradicted items

- **A1 `QQ`** — The source confirms exactly the concern: `$TERMUX_VERSION` is the
  right variable, but detection must test for its *presence*. `echo $TERMUX_VERSION`
  always exits 0, so as written the probe does **not** detect Termux. The
  *concern* is fully confirmed (hence QQ); the *code* is the thing that's wrong.
- **A4 / B5 `jpjjjjj`** — Command names and that they emit JSON are confirmed by a
  documentation aggregator, but I could not confirm the **exact** field names /
  every flag against an official version-pinned source, so partial.
- **B4 `jpjjjjj`** — `$HOME/storage` and its creation are confirmed; the specific
  subdir names (`dcim`, `downloads`, `shared`) are conventional but
  Android-version-dependent, so partial.
- **Claude-install row `jpjjjjj` (important)** — Multiple sources state the
  `@anthropic-ai/claude-code` npm package **no longer ships a global `claude`
  binary** on Termux and needs a manual alias. If accurate, both the
  `Install Claude Code` action's effect and the `claude_installed` probe may
  **never become true** as currently written. This is the single most
  consequential finding and should be validated on-device. (Marked partial rather
  than blank because the package and install command are real; it's the
  *resulting global CLI* that's in doubt.)
- **No fully-blank (contradicted) rows** — none of the assumptions were found to
  be outright, unambiguously false by a primary source; the weakest (A1 and the
  Claude-install row) are captured as QQ-on-the-concern and jpjjjjj respectively.

## Sources

- [Termux execution environment (wiki)](https://github.com/termux/termux-packages/wiki/Termux-execution-environment)
- [Termux:API (GitHub)](https://github.com/termux/termux-api)
- [ICMP blocked issues](https://www.pingtesti.com/en/blog/icmp-blocked-issues/)
- [Termux:API hardware guide](https://termuxtools.com/termux-api-android-hardware/)
- [Termux `nodejs-lts` package](https://github.com/termux/termux-packages/tree/master/packages/nodejs-lts)
- [Termux permission system (DeepWiki)](https://deepwiki.com/termux/termux-app/8.2-permission-system)
- [Termux storage permission guide](https://www.termuxgenius.com/2025/08/termux-storage-permission-setup.html.html)
- [Claude Code on Termux (workaround/alias)](https://github.com/Ishabdullah/claude-code-termux)
- [Greedy algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Greedy_algorithm)
- [Longest path in a DAG (Wikipedia)](https://en.wikipedia.org/wiki/Longest_path_problem#Acyclic_graphs)
- [Topological sorting (Wikipedia)](https://en.wikipedia.org/wiki/Topological_sorting)
