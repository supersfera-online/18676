#!/data/data/com.termux/files/usr/bin/bash
#
# One-command bootstrap for Claude Code on a phone (Termux, tuned for the
# Samsung Galaxy S22+). Paste this single line into Termux:
#
#   pkg install -y curl && curl -fsSL \
#     https://raw.githubusercontent.com/supersfera-online/18676/main/scripts/bootstrap.sh | bash
#
# It clones (or updates) the repo, runs the full setup, and installs a
# Termux:Widget shortcut so every later launch is a single tap from the home
# screen. Safe to re-run: every step is idempotent.

set -euo pipefail

REPO_URL="https://github.com/supersfera-online/18676.git"
INSTALL_DIR="$HOME/18676"
RAW_BOOTSTRAP="https://raw.githubusercontent.com/supersfera-online/18676/main/scripts/bootstrap.sh"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Claude Code — one-tap bootstrap ===${NC}"

# 1. Make sure git is available, then clone or fast-forward the repo.
echo -e "${YELLOW}[1/3] Fetching the project...${NC}"
pkg install -y git
if [ -d "$INSTALL_DIR/.git" ]; then
    git -C "$INSTALL_DIR" pull --ff-only
else
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# 2. Run the main installer (toolchain, Termux:API, Claude Code).
echo -e "${YELLOW}[2/3] Running setup...${NC}"
bash "$INSTALL_DIR/scripts/setup-termux.sh"

# 3. Install Termux:Widget shortcuts for true one-tap use afterwards.
echo -e "${YELLOW}[3/3] Installing home-screen shortcuts...${NC}"
shortcuts_dir="$HOME/.shortcuts"
mkdir -p "$shortcuts_dir"

launch_shortcut="$shortcuts_dir/Claude Code"
cat > "$launch_shortcut" <<'LAUNCH'
#!/data/data/com.termux/files/usr/bin/bash
exec claude
LAUNCH
chmod +x "$launch_shortcut"

update_shortcut="$shortcuts_dir/Update Claude Code"
cat > "$update_shortcut" <<UPDATE
#!/data/data/com.termux/files/usr/bin/bash
pkg install -y curl && curl -fsSL "$RAW_BOOTSTRAP" | bash
UPDATE
chmod +x "$update_shortcut"

echo ""
echo -e "${GREEN}=== All set! ===${NC}"
echo "Add the 'Termux:Widget' app's widget to your home screen, then tap"
echo "'Claude Code' to launch — or 'Update Claude Code' to re-run this."
echo "Install Termux:Widget from F-Droid if you don't have it yet."
