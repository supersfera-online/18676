# Contributing

Thanks for your interest in improving `claude-phone`!

## Development setup

```bash
git clone https://github.com/supersfera-online/18676.git
cd 18676
pip install -e ".[dev]"
pre-commit install
```

## Workflow

1. Create a branch off `main`.
2. Make your change. Add or update tests in `tests/`.
3. Run the full quality gate locally:

   ```bash
   make check        # ruff + mypy + pytest(+cov) + bandit + shellcheck
   ```

   Or individually: `make lint`, `make test`, `make security`, `make shell`.
4. Commit with a clear message and open a pull request. CI must be green.

## Conventions

- **Formatting / linting:** [ruff](https://docs.astral.sh/ruff/) (`make format` autofixes).
- **Types:** code under `src/` must pass `mypy --strict`.
- **Shell scripts:** must pass `shellcheck` and use `set -euo pipefail`
  (or `set -uo pipefail` for interactive scripts).
- **Security:** new `subprocess`/`shell=True` usage must operate on trusted
  literal commands only, never on user input. Annotate with `# nosec` and a note.
- **Adding actions:** append to `actions.phone_remnants()`; the planner and
  `tests/test_actions.py` will pick it up.

## Reporting security issues

See [SECURITY.md](SECURITY.md).
