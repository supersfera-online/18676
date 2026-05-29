import subprocess
import shlex
from dataclasses import dataclass, field
from typing import Callable, Optional
from collections import deque


@dataclass
class InformationRemnant:

    name: str
    preconditions: list[str]
    effects: list[str]
    complexity: float = 1.0
    action: Optional[Callable] = None
    description: str = ""

    def can_execute(self, state: set[str]) -> bool:
        return all(p in state for p in self.preconditions)

    def execute(self, state: set[str]) -> set[str]:
        if not self.can_execute(state):
            missing = [p for p in self.preconditions if p not in state]
            raise RuntimeError(
                f"[{self.name}] Cannot run: missing {missing}"
            )

        success = True
        if self.action is not None:
            success = self.action()

        if success or success is None:
            new_state = state | set(self.effects)
            return new_state
        else:
            raise RuntimeError(f"[{self.name}] Action failed")

    def __repr__(self):
        return f"Remnant({self.name}, {self.preconditions} → {self.effects}, c={self.complexity})"


def shell(cmd: str) -> Callable:
    def run():
        print(f"  $ {cmd}")
        result = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True
        )
        if result.stdout.strip():
            print(f"  {result.stdout.strip()}")
        if result.returncode != 0:
            if result.stderr.strip():
                print(f"  ERROR: {result.stderr.strip()}")
            return False
        return True
    return run


def probe(cmd: str) -> Callable:
    def check():
        result = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True
        )
        return result.returncode == 0
    return check


class Planner:

    def __init__(self, remnants: list[InformationRemnant]):
        self.remnants = remnants
        self._producers: dict[str, list[InformationRemnant]] = {}
        for r in remnants:
            for e in r.effects:
                self._producers.setdefault(e, []).append(r)

    def plan(self, initial: set[str], target: set[str]) -> list[InformationRemnant]:
        needed = set(target) - initial
        plan_set: dict[str, InformationRemnant] = {}
        queue = deque(needed)
        visited = set()

        while queue:
            fact = queue.popleft()
            if fact in initial or fact in visited:
                continue
            visited.add(fact)

            producers = self._producers.get(fact, [])
            if not producers:
                raise RuntimeError(
                    f"Cannot reach '{fact}': no action produces it"
                )

            best = min(producers, key=lambda r: r.complexity)

            if best.name not in plan_set:
                plan_set[best.name] = best
                for pre in best.preconditions:
                    if pre not in initial:
                        queue.append(pre)

        return self._topo_sort(list(plan_set.values()), initial)

    def _topo_sort(self, remnants: list[InformationRemnant], initial: set[str]) -> list[InformationRemnant]:
        sorted_plan = []
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

    def critical_path(self, plan: list[InformationRemnant], initial: set[str]) -> tuple[list[InformationRemnant], float]:
        cost_to: dict[str, float] = {}
        prev: dict[str, Optional[InformationRemnant]] = {}

        for r in plan:
            max_pre_cost = 0
            max_pre_name = None
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
            return [], 0

        end_name = max(cost_to, key=cost_to.get)
        path = []
        name = end_name
        while name is not None:
            remnant = next(r for r in plan if r.name == name)
            path.append(remnant)
            name = prev[name]
        path.reverse()
        return path, cost_to[end_name]


class Executor:

    def __init__(self, initial: set[str] = None):
        self.state = set(initial) if initial else set()
        self.history: list[tuple[str, set[str]]] = []

    def probe_state(self, probes: dict[str, Callable]) -> set[str]:
        for fact, check in probes.items():
            if check():
                self.state.add(fact)
                print(f"  ✓ {fact}")
            else:
                self.state.discard(fact)
                print(f"  ✗ {fact}")
        return self.state

    def execute_plan(self, plan: list[InformationRemnant], dry_run: bool = False) -> set[str]:
        total = sum(r.complexity for r in plan)
        print(f"\n{'=' * 50}")
        print(f"  Plan: {len(plan)} actions, complexity: {total}")
        print(f"{'=' * 50}\n")

        for i, remnant in enumerate(plan, 1):
            prefix = "[DRY]" if dry_run else f"[{i}/{len(plan)}]"
            print(f"{prefix} {remnant.name} (complexity: {remnant.complexity})")

            if remnant.description:
                print(f"       {remnant.description}")

            if not remnant.can_execute(self.state):
                missing = [p for p in remnant.preconditions if p not in self.state]
                print(f"  ✗ SKIP: missing {missing}")
                continue

            if dry_run:
                self.state |= set(remnant.effects)
                print(f"  → {remnant.effects}")
                continue

            try:
                self.state = remnant.execute(self.state)
                self.history.append((remnant.name, set(self.state)))
                print(f"  ✓ Done → state: +{remnant.effects}")
            except RuntimeError as e:
                print(f"  ✗ {e}")
                print(f"\nStopped at step {i}. World state: {self.state}")
                return self.state

        print(f"\n{'=' * 50}")
        print(f"  Final state: {sorted(self.state)}")
        print(f"{'=' * 50}")
        return self.state
