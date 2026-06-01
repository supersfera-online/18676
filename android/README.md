# Claude Code Installer (Android APK)

A tiny Android app that turns installing Claude Code on the phone into **one
tap**. The app icon → tap **Install / Launch** → Termux runs the project
bootstrap (clone → setup → Claude Code) and starts it.

It is a thin wrapper around [`scripts/bootstrap.sh`](../scripts/bootstrap.sh):
the app sends that one-liner to Termux via the `RUN_COMMAND` service, and also
copies it to the clipboard as a fallback.

## Get the APK

The APK is built in CI on every change under `android/`. Download it from the
**Android APK** workflow run → *Artifacts* → `claude-code-installer-debug`
(this is a debug-signed APK; enable "install from unknown sources" to install).

## Requirements / honest caveats

- **Termux must be installed** (from F-Droid, not Google Play). If it isn't, the
  app sends you to the F-Droid page. Bundling Termux itself would be a far larger
  project and a licensing question, so this app drives the official Termux.
- **Auto-run needs one Termux setting.** Termux only honours `RUN_COMMAND` when
  `allow-external-apps=true` is set in `~/.termux/termux.properties`. If it
  isn't, the app falls back to opening Termux with the command already on your
  clipboard — paste and run. After that first install, add the **Termux:Widget**
  shortcut the bootstrap creates for true one-tap launches.
- **Two taps remain unavoidable** (Android, not us): the storage-permission
  popup, and pasting your Anthropic API key on first `claude` launch.

## Status

Built and packaged by CI; **not yet verified on a physical device** (no Android
hardware available in the build environment). The Gradle build producing a valid
APK is the current proof point — on-device verification is the open item.
