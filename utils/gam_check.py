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


def check_gam_auth():
    """
    Check if GAM is properly authenticated by running a simple domain info command.

    Returns:
        tuple: (success: bool, error_message: str or None)
            - (True, None) if GAM is authenticated
            - (False, error_message) if GAM is not authenticated or command fails
    """
    # Find GAM executable
    gam_cmd = find_gam_executable()

    if not gam_cmd:
        return (False, "GAM is not installed or not found in PATH.")

    try:
        # Run a simple GAM command that requires authentication
        result = subprocess.run(
            [gam_cmd, 'info', 'domain'],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Check if command was successful
        if result.returncode != 0:
            # Check for common authentication error messages
            output = result.stdout + result.stderr
            if 'oauth' in output.lower() or 'authentication' in output.lower() or 'credentials' in output.lower():
                return (False, "GAM is not authenticated. Please run 'gam oauth create' or visit: https://github.com/GAM-team/GAM/wiki/Authorization")
            else:
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
