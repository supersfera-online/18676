#!/data/data/com.termux/files/usr/bin/bash

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN} Claude Code — Установка на телефон   ${NC}"
echo -e "${GREEN} Samsung Galaxy S22+                  ${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

echo -e "${YELLOW}[1/6] Обновляю пакеты Termux...${NC}"
pkg update -y && pkg upgrade -y

echo -e "${YELLOW}[2/6] Устанавливаю Node.js, Git, Python...${NC}"
pkg install -y nodejs-lts git python

echo -e "${YELLOW}[3/6] Настраиваю доступ к хранилищу телефона...${NC}"
echo "Нажмите 'Разрешить' во всплывающем окне!"
termux-setup-storage

echo -e "${YELLOW}[4/6] Устанавливаю Termux:API...${NC}"
pkg install -y termux-api

echo -e "${YELLOW}[5/6] Устанавливаю Claude Code...${NC}"
npm install -g @anthropic-ai/claude-code

echo -e "${YELLOW}[6/6] Проверяю установку...${NC}"
echo ""

NODE_VER=$(node --version 2>/dev/null || echo "не найден")
NPM_VER=$(npm --version 2>/dev/null || echo "не найден")
CLAUDE_VER=$(claude --version 2>/dev/null || echo "не найден")

echo -e "  Node.js:     ${GREEN}${NODE_VER}${NC}"
echo -e "  npm:         ${GREEN}${NPM_VER}${NC}"
echo -e "  Claude Code: ${GREEN}${CLAUDE_VER}${NC}"
echo ""

if command -v claude &> /dev/null; then
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  Готово! Claude Code установлен!     ${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo "Для начала работы:"
    echo ""
    echo "  1. Введите:  claude"
    echo "  2. При первом запуске введите API-ключ"
    echo "     (получить на console.anthropic.com)"
    echo ""
    echo "Полезные команды:"
    echo "  claude          — запустить Claude Code"
    echo "  cd ~/storage    — перейти к файлам телефона"
    echo ""
else
    echo -e "${RED}Ошибка: Claude Code не установился.${NC}"
    echo "Попробуйте вручную: npm install -g @anthropic-ai/claude-code"
    exit 1
fi
