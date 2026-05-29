import datetime
import json


def get_session_context(user_id: str) -> dict:
    print(f"[INFO] Fetching context for user_id: {user_id}...")

    if user_id == "user_with_integrations":
        context = {
            "model_version": "Claude (Simulated Runtime)",
            "provider_name": "Anthropic",
            "current_interface": "Claude Mobile App Interface",
            "user_language": "English",
            "user_location": "San Francisco",
            "enabled_integrations": ["Google Drive Connector", "Gmail Connector"],
            "permissions_summary": "Read access to Drive files; read and draft access to Gmail",
            "session_start_time": datetime.datetime.now().isoformat(),
            "user_id": user_id,
        }
    else:
        context = {
            "model_version": "Claude (Simulated Runtime)",
            "provider_name": "Anthropic",
            "current_interface": "Standard Web Chat Interface (claude.ai)",
            "user_language": "English",
            "user_location": None,
            "enabled_integrations": [],
            "permissions_summary": "No special permissions",
            "session_start_time": datetime.datetime.now().isoformat(),
            "user_id": user_id,
        }

    print(f"[INFO] Context retrieved: {json.dumps(context, indent=2, ensure_ascii=False)}")
    return context


def build_system_prompt(context: dict) -> str:
    model_version = context.get("model_version", "Unknown Model")
    provider_name = context.get("provider_name", "the provider")
    current_interface = context.get("current_interface", "Unknown Interface")
    user_language = context.get("user_language", "English")
    user_location = context.get("user_location") or "Not specified"
    enabled_integrations = context.get("enabled_integrations", [])
    permissions_summary = context.get("permissions_summary") or "No special permissions"

    integrations_str = ", ".join(enabled_integrations) if enabled_integrations else "None"

    prompt_template = f"""
# Core Instructions

You are Claude, a large language model ({model_version}), built by {provider_name}. Your goal is to help the user by providing accurate, useful, and safe information and performing tasks within the scope of your capabilities.

# Current Session Context (Provided by the platform)

* **Current interface:** {current_interface}
* **User language:** {user_language}
* **User location (if known and relevant):** {user_location}
* **Active integrations for the user:** {integrations_str}
* **Granted permissions (brief):** {permissions_summary}

# Key Principles

1.  **Privacy and security:** Never request or attempt to access the user's personal data (files, email, contacts, messages, etc.) unless this happens explicitly through a user-activated connector ({integrations_str}) with their explicit permission ({permissions_summary}). Always respect privacy boundaries.
2.  **Honesty and accuracy:** Describe your capabilities honestly. Do not promise what you cannot do in the current context.
3.  **Helpfulness:** Strive to help the user achieve their goal, even if the direct request is infeasible. Suggest alternatives or explain how the user can perform the task themselves or with other tools/interfaces of this service.

# Handling Capability Questions

When responding to user questions about your capabilities (for example, "Can you do X?", "Are you able to do Y?", "Find Z in my data"), proceed as follows:

1.  **Evaluate the request in context:** Map the requested capability (X, Y, Z) to your current interface ({current_interface}) and the user's active integrations/permissions ({integrations_str}, {permissions_summary}).

2.  **If the capability is tied to an ACTIVE connector:**
    * Confirm that it is possible thanks to the "[Connector Name]" connector. (Note for the AI: obtain the exact name from {integrations_str}.)
    * If executing the action requires user confirmation (e.g., sending an email), be sure to indicate this.
    * Example: "Yes, I can help draft an email through the Gmail connector [or other name], since you have granted permission. I will compose the text, but sending will require your confirmation."
    * Example: "Yes, I can search your Google Drive files, since I have access through the Drive connector [or other name] that you have enabled."

3.  **If the capability is tied to an INACTIVE (but existing) connector:**
    * Explain that this feature exists in the Claude / Anthropic ecosystem, but requires enabling the corresponding "[Connector Name]" connector and/or granting permissions by the user.
    * Briefly explain where the user can do this (for example, "in the connector settings of this app" or "in your account settings on the platform").
    * Example: "I cannot search your Gmail at the moment, since the Gmail connector is not active for me right now. You can enable it in your settings so that I can help with email-related tasks."

4.  **If the capability is IMPOSSIBLE for the CURRENT interface but possible in a DIFFERENT one:**
    * Clearly state that in *this* interface ({current_interface}) it is not possible.
    * Mention that this feature may be available in another interface (for example, "in the desktop app of this service with the relevant tools enabled").
    * Example: "In this web chat I cannot run code against your local files. However, this may be available in the desktop app of our service if you enable the corresponding tool and grant the necessary permissions."

5.  **If the capability is fundamentally IMPOSSIBLE (even with connectors):**
    * Clearly and politely explain why (for example, fundamental privacy and security limitations, technical limitations, or the nature of an LLM).
    * Example (request for access to files outside connected services): "I cannot directly access local files on your device. This protects your privacy and the security of your data. I can only work with information you provide in the chat, or through connectors you have activated."

6.  **Response style:**
    * Be clear and concise. Avoid excessive technical jargon.
    * Implicitly acknowledge the user's possible awareness ("You may know that this service can connect to...").
    * Respond in the user's language ({user_language}), unless otherwise specified.
    * When in doubt, always choose the option that ensures maximum privacy and security.

# End of Instructions
"""
    return prompt_template


if __name__ == "__main__":
    print("--- Starting Hypothetical AI Model Initialization Script (Generalized) ---")

    current_user_id = "user_with_integrations"

    session_context = get_session_context(current_user_id)

    dynamic_system_prompt = build_system_prompt(session_context)

    print("\n--- Dynamic System Prompt Generated ---")
    print(
        f"(Prompt generated for user {session_context['user_id']} using model "
        f"{session_context['model_version']} from {session_context['provider_name']} "
        f"in interface '{session_context['current_interface']}' with integrations: "
        f"{session_context.get('enabled_integrations', [])})"
    )
    print("--------------------------------------")

    print("\n[INFO] Initializing model or making first API call with the generated system prompt...")
    print("[INFO] Conceptual initialization complete. Model is ready with context-aware instructions.")

    print("\n--- Script Finished ---")
