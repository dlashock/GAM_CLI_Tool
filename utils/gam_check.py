"""
GAM version and authentication verification module.

This module checks if GAM7 is installed and properly authenticated
before allowing the application to proceed.
"""

import subprocess
import re


def check_gam_version():
    """
    Check if GAM7 is installed and accessible.

    Returns:
        tuple: (success: bool, error_message: str or None)
            - (True, None) if GAM7 is detected
            - (False, error_message) if GAM7 is not detected or command fails
    """
    try:
        # Run gam version command
        result = subprocess.run(
            ['gam', 'version'],
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
    try:
        # Run a simple GAM command that requires authentication
        result = subprocess.run(
            ['gam', 'info', 'domain'],
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
