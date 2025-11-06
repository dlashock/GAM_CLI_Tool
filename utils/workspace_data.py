"""
Workspace data fetching module.

Fetches and caches user and group information from Google Workspace
using GAM commands. Data is cached for the session to minimize API calls.
"""

import subprocess
import csv
from io import StringIO
from .logger import log_error


# Session cache for users and groups
_users_cache = None
_groups_cache = None


def fetch_users(force_refresh=False):
    """
    Fetch all users from Google Workspace.

    Args:
        force_refresh (bool): If True, bypass cache and fetch fresh data

    Returns:
        list: List of user email addresses, or empty list on error
    """
    global _users_cache

    # Return cached data if available and not forcing refresh
    if _users_cache is not None and not force_refresh:
        return _users_cache

    try:
        # Run GAM command to get all users
        # Using 'gam print users' which outputs CSV format
        result = subprocess.run(
            ['gam', 'print', 'users'],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            error_msg = f"GAM command failed: {result.stderr[:200]}"
            log_error("Fetch Users", error_msg)
            return []

        # Parse CSV output
        output = result.stdout
        if not output.strip():
            log_error("Fetch Users", "GAM returned empty output")
            return []

        # Parse CSV - GAM typically returns primaryEmail as one of the columns
        users = []
        csv_reader = csv.DictReader(StringIO(output))

        for row in csv_reader:
            # Try common field names for email
            email = row.get('primaryEmail') or row.get('email') or row.get('Email')
            if email:
                users.append(email.strip())

        # Cache the results
        _users_cache = users

        return users

    except subprocess.TimeoutExpired:
        log_error("Fetch Users", "Command timed out after 60 seconds")
        return []
    except FileNotFoundError:
        log_error("Fetch Users", "GAM command not found")
        return []
    except Exception as e:
        log_error("Fetch Users", f"Unexpected error: {str(e)}")
        return []


def fetch_groups(force_refresh=False):
    """
    Fetch all groups from Google Workspace.

    Args:
        force_refresh (bool): If True, bypass cache and fetch fresh data

    Returns:
        list: List of group email addresses, or empty list on error
    """
    global _groups_cache

    # Return cached data if available and not forcing refresh
    if _groups_cache is not None and not force_refresh:
        return _groups_cache

    try:
        # Run GAM command to get all groups
        # Using 'gam print groups' which outputs CSV format
        result = subprocess.run(
            ['gam', 'print', 'groups'],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            error_msg = f"GAM command failed: {result.stderr[:200]}"
            log_error("Fetch Groups", error_msg)
            return []

        # Parse CSV output
        output = result.stdout
        if not output.strip():
            log_error("Fetch Groups", "GAM returned empty output")
            return []

        # Parse CSV - GAM typically returns email as one of the columns
        groups = []
        csv_reader = csv.DictReader(StringIO(output))

        for row in csv_reader:
            # Try common field names for email
            email = row.get('email') or row.get('Email') or row.get('id')
            if email:
                groups.append(email.strip())

        # Cache the results
        _groups_cache = groups

        return groups

    except subprocess.TimeoutExpired:
        log_error("Fetch Groups", "Command timed out after 60 seconds")
        return []
    except FileNotFoundError:
        log_error("Fetch Groups", "GAM command not found")
        return []
    except Exception as e:
        log_error("Fetch Groups", f"Unexpected error: {str(e)}")
        return []


def clear_cache():
    """
    Clear the cached user and group data.

    Use this if you need to force a refresh of workspace data.
    """
    global _users_cache, _groups_cache
    _users_cache = None
    _groups_cache = None


def get_cache_status():
    """
    Get information about what's currently cached.

    Returns:
        dict: Dictionary with cache status information
    """
    return {
        'users_cached': _users_cache is not None,
        'groups_cached': _groups_cache is not None,
        'users_count': len(_users_cache) if _users_cache else 0,
        'groups_count': len(_groups_cache) if _groups_cache else 0
    }


def fetch_group_members(group_email):
    """
    Fetch members of a specific group.

    Args:
        group_email (str): Email address of the group

    Returns:
        list: List of member email addresses, or empty list on error
    """
    try:
        # Run GAM command to get group members
        result = subprocess.run(
            ['gam', 'print', 'group-members', 'group', group_email],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            error_msg = f"GAM command failed for group {group_email}: {result.stderr[:200]}"
            log_error("Fetch Group Members", error_msg)
            return []

        # Parse CSV output
        output = result.stdout
        if not output.strip():
            return []

        # Parse CSV
        members = []
        csv_reader = csv.DictReader(StringIO(output))

        for row in csv_reader:
            # Try common field names for email
            email = row.get('email') or row.get('Email') or row.get('id')
            if email:
                members.append(email.strip())

        return members

    except subprocess.TimeoutExpired:
        log_error("Fetch Group Members", f"Command timed out for group {group_email}")
        return []
    except Exception as e:
        log_error("Fetch Group Members", f"Error fetching members for {group_email}: {str(e)}")
        return []
