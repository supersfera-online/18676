"""
Ядро планировщика-исполнителя.

InformationRemnant — действие, которое при выполнении оставляет след в реальности.
Planner — строит оптимальный план из текущего состояния к цели.
Executor — выполняет план, отслеживая состояние мира.
"""

import subprocess
import shlex
from dataclasses import dataclass, field
from typing import Callable, Optional
from collections import deque


@dataclass
class InformationRemnant:
    """Флуктуация реальности. Действие, которое трансформирует состояние мира."""

    name: str
    preconditions: list[str]          # что должно быть истиной ДО
    effects: list[str]                # что станет истиной ПОСЛЕ
    complexity: float = 1.0           # стоимость
    action: Optional[Callable] = None # реальное действие (shell-команда или функция)
    description: str = ""             # человекочитаемое описание

    def can_execute(self, state: set[str]) -> bool:
        """Все предусловия выполнены?"""
        return all(p in state for p in self.preconditions)

    def execute(self, state: set[str]) -> set[str]:
        """Выполнить действие и вернуть новое состояние мира."""
        if not self.can_execute(state):
            missing = [p for p in self.preconditions if p not in state]
            raise RuntimeError(
                f"[{self.name}] Невозможно: не хватает {missing}"
            )

        success = True
        if self.action is not None:
            success = self.action()

        if success or success is None:
            new_state = state | set(self.effects)
            return new_state
        else:
            raise RuntimeError(f"[{self.name}] Действие провалилось")

    def __repr__(self):
        return f"Remnant({self.name}, {self.preconditions} → {self.effects}, c={self.complexity})"


def shell(cmd: str) -> Callable:
    """Обёртка: превращает shell-команду в callable для remnant.action."""
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
                print(f"  ОШИБКА: {result.stderr.strip()}")
            return False
        return True
    return run


def probe(cmd: str) -> Callable:
    """Проверка состояния: выполняет команду, возвращает True/False без ошибки."""
    def check():
        result = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True
        )
        return result.returncode == 0
    return check


class Planner:
    """
    Строит план достижения цели из текущего состояния.
    Использует обратный поиск от цели + топологическую сортировку.
    """

    def __init__(self, remnants: list[InformationRemnant]):
        self.remnants = remnants
        # Индекс: какой remnant производит какой эффект
        self._producers: dict[str, list[InformationRemnant]] = {}
        for r in remnants:
            for e in r.effects:
                self._producers.setdefault(e, []).append(r)

    def plan(self, initial: set[str], target: set[str]) -> list[InformationRemnant]:
        """
        Найти минимальный набор действий и их порядок,
        чтобы из initial достичь target.
        """
        needed = set(target) - initial
        plan_set: dict[str, InformationRemnant] = {}
        queue = deque(needed)
        visited = set()

        # Обратный поиск: от цели к началу
        while queue:
            fact = queue.popleft()
            if fact in initial or fact in visited:
                continue
            visited.add(fact)

            producers = self._producers.get(fact, [])
            if not producers:
                raise RuntimeError(
                    f"Невозможно достичь '{fact}': нет действия, которое его производит"
                )

            # Выбираем наименее сложный способ получить этот факт
            best = min(producers, key=lambda r: r.complexity)

            if best.name not in plan_set:
                plan_set[best.name] = best
                # Добавляем предусловия этого действия в очередь
                for pre in best.preconditions:
                    if pre not in initial:
                        queue.append(pre)

        # Топологическая сортировка
        return self._topo_sort(list(plan_set.values()), initial)

    def _topo_sort(self, remnants: list[InformationRemnant], initial: set[str]) -> list[InformationRemnant]:
        """Упорядочить действия так, чтобы зависимости выполнялись первыми."""
        sorted_plan = []
        available = set(initial)
        remaining = list(remnants)

        while remaining:
            # Найти все, что можно выполнить прямо сейчас
            ready = [r for r in remaining if r.can_execute(available)]
            if not ready:
                stuck = [r.name for r in remaining]
                raise RuntimeError(f"Тупик! Не могу выполнить: {stuck}")

            # Из готовых — сначала самые простые
            ready.sort(key=lambda r: r.complexity)

            for r in ready:
                sorted_plan.append(r)
                available |= set(r.effects)
                remaining.remove(r)

        return sorted_plan

    def critical_path(self, plan: list[InformationRemnant], initial: set[str]) -> tuple[list[InformationRemnant], float]:
        """Найти критический путь (самую длинную цепочку зависимостей)."""
        # Для каждого remnant — максимальная стоимость пути до него
        cost_to: dict[str, float] = {}
        prev: dict[str, Optional[InformationRemnant]] = {}

        for r in plan:
            max_pre_cost = 0
            max_pre_name = None
            for pre in r.preconditions:
                if pre in initial:
                    continue
                # Кто произвёл этот precondition?
                for pr in plan:
                    if pre in pr.effects and cost_to.get(pr.name, 0) > max_pre_cost:
                        max_pre_cost = cost_to[pr.name]
                        max_pre_name = pr.name

            cost_to[r.name] = max_pre_cost + r.complexity
            prev[r.name] = max_pre_name

        if not cost_to:
            return [], 0

        # Восстанавливаем путь от самого дорогого
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
    """Выполняет план шаг за шагом, отслеживая состояние мира."""

    def __init__(self, initial: set[str] = None):
        self.state = set(initial) if initial else set()
        self.history: list[tuple[str, set[str]]] = []

    def probe_state(self, probes: dict[str, Callable]) -> set[str]:
        """Опросить реальность: выполнить проверки и узнать текущее состояние."""
        for fact, check in probes.items():
            if check():
                self.state.add(fact)
                print(f"  ✓ {fact}")
            else:
                self.state.discard(fact)
                print(f"  ✗ {fact}")
        return self.state

    def execute_plan(self, plan: list[InformationRemnant], dry_run: bool = False) -> set[str]:
        """
        Выполнить план.
        dry_run=True — только показать что будет сделано.
        """
        total = sum(r.complexity for r in plan)
        print(f"\n{'=' * 50}")
        print(f"  План: {len(plan)} действий, сложность: {total}")
        print(f"{'=' * 50}\n")

        for i, remnant in enumerate(plan, 1):
            prefix = "[DRY]" if dry_run else f"[{i}/{len(plan)}]"
            print(f"{prefix} {remnant.name} (сложность: {remnant.complexity})")

            if remnant.description:
                print(f"       {remnant.description}")

            if not remnant.can_execute(self.state):
                missing = [p for p in remnant.preconditions if p not in self.state]
                print(f"  ✗ ПРОПУСК: не хватает {missing}")
                continue

            if dry_run:
                self.state |= set(remnant.effects)
                print(f"  → {remnant.effects}")
                continue

            try:
                self.state = remnant.execute(self.state)
                self.history.append((remnant.name, set(self.state)))
                print(f"  ✓ Готово → состояние: +{remnant.effects}")
            except RuntimeError as e:
                print(f"  ✗ {e}")
                print(f"\nОстановка на шаге {i}. Состояние мира: {self.state}")
                return self.state

        print(f"\n{'=' * 50}")
        print(f"  Финальное состояние: {sorted(self.state)}")
        print(f"{'=' * 50}")
        return self.state
