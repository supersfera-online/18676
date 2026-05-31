"""Tests for the planning core."""

from __future__ import annotations

import pytest

from claude_phone.planner import InformationRemnant, Planner


def make_remnant(name, pre, eff, complexity=1.0, action=None):
    return InformationRemnant(
        name=name, preconditions=pre, effects=eff, complexity=complexity, action=action
    )


def test_plan_reaches_simple_goal():
    remnants = [
        make_remnant("A", ["start"], ["a"]),
        make_remnant("B", ["a"], ["goal"]),
    ]
    plan = Planner(remnants).plan({"start"}, {"goal"})
    assert [r.name for r in plan] == ["A", "B"]


def test_plan_unreachable_fact_raises():
    remnants = [make_remnant("A", ["start"], ["a"])]
    with pytest.raises(RuntimeError, match="Cannot reach 'goal'"):
        Planner(remnants).plan({"start"}, {"goal"})


def test_plan_picks_cheapest_producer():
    cheap = make_remnant("cheap", ["start"], ["goal"], complexity=1)
    pricey = make_remnant("pricey", ["start"], ["goal"], complexity=99)
    plan = Planner([pricey, cheap]).plan({"start"}, {"goal"})
    assert [r.name for r in plan] == ["cheap"]


def test_plan_skips_facts_already_in_initial():
    remnants = [make_remnant("A", ["start"], ["goal"])]
    # goal already satisfied -> empty plan
    assert Planner(remnants).plan({"start", "goal"}, {"goal"}) == []


def test_topo_sort_orders_dependencies():
    remnants = [
        make_remnant("C", ["b"], ["goal"]),
        make_remnant("A", ["start"], ["a"]),
        make_remnant("B", ["a"], ["b"]),
    ]
    plan = Planner(remnants).plan({"start"}, {"goal"})
    names = [r.name for r in plan]
    assert names.index("A") < names.index("B") < names.index("C")


def test_topo_sort_detects_deadlock():
    # Two actions that each depend on the other's effect -> cycle.
    a = make_remnant("A", ["b"], ["a"])
    b = make_remnant("B", ["a"], ["b"])
    planner = Planner([a, b])
    with pytest.raises(RuntimeError, match="Deadlock"):
        planner._topo_sort([a, b], set())


def test_critical_path_returns_longest_chain():
    remnants = [
        make_remnant("A", ["start"], ["a"], complexity=2),
        make_remnant("B", ["a"], ["b"], complexity=3),
        make_remnant("Side", ["start"], ["s"], complexity=1),
    ]
    planner = Planner(remnants)
    plan = planner.plan({"start"}, {"b", "s"})
    path, cost = planner.critical_path(plan, {"start"})
    assert [r.name for r in path] == ["A", "B"]
    assert cost == pytest.approx(5)


def test_critical_path_empty_plan():
    assert Planner([]).critical_path([], set()) == ([], 0.0)
