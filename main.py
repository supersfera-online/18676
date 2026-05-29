#!/usr/bin/env python3
import sys
import argparse

from remnant import Planner, Executor
from phone_remnants import phone_remnants, PROBES


def show_actions(remnants):
    print("\nAvailable actions:")
    print(f"{'─' * 60}")
    for r in sorted(remnants, key=lambda x: x.complexity):
        effects = ", ".join(r.effects)
        pre = ", ".join(r.preconditions) if r.preconditions else "—"
        print(f"  {r.name:<30} c={r.complexity:<5} {pre} → {effects}")
    print()


def show_graph(remnants):
    print("\nDependency graph:")
    print(f"{'─' * 60}")

    available_facts = set()
    placed = set()
    level = 0

    while True:
        layer = [r for r in remnants
                 if r.name not in placed
                 and all(p in available_facts or
                         not any(p in rr.effects for rr in remnants)
                         for p in r.preconditions)]
        if not layer:
            break

        print(f"\n  Level {level}:")
        for r in sorted(layer, key=lambda x: x.complexity):
            deps = " + ".join(r.preconditions) if r.preconditions else "(none)"
            eff = ", ".join(r.effects)
            print(f"    [{r.complexity:>4}] {r.name:<30} {deps} → {eff}")
            placed.add(r.name)
            available_facts |= set(r.effects)

        level += 1

    unplaced = [r for r in remnants if r.name not in placed]
    if unplaced:
        print(f"\n  Not placed (possible cycle):")
        for r in unplaced:
            print(f"    {r.name}: {r.preconditions} → {r.effects}")


def probe_reality():
    print("\nProbing reality...")
    print(f"{'─' * 40}")
    state = set()
    for fact, check in PROBES.items():
        try:
            result = check()
            symbol = "✓" if result else "✗"
            state_change = "" if not result else f" → {fact}"
            print(f"  {symbol} {fact}{state_change}")
            if result:
                state.add(fact)
        except Exception:
            print(f"  ? {fact} (check error)")
    print(f"\nCurrent state: {sorted(state) if state else '(empty)'}")
    return state


def main():
    parser = argparse.ArgumentParser(
        description="Planner-executor for Samsung Galaxy S22+"
    )
    parser.add_argument(
        "--target", nargs="*", default=["fully_configured"],
        help="Target state (default: fully_configured)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Only show the plan, do not execute"
    )
    parser.add_argument(
        "--probe", action="store_true",
        help="Only probe the current state"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Show all available actions"
    )
    parser.add_argument(
        "--graph", action="store_true",
        help="Show the dependency graph"
    )
    parser.add_argument(
        "--skip-probe", action="store_true",
        help="Do not probe reality; assume nothing is present"
    )

    args = parser.parse_args()
    remnants = phone_remnants()

    if args.list:
        show_actions(remnants)
        return

    if args.graph:
        show_graph(remnants)
        return

    if args.probe:
        probe_reality()
        return

    if args.skip_probe:
        initial = set()
        print("\nSkipping probe. Initial state: (empty)")
    else:
        initial = probe_reality()

    initial.add("termux_ready")

    target = set(args.target)
    already = target & initial
    if already:
        print(f"\nAlready achieved: {sorted(already)}")
        target -= already

    if not target:
        print("\nGoal already achieved. Nothing to do.")
        return

    print(f"\nGoal: {sorted(target)}")
    planner = Planner(remnants)

    try:
        plan = planner.plan(initial, target)
    except RuntimeError as e:
        print(f"\nPlanning error: {e}")
        sys.exit(1)

    crit_path, crit_cost = planner.critical_path(plan, initial)
    if crit_path:
        print(f"\nCritical path (complexity {crit_cost}):")
        for r in crit_path:
            print(f"  → {r.name} ({r.complexity})")

    executor = Executor(initial)
    executor.execute_plan(plan, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
