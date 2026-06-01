#!/data/data/com.termux/files/usr/bin/bash
#
# Interactive phone control menu for Termux (Samsung Galaxy S22+).

set -uo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

show_menu() {
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  Samsung S22+ — Control              ${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo -e "  ${CYAN}1${NC}  Battery info"
    echo -e "  ${CYAN}2${NC}  Wi-Fi status"
    echo -e "  ${CYAN}3${NC}  Toggle torch"
    echo -e "  ${CYAN}4${NC}  Volume control"
    echo -e "  ${CYAN}5${NC}  Take photo"
    echo -e "  ${CYAN}6${NC}  SIM card info"
    echo -e "  ${CYAN}7${NC}  Send notification"
    echo -e "  ${CYAN}8${NC}  Vibration"
    echo -e "  ${CYAN}9${NC}  Clipboard"
    echo -e "  ${CYAN}10${NC} Location (GPS)"
    echo -e "  ${CYAN}11${NC} Sensor list"
    echo -e "  ${CYAN}12${NC} Share text"
    echo -e "  ${CYAN}0${NC}  Exit"
    echo ""
}

battery_info() {
    echo -e "${YELLOW}Battery:${NC}"
    termux-battery-status | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  Level:        {d.get('percentage', '?')}%\")
print(f\"  Status:       {d.get('status', '?')}\")
print(f\"  Health:       {d.get('health', '?')}\")
print(f\"  Temperature:  {d.get('temperature', '?')}°C\")
print(f\"  Power source: {d.get('plugged', '?')}\")
"
}

wifi_info() {
    echo -e "${YELLOW}Wi-Fi:${NC}"
    termux-wifi-connectioninfo | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  Network (SSID): {d.get('ssid', '?')}\")
print(f\"  BSSID:          {d.get('bssid', '?')}\")
print(f\"  IP:             {d.get('ip', '?')}\")
print(f\"  Signal:         {d.get('rssi', '?')} dBm\")
print(f\"  Speed:          {d.get('link_speed_mbps', '?')} Mbps\")
print(f\"  Frequency:      {d.get('frequency_mhz', '?')} MHz\")
"
}

toggle_torch() {
    echo -n "Turn the torch on (on) or off (off)? "
    read -r choice
    if [ "$choice" = "on" ] || [ "$choice" = "off" ]; then
        termux-torch "$choice"
        echo -e "${GREEN}Torch: $choice${NC}"
    else
        echo "Enter 'on' or 'off'"
    fi
}

volume_control() {
    echo -e "${YELLOW}Current volume:${NC}"
    termux-volume | python3 -c "
import sys, json
streams = json.load(sys.stdin)
for s in streams:
    print(f\"  {s['stream']:12s}: {s['volume']}/{s['max_volume']}\")
"
    echo ""
    echo "Change volume? (music/ring/alarm/notification/system/call)"
    read -r stream
    case "$stream" in
        music|ring|alarm|notification|system|call) ;;
        "") return ;;
        *) echo -e "${RED}Invalid stream: $stream${NC}"; return ;;
    esac
    echo "Enter level (0-15):"
    read -r level
    if ! [[ "$level" =~ ^[0-9]+$ ]] || [ "$level" -gt 15 ]; then
        echo -e "${RED}Invalid level: $level (expected 0-15)${NC}"
        return
    fi
    termux-volume "$stream" "$level"
    echo -e "${GREEN}Volume $stream set to $level${NC}"
}

take_photo() {
    PHOTO_PATH="$HOME/storage/dcim/termux_photo_$(date +%Y%m%d_%H%M%S).jpg"
    echo "Taking photo..."
    termux-camera-photo "$PHOTO_PATH"
    echo -e "${GREEN}Photo saved: $PHOTO_PATH${NC}"
}

sim_info() {
    echo -e "${YELLOW}SIM card:${NC}"
    termux-telephony-deviceinfo | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k, v in d.items():
    name = k.replace('_', ' ').title()
    print(f'  {name}: {v}')
"
}

send_notification() {
    echo "Title:"
    read -r title
    echo "Text:"
    read -r text
    termux-notification --title "$title" --content "$text"
    echo -e "${GREEN}Notification sent!${NC}"
}

vibrate() {
    echo "Vibration duration (ms, default 500):"
    read -r duration
    duration=${duration:-500}
    if ! [[ "$duration" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}Invalid duration: $duration${NC}"
        return
    fi
    termux-vibrate -d "$duration"
    echo -e "${GREEN}Vibration: ${duration}ms${NC}"
}

clipboard() {
    echo "1 — Show clipboard"
    echo "2 — Copy text to clipboard"
    read -r choice
    case $choice in
        1)
            echo -e "${YELLOW}Clipboard:${NC}"
            termux-clipboard-get
            ;;
        2)
            echo "Enter text:"
            read -r text
            echo -n "$text" | termux-clipboard-set
            echo -e "${GREEN}Copied!${NC}"
            ;;
    esac
}

location_info() {
    echo "Getting location (may take a few seconds)..."
    termux-location | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  Latitude:  {d.get('latitude', '?')}\")
print(f\"  Longitude: {d.get('longitude', '?')}\")
print(f\"  Altitude:  {d.get('altitude', '?')} m\")
print(f\"  Accuracy:  {d.get('accuracy', '?')} m\")
"
}

sensor_list() {
    echo -e "${YELLOW}Device sensors:${NC}"
    termux-sensor -l 2>/dev/null | head -30
}

share_text() {
    echo "Enter text to share:"
    read -r text
    echo "$text" | termux-share -a send
    echo -e "${GREEN}Opened the 'Share' menu${NC}"
}

while true; do
    show_menu
    echo -n "Select an action: "
    read -r action
    echo ""

    case $action in
        1) battery_info ;;
        2) wifi_info ;;
        3) toggle_torch ;;
        4) volume_control ;;
        5) take_photo ;;
        6) sim_info ;;
        7) send_notification ;;
        8) vibrate ;;
        9) clipboard ;;
        10) location_info ;;
        11) sensor_list ;;
        12) share_text ;;
        0) echo "Exit."; exit 0 ;;
        *) echo -e "Unknown command: $action" ;;
    esac
    echo ""
    echo "Press Enter to continue..."
    read -r
done
