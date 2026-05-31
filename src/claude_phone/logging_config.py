"""Logging configuration for the CLI.

The tool's output doubles as a user-facing console UI, so the default handler
emits messages verbatim (``%(message)s``) to keep the friendly look of the
original ``print`` based output, while still going through the ``logging``
machinery so verbosity can be controlled and errors can be filtered.
"""

from __future__ import annotations

import logging

PACKAGE_LOGGER = "claude_phone"


def configure_logging(verbose: int = 0, quiet: bool = False) -> None:
    """Configure the package logger.

    :param verbose: ``-v`` count; ``>=1`` enables ``DEBUG`` output.
    :param quiet: when set, only warnings and errors are shown.
    """
    if quiet:
        level = logging.WARNING
    elif verbose >= 1:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger = logging.getLogger(PACKAGE_LOGGER)
    logger.setLevel(level)

    # Avoid duplicate handlers if configure_logging is called more than once
    # (e.g. in tests).
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
