#!/data/data/com.termux/files/usr/bin/bash
# ============================================
# Утилиты для управления Samsung Galaxy S22+
# Требует: Termux + Termux:API
# ============================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

show_menu() {
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  Samsung S22+ — Управление           ${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo -e "  ${CYAN}1${NC}  Информация о батарее"
    echo -e "  ${CYAN}2${NC}  Статус Wi-Fi"
    echo -e "  ${CYAN}3${NC}  Включить/выключить фонарик"
    echo -e "  ${CYAN}4${NC}  Управление громкостью"
    echo -e "  ${CYAN}5${NC}  Сделать фото"
    echo -e "  ${CYAN}6${NC}  Информация о SIM-карте"
    echo -e "  ${CYAN}7${NC}  Отправить уведомление"
    echo -e "  ${CYAN}8${NC}  Вибрация"
    echo -e "  ${CYAN}9${NC}  Буфер обмена"
    echo -e "  ${CYAN}10${NC} Местоположение (GPS)"
    echo -e "  ${CYAN}11${NC} Список датчиков"
    echo -e "  ${CYAN}12${NC} Поделиться текстом"
    echo -e "  ${CYAN}0${NC}  Выход"
    echo ""
}

battery_info() {
    echo -e "${YELLOW}Батарея:${NC}"
    termux-battery-status | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  Уровень:      {d.get('percentage', '?')}%\")
print(f\"  Статус:       {d.get('status', '?')}\")
print(f\"  Здоровье:     {d.get('health', '?')}\")
print(f\"  Температура:  {d.get('temperature', '?')}°C\")
print(f\"  Источник:     {d.get('plugged', '?')}\")
"
}

wifi_info() {
    echo -e "${YELLOW}Wi-Fi:${NC}"
    termux-wifi-connectioninfo | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  Сеть (SSID):  {d.get('ssid', '?')}\")
print(f\"  BSSID:        {d.get('bssid', '?')}\")
print(f\"  IP:           {d.get('ip', '?')}\")
print(f\"  Сигнал:       {d.get('rssi', '?')} dBm\")
print(f\"  Скорость:     {d.get('link_speed_mbps', '?')} Mbps\")
print(f\"  Частота:      {d.get('frequency_mhz', '?')} MHz\")
"
}

toggle_torch() {
    echo -n "Включить (on) или выключить (off) фонарик? "
    read -r choice
    if [ "$choice" = "on" ] || [ "$choice" = "off" ]; then
        termux-torch "$choice"
        echo -e "${GREEN}Фонарик: $choice${NC}"
    else
        echo "Введите 'on' или 'off'"
    fi
}

volume_control() {
    echo -e "${YELLOW}Текущая громкость:${NC}"
    termux-volume | python3 -c "
import sys, json
streams = json.load(sys.stdin)
for s in streams:
    print(f\"  {s['stream']:12s}: {s['volume']}/{s['max_volume']}\")
"
    echo ""
    echo "Изменить громкость? (music/ring/alarm/notification)"
    read -r stream
    if [ -n "$stream" ]; then
        echo "Введите уровень (0-15):"
        read -r level
        termux-volume "$stream" "$level"
        echo -e "${GREEN}Громкость $stream установлена на $level${NC}"
    fi
}

take_photo() {
    PHOTO_PATH="$HOME/storage/dcim/termux_photo_$(date +%Y%m%d_%H%M%S).jpg"
    echo "Делаю фото..."
    termux-camera-photo "$PHOTO_PATH"
    echo -e "${GREEN}Фото сохранено: $PHOTO_PATH${NC}"
}

sim_info() {
    echo -e "${YELLOW}SIM-карта:${NC}"
    termux-telephony-deviceinfo | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k, v in d.items():
    name = k.replace('_', ' ').title()
    print(f'  {name}: {v}')
"
}

send_notification() {
    echo "Заголовок:"
    read -r title
    echo "Текст:"
    read -r text
    termux-notification --title "$title" --content "$text"
    echo -e "${GREEN}Уведомление отправлено!${NC}"
}

vibrate() {
    echo "Длительность вибрации (мс, по умолчанию 500):"
    read -r duration
    duration=${duration:-500}
    termux-vibrate -d "$duration"
    echo -e "${GREEN}Вибрация: ${duration}мс${NC}"
}

clipboard() {
    echo "1 — Показать буфер обмена"
    echo "2 — Скопировать текст в буфер"
    read -r choice
    case $choice in
        1)
            echo -e "${YELLOW}Буфер обмена:${NC}"
            termux-clipboard-get
            ;;
        2)
            echo "Введите текст:"
            read -r text
            echo -n "$text" | termux-clipboard-set
            echo -e "${GREEN}Скопировано!${NC}"
            ;;
    esac
}

location_info() {
    echo "Получаю местоположение (может занять несколько секунд)..."
    termux-location | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  Широта:   {d.get('latitude', '?')}\")
print(f\"  Долгота:  {d.get('longitude', '?')}\")
print(f\"  Высота:   {d.get('altitude', '?')} м\")
print(f\"  Точность: {d.get('accuracy', '?')} м\")
"
}

sensor_list() {
    echo -e "${YELLOW}Датчики устройства:${NC}"
    termux-sensor -l 2>/dev/null | head -30
}

share_text() {
    echo "Введите текст для отправки:"
    read -r text
    echo "$text" | termux-share -a send
    echo -e "${GREEN}Открыто меню 'Поделиться'${NC}"
}

# --- Главный цикл ---
while true; do
    show_menu
    echo -n "Выберите действие: "
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
        0) echo "Выход."; exit 0 ;;
        *) echo -e "Неизвестная команда: $action" ;;
    esac
    echo ""
    echo "Нажмите Enter для продолжения..."
    read -r
done
