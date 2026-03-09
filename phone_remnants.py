
"""
Флуктуации для Samsung Galaxy S22+.
Реальные действия, которые трансформируют состояние телефона через Termux.
"""

from remnant import InformationRemnant, shell, probe


# ============================================================
# Пробы — узнать текущее состояние реальности
# ============================================================

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


# ============================================================
# Флуктуации — действия, которые меняют реальность
# ============================================================

def phone_remnants() -> list[InformationRemnant]:
    """Полный набор действий для настройки и управления Samsung S22+."""

    return [
        # --- Базовая инфраструктура ---

        InformationRemnant(
            name="Обновить Termux",
            preconditions=["termux_ready"],
            effects=["packages_updated"],
            complexity=3,
            action=shell("pkg update -y && pkg upgrade -y"),
            description="Обновить все пакеты Termux до последних версий",
        ),

        InformationRemnant(
            name="Настроить хранилище",
            preconditions=["termux_ready"],
            effects=["storage_accessible"],
            complexity=0.5,
            action=shell("termux-setup-storage"),
            description="Дать Termux доступ к файлам телефона (фото, загрузки и т.д.)",
        ),

        InformationRemnant(
            name="Установить Termux:API",
            preconditions=["termux_ready", "packages_updated"],
            effects=["termux_api_ready"],
            complexity=1,
            action=shell("pkg install -y termux-api"),
            description="Пакет для доступа к датчикам и настройкам телефона",
        ),

        InformationRemnant(
            name="Установить Python",
            preconditions=["termux_ready", "packages_updated"],
            effects=["python_ready"],
            complexity=1,
            action=shell("pkg install -y python"),
        ),

        InformationRemnant(
            name="Установить Git",
            preconditions=["termux_ready", "packages_updated"],
            effects=["git_ready"],
            complexity=0.5,
            action=shell("pkg install -y git"),
        ),

        InformationRemnant(
            name="Установить Node.js",
            preconditions=["termux_ready", "packages_updated"],
            effects=["nodejs_ready"],
            complexity=2,
            action=shell("pkg install -y nodejs-lts"),
        ),

        # --- Claude Code ---

        InformationRemnant(
            name="Установить Claude Code",
            preconditions=["nodejs_ready", "has_internet"],
            effects=["claude_installed"],
            complexity=3,
            action=shell("npm install -g @anthropic-ai/claude-code"),
            description="Установить Claude Code CLI глобально через npm",
        ),

        # --- Сеть ---

        InformationRemnant(
            name="Проверить интернет",
            preconditions=["termux_ready"],
            effects=["has_internet"],
            complexity=0.1,
            action=shell("ping -c 1 -W 2 8.8.8.8"),
        ),

        InformationRemnant(
            name="Информация Wi-Fi",
            preconditions=["termux_api_ready", "wifi_connected"],
            effects=["wifi_info_known"],
            complexity=0.2,
            action=shell("termux-wifi-connectioninfo"),
        ),

        InformationRemnant(
            name="Сканировать Wi-Fi сети",
            preconditions=["termux_api_ready"],
            effects=["wifi_scanned"],
            complexity=0.5,
            action=shell("termux-wifi-scaninfo"),
        ),

        # --- Состояние устройства ---

        InformationRemnant(
            name="Статус батареи",
            preconditions=["termux_api_ready"],
            effects=["battery_known"],
            complexity=0.1,
            action=shell("termux-battery-status"),
        ),

        InformationRemnant(
            name="Информация о SIM",
            preconditions=["termux_api_ready"],
            effects=["sim_info_known"],
            complexity=0.2,
            action=shell("termux-telephony-deviceinfo"),
        ),

        InformationRemnant(
            name="Местоположение",
            preconditions=["termux_api_ready"],
            effects=["location_known"],
            complexity=1,
            action=shell("termux-location -p gps"),
            description="Получить GPS-координаты (может занять несколько секунд)",
        ),

        InformationRemnant(
            name="Список датчиков",
            preconditions=["termux_api_ready"],
            effects=["sensors_listed"],
            complexity=0.2,
            action=shell("termux-sensor -l"),
        ),

        # --- Управление ---

        InformationRemnant(
            name="Фонарик ВКЛ",
            preconditions=["termux_api_ready"],
            effects=["torch_on"],
            complexity=0.1,
            action=shell("termux-torch on"),
        ),

        InformationRemnant(
            name="Фонарик ВЫКЛ",
            preconditions=["termux_api_ready"],
            effects=["torch_off"],
            complexity=0.1,
            action=shell("termux-torch off"),
        ),

        InformationRemnant(
            name="Вибрация",
            preconditions=["termux_api_ready"],
            effects=["vibrated"],
            complexity=0.1,
            action=shell("termux-vibrate -d 500"),
        ),

        InformationRemnant(
            name="Показать громкость",
            preconditions=["termux_api_ready"],
            effects=["volume_known"],
            complexity=0.1,
            action=shell("termux-volume"),
        ),

        InformationRemnant(
            name="Уведомление",
            preconditions=["termux_api_ready"],
            effects=["notification_sent"],
            complexity=0.2,
            action=shell('termux-notification --title "Claude" --content "Привет с телефона!"'),
        ),

        InformationRemnant(
            name="Сделать фото",
            preconditions=["termux_api_ready", "storage_accessible"],
            effects=["photo_taken"],
            complexity=1,
            action=shell('termux-camera-photo "$HOME/storage/dcim/claude_photo.jpg"'),
        ),

        InformationRemnant(
            name="Буфер обмена — прочитать",
            preconditions=["termux_api_ready"],
            effects=["clipboard_read"],
            complexity=0.1,
            action=shell("termux-clipboard-get"),
        ),

        # --- Файловая система ---

        InformationRemnant(
            name="Показать загрузки",
            preconditions=["storage_accessible"],
            effects=["downloads_listed"],
            complexity=0.1,
            action=shell("ls -la $HOME/storage/downloads/"),
        ),

        InformationRemnant(
            name="Показать фото",
            preconditions=["storage_accessible"],
            effects=["photos_listed"],
            complexity=0.1,
            action=shell("ls -la $HOME/storage/dcim/"),
        ),

        # --- Полная настройка (составная цель) ---

        InformationRemnant(
            name="Полная готовность",
            preconditions=[
                "packages_updated", "termux_api_ready", "storage_accessible",
                "python_ready", "nodejs_ready", "git_ready",
                "claude_installed", "has_internet",
            ],
            effects=["fully_configured"],
            complexity=0.1,
            action=shell("echo '=== Samsung S22+ полностью настроен для Claude Code ==='"),
            description="Все компоненты установлены и готовы к работе",
        ),
    ]
