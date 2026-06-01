package online.supersfera.claudephone

import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

/**
 * One-tap installer for Claude Code on the phone.
 *
 * Tapping "Install / Launch" asks Termux to run the project's bootstrap script
 * (clone → setup → Claude Code) via Termux's RUN_COMMAND service. The exact same
 * one-liner is also copied to the clipboard as a fallback, so if RUN_COMMAND is
 * blocked the user can paste it into Termux manually.
 */
class MainActivity : AppCompatActivity() {

    private companion object {
        const val TERMUX_PACKAGE = "com.termux"
        const val RUN_COMMAND_SERVICE = "com.termux.app.RunCommandService"
        const val ACTION_RUN_COMMAND = "com.termux.RUN_COMMAND"
        const val EXTRA_COMMAND_PATH = "com.termux.RUN_COMMAND_PATH"
        const val EXTRA_COMMAND_ARGS = "com.termux.RUN_COMMAND_ARGUMENTS"
        const val EXTRA_BACKGROUND = "com.termux.RUN_COMMAND_BACKGROUND"
        const val EXTRA_SESSION_ACTION = "com.termux.RUN_COMMAND_SESSION_ACTION"

        const val BOOTSTRAP_URL =
            "https://raw.githubusercontent.com/supersfera-online/18676/main/scripts/bootstrap.sh"
        val ONE_LINER =
            "pkg install -y curl && curl -fsSL $BOOTSTRAP_URL | bash"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<TextView>(R.id.command).text = ONE_LINER

        findViewById<Button>(R.id.install).setOnClickListener {
            if (!isTermuxInstalled()) {
                openTermuxOnFDroid()
                return@setOnClickListener
            }
            copyOneLinerToClipboard()
            runBootstrapInTermux()
        }

        findViewById<Button>(R.id.getTermux).setOnClickListener { openTermuxOnFDroid() }
    }

    private fun isTermuxInstalled(): Boolean =
        try {
            packageManager.getPackageInfo(TERMUX_PACKAGE, 0)
            true
        } catch (e: Exception) {
            false
        }

    private fun runBootstrapInTermux() {
        // Run: bash -lc "<one-liner>" inside Termux, foreground so the user sees it.
        val intent = Intent(ACTION_RUN_COMMAND).apply {
            setClassName(TERMUX_PACKAGE, RUN_COMMAND_SERVICE)
            putExtra(EXTRA_COMMAND_PATH, "/data/data/com.termux/files/usr/bin/bash")
            putExtra(EXTRA_COMMAND_ARGS, arrayOf("-lc", ONE_LINER))
            putExtra(EXTRA_BACKGROUND, false)
            putExtra(EXTRA_SESSION_ACTION, "0")
        }
        try {
            // minSdk is 31 (Galaxy S22+), so startForegroundService always exists;
            // ContextCompat is used purely as the idiomatic, future-proof call.
            ContextCompat.startForegroundService(this, intent)
            Toast.makeText(this, R.string.launched, Toast.LENGTH_LONG).show()
        } catch (e: Exception) {
            // RUN_COMMAND blocked (allow-external-apps not enabled) — fall back to
            // just opening Termux; the command is already on the clipboard.
            Toast.makeText(this, R.string.paste_fallback, Toast.LENGTH_LONG).show()
            launchTermux()
        }
    }

    private fun launchTermux() {
        val launch = packageManager.getLaunchIntentForPackage(TERMUX_PACKAGE)
        if (launch != null) {
            startActivity(launch)
        } else {
            openTermuxOnFDroid()
        }
    }

    private fun copyOneLinerToClipboard() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        clipboard.setPrimaryClip(ClipData.newPlainText("claude-phone-install", ONE_LINER))
    }

    private fun openTermuxOnFDroid() {
        val fdroid = Intent(
            Intent.ACTION_VIEW,
            Uri.parse("https://f-droid.org/packages/com.termux/"),
        )
        try {
            startActivity(fdroid)
        } catch (e: ActivityNotFoundException) {
            Toast.makeText(this, R.string.open_browser_failed, Toast.LENGTH_LONG).show()
        }
    }
}
