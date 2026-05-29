from remnant import InformationRemnant, shell, probe


PROBES = {
    "termux_ready":      probe("echo $TERMUX_VERSION"),
    "termux_api_ready":  probe("command -v termux-battery-status"),
    "storage_accessible": probe("test -d $HOME/storage/shared"),
    "nodejs_ready":      probe("command -v node"),
    "python_ready":      probe("command -v python3"),
    "git_ready":         probe("command -v git"),
    "claude_installed":  probe("command -v claude"),
    "has_internet":      probe("ping -c 1 -W 2 8.8.8.8"),
    "wifi_connected":    probe("termux-wifi-connectioninfo 2>/dev/null | grep -q ssid"),
    "battery_known":     probe("termux-battery-status 2>/dev/null | grep -q percentage"),
}


def phone_remnants() -> list[InformationRemnant]:

    return [
        InformationRemnant(
            name="Update Termux",
            preconditions=["termux_ready"],
            effects=["packages_updated"],
            complexity=3,
            action=shell("pkg update -y && pkg upgrade -y"),
            description="Update all Termux packages to the latest versions",
        ),

        InformationRemnant(
            name="Set up storage",
            preconditions=["termux_ready"],
            effects=["storage_accessible"],
            complexity=0.5,
            action=shell("termux-setup-storage"),
            description="Give Termux access to phone files (photos, downloads, etc.)",
        ),

        InformationRemnant(
            name="Install Termux:API",
            preconditions=["termux_ready", "packages_updated"],
            effects=["termux_api_ready"],
            complexity=1,
            action=shell("pkg install -y termux-api"),
            description="Package for access to phone sensors and settings",
        ),

        InformationRemnant(
            name="Install Python",
            preconditions=["termux_ready", "packages_updated"],
            effects=["python_ready"],
            complexity=1,
            action=shell("pkg install -y python"),
        ),

        InformationRemnant(
            name="Install Git",
            preconditions=["termux_ready", "packages_updated"],
            effects=["git_ready"],
            complexity=0.5,
            action=shell("pkg install -y git"),
        ),

        InformationRemnant(
            name="Install Node.js",
            preconditions=["termux_ready", "packages_updated"],
            effects=["nodejs_ready"],
            complexity=2,
            action=shell("pkg install -y nodejs-lts"),
        ),

        InformationRemnant(
            name="Install Claude Code",
            preconditions=["nodejs_ready", "has_internet"],
            effects=["claude_installed"],
            complexity=3,
            action=shell("npm install -g @anthropic-ai/claude-code"),
            description="Install the Claude Code CLI globally via npm",
        ),

        InformationRemnant(
            name="Check internet",
            preconditions=["termux_ready"],
            effects=["has_internet"],
            complexity=0.1,
            action=shell("ping -c 1 -W 2 8.8.8.8"),
        ),

        InformationRemnant(
            name="Wi-Fi info",
            preconditions=["termux_api_ready", "wifi_connected"],
            effects=["wifi_info_known"],
            complexity=0.2,
            action=shell("termux-wifi-connectioninfo"),
        ),

        InformationRemnant(
            name="Scan Wi-Fi networks",
            preconditions=["termux_api_ready"],
            effects=["wifi_scanned"],
            complexity=0.5,
            action=shell("termux-wifi-scaninfo"),
        ),

        InformationRemnant(
            name="Battery status",
            preconditions=["termux_api_ready"],
            effects=["battery_known"],
            complexity=0.1,
            action=shell("termux-battery-status"),
        ),

        InformationRemnant(
            name="SIM info",
            preconditions=["termux_api_ready"],
            effects=["sim_info_known"],
            complexity=0.2,
            action=shell("termux-telephony-deviceinfo"),
        ),

        InformationRemnant(
            name="Location",
            preconditions=["termux_api_ready"],
            effects=["location_known"],
            complexity=1,
            action=shell("termux-location -p gps"),
            description="Get GPS coordinates (may take a few seconds)",
        ),

        InformationRemnant(
            name="Sensor list",
            preconditions=["termux_api_ready"],
            effects=["sensors_listed"],
            complexity=0.2,
            action=shell("termux-sensor -l"),
        ),

        InformationRemnant(
            name="Torch ON",
            preconditions=["termux_api_ready"],
            effects=["torch_on"],
            complexity=0.1,
            action=shell("termux-torch on"),
        ),

        InformationRemnant(
            name="Torch OFF",
            preconditions=["termux_api_ready"],
            effects=["torch_off"],
            complexity=0.1,
            action=shell("termux-torch off"),
        ),

        InformationRemnant(
            name="Vibration",
            preconditions=["termux_api_ready"],
            effects=["vibrated"],
            complexity=0.1,
            action=shell("termux-vibrate -d 500"),
        ),

        InformationRemnant(
            name="Show volume",
            preconditions=["termux_api_ready"],
            effects=["volume_known"],
            complexity=0.1,
            action=shell("termux-volume"),
        ),

        InformationRemnant(
            name="Notification",
            preconditions=["termux_api_ready"],
            effects=["notification_sent"],
            complexity=0.2,
            action=shell('termux-notification --title "Claude" --content "Hello from the phone!"'),
        ),

        InformationRemnant(
            name="Take photo",
            preconditions=["termux_api_ready", "storage_accessible"],
            effects=["photo_taken"],
            complexity=1,
            action=shell('termux-camera-photo "$HOME/storage/dcim/claude_photo.jpg"'),
        ),

        InformationRemnant(
            name="Clipboard — read",
            preconditions=["termux_api_ready"],
            effects=["clipboard_read"],
            complexity=0.1,
            action=shell("termux-clipboard-get"),
        ),

        InformationRemnant(
            name="Show downloads",
            preconditions=["storage_accessible"],
            effects=["downloads_listed"],
            complexity=0.1,
            action=shell("ls -la $HOME/storage/downloads/"),
        ),

        InformationRemnant(
            name="Show photos",
            preconditions=["storage_accessible"],
            effects=["photos_listed"],
            complexity=0.1,
            action=shell("ls -la $HOME/storage/dcim/"),
        ),

        InformationRemnant(
            name="Fully ready",
            preconditions=[
                "packages_updated", "termux_api_ready", "storage_accessible",
                "python_ready", "nodejs_ready", "git_ready",
                "claude_installed", "has_internet",
            ],
            effects=["fully_configured"],
            complexity=0.1,
            action=shell("echo '=== Samsung S22+ is fully configured for Claude Code ==='"),
            description="All components installed and ready",
        ),
    ]
