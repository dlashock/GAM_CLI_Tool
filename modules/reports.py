"""
Reports module for GAM Admin Tool.

Provides backend functions for Google Workspace audit and usage reports:
- Admin audit activity reports
- Email usage reports (per-user)
"""

import subprocess
from modules.base_operations import get_gam_command, execute_gam_command
from utils.logger import log_error, log_info


# Valid GAM admin audit event names.
# These correspond to the Google Workspace Admin SDK activityName values
# for the 'admin' application.  Passing any other string (e.g. "USER_SETTINGS")
# causes GAM to return "Event X not found in manifest" (issue #42).
ADMIN_EVENT_TYPES = [
    "All Events",
    "CHANGE_APPLICATION_SETTING",
    "CREATE_USER",
    "DELETE_USER",
    "CHANGE_PASSWORD",
    "RENAME_USER",
    "SUSPEND_USER",
    "UNSUSPEND_USER",
    "CREATE_GROUP",
    "DELETE_GROUP",
    "ADD_TO_GROUP",
    "REMOVE_FROM_GROUP",
    "CHANGE_GROUP_SETTING",
    "CREATE_ORG",
    "DELETE_ORG",
    "MOVE_ORG_USER",
    "CREATE_ALIAS",
    "DELETE_ALIAS",
    "REVOKE_ASP",
    "GENERATE_ASP",
    "TOGGLE_SERVICE_ENABLED",
    "CHANGE_DEVICE_POLICY",
]


def fetch_admin_audit(start_date=None, end_date=None, event_type=None):
    """
    Fetch admin audit activity report.

    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
        event_type (str, optional): GAM admin event name, e.g. "CREATE_USER".
            Pass None or "All Events" to return all event types.

    Returns:
        dict: {"output": str, "error": str, "success": bool}
    """
    gam_cmd = get_gam_command()
    cmd = [gam_cmd, 'report', 'admin']

    # Only add eventname when a specific type is requested — "All Events"
    # (or None) means we omit the flag, which returns everything.
    if event_type and event_type != "All Events":
        cmd += ['eventname', event_type]

    if start_date:
        cmd += ['starttime', start_date]
    if end_date:
        cmd += ['endtime', end_date]

    log_info("Admin Audit", f"Running: {' '.join(cmd)}")

    try:
        result = execute_gam_command(cmd, timeout=120, operation_name="Admin Audit")
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            log_error("Admin Audit", f"Command failed: {error_msg}")
            return {"output": result.stdout, "error": error_msg, "success": False}
        return {"output": result.stdout, "error": result.stderr, "success": True}
    except Exception as e:
        log_error("Admin Audit", f"Exception: {str(e)}")
        return {"output": "", "error": str(e), "success": False}


def fetch_email_usage(user_email, date=None, parameters=None):
    """
    Fetch email usage statistics for a specific user.

    The correct GAM syntax is:
        gam report usage user <email> [parameters <params>] [date <YYYY-MM-DD>]

    NOT "gam user <email> report usage ..." (issue #43).

    Args:
        user_email (str): User's email address
        date (str, optional): Date in YYYY-MM-DD format (most recent available
            if omitted)
        parameters (str, optional): Comma-separated gmail parameters, e.g.
            "gmail:num_emails_sent,gmail:num_emails_received"

    Returns:
        dict: {"output": str, "error": str, "success": bool}
    """
    gam_cmd = get_gam_command()
    cmd = [gam_cmd, 'report', 'usage', 'user', user_email]

    if parameters:
        cmd += ['parameters', parameters]
    if date:
        cmd += ['date', date]

    log_info("Email Usage", f"Running: {' '.join(cmd)}")

    try:
        result = execute_gam_command(cmd, timeout=120, operation_name="Email Usage")
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            log_error("Email Usage", f"Command failed: {error_msg}")
            return {"output": result.stdout, "error": error_msg, "success": False}
        return {"output": result.stdout, "error": result.stderr, "success": True}
    except Exception as e:
        log_error("Email Usage", f"Exception: {str(e)}")
        return {"output": "", "error": str(e), "success": False}
