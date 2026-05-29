#!/data/data/com.termux/files/usr/bin/bash

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN} Claude Code — Install on phone       ${NC}"
echo -e "${GREEN} Samsung Galaxy S22+                  ${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

echo -e "${YELLOW}[1/6] Updating Termux packages...${NC}"
pkg update -y && pkg upgrade -y

echo -e "${YELLOW}[2/6] Installing Node.js, Git, Python...${NC}"
pkg install -y nodejs-lts git python

echo -e "${YELLOW}[3/6] Setting up access to phone storage...${NC}"
echo "Tap 'Allow' in the popup!"
termux-setup-storage

echo -e "${YELLOW}[4/6] Installing Termux:API...${NC}"
pkg install -y termux-api

echo -e "${YELLOW}[5/6] Installing Claude Code...${NC}"
npm install -g @anthropic-ai/claude-code

echo -e "${YELLOW}[6/6] Verifying installation...${NC}"
echo ""

NODE_VER=$(node --version 2>/dev/null || echo "not found")
NPM_VER=$(npm --version 2>/dev/null || echo "not found")
CLAUDE_VER=$(claude --version 2>/dev/null || echo "not found")

echo -e "  Node.js:     ${GREEN}${NODE_VER}${NC}"
echo -e "  npm:         ${GREEN}${NPM_VER}${NC}"
echo -e "  Claude Code: ${GREEN}${CLAUDE_VER}${NC}"
echo ""

if command -v claude &> /dev/null; then
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  Done! Claude Code installed!        ${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo "To get started:"
    echo ""
    echo "  1. Run:  claude"
    echo "  2. On first launch, enter your API key"
    echo "     (get it at console.anthropic.com)"
    echo ""
    echo "Useful commands:"
    echo "  claude          — run Claude Code"
    echo "  cd ~/storage    — go to phone files"
    echo ""
else
    echo -e "${RED}Error: Claude Code did not install.${NC}"
    echo "Try manually: npm install -g @anthropic-ai/claude-code"
    exit 1
fi
