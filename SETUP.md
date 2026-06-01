# Claude Code on Samsung Galaxy S22+

Step-by-step guide to installing Claude Code on a phone via Termux.

## Step 1: Install Termux

**Important:** Download Termux only from F-Droid, NOT from Google Play (the version there is outdated).

1. Open the browser on your phone
2. Go to https://f-droid.org/
3. Download and install F-Droid
4. In F-Droid, find and install **Termux**
5. Also install **Termux:API** (for access to phone settings) and
   **Termux:Widget** (for a one-tap home-screen launcher)

## Step 2: One-command install

Open Termux and paste this **single line**:

```bash
pkg install -y curl && curl -fsSL https://raw.githubusercontent.com/supersfera-online/18676/main/scripts/bootstrap.sh | bash
```

It clones the repo, runs the full setup (toolchain, Termux:API, Claude Code),
and installs two **Termux:Widget** shortcuts: **Claude Code** (launch) and
**Update Claude Code** (re-run the bootstrap). Two steps still need a finger:
tapping *Allow* on the storage-permission popup, and pasting your API key on
first launch.

### One-tap launch afterwards

1. Long-press your home screen → **Widgets** → add the **Termux:Widget**.
2. Tap **Claude Code** to launch — or **Update Claude Code** to re-install/update.

### Manual install (if you prefer)

```bash
pkg install -y git
git clone https://github.com/supersfera-online/18676.git
cd 18676
bash scripts/setup-termux.sh
```

Or fully manually, without the repo:

```bash
pkg update -y && pkg upgrade -y
pkg install -y nodejs-lts git python termux-api
npm install -g @anthropic-ai/claude-code
termux-setup-storage
```

## Step 3: Get an API key

1. Go to https://console.anthropic.com/
2. Sign up / log in
3. Go to the API Keys section
4. Create a new key
5. Copy it

## Step 4: Run Claude Code

```bash
claude
```

On first launch, enter the API key from Step 3.

## What Claude Code can do on a phone

After installation, Claude Code works on a phone the same way as on a computer:

- Read and edit files
- Run commands in the terminal
- Work with Git
- Write and run scripts

### Access to phone files

```bash
# Photos
ls ~/storage/dcim/

# Downloads
ls ~/storage/downloads/

# Documents
ls ~/storage/documents/
```

### Phone information (requires Termux:API)

```bash
# Battery level
termux-battery-status

# Wi-Fi info
termux-wifi-connectioninfo

# Volume
termux-volume

# Torch
termux-torch on
termux-torch off
```

## Troubleshooting

### "Permission denied"
```bash
termux-setup-storage
```
Tap "Allow" in the popup.

### "npm: command not found"
```bash
pkg install -y nodejs-lts
```

### Claude Code does not start
```bash
npm install -g @anthropic-ai/claude-code
```

### Low on space
```bash
# Check free space
df -h
# Clear the npm cache
npm cache clean --force
```

## Tips

- Use an **external Bluetooth keyboard** for comfortable typing
- Install **Termux:Widget** to launch Claude Code with a single button from the home screen
- The `termux-reload-settings` command applies Termux settings changes
