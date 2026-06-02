# claude-phone

[![CI](https://github.com/supersfera-online/18676/actions/workflows/ci.yml/badge.svg)](https://github.com/supersfera-online/18676/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

A small **STRIPS-style planner-executor** that bootstraps and controls
[Claude Code](https://www.anthropic.com/claude-code) on an Android phone
(tuned for the Samsung Galaxy S22+) running [Termux](https://termux.dev/).

Instead of a fixed install script, the world is described as **facts**,
**actions** declare their preconditions and effects, and the planner figures
out the cheapest ordered set of steps to reach a goal such as
`fully_configured`. It also probes the device first, so it only does the work
that is actually missing.

## Features

- Backward-chaining planner with cost-based action selection and critical-path analysis.
- Reality probing: detects what is already installed/available before planning.
- Dry-run mode to preview the plan without touching the device.
- 24 phone actions (install toolchain, Termux:API, torch, battery, GPS, camera, …).
- `prompt` subcommand that generates a Claude Code system prompt from the device's
  real probed state — it lists only the capabilities actually available and
  regenerates as the device changes.

## Installation

On the phone (Termux), see the full guide in [SETUP.md](SETUP.md). The quick path
is a single paste into Termux:

```bash
pkg install -y curl && curl -fsSL https://raw.githubusercontent.com/supersfera-online/18676/main/scripts/bootstrap.sh | bash
```

This clones the repo, runs the full setup, and installs a **Termux:Widget**
shortcut so every later launch is one tap from the home screen. (Two steps still
need a finger: tapping *Allow* on the storage-permission popup, and pasting your
API key on first launch of `claude`.)

For development on any machine:

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# Probe the device and run the plan to reach the default goal (fully_configured)
claude-phone plan

# Preview the plan without executing anything
claude-phone plan --dry-run

# Inspect the action catalogue and dependency graph
claude-phone list
claude-phone graph

# Only probe current state
claude-phone probe

# Aim for a specific fact
claude-phone plan --target battery_known

# Generate a system prompt from the phone's actual probed state
claude-phone prompt
claude-phone prompt --skip-probe          # prompt for a bare (un-set-up) device
claude-phone prompt --output CLAUDE.md
```

`python -m claude_phone ...` works identically to the `claude-phone` command.
The legacy flag interface (`--probe`, `--list`, `--graph`, `--target`,
`--dry-run`, `--skip-probe`) is still supported.

## Documentation

Core:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how the planner works.
- [SETUP.md](SETUP.md) — installing Claude Code on the phone.




## Development

```bash
make check   # ruff + mypy + pytest(+cov) + bandit + shellcheck
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
