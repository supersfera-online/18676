"""Tests for the system-prompt builder."""

from __future__ import annotations

import datetime

from claude_phone.prompt_builder import (
    build_system_prompt,
    get_session_context,
)


def test_context_for_known_user_has_integrations():
    ctx = get_session_context("user_with_integrations")
    assert "Gmail Connector" in ctx["enabled_integrations"]
    assert ctx["user_id"] == "user_with_integrations"


def test_context_for_unknown_user_uses_defaults():
    ctx = get_session_context("somebody_else")
    assert ctx["enabled_integrations"] == []
    assert ctx["permissions_summary"] == "No special permissions"
    assert ctx["user_id"] == "somebody_else"


def test_context_timestamp_is_injectable():
    fixed = datetime.datetime(2026, 1, 1, 12, 0, 0)
    ctx = get_session_context("default", now=fixed)
    assert ctx["session_start_time"] == fixed.isoformat()


def test_prompt_mentions_active_integrations():
    ctx = get_session_context("user_with_integrations")
    prompt = build_system_prompt(ctx)
    assert "Gmail Connector" in prompt
    assert "Claude Mobile App Interface" in prompt


def test_prompt_handles_no_integrations():
    prompt = build_system_prompt(get_session_context("nobody"))
    assert "Active integrations for the user:** None" in prompt
