"""claude-phone: a STRIPS-style planner-executor for bootstrapping Claude Code
on an Android phone via Termux."""

from __future__ import annotations

from .planner import Executor, InformationRemnant, Planner

__version__ = "0.1.0"

__all__ = ["Executor", "InformationRemnant", "Planner", "__version__"]
