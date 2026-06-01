"""Project-wide constants.

Centralising these values keeps "magic" strings out of the action and probe
definitions and makes the tool easy to retarget to a different device or
network without touching the planner logic.
"""

from __future__ import annotations

# Human-readable device this tool is tuned for (used in banners/messages only).
PHONE_MODEL = "Samsung Galaxy S22+"

# Host used for the connectivity probe/action. A literal IP avoids depending on
# DNS being configured before the network is verified.
PING_TARGET = "8.8.8.8"

# Default goal fact the planner aims for when no target is supplied.
DEFAULT_TARGET = "fully_configured"

# Subprocess timeouts (seconds). Without these a hanging command (e.g. a GPS
# fix or an unreachable ping) would block the whole run indefinitely.
DEFAULT_TIMEOUT = 60.0
# GPS fixes legitimately take longer than a normal command.
LOCATION_TIMEOUT = 120.0
