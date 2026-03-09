"""
GAM version and authentication verification module.

This module checks if GAM7 is installed and properly authenticated
before allowing the application to proceed.

Enhanced to search common GAM installation locations if not in PATH.
"""

import subprocess
import re
import os
import sys
import time


# Cache for GAM executable path
_gam_path = None


def find_gam_executable():
    """
    Find the GAM executable in PATH or common installation locations.

    Returns:
        str or None: Path to GAM executable, or None if not found
    """
    global _gam_path

    # Return cached path if available
    if _gam_path:
        return _gam_path

    # First, try 'gam' in PATH
    try:
        result = subprocess.run(
            ['which', 'gam'] if sys.platform != 'win32' else ['where', 'gam'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            _gam_path = 'gam'  # Use 'gam' command directly
            return _gam_path
    except:
        pass

    # Common GAM installation locations
    common_locations = [
        # Mac/Linux locations
        os.path.expanduser('~/bin/gam7/gam'),
        os.path.expanduser('~/bin/gam'),
        '/usr/local/bin/gam',
        '/usr/bin/gam',
        os.path.expanduser('~/.local/bin/gam'),
        # Windows locations
        os.path.expanduser('~/bin/gam7/gam.exe'),
        'C:\\GAM\\gam.exe',
        'C:\\Program Files\\GAM\\gam.exe',
        'C:\\Program Files (x86)\\GAM\\gam.exe',
    ]

    # Search common locations
    for location in common_locations:
        if os.path.isfile(location) and os.access(location, os.X_OK):
            _gam_path = location
            return _gam_path

    return None


def check_gam_version():
    """
    Check if GAM7 is installed and accessible.

    Returns:
        tuple: (success: bool, error_message: str or None)
            - (True, None) if GAM7 is detected
            - (False, error_message) if GAM7 is not detected or command fails
    """
    # Find GAM executable
    gam_cmd = find_gam_executable()

    if not gam_cmd:
        return (False,
                "GAM is not installed or not found in PATH.\n\n"
                "Please install GAM7 from: https://github.com/GAM-team/GAM\n\n"
                "Or add GAM to your PATH:\n"
                "  Mac/Linux: Add 'export PATH=\"$HOME/bin/gam7:$PATH\"' to ~/.zshrc or ~/.bash_profile\n"
                "  Windows: Add GAM directory to system PATH environment variable")

    try:
        # Run gam version command
        result = subprocess.run(
            [gam_cmd, 'version'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Check if command was successful
        if result.returncode != 0:
            return (False, "GAM command failed. Please ensure GAM is installed and in your PATH.")

        # Get the output (could be in stdout or stderr)
        output = result.stdout + result.stderr

        # Check for GAM7 or version 7.x
        # GAM7 typically shows "GAM 7.x.x" in the version output
        if re.search(r'GAM\s+7\.\d+', output, re.IGNORECASE) or 'GAM7' in output:
            return (True, None)
        else:
            return (False, "Please upgrade to GAM7. Visit: https://github.com/GAM-team/GAM")

    except FileNotFoundError:
        return (False, "GAM is not installed or not found in PATH. Please install GAM7 from: https://github.com/GAM-team/GAM")
    except subprocess.TimeoutExpired:
        return (False, "GAM version check timed out. Please check your GAM installation.")
    except Exception as e:
        return (False, f"Error checking GAM version: {str(e)}")


def _parse_clock_skew(output):
    """
    Parse clock skew seconds from a 'Token used too early' GAM error.

    The error looks like:
        ERROR: Token used too early, 1773064624 < 1773064637.

    Returns the number of seconds to wait (int), or None if not a clock skew error.
    """
    match = re.search(r'token used too early[^,]*,\s*(\d+)\s*<\s*(\d+)', output, re.IGNORECASE)
    if match:
        current_ts = int(match.group(1))
        nbf_ts = int(match.group(2))
        skew = nbf_ts - current_ts
        return max(skew, 1)  # wait at least 1 second
    return None


def check_gam_auth():
    """
    Check if GAM is properly authenticated by running a simple domain info command.

    Automatically retries once when a small clock skew error is detected
    (e.g. "Token used too early") by waiting out the reported skew duration.

    Returns:
        tuple: (success: bool, error_message: str or None)
            - (True, None) if GAM is authenticated
            - (False, error_message) if GAM is not authenticated or command fails
    """
    # Find GAM executable
    gam_cmd = find_gam_executable()

    if not gam_cmd:
        return (False, "GAM is not installed or not found in PATH.")

    def _run_auth_check():
        return subprocess.run(
            [gam_cmd, 'info', 'domain'],
            capture_output=True,
            text=True,
            timeout=30
        )

    try:
        result = _run_auth_check()

        # Check if command was successful
        if result.returncode != 0:
            output = result.stdout + result.stderr

            # Detect clock skew ("Token used too early") and retry automatically
            skew_seconds = _parse_clock_skew(output)
            if skew_seconds is not None:
                # Cap the wait to avoid hanging indefinitely (max 60 s)
                wait = min(skew_seconds + 1, 60)
                time.sleep(wait)
                result = _run_auth_check()
                if result.returncode == 0:
                    return (True, None)
                # Retry also failed — fall through to error reporting below
                output = result.stdout + result.stderr
                if _parse_clock_skew(output) is not None:
                    return (
                        False,
                        f"GAM authentication check failed:\n"
                        f"ERROR: Please correct your system time.\n\n"
                        f"ERROR: Token used too early, clock skew of ~{skew_seconds}s detected.\n"
                        f"Check that your computer's clock is set correctly.\n\n"
                        f"If your clock is already synced, try running:\n"
                        f"  sudo ntpdate -u pool.ntp.org  (Linux/Mac)\n"
                        f"  w32tm /resync /force           (Windows)"
                    )

            # Check for common authentication error messages
            if 'oauth' in output.lower() or 'authentication' in output.lower() or 'credentials' in output.lower():
                return (False, "GAM is not authenticated. Please run 'gam oauth create' or visit: https://github.com/GAM-team/GAM/wiki/Authorization")

            return (False, f"GAM authentication check failed: {output[:200]}")

        # If we got here, the command succeeded
        return (True, None)

    except FileNotFoundError:
        return (False, "GAM is not installed or not found in PATH.")
    except subprocess.TimeoutExpired:
        return (False, "GAM authentication check timed out. Please check your network connection.")
    except Exception as e:
        return (False, f"Error checking GAM authentication: {str(e)}")


def verify_gam_setup():
    """
    Convenience function to check both version and authentication.

    Returns:
        tuple: (success: bool, error_message: str or None)
            Returns the first error encountered, or (True, None) if all checks pass.
    """
    # Check version first
    version_ok, version_error = check_gam_version()
    if not version_ok:
        return (False, version_error)

    # Then check authentication
    auth_ok, auth_error = check_gam_auth()
    if not auth_ok:
        return (False, auth_error)

    return (True, None)


def get_gam_path():
    """
    Get the path to the GAM executable.

    Returns:
        str or None: Path to GAM executable
    """
    return find_gam_executable()
