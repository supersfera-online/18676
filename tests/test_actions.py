"""Consistency tests for the action/probe catalogue."""

from __future__ import annotations

from claude_phone.actions import PROBES, phone_remnants
from claude_phone.planner import Planner


def test_no_duplicate_action_names():
    names = [r.name for r in phone_remnants()]
    assert len(names) == len(set(names))


def test_every_precondition_has_a_producer_or_probe():
    remnants = phone_remnants()
    produced = {e for r in remnants for e in r.effects}
    known = produced | set(PROBES) | {"termux_ready"}
    for r in remnants:
        for pre in r.preconditions:
            assert pre in known, f"{r.name} needs unreachable precondition '{pre}'"


def test_fully_configured_is_reachable_from_bootstrap_state():
    remnants = phone_remnants()
    planner = Planner(remnants)
    plan = planner.plan({"termux_ready"}, {"fully_configured"})
    assert plan, "expected a non-empty plan"
    assert plan[-1].name == "Fully ready"


def test_probes_are_callables():
    assert all(callable(c) for c in PROBES.values())


def test_termux_ready_probe_is_false_outside_termux(monkeypatch):
    """Regression for UNCERTAINTIES A1: the probe must actually detect Termux,
    not return True everywhere because `echo` always exits 0."""
    monkeypatch.delenv("TERMUX_VERSION", raising=False)
    assert PROBES["termux_ready"]() is False


def test_termux_ready_probe_is_true_inside_termux(monkeypatch):
    monkeypatch.setenv("TERMUX_VERSION", "0.118.0")
    assert PROBES["termux_ready"]() is True
