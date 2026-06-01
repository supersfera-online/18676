"""Generate a system prompt that reflects the phone's *actual* state.

This used to be a standalone demo that emitted a generic web-assistant prompt
disconnected from the rest of the tool. It is now wired into the planner: the
prompt is built from the device facts discovered by ``probe_reality`` plus the
live action catalogue (:func:`claude_phone.actions.phone_remnants`), so it
always describes what Claude Code can really do on *this* device right now.

Because the context is derived from state, the prompt **regenerates** whenever
the device changes — re-probe (or re-run ``claude-phone prompt``) and the
capabilities, configured-status, and remaining setup steps update accordingly.
"""

from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any

from . import config

if TYPE_CHECKING:
    from .planner import InformationRemnant

logger = logging.getLogger(__name__)

# Headline capabilities unlocked by each fact. A capability is rendered only when
# its fact holds in the probed state, so the prompt never claims something the
# device cannot currently do.
CAPABILITY_BY_FACT: dict[str, str] = {
    "claude_installed": "Operate as the Claude Code CLI (installed globally via npm).",
    "has_internet": "Reach the network (verified by a connectivity probe).",
    "python_ready": "Run Python 3 scripts.",
    "nodejs_ready": "Run Node.js.",
    "git_ready": "Use git for version control.",
    "storage_accessible": ("Read and write the phone's shared storage (downloads, DCIM/photos)."),
    "termux_api_ready": (
        "Control phone hardware through Termux:API — torch, camera, GPS location, "
        "battery status, sensors, vibration, notifications, clipboard and Wi-Fi info."
    ),
}

# Fact that marks a fully set-up device, used to locate the "fully configured"
# action in the catalogue so the required-facts list has a single source of truth.
_CONFIGURED_FACT = "fully_configured"


def _core_facts(remnants: list[InformationRemnant]) -> list[str]:
    """The facts required for a fully-configured device, read from the catalogue.

    Derived from the action that produces :data:`_CONFIGURED_FACT` so this list
    cannot drift from the planner's own definition of "done".
    """
    for r in remnants:
        if _CONFIGURED_FACT in r.effects:
            return list(r.preconditions)
    return []


def _enabling_action(fact: str, remnants: list[InformationRemnant]) -> str | None:
    """Name of the action that would make ``fact`` true (if any)."""
    for r in remnants:
        if fact in r.effects:
            return r.name
    return None


def get_device_context(
    state: set[str],
    remnants: list[InformationRemnant],
    *,
    now: datetime.datetime | None = None,
) -> dict[str, Any]:
    """Build the prompt context from the probed ``state`` and action catalogue.

    :param state: facts currently known to hold (from ``probe_reality``).
    :param remnants: the live action catalogue.
    :param now: injectable timestamp (defaults to the current time) so tests are
        deterministic.
    """
    logger.debug("Building device context from %d facts", len(state))
    core = _core_facts(remnants)
    missing = [f for f in core if f not in state]

    capabilities = [CAPABILITY_BY_FACT[fact] for fact in CAPABILITY_BY_FACT if fact in state]
    next_steps = [
        f"{fact} — run “{action}”"
        for fact in missing
        if (action := _enabling_action(fact, remnants)) is not None
    ]

    return {
        "phone_model": config.PHONE_MODEL,
        "session_start_time": (now or datetime.datetime.now()).isoformat(),
        "facts": sorted(state),
        "configured": not missing,
        "capabilities": capabilities,
        "next_steps": next_steps,
    }


def build_system_prompt(context: dict[str, Any]) -> str:
    """Render the on-device system prompt text from a device ``context`` dict."""
    phone_model = context.get("phone_model", "an Android phone")
    generated_at = context.get("session_start_time", "unknown")
    configured = context.get("configured", False)
    facts = context.get("facts", [])
    capabilities = context.get("capabilities", [])
    next_steps = context.get("next_steps", [])

    status = "fully configured for Claude Code" if configured else "not yet fully configured"
    facts_str = ", ".join(facts) if facts else "none detected yet"

    if capabilities:
        capabilities_block = "\n".join(f"* {cap}" for cap in capabilities)
    else:
        capabilities_block = (
            "* None yet — the device has not been set up. Only basic shell access is available."
        )

    if next_steps:
        next_block = "\n".join(f"* {step}" for step in next_steps)
    else:
        next_block = "* None — every required component is already in place."

    return f"""\
# Core Instructions

You are Claude Code running inside Termux on a {phone_model} (Android). This
system prompt is generated from the device's **actual probed state**, so it
reflects what is genuinely available right now. It is regenerated whenever the
device changes — never assume a capability that is not listed below.

# Current Device Context (probed)

* **Device:** {phone_model}
* **Generated at:** {generated_at}
* **Status:** {status}
* **Known facts:** {facts_str}

# Capabilities available now

{capabilities_block}

# Remaining setup (not yet available)

{next_block}

# Key Principles

1.  **Honesty about capabilities:** Only offer to do things backed by a
    capability under "Capabilities available now". If a capability is missing,
    say so and point to the setup step that would enable it (run
    `claude-phone plan` to perform the remaining setup).
2.  **Phone hardware needs Termux:API:** Torch, camera, GPS, battery, sensors,
    vibration, notifications, clipboard and Wi-Fi info only work once
    `termux_api_ready` holds. Do not claim them otherwise.
3.  **Storage boundaries:** Read or write phone files only when
    `storage_accessible` holds, and only within the shared storage paths.
4.  **Privacy and security:** Never access the user's data beyond what the
    granted capabilities allow; when in doubt, choose the safer option.

# End of Instructions
"""
