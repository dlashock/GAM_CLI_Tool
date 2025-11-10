"""
User Management Module for GAM Admin Tool.

This module provides backend functions for executing GAM commands
related to user management including creating, deleting, suspending,
updating user information, managing aliases, and organizational units.
"""

import subprocess
from modules.base_operations import (
    get_gam_command,
    execute_gam_command,
    build_gam_command,
    validate_email,
    get_user_friendly_error
)
from utils.logger import log_error


def create_user(users_data, dry_run=False):
    """
    Create new user accounts.

    Args:
        users_data (list): List of dicts with keys:
                          - email (required)
                          - firstName (required)
                          - lastName (required)
                          - password (required)
                          - orgUnit (optional, default: /)
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users_data)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_data in enumerate(users_data, start=1):
        email = user_data.get('email', '').strip()
        first_name = user_data.get('firstName', '').strip()
        last_name = user_data.get('lastName', '').strip()
        password = user_data.get('password', '').strip()
        org_unit = user_data.get('orgUnit', '/').strip()

        yield {
            'status': 'processing',
            'email': email,
            'current': i,
            'total': total,
            'message': f"Creating user {email}..."
        }

        # Validation
        if not email or not validate_email(email):
            failure_count += 1
            errors.append((email, "Invalid email address"))
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Invalid email address: {email}"
            }
            continue

        if not first_name or not last_name:
            failure_count += 1
            errors.append((email, "Missing first or last name"))
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Missing name for {email}"
            }
            continue

        if not password:
            failure_count += 1
            errors.append((email, "Missing password"))
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Missing password for {email}"
            }
            continue

        try:
            # Build command
            cmd = [
                get_gam_command(), 'create', 'user', email,
                'firstname', first_name,
                'lastname', last_name,
                'password', password,
                'ou', org_unit
            ]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': email,
                    'message': f"[DRY RUN] Would create user: {email}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': email,
                    'message': f"✓ Created user {email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((email, error_msg))
                log_error("Create User", f"Failed for {email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': email,
                    'message': f"✗ Failed to create {email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((email, error_msg))
            log_error("Create User", f"Exception for {email}: {error_msg}")
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


def delete_user(users, dry_run=False):
    """
    Delete user accounts.

    WARNING: This permanently deletes users. Use with caution.

    Args:
        users (list): List of user emails to delete
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_email in enumerate(users, start=1):
        yield {
            'status': 'processing',
            'email': user_email,
            'current': i,
            'total': total,
            'message': f"Deleting user {user_email}..."
        }

        try:
            cmd = [get_gam_command(), 'delete', 'user', user_email]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': user_email,
                    'message': f"[DRY RUN] Would delete user: {user_email}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': user_email,
                    'message': f"✓ Deleted user {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Delete User", f"Failed for {user_email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': user_email,
                    'message': f"✗ Failed to delete {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Delete User", f"Exception for {user_email}: {error_msg}")
            yield {
                'status': 'error',
                'email': user_email,
                'message': f"✗ Error deleting {user_email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def suspend_user(users, dry_run=False):
    """
    Suspend user accounts.

    Args:
        users (list): List of user emails to suspend
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_email in enumerate(users, start=1):
        yield {
            'status': 'processing',
            'email': user_email,
            'current': i,
            'total': total,
            'message': f"Suspending user {user_email}..."
        }

        try:
            cmd = [get_gam_command(), 'update', 'user', user_email, 'suspended', 'on']

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': user_email,
                    'message': f"[DRY RUN] Would suspend user: {user_email}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': user_email,
                    'message': f"✓ Suspended user {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Suspend User", f"Failed for {user_email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': user_email,
                    'message': f"✗ Failed to suspend {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Suspend User", f"Exception for {user_email}: {error_msg}")
            yield {
                'status': 'error',
                'email': user_email,
                'message': f"✗ Error suspending {user_email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def restore_user(users, dry_run=False):
    """
    Restore (unsuspend) user accounts.

    Args:
        users (list): List of user emails to restore
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_email in enumerate(users, start=1):
        yield {
            'status': 'processing',
            'email': user_email,
            'current': i,
            'total': total,
            'message': f"Restoring user {user_email}..."
        }

        try:
            cmd = [get_gam_command(), 'update', 'user', user_email, 'suspended', 'off']

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': user_email,
                    'message': f"[DRY RUN] Would restore user: {user_email}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': user_email,
                    'message': f"✓ Restored user {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Restore User", f"Failed for {user_email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': user_email,
                    'message': f"✗ Failed to restore {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Restore User", f"Exception for {user_email}: {error_msg}")
            yield {
                'status': 'error',
                'email': user_email,
                'message': f"✗ Error restoring {user_email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def reset_password(users_data, dry_run=False):
    """
    Reset user passwords.

    Args:
        users_data (list): List of dicts with keys:
                          - email (required)
                          - password (required)
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users_data)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_data in enumerate(users_data, start=1):
        email = user_data.get('email', '').strip()
        password = user_data.get('password', '').strip()

        yield {
            'status': 'processing',
            'email': email,
            'current': i,
            'total': total,
            'message': f"Resetting password for {email}..."
        }

        if not password:
            failure_count += 1
            errors.append((email, "Missing password"))
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Missing password for {email}"
            }
            continue

        try:
            cmd = [get_gam_command(), 'update', 'user', email, 'password', password]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': email,
                    'message': f"[DRY RUN] Would reset password for: {email}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': email,
                    'message': f"✓ Reset password for {email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((email, error_msg))
                log_error("Reset Password", f"Failed for {email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': email,
                    'message': f"✗ Failed to reset password for {email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((email, error_msg))
            log_error("Reset Password", f"Exception for {email}: {error_msg}")
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Error resetting password for {email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def update_user_info(users_data, dry_run=False):
    """
    Update user information (name, address, employee info, etc.).

    Args:
        users_data (list): List of dicts with keys:
                          - email (required)
                          - firstName (optional)
                          - lastName (optional)
                          - employeeId (optional)
                          - jobTitle (optional)
                          - manager (optional)
                          - department (optional)
                          - costCenter (optional)
                          - buildingId (optional)
                          - address (optional)
                          - galHidden (optional) - boolean or string "true"/"false"
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users_data)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_data in enumerate(users_data, start=1):
        email = user_data.get('email', '').strip()

        yield {
            'status': 'processing',
            'email': email,
            'current': i,
            'total': total,
            'message': f"Updating info for {email}..."
        }

        try:
            cmd = [get_gam_command(), 'update', 'user', email]

            # Add optional fields
            if 'firstName' in user_data and user_data['firstName']:
                cmd.extend(['firstname', user_data['firstName'].strip()])
            if 'lastName' in user_data and user_data['lastName']:
                cmd.extend(['lastname', user_data['lastName'].strip()])
            if 'employeeId' in user_data and user_data['employeeId']:
                cmd.extend(['externalid', 'organization', user_data['employeeId'].strip()])
            if 'jobTitle' in user_data and user_data['jobTitle']:
                cmd.extend(['organization', 'title', user_data['jobTitle'].strip()])
            if 'manager' in user_data and user_data['manager']:
                cmd.extend(['relation', 'manager', user_data['manager'].strip()])
            if 'department' in user_data and user_data['department']:
                cmd.extend(['organization', 'department', user_data['department'].strip()])
            if 'costCenter' in user_data and user_data['costCenter']:
                cmd.extend(['organization', 'costcenter', user_data['costCenter'].strip()])
            if 'buildingId' in user_data and user_data['buildingId']:
                cmd.extend(['location', 'buildingid', user_data['buildingId'].strip()])
            if 'address' in user_data and user_data['address']:
                cmd.extend(['address', 'type', 'work', 'unstructured', user_data['address'].strip()])

            # GAL visibility
            if 'galHidden' in user_data:
                gal_hidden = user_data['galHidden']
                # Handle both boolean and string values
                if isinstance(gal_hidden, str):
                    gal_hidden = gal_hidden.lower() in ['true', '1', 'yes']
                if gal_hidden:
                    cmd.extend(['gal', 'off'])
                else:
                    cmd.extend(['gal', 'on'])

            # Check if any updates provided
            if len(cmd) == 4:  # Only [gam, update, user, email]
                failure_count += 1
                errors.append((email, "No update fields provided"))
                yield {
                    'status': 'error',
                    'email': email,
                    'message': f"✗ No update fields for {email}"
                }
                continue

            if dry_run:
                fields = ', '.join(cmd[4::2])  # Get field names
                yield {
                    'status': 'dry-run',
                    'email': email,
                    'message': f"[DRY RUN] Would update {fields} for: {email}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': email,
                    'message': f"✓ Updated info for {email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((email, error_msg))
                log_error("Update User Info", f"Failed for {email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': email,
                    'message': f"✗ Failed to update {email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((email, error_msg))
            log_error("Update User Info", f"Exception for {email}: {error_msg}")
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Error updating {email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def change_org_unit(users_data, dry_run=False):
    """
    Move users to a different organizational unit.

    Args:
        users_data (list): List of dicts with keys:
                          - email (required)
                          - orgUnit (required)
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users_data)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_data in enumerate(users_data, start=1):
        email = user_data.get('email', '').strip()
        org_unit = user_data.get('orgUnit', '').strip()

        yield {
            'status': 'processing',
            'email': email,
            'current': i,
            'total': total,
            'message': f"Moving {email} to {org_unit}..."
        }

        if not org_unit:
            failure_count += 1
            errors.append((email, "Missing organizational unit"))
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Missing OU for {email}"
            }
            continue

        try:
            cmd = [get_gam_command(), 'update', 'user', email, 'ou', org_unit]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': email,
                    'message': f"[DRY RUN] Would move {email} to: {org_unit}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': email,
                    'message': f"✓ Moved {email} to {org_unit}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((email, error_msg))
                log_error("Change OU", f"Failed for {email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': email,
                    'message': f"✗ Failed to move {email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((email, error_msg))
            log_error("Change OU", f"Exception for {email}: {error_msg}")
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Error moving {email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def add_alias(users_data, dry_run=False):
    """
    Add email aliases to users.

    Args:
        users_data (list): List of dicts with keys:
                          - email (required) - primary user email
                          - alias (required) - alias email to add
        dry_run (bool): If True, preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users_data)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_data in enumerate(users_data, start=1):
        email = user_data.get('email', '').strip()
        alias = user_data.get('alias', '').strip()

        yield {
            'status': 'processing',
            'email': email,
            'current': i,
            'total': total,
            'message': f"Adding alias {alias} to {email}..."
        }

        if not alias or not validate_email(alias):
            failure_count += 1
            errors.append((email, "Invalid alias email"))
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Invalid alias for {email}"
            }
            continue

        try:
            cmd = [get_gam_command(), 'create', 'alias', alias, 'user', email]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'email': email,
                    'message': f"[DRY RUN] Would add alias {alias} to: {email}"
                }
                success_count += 1
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': email,
                    'message': f"✓ Added alias {alias} to {email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((email, error_msg))
                log_error("Add Alias", f"Failed for {email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': email,
                    'message': f"✗ Failed to add alias to {email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((email, error_msg))
            log_error("Add Alias", f"Exception for {email}: {error_msg}")
            yield {
                'status': 'error',
                'email': email,
                'message': f"✗ Error adding alias to {email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def remove_alias(aliases, dry_run=False):
    """
    Remove email aliases.

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
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((alias, error_msg))
                log_error("Remove Alias", f"Failed for {alias}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': alias,
                    'message': f"✗ Failed to remove {alias}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((alias, error_msg))
            log_error("Remove Alias", f"Exception for {alias}: {error_msg}")
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


def get_user_info(user_email):
    """
    Get detailed information about a user.

    Args:
        user_email (str): User email address

    Returns:
        tuple: (success: bool, data: dict or error_message: str)
    """
    try:
        cmd = [get_gam_command(), 'info', 'user', user_email]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Parse the output into a dictionary
            user_info = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    user_info[key.strip()] = value.strip()

            return (True, user_info)
        else:
            error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
            log_error("Get User Info", f"Failed for {user_email}: {error_msg}")
            return (False, error_msg)

    except Exception as e:
        error_msg = str(e)
        log_error("Get User Info", f"Exception for {user_email}: {error_msg}")
        return (False, error_msg)


def list_user_aliases(user_email):
    """
    List all aliases for a user.

    Args:
        user_email (str): User email address

    Returns:
        tuple: (success: bool, aliases: list or error_message: str)
    """
    try:
        cmd = [get_gam_command(), 'user', user_email, 'show', 'aliases']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Parse aliases from output
            aliases = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if '@' in line and 'alias' in line.lower():
                    # Extract email from line
                    parts = line.split()
                    for part in parts:
                        if '@' in part:
                            aliases.append(part)

            return (True, aliases)
        else:
            error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
            log_error("List Aliases", f"Failed for {user_email}: {error_msg}")
            return (False, error_msg)

    except Exception as e:
        error_msg = str(e)
        log_error("List Aliases", f"Exception for {user_email}: {error_msg}")
        return (False, error_msg)


def list_org_units():
    """
    List all organizational units.

    Returns:
        list: List of org unit paths, or empty list on error
    """
    try:
        cmd = [get_gam_command(), 'print', 'orgs']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            # Parse org units from output
            import csv
            from io import StringIO
            orgs = []
            csv_reader = csv.DictReader(StringIO(result.stdout))

            for row in csv_reader:
                org_path = row.get('orgUnitPath') or row.get('Path') or row.get('path')
                if org_path:
                    orgs.append(org_path.strip())

            # Always include root
            if '/' not in orgs:
                orgs.insert(0, '/')

            return orgs
        else:
            log_error("List OUs", f"Failed: {result.stderr[:200]}")
            return ['/']

    except Exception as e:
        log_error("List OUs", f"Exception: {str(e)}")
        return ['/']


# ==================== MFA MANAGEMENT ====================

def enable_mfa(users):
    """
    Enable Multi-Factor Authentication (MFA) for users.

    Args:
        users (list): List of user emails

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_email in enumerate(users, start=1):
        yield {
            'status': 'processing',
            'email': user_email,
            'current': i,
            'total': total,
            'message': f"Enabling MFA for {user_email}..."
        }

        try:
            cmd = [get_gam_command(), 'update', 'user', user_email, 'enroll2sv']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': user_email,
                    'message': f"✓ Enabled MFA for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Enable MFA", f"Failed for {user_email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': user_email,
                    'message': f"✗ Failed to enable MFA for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Enable MFA", f"Exception for {user_email}: {error_msg}")
            yield {
                'status': 'error',
                'email': user_email,
                'message': f"✗ Error enabling MFA for {user_email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def disable_mfa(users):
    """
    Disable Multi-Factor Authentication (MFA) for users.

    Args:
        users (list): List of user emails

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_email in enumerate(users, start=1):
        yield {
            'status': 'processing',
            'email': user_email,
            'current': i,
            'total': total,
            'message': f"Disabling MFA for {user_email}..."
        }

        try:
            cmd = [get_gam_command(), 'update', 'user', user_email, 'turn2svoff']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': user_email,
                    'message': f"✓ Disabled MFA for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Disable MFA", f"Failed for {user_email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': user_email,
                    'message': f"✗ Failed to disable MFA for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Disable MFA", f"Exception for {user_email}: {error_msg}")
            yield {
                'status': 'error',
                'email': user_email,
                'message': f"✗ Error disabling MFA for {user_email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def remove_mfa_factor(users):
    """
    Remove MFA enrollment/factors for users.

    Args:
        users (list): List of user emails

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_email in enumerate(users, start=1):
        yield {
            'status': 'processing',
            'email': user_email,
            'current': i,
            'total': total,
            'message': f"Removing MFA factor for {user_email}..."
        }

        try:
            cmd = [get_gam_command(), 'user', user_email, 'remove2sv']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'email': user_email,
                    'message': f"✓ Removed MFA factor for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Remove MFA Factor", f"Failed for {user_email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': user_email,
                    'message': f"✗ Failed to remove MFA factor for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Remove MFA Factor", f"Exception for {user_email}: {error_msg}")
            yield {
                'status': 'error',
                'email': user_email,
                'message': f"✗ Error removing MFA factor for {user_email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def get_backup_codes(users):
    """
    Retrieve MFA backup verification codes for users.

    Args:
        users (list): List of user emails

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    for i, user_email in enumerate(users, start=1):
        yield {
            'status': 'processing',
            'email': user_email,
            'current': i,
            'total': total,
            'message': f"Retrieving backup codes for {user_email}..."
        }

        try:
            cmd = [get_gam_command(), 'user', user_email, 'show', 'backupcodes']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                # Extract backup codes from output
                backup_codes = []
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and line[0].isdigit():
                        backup_codes.append(line)

                if backup_codes:
                    codes_str = ', '.join(backup_codes)
                    yield {
                        'status': 'success',
                        'email': user_email,
                        'message': f"✓ Backup codes for {user_email}: {codes_str}"
                    }
                else:
                    yield {
                        'status': 'success',
                        'email': user_email,
                        'message': f"✓ Retrieved info for {user_email} (see full output in logs)"
                    }
            else:
                failure_count += 1
                error_msg = result.stderr[:2000] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Get Backup Codes", f"Failed for {user_email}: {error_msg}")
                yield {
                    'status': 'error',
                    'email': user_email,
                    'message': f"✗ Failed to get backup codes for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Get Backup Codes", f"Exception for {user_email}: {error_msg}")
            yield {
                'status': 'error',
                'email': user_email,
                'message': f"✗ Error getting backup codes for {user_email}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }
