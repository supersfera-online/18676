"""Command-line interface for claude-phone.

Usage is subcommand based (``plan``, ``probe``, ``list``, ``graph``,
``prompt``) with ``plan`` as the default when no subcommand is given. The
original flag-only interface (``--probe``/``--list``/``--graph`` and the
``plan`` flags) is preserved for backward compatibility.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from . import config
from .actions import PROBES, phone_remnants
from .logging_config import configure_logging
from .planner import Executor, InformationRemnant, Planner
from .prompt_builder import build_system_prompt, get_device_context

logger = logging.getLogger("claude_phone")

COMMANDS = ("plan", "probe", "list", "graph", "prompt")


def show_actions(remnants: list[InformationRemnant]) -> None:
    logger.info("\nAvailable actions:")
    logger.info("%s", "─" * 60)
    for r in sorted(remnants, key=lambda x: x.complexity):
        effects = ", ".join(r.effects)
        pre = ", ".join(r.preconditions) if r.preconditions else "—"
        logger.info("  %-30s c=%-5s %s → %s", r.name, r.complexity, pre, effects)


def show_graph(remnants: list[InformationRemnant]) -> None:
    logger.info("\nDependency graph:")
    logger.info("%s", "─" * 60)

    available_facts: set[str] = set()
    placed: set[str] = set()
    level = 0

    while True:
        layer = [
            r
            for r in remnants
            if r.name not in placed
            and all(
                p in available_facts or not any(p in rr.effects for rr in remnants)
                for p in r.preconditions
            )
        ]
        if not layer:
            break

        logger.info("\n  Level %d:", level)
        for r in sorted(layer, key=lambda x: x.complexity):
            deps = " + ".join(r.preconditions) if r.preconditions else "(none)"
            eff = ", ".join(r.effects)
            logger.info("    [%4s] %-30s %s → %s", r.complexity, r.name, deps, eff)
            placed.add(r.name)
            available_facts |= set(r.effects)
        level += 1

    unplaced = [r for r in remnants if r.name not in placed]
    if unplaced:
        logger.warning("\n  Not placed (possible cycle):")
        for r in unplaced:
            logger.warning("    %s: %s → %s", r.name, r.preconditions, r.effects)


def probe_reality() -> set[str]:
    logger.info("\nProbing reality...")
    logger.info("%s", "─" * 40)
    state: set[str] = set()
    for fact, check in PROBES.items():
        try:
            result = check()
        except Exception as exc:  # noqa: BLE001 - report but keep probing other facts
            logger.warning("  ? %s (check error)", fact)
            logger.debug("probe %s raised: %r", fact, exc)
            continue
        symbol = "✓" if result else "✗"
        suffix = f" → {fact}" if result else ""
        logger.info("  %s %s%s", symbol, fact, suffix)
        if result:
            state.add(fact)
    logger.info("\nCurrent state: %s", sorted(state) if state else "(empty)")
    return state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="claude-phone",
        description=f"Planner-executor for {config.PHONE_MODEL}",
    )
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbose (debug) output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Only show warnings and errors")

    # Optional subcommand; defaults to "plan" when omitted.
    parser.add_argument(
        "command",
        nargs="?",
        choices=COMMANDS,
        default="plan",
        help="Subcommand to run (default: plan)",
    )

    # plan options
    parser.add_argument(
        "--target",
        nargs="*",
        default=[config.DEFAULT_TARGET],
        help=f"Target state (default: {config.DEFAULT_TARGET})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Only show the plan, do not execute")
    parser.add_argument(
        "--skip-probe", action="store_true", help="Do not probe reality; assume nothing is present"
    )

    # prompt options (the prompt also honours the global --skip-probe flag)
    parser.add_argument(
        "--output", help="Write the generated prompt to this file instead of stdout"
    )

    # Legacy flag aliases (backward compatibility).
    parser.add_argument("--probe", dest="legacy_probe", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--list", dest="legacy_list", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--graph", dest="legacy_graph", action="store_true", help=argparse.SUPPRESS)
    return parser


def _resolve_command(args: argparse.Namespace) -> str:
    """Map legacy flags onto the resolved subcommand."""
    if args.legacy_probe:
        return "probe"
    if args.legacy_list:
        return "list"
    if args.legacy_graph:
        return "graph"
    return str(args.command)


def _run_prompt(args: argparse.Namespace, remnants: list[InformationRemnant]) -> int:
    if args.skip_probe:
        state: set[str] = set()
        logger.info("\nSkipping probe; generating prompt for a bare device.")
    else:
        state = probe_reality()
    state.add("termux_ready")

    context = get_device_context(state, remnants)
    prompt = build_system_prompt(context)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(prompt)
        logger.info("Prompt written to %s", args.output)
    else:
        # Use print so the prompt can be piped cleanly regardless of log level.
        print(prompt)
    return 0


def _run_plan(args: argparse.Namespace, remnants: list[InformationRemnant]) -> int:
    if args.skip_probe:
        initial: set[str] = set()
        logger.info("\nSkipping probe. Initial state: (empty)")
    else:
        initial = probe_reality()

    initial.add("termux_ready")

    target = set(args.target)
    already = target & initial
    if already:
        logger.info("\nAlready achieved: %s", sorted(already))
        target -= already

    if not target:
        logger.info("\nGoal already achieved. Nothing to do.")
        return 0

    logger.info("\nGoal: %s", sorted(target))
    planner = Planner(remnants)

    try:
        plan = planner.plan(initial, target)
    except RuntimeError as e:
        logger.error("\nPlanning error: %s", e)
        return 1

    crit_path, crit_cost = planner.critical_path(plan, initial)
    if crit_path:
        logger.info("\nCritical path (complexity %s):", crit_cost)
        for r in crit_path:
            logger.info("  → %s (%s)", r.name, r.complexity)

    executor = Executor(initial)
    ok = executor.execute_plan(plan, dry_run=args.dry_run)
    return 0 if ok else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(verbose=args.verbose, quiet=args.quiet)

    command = _resolve_command(args)
    remnants = phone_remnants()

    if command == "list":
        show_actions(remnants)
        return 0
    if command == "graph":
        show_graph(remnants)
        return 0
    if command == "probe":
        probe_reality()
        return 0
    if command == "prompt":
        return _run_prompt(args, remnants)
    return _run_plan(args, remnants)


if __name__ == "__main__":
    sys.exit(main())
