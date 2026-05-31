"""Tests for the trusted command runner (subprocess is mocked)."""

from __future__ import annotations

import subprocess
from types import SimpleNamespace

import pytest

from claude_phone import runner


def fake_completed(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_shell_success(monkeypatch):
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: fake_completed(0, "hello"))
    assert runner.shell("echo hello")() is True


def test_shell_nonzero_returns_false(monkeypatch):
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: fake_completed(1, "", "boom"))
    assert runner.shell("false")() is False


def test_shell_timeout_is_soft_failure(monkeypatch):
    def raise_timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd="sleep", timeout=1)

    monkeypatch.setattr(runner.subprocess, "run", raise_timeout)
    assert runner.shell("sleep 999", timeout=1)() is False


def test_probe_success(monkeypatch):
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: fake_completed(0))
    assert runner.probe("command -v node")() is True


def test_probe_failure(monkeypatch):
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: fake_completed(127))
    assert runner.probe("command -v nope")() is False


def test_probe_timeout_returns_false(monkeypatch):
    def raise_timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd="x", timeout=1)

    monkeypatch.setattr(runner.subprocess, "run", raise_timeout)
    assert runner.probe("x", timeout=1)() is False


def test_runner_passes_timeout_to_subprocess(monkeypatch):
    captured = {}

    def capture(*a, **k):
        captured.update(k)
        return fake_completed(0)

    monkeypatch.setattr(runner.subprocess, "run", capture)
    runner.shell("echo hi", timeout=42)()
    assert captured["timeout"] == 42
    assert captured["shell"] is True


@pytest.mark.parametrize("rc,expected", [(0, True), (2, False)])
def test_shell_return_matches_exit_code(monkeypatch, rc, expected):
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: fake_completed(rc))
    assert runner.shell("cmd")() is expected
