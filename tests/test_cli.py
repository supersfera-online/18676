"""Tests for the CLI: argument resolution, exit codes, subcommands."""

from __future__ import annotations

import logging

import pytest

from claude_phone import cli


@pytest.fixture(autouse=True)
def _reset_logging():
    # configure_logging adds handlers; keep tests isolated.
    yield
    logging.getLogger("claude_phone").handlers.clear()


def test_list_command_returns_zero():
    assert cli.main(["list"]) == 0


def test_graph_command_returns_zero():
    assert cli.main(["graph"]) == 0


def test_default_command_is_plan(monkeypatch):
    captured = {}

    def fake_plan(args, remnants):
        captured["called"] = True
        return 0

    monkeypatch.setattr(cli, "_run_plan", fake_plan)
    assert cli.main([]) == 0
    assert captured["called"]


def test_legacy_probe_flag_maps_to_probe(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "probe_reality", lambda: calls.append(1) or set())
    assert cli.main(["--probe"]) == 0
    assert calls == [1]


def test_legacy_list_flag_maps_to_list():
    assert cli.main(["--list"]) == 0


def test_plan_dry_run_skip_probe_succeeds():
    # Pure planning + dry-run: no real commands are executed.
    assert cli.main(["plan", "--skip-probe", "--dry-run"]) == 0


def test_plan_unreachable_target_returns_one():
    assert cli.main(["plan", "--skip-probe", "--target", "no_such_fact"]) == 1


def test_plan_already_achieved_returns_zero():
    # termux_ready is auto-added to the initial state.
    assert cli.main(["plan", "--skip-probe", "--target", "termux_ready"]) == 0


def test_prompt_command_prints(capsys):
    # --skip-probe makes the generated prompt deterministic (bare device).
    assert cli.main(["prompt", "--skip-probe"]) == 0
    out = capsys.readouterr().out
    assert "Claude Code running inside Termux" in out
    assert "not yet fully configured" in out


def test_prompt_command_writes_file(tmp_path):
    target = tmp_path / "CLAUDE.md"
    assert cli.main(["prompt", "--skip-probe", "--output", str(target)]) == 0
    assert "Core Instructions" in target.read_text(encoding="utf-8")


def test_resolve_command_prefers_legacy_graph():
    parser = cli.build_parser()
    args = parser.parse_args(["--graph"])
    assert cli._resolve_command(args) == "graph"
