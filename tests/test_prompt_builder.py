"""Tests for the device-state-aware system-prompt builder."""

from __future__ import annotations

import datetime

from claude_phone.actions import phone_remnants
from claude_phone.prompt_builder import build_system_prompt, get_device_context

REMNANTS = phone_remnants()


def test_bare_device_reports_not_configured_and_no_capabilities():
    ctx = get_device_context(set(), REMNANTS)
    assert ctx["configured"] is False
    assert ctx["capabilities"] == []
    # The remaining-setup list is derived from the catalogue's "fully_configured".
    assert any("claude_installed" in step for step in ctx["next_steps"])

    prompt = build_system_prompt(ctx)
    assert "not yet fully configured" in prompt
    assert "Only basic shell access is available" in prompt


def test_termux_api_unlocks_hardware_capabilities():
    ctx = get_device_context({"termux_api_ready"}, REMNANTS)
    prompt = build_system_prompt(ctx)
    # The hardware capability line is present only because the fact holds.
    assert "Termux:API" in prompt
    assert any("torch" in cap for cap in ctx["capabilities"])


def test_capability_absent_when_fact_absent():
    ctx = get_device_context(set(), REMNANTS)
    assert not any("Termux:API" in cap for cap in ctx["capabilities"])


def test_fully_configured_device_lists_no_remaining_setup():
    core = next(r for r in REMNANTS if "fully_configured" in r.effects).preconditions
    ctx = get_device_context(set(core), REMNANTS)
    assert ctx["configured"] is True
    assert ctx["next_steps"] == []
    prompt = build_system_prompt(ctx)
    assert "fully configured for Claude Code" in prompt
    assert "every required component is already in place" in prompt


def test_prompt_rebuilds_when_state_changes():
    """The whole point: a different device state yields a different prompt."""
    before = build_system_prompt(get_device_context(set(), REMNANTS))
    after = build_system_prompt(get_device_context({"termux_api_ready"}, REMNANTS))
    assert before != after


def test_context_timestamp_is_injectable():
    fixed = datetime.datetime(2026, 1, 1, 12, 0, 0)
    ctx = get_device_context(set(), REMNANTS, now=fixed)
    assert ctx["session_start_time"] == fixed.isoformat()
    assert fixed.isoformat() in build_system_prompt(ctx)
