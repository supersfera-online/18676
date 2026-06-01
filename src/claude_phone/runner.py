"""Safe execution helpers for actions and probes.

SECURITY MODEL
--------------
``shell()`` and ``probe()`` run their command via ``shell=True``. This is only
safe because every command string originates from a **trusted literal** defined
inside this package (see :mod:`claude_phone.actions`). Command strings are never
constructed from, or interpolated with, user-supplied input: the CLI's
``--target`` argument is used solely as a *fact name* for the planner and is
never passed to a shell. The ``# nosec B602`` annotations below record this
invariant for Bandit.
"""

from __future__ import annotations

import logging
import subprocess  # nosec B404
from collections.abc import Callable

from . import config

logger = logging.getLogger(__name__)


def shell(cmd: str, timeout: float = config.DEFAULT_TIMEOUT) -> Callable[[], bool]:
    """Build an action callable that runs a trusted, static shell command.

    Returns a zero-argument callable that returns ``True`` on success
    (exit code 0) and ``False`` on failure or timeout.
    """

    def run() -> bool:
        logger.info("  $ %s", cmd)
        try:
            result = subprocess.run(  # nosec B602
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            logger.error("  ERROR: command timed out after %ss", timeout)
            return False

        if result.stdout.strip():
            logger.info("  %s", result.stdout.strip())
        if result.returncode != 0:
            if result.stderr.strip():
                logger.error("  ERROR: %s", result.stderr.strip())
            return False
        return True

    return run


def probe(cmd: str, timeout: float = config.DEFAULT_TIMEOUT) -> Callable[[], bool]:
    """Build a probe callable that reports whether a trusted command succeeds.

    Returns a zero-argument callable that returns ``True`` when the command
    exits 0, and ``False`` otherwise (including on timeout).
    """

    def check() -> bool:
        try:
            result = subprocess.run(  # nosec B602
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            logger.debug("probe timed out (%ss): %s", timeout, cmd)
            return False
        return result.returncode == 0

    return check
