"""STRIPS-style backward-chaining planner and executor.

The world is modelled as a *set of facts* (strings). An
:class:`InformationRemnant` is an action with ``preconditions`` (facts that must
hold before it runs) and ``effects`` (facts it makes true). The :class:`Planner`
chains backwards from a target set of facts to a runnable, dependency-ordered
plan, and the :class:`Executor` runs it while tracking world state.

See ``docs/ARCHITECTURE.md`` for a fuller explanation.
"""

from __future__ import annotations

import logging
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class InformationRemnant:
    """A single action: it requires ``preconditions`` and produces ``effects``."""

    name: str
    preconditions: list[str]
    effects: list[str]
    complexity: float = 1.0
    action: Callable[[], bool | None] | None = None
    description: str = ""

    def can_execute(self, state: set[str]) -> bool:
        """Return ``True`` if every precondition holds in ``state``."""
        return all(p in state for p in self.preconditions)

    def execute(self, state: set[str]) -> set[str]:
        """Run the action and return the new state, or raise on failure.

        An action callable returning ``None`` is treated as success (the action
        had no meaningful boolean result).
        """
        if not self.can_execute(state):
            missing = [p for p in self.preconditions if p not in state]
            raise RuntimeError(f"[{self.name}] Cannot run: missing {missing}")

        success: bool | None = True
        if self.action is not None:
            success = self.action()

        if success or success is None:
            return state | set(self.effects)
        raise RuntimeError(f"[{self.name}] Action failed")

    def __repr__(self) -> str:
        return f"Remnant({self.name}, {self.preconditions} -> {self.effects}, c={self.complexity})"


class Planner:
    """Builds a dependency-ordered plan from an initial state to a target."""

    def __init__(self, remnants: list[InformationRemnant]) -> None:
        self.remnants = remnants
        self._producers: dict[str, list[InformationRemnant]] = {}
        for r in remnants:
            for e in r.effects:
                self._producers.setdefault(e, []).append(r)

    def plan(self, initial: set[str], target: set[str]) -> list[InformationRemnant]:
        """Return an ordered plan that reaches ``target`` from ``initial``.

        Raises ``RuntimeError`` if a required fact has no producing action, or
        if the selected actions cannot be ordered (a dependency cycle).
        """
        needed = set(target) - initial
        plan_set: dict[str, InformationRemnant] = {}
        queue: deque[str] = deque(needed)
        visited: set[str] = set()

        while queue:
            fact = queue.popleft()
            if fact in initial or fact in visited:
                continue
            visited.add(fact)

            producers = self._producers.get(fact, [])
            if not producers:
                raise RuntimeError(f"Cannot reach '{fact}': no action produces it")

            # Greedily pick the cheapest producer for this fact.
            best = min(producers, key=lambda r: r.complexity)

            if best.name not in plan_set:
                plan_set[best.name] = best
                for pre in best.preconditions:
                    if pre not in initial:
                        queue.append(pre)

        return self._topo_sort(list(plan_set.values()), initial)

    def _topo_sort(
        self, remnants: list[InformationRemnant], initial: set[str]
    ) -> list[InformationRemnant]:
        sorted_plan: list[InformationRemnant] = []
        available = set(initial)
        remaining = list(remnants)

        while remaining:
            ready = [r for r in remaining if r.can_execute(available)]
            if not ready:
                stuck = [r.name for r in remaining]
                raise RuntimeError(f"Deadlock! Cannot execute: {stuck}")

            ready.sort(key=lambda r: r.complexity)
            for r in ready:
                sorted_plan.append(r)
                available |= set(r.effects)
                remaining.remove(r)

        return sorted_plan

    def critical_path(
        self, plan: list[InformationRemnant], initial: set[str]
    ) -> tuple[list[InformationRemnant], float]:
        """Return the longest-cost dependency chain and its total complexity."""
        cost_to: dict[str, float] = {}
        prev: dict[str, str | None] = {}

        for r in plan:
            max_pre_cost = 0.0
            max_pre_name: str | None = None
            for pre in r.preconditions:
                if pre in initial:
                    continue
                for pr in plan:
                    if pre in pr.effects and cost_to.get(pr.name, 0) > max_pre_cost:
                        max_pre_cost = cost_to[pr.name]
                        max_pre_name = pr.name

            cost_to[r.name] = max_pre_cost + r.complexity
            prev[r.name] = max_pre_name

        if not cost_to:
            return [], 0.0

        end_name = max(cost_to, key=lambda k: cost_to[k])
        path: list[InformationRemnant] = []
        name: str | None = end_name
        while name is not None:
            remnant = next(r for r in plan if r.name == name)
            path.append(remnant)
            name = prev[name]
        path.reverse()
        return path, cost_to[end_name]


class Executor:
    """Runs a plan, tracking world state and execution history."""

    def __init__(self, initial: set[str] | None = None) -> None:
        self.state: set[str] = set(initial) if initial else set()
        self.history: list[tuple[str, set[str]]] = []

    def probe_state(self, probes: dict[str, Callable[[], bool]]) -> set[str]:
        """Update ``state`` from a mapping of fact name to probe callable."""
        for fact, check in probes.items():
            if check():
                self.state.add(fact)
                logger.info("  ✓ %s", fact)
            else:
                self.state.discard(fact)
                logger.info("  ✗ %s", fact)
        return self.state

    def execute_plan(self, plan: list[InformationRemnant], dry_run: bool = False) -> bool:
        """Execute ``plan`` in order.

        Returns ``True`` if every action completed (or was simulated in
        ``dry_run``), and ``False`` if execution stopped early because an action
        failed or its preconditions were unmet.
        """
        total = sum(r.complexity for r in plan)
        logger.info("\n%s", "=" * 50)
        logger.info("  Plan: %d actions, complexity: %s", len(plan), total)
        logger.info("%s\n", "=" * 50)

        ok = True
        for i, remnant in enumerate(plan, 1):
            prefix = "[DRY]" if dry_run else f"[{i}/{len(plan)}]"
            logger.info("%s %s (complexity: %s)", prefix, remnant.name, remnant.complexity)

            if remnant.description:
                logger.info("       %s", remnant.description)

            if not remnant.can_execute(self.state):
                missing = [p for p in remnant.preconditions if p not in self.state]
                logger.warning("  ✗ SKIP: missing %s", missing)
                ok = False
                continue

            if dry_run:
                self.state |= set(remnant.effects)
                logger.info("  → %s", remnant.effects)
                continue

            try:
                self.state = remnant.execute(self.state)
                self.history.append((remnant.name, set(self.state)))
                logger.info("  ✓ Done → state: +%s", remnant.effects)
            except RuntimeError as e:
                logger.error("  ✗ %s", e)
                logger.error("\nStopped at step %d. World state: %s", i, self.state)
                return False

        logger.info("\n%s", "=" * 50)
        logger.info("  Final state: %s", sorted(self.state))
        logger.info("%s", "=" * 50)
        return ok
