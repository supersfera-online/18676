"""Tests for the Executor and InformationRemnant execution semantics."""

from __future__ import annotations

import pytest

from claude_phone.planner import Executor, InformationRemnant


def make_remnant(name, pre, eff, action=None, complexity=1.0):
    return InformationRemnant(
        name=name, preconditions=pre, effects=eff, action=action, complexity=complexity
    )


def test_remnant_execute_missing_precondition_raises():
    r = make_remnant("A", ["needed"], ["a"])
    with pytest.raises(RuntimeError, match="missing"):
        r.execute(set())


def test_remnant_execute_action_returning_none_is_success():
    r = make_remnant("A", [], ["a"], action=lambda: None)
    assert r.execute(set()) == {"a"}


def test_remnant_execute_action_failure_raises():
    r = make_remnant("A", [], ["a"], action=lambda: False)
    with pytest.raises(RuntimeError, match="Action failed"):
        r.execute(set())


def test_dry_run_applies_effects_without_calling_action():
    called = []
    r = make_remnant("A", [], ["a"], action=lambda: called.append(1) or True)
    ex = Executor()
    assert ex.execute_plan([r], dry_run=True) is True
    assert "a" in ex.state
    assert called == []  # action not invoked in dry-run


def test_real_run_invokes_actions_and_tracks_history():
    calls = []
    plan = [
        make_remnant("A", [], ["a"], action=lambda: calls.append("A") or True),
        make_remnant("B", ["a"], ["b"], action=lambda: calls.append("B") or True),
    ]
    ex = Executor()
    assert ex.execute_plan(plan) is True
    assert calls == ["A", "B"]
    assert ex.state == {"a", "b"}
    assert [h[0] for h in ex.history] == ["A", "B"]


def test_run_stops_on_failure_and_reports_false():
    plan = [
        make_remnant("A", [], ["a"], action=lambda: True),
        make_remnant("B", ["a"], ["b"], action=lambda: False),
        make_remnant("C", ["b"], ["c"], action=lambda: True),
    ]
    ex = Executor()
    assert ex.execute_plan(plan) is False
    assert "a" in ex.state
    assert "c" not in ex.state  # never reached


def test_skipped_step_with_unmet_preconditions_reports_false():
    # 'a' is never produced, so B can't run; execute_plan returns False.
    plan = [make_remnant("B", ["a"], ["b"], action=lambda: True)]
    ex = Executor()
    assert ex.execute_plan(plan) is False
    assert ex.state == set()


def test_probe_state_updates_facts():
    ex = Executor({"stale"})
    probes = {"present": lambda: True, "absent": lambda: False, "stale": lambda: False}
    state = ex.probe_state(probes)
    assert "present" in state
    assert "absent" not in state
    assert "stale" not in state
