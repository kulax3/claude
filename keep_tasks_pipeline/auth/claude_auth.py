"""Claude API key resolution.

Priority order:
1. Environment variable ANTHROPIC_API_KEY
2. Claude CLI keychain (same detection as Siftly)
"""

import os
import subprocess


def get_claude_api_key() -> str:
    """Return Anthropic API key or raise if unavailable."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key

    # Try Claude CLI keychain (macOS / Linux)
    key = _read_from_cli_keychain()
    if key:
        return key

    raise EnvironmentError(
        "Anthropic API key not found.\n"
        "Set it with:  export ANTHROPIC_API_KEY=sk-ant-...\n"
        "Or install Claude CLI which stores the key automatically."
    )


def _read_from_cli_keychain() -> str:
    """Attempt to read API key stored by the Claude CLI."""
    # macOS Keychain
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "claude-code", "-w"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Linux secret-tool (libsecret)
    try:
        result = subprocess.run(
            ["secret-tool", "lookup", "service", "claude-code"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return ""
