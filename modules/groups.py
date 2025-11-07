"""
Group Management Module for GAM Admin Tool.

This module provides backend functions for executing GAM commands
related to group management including creating, deleting, managing members,
group settings, and aliases.
"""

import subprocess
from modules.base_operations import (
    get_gam_command,
    execute_gam_command,
    validate_email,
    get_user_friendly_error
)
from utils.logger import log_error


def create_group(groups_data, dry_run=False):
    """
    Create new groups.

    Args:
        groups_data (list): List of dicts with keys:
                           - email (required)
                           - name (required)
                           - description (optional)
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(groups_data)
    success_count = 0
    failure_count = 0
    errors = []

    for i, group_data in enumerate(groups_data, start=1):
        email = group_data.get('email', '').strip()
        name = group_data.get('name', '').strip()
        description = group_data.get('description', '').strip()

        yield {
            'status': 'processing',
            'email': email,
            'current': i,
            'total': total,
            'message': f"Creating group {email}..."
        }

        # Validation
        if not email or not validate_email(email):
            failure_count += 1
            errors.append((email, "Invalid email address"))
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Invalid email: {email}"
            }
            continue

        if not name:
            failure_count += 1
            errors.append((email, "Missing group name"))
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Missing name for {email}"
            }
            continue

        try:
            cmd = [get_gam_command(), 'create', 'group', email, 'name', name]

            if description:
                cmd.extend(['description', description])

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': email,
                    'message': f"[DRY RUN] Would create group: {email}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': email,
                    'message': f"✓ Created group {email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((email, error_msg))
                log_error("Create Group", f"Failed for {email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': email,
                    'message': f"✗ Failed to create {email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((email, error_msg))
            log_error("Create Group", f"Exception for {email}: {error_msg}")
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Error creating {email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def delete_group(groups, dry_run=False):
    """
    Delete groups.

    Args:
        groups (list): List of group emails to delete
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(groups)
    success_count = 0
    failure_count = 0
    errors = []

    for i, group_email in enumerate(groups, start=1):
        yield {
            'status': 'processing',
            'email': group_email,
            'current': i,
            'total': total,
            'message': f"Deleting group {group_email}..."
        }

        try:
            cmd = [get_gam_command(), 'delete', 'group', group_email]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': group_email,
                    'message': f"[DRY RUN] Would delete group: {group_email}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': group_email,
                    'message': f"✓ Deleted group {group_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((group_email, error_msg))
                log_error("Delete Group", f"Failed for {group_email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': group_email,
                    'message': f"✗ Failed to delete {group_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((group_email, error_msg))
            log_error("Delete Group", f"Exception for {group_email}: {error_msg}")
            yield {
                'status': 'error',
                'email': group_email,
                'message': f"✗ Error deleting {group_email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def add_members(membership_data, dry_run=False):
    """
    Add members to groups.

    Args:
        membership_data (list): List of dicts with keys:
                               - group (required)
                               - member (required)
                               - role (optional: MEMBER, MANAGER, OWNER - default: MEMBER)
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(membership_data)
    success_count = 0
    failure_count = 0
    errors = []

    for i, data in enumerate(membership_data, start=1):
        group = data.get('group', '').strip()
        member = data.get('member', '').strip()
        role = data.get('role', 'MEMBER').strip().upper()

        yield {
            'status': 'processing',
            'email': f"{member} to {group}",
            'current': i,
            'total': total,
            'message': f"Adding {member} to {group} as {role}..."
        }

        # Validation
        if role not in ['MEMBER', 'MANAGER', 'OWNER']:
            role = 'MEMBER'

        try:
            # GAM command varies by role
            if role == 'MEMBER':
                cmd = [get_gam_command(), 'update', 'group', group, 'add', 'member', 'user', member]
            elif role == 'MANAGER':
                cmd = [get_gam_command(), 'update', 'group', group, 'add', 'manager', 'user', member]
            else:  # OWNER
                cmd = [get_gam_command(), 'update', 'group', group, 'add', 'owner', 'user', member]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': f"{member} to {group}",
                    'message': f"[DRY RUN] Would add {member} to {group} as {role}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': f"{member} to {group}",
                    'message': f"✓ Added {member} to {group} as {role}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((f"{member} to {group}", error_msg))
                log_error("Add Member", f"Failed for {member} to {group}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': f"{member} to {group}",
                    'message': f"✗ Failed to add {member} to {group}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((f"{member} to {group}", error_msg))
            log_error("Add Member", f"Exception for {member} to {group}: {error_msg}")
            yield {
                'status': 'error',
                'email': f"{member} to {group}",
                'message': f"✗ Error adding {member} to {group}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def remove_members(membership_data, dry_run=False):
    """
    Remove members from groups.

    Args:
        membership_data (list): List of dicts with keys:
                               - group (required)
                               - member (required)
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(membership_data)
    success_count = 0
    failure_count = 0
    errors = []

    for i, data in enumerate(membership_data, start=1):
        group = data.get('group', '').strip()
        member = data.get('member', '').strip()

        yield {
            'status': 'processing',
            'email': f"{member} from {group}",
            'current': i,
            'total': total,
            'message': f"Removing {member} from {group}..."
        }

        try:
            cmd = [get_gam_command(), 'update', 'group', group, 'remove', 'member', 'user', member]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': f"{member} from {group}",
                    'message': f"[DRY RUN] Would remove {member} from {group}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': f"{member} from {group}",
                    'message': f"✓ Removed {member} from {group}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((f"{member} from {group}", error_msg))
                log_error("Remove Member", f"Failed for {member} from {group}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': f"{member} from {group}",
                    'message': f"✗ Failed to remove {member} from {group}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((f"{member} from {group}", error_msg))
            log_error("Remove Member", f"Exception for {member} from {group}: {error_msg}")
            yield {
                'status': 'error',
                'email': f"{member} from {group}",
                'message': f"✗ Error removing {member} from {group}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def list_members(group_email):
    """
    List all members of a group.

    Args:
        group_email (str): Group email address

    Returns:
        tuple: (success: bool, members: list or error_message: str)
    """
    try:
        cmd = [get_gam_command(), 'print', 'group-members', 'group', group_email]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            members = []
            lines = result.stdout.strip().split('\n')

            if not lines or len(lines) < 2:
                return (True, [])  # No members

            # Parse CSV output using DictReader for reliability
            import csv
            from io import StringIO

            reader = csv.DictReader(StringIO(result.stdout))
            for row in reader:
                # GAM output typically has: group, email, role, type, status
                # The member email can be in 'email' or 'member' column
                member_email = row.get('email', row.get('member', '')).strip()
                role = row.get('role', 'MEMBER').strip().upper()

                if member_email and member_email != group_email:
                    members.append({
                        'email': member_email,
                        'role': role
                    })

            return (True, members)
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            log_error("List Members", f"Failed for {group_email}: {error_msg}")
            return (False, error_msg)

    except Exception as e:
        error_msg = str(e)
        log_error("List Members", f"Exception for {group_email}: {error_msg}")
        return (False, error_msg)


def update_group_settings(settings_data, dry_run=False):
    """
    Update group settings.

    Args:
        settings_data (list): List of dicts with keys:
                             - group (required)
                             - whoCanPostMessage (optional)
                             - whoCanViewGroup (optional)
                             - whoCanJoin (optional)
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(settings_data)
    success_count = 0
    failure_count = 0
    errors = []

    for i, data in enumerate(settings_data, start=1):
        group = data.get('group', '').strip()

        yield {
            'status': 'processing',
            'email': group,
            'current': i,
            'total': total,
            'message': f"Updating settings for {group}..."
        }

        try:
            cmd = [get_gam_command(), 'update', 'group', group]
            settings_added = False

            # Add settings if provided
            if 'whoCanPostMessage' in data and data['whoCanPostMessage']:
                cmd.extend(['who_can_post_message', data['whoCanPostMessage']])
                settings_added = True
            if 'whoCanViewGroup' in data and data['whoCanViewGroup']:
                cmd.extend(['who_can_view_group', data['whoCanViewGroup']])
                settings_added = True
            if 'whoCanJoin' in data and data['whoCanJoin']:
                cmd.extend(['who_can_join', data['whoCanJoin']])
                settings_added = True

            if not settings_added:
                failure_count += 1
                errors.append((group, "No settings to update"))
                yield {
                    'status': 'error',
                    'email': group,
                    'message': f"✗ No settings provided for {group}"
                }
                continue

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': group,
                    'message': f"[DRY RUN] Would update settings for: {group}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': group,
                    'message': f"✓ Updated settings for {group}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((group, error_msg))
                log_error("Update Settings", f"Failed for {group}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': group,
                    'message': f"✗ Failed to update {group}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((group, error_msg))
            log_error("Update Settings", f"Exception for {group}: {error_msg}")
            yield {
                'status': 'error',
                'email': group,
                'message': f"✗ Error updating {group}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def get_group_info(group_email):
    """
    Get detailed information about a group.

    Args:
        group_email (str): Group email address

    Returns:
        tuple: (success: bool, data: dict or error_message: str)
    """
    try:
        cmd = [get_gam_command(), 'info', 'group', group_email]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            group_info = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    group_info[key.strip()] = value.strip()

            return (True, group_info)
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            log_error("Get Group Info", f"Failed for {group_email}: {error_msg}")
            return (False, error_msg)

    except Exception as e:
        error_msg = str(e)
        log_error("Get Group Info", f"Exception for {group_email}: {error_msg}")
        return (False, error_msg)


def list_user_groups(user_email):
    """
    List all groups a user belongs to.

    Args:
        user_email (str): User email address

    Returns:
        tuple: (success: bool, groups: list or error_message: str)
    """
    try:
        cmd = [get_gam_command(), 'user', user_email, 'print', 'groups']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            groups = []
            lines = result.stdout.strip().split('\n')

            if not lines or len(lines) < 2:
                return (True, [])  # No groups

            # Parse CSV output using DictReader for reliability
            import csv
            from io import StringIO

            reader = csv.DictReader(StringIO(result.stdout))
            for row in reader:
                # GAM output typically has: user, group, role, type, status
                # The group email can be in 'group' or 'email' column
                group_email = row.get('group', row.get('email', '')).strip()

                if group_email and group_email != user_email:
                    groups.append(group_email)

            return (True, groups)
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            log_error("List User Groups", f"Failed for {user_email}: {error_msg}")
            return (False, error_msg)

    except Exception as e:
        error_msg = str(e)
        log_error("List User Groups", f"Exception for {user_email}: {error_msg}")
        return (False, error_msg)


def add_group_alias(alias_data, dry_run=False):
    """
    Add aliases to groups.

    Args:
        alias_data (list): List of dicts with keys:
                          - group (required)
                          - alias (required)
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(alias_data)
    success_count = 0
    failure_count = 0
    errors = []

    for i, data in enumerate(alias_data, start=1):
        group = data.get('group', '').strip()
        alias = data.get('alias', '').strip()

        yield {
            'status': 'processing',
            'email': f"{alias} to {group}",
            'current': i,
            'total': total,
            'message': f"Adding alias {alias} to {group}..."
        }

        if not alias or not validate_email(alias):
            failure_count += 1
            errors.append((group, "Invalid alias email"))
            yield {
                'status': 'error',
                'email': group,
                'message': f"✗ Invalid alias for {group}"
            }
            continue

        try:
            cmd = [get_gam_command(), 'create', 'alias', alias, 'group', group]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': f"{alias} to {group}",
                    'message': f"[DRY RUN] Would add alias {alias} to: {group}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': f"{alias} to {group}",
                    'message': f"✓ Added alias {alias} to {group}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((group, error_msg))
                log_error("Add Group Alias", f"Failed for {group}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': group,
                    'message': f"✗ Failed to add alias to {group}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((group, error_msg))
            log_error("Add Group Alias", f"Exception for {group}: {error_msg}")
            yield {
                'status': 'error',
                'email': group,
                'message': f"✗ Error adding alias to {group}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def remove_group_alias(aliases, dry_run=False):
    """
    Remove group aliases.

    Args:
        aliases (list): List of alias emails to remove
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(aliases)
    success_count = 0
    failure_count = 0
    errors = []

    for i, alias in enumerate(aliases, start=1):
        alias = alias.strip()

        yield {
            'status': 'processing',
            'email': alias,
            'current': i,
            'total': total,
            'message': f"Removing alias {alias}..."
        }

        try:
            cmd = [get_gam_command(), 'delete', 'alias', alias]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': alias,
                    'message': f"[DRY RUN] Would remove alias: {alias}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': alias,
                    'message': f"✓ Removed alias {alias}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((alias, error_msg))
                log_error("Remove Group Alias", f"Failed for {alias}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': alias,
                    'message': f"✗ Failed to remove {alias}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((alias, error_msg))
            log_error("Remove Group Alias", f"Exception for {alias}: {error_msg}")
            yield {
                'status': 'error',
                'email': alias,
                'message': f"✗ Error removing {alias}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }
