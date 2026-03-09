
#!/usr/bin/env python3
"""
Планировщик-исполнитель для Samsung Galaxy S22+.

Опрашивает реальность, строит план, выполняет.

Использование:
  python3 main.py                    — полная настройка телефона
  python3 main.py --target battery_known torch_on
  python3 main.py --target fully_configured
  python3 main.py --dry-run          — показать план без выполнения
  python3 main.py --probe            — только опросить состояние
  python3 main.py --list             — показать все доступные действия
  python3 main.py --graph            — показать граф зависимостей
"""

import sys
import argparse

from remnant import Planner, Executor
from phone_remnants import phone_remnants, PROBES


def show_actions(remnants):
    print("\nДоступные действия:")
    print(f"{'─' * 60}")
    for r in sorted(remnants, key=lambda x: x.complexity):
        effects = ", ".join(r.effects)
        pre = ", ".join(r.preconditions) if r.preconditions else "—"
        print(f"  {r.name:<30} c={r.complexity:<5} {pre} → {effects}")
    print()


def show_graph(remnants):
    """ASCII-граф зависимостей."""
    print("\nГраф зависимостей:")
    print(f"{'─' * 60}")

    # Группировка по уровням (топологически)
    available_facts = set()  # факты, доступные от предыдущих уровней
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

        print(f"\n  Уровень {level}:")
        for r in sorted(layer, key=lambda x: x.complexity):
            deps = " + ".join(r.preconditions) if r.preconditions else "(нет)"
            eff = ", ".join(r.effects)
            print(f"    [{r.complexity:>4}] {r.name:<30} {deps} → {eff}")
            placed.add(r.name)
            available_facts |= set(r.effects)

        level += 1

    # Оставшиеся (если есть циклы)
    unplaced = [r for r in remnants if r.name not in placed]
    if unplaced:
        print(f"\n  Не размещены (возможен цикл):")
        for r in unplaced:
            print(f"    {r.name}: {r.preconditions} → {r.effects}")


def probe_reality():
    print("\nОпрос реальности...")
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
            print(f"  ? {fact} (ошибка проверки)")
    print(f"\nТекущее состояние: {sorted(state) if state else '(пусто)'}")
    return state


def main():
    parser = argparse.ArgumentParser(
        description="Планировщик-исполнитель для Samsung Galaxy S22+"
    )
    parser.add_argument(
        "--target", nargs="*", default=["fully_configured"],
        help="Целевое состояние (по умолчанию: fully_configured)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Только показать план, не выполнять"
    )
    parser.add_argument(
        "--probe", action="store_true",
        help="Только опросить текущее состояние"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Показать все доступные действия"
    )
    parser.add_argument(
        "--graph", action="store_true",
        help="Показать граф зависимостей"
    )
    parser.add_argument(
        "--skip-probe", action="store_true",
        help="Не опрашивать реальность, считать что ничего нет"
    )

    args = parser.parse_args()
    remnants = phone_remnants()

    if args.list:
        show_actions(remnants)
        return

    if args.graph:
        show_graph(remnants)
        return

    # 1. Опросить реальность
    if args.probe:
        probe_reality()
        return

    if args.skip_probe:
        initial = set()
        print("\nПропуск опроса. Начальное состояние: (пусто)")
    else:
        initial = probe_reality()

    # Termux — всегда, если мы вообще запустились
    initial.add("termux_ready")

    target = set(args.target)
    already = target & initial
    if already:
        print(f"\nУже достигнуто: {sorted(already)}")
        target -= already

    if not target:
        print("\nЦель уже достигнута. Нечего делать.")
        return

    # 2. Построить план
    print(f"\nЦель: {sorted(target)}")
    planner = Planner(remnants)

    try:
        plan = planner.plan(initial, target)
    except RuntimeError as e:
        print(f"\nОшибка планирования: {e}")
        sys.exit(1)

    # 3. Критический путь
    crit_path, crit_cost = planner.critical_path(plan, initial)
    if crit_path:
        print(f"\nКритический путь (сложность {crit_cost}):")
        for r in crit_path:
            print(f"  → {r.name} ({r.complexity})")

    # 4. Выполнить
    executor = Executor(initial)
    executor.execute_plan(plan, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
