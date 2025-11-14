"""
Calendar Operations Module for GAM Admin Tool.

Provides backend functions for Google Calendar operations including:
- Calendar ACL/permission management
- Calendar creation and deletion
- Calendar information retrieval
- Import/Export calendar data
- Calendar settings management

All functions yield progress updates for GUI display.
"""

import subprocess
import os
import csv
import io
from modules.base_operations import get_gam_command, execute_gam_command
from utils.logger import log_error, log_info


def get_user_calendars(user_email):
    """
    Get list of calendars for a user.

    Args:
        user_email (str): User's email address

    Returns:
        list: List of dicts with calendar info (id, summary, accessRole)

    Example:
        calendars = get_user_calendars('user@domain.com')
        # [{'id': 'primary', 'summary': 'John Doe', 'accessRole': 'owner'}, ...]
    """
    gam_cmd = get_gam_command()
    cmd = [gam_cmd, 'user', user_email, 'print', 'calendars']

    try:
        result = execute_gam_command(cmd, timeout=60, operation_name="Get User Calendars")

        if result.returncode != 0:
            log_error("Get User Calendars", f"Failed for {user_email}: {result.stderr}")
            return []

        # Parse CSV output
        calendars = []
        if result.stdout:
            reader = csv.DictReader(io.StringIO(result.stdout))
            for row in reader:
                calendars.append({
                    'id': row.get('id', ''),
                    'summary': row.get('summary', ''),
                    'accessRole': row.get('accessRole', '')
                })

        return calendars

    except Exception as e:
        log_error("Get User Calendars", f"Exception for {user_email}: {str(e)}")
        return []


def get_calendar_info(calendar_id, user_email=None):
    """
    Get detailed information about a calendar.

    Args:
        calendar_id (str): Calendar ID
        user_email (str, optional): User email if accessing user's calendar

    Returns:
        dict: Calendar information

    Yields:
        dict: Progress updates
    """
    gam_cmd = get_gam_command()

    # If user_email provided, use user context, otherwise direct calendar access
    if user_email:
        cmd = [gam_cmd, 'user', user_email, 'info', 'calendar', calendar_id]
    else:
        cmd = [gam_cmd, 'calendar', calendar_id, 'info']

    yield {
        'status': 'info',
        'message': f'Retrieving information for calendar {calendar_id}...'
    }

    try:
        result = execute_gam_command(cmd, timeout=30, operation_name="Get Calendar Info")

        if result.returncode != 0:
            yield {
                'status': 'error',
                'message': f'Failed to get calendar info: {result.stderr}'
            }
            return None

        yield {
            'status': 'success',
            'message': f'Calendar information retrieved:\n\n{result.stdout}'
        }

        return result.stdout

    except Exception as e:
        error_msg = f'Exception getting calendar info: {str(e)}'
        log_error("Get Calendar Info", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None


def get_calendar_acl(calendar_id):
    """
    Get calendar ACL (permissions).

    Args:
        calendar_id (str): Calendar ID

    Returns:
        str: ACL information

    Yields:
        dict: Progress updates
    """
    gam_cmd = get_gam_command()
    cmd = [gam_cmd, 'calendar', calendar_id, 'showacl']

    yield {
        'status': 'info',
        'message': f'Retrieving permissions for calendar {calendar_id}...'
    }

    try:
        result = execute_gam_command(cmd, timeout=30, operation_name="Get Calendar ACL")

        if result.returncode != 0:
            yield {
                'status': 'error',
                'message': f'Failed to get calendar permissions: {result.stderr}'
            }
            return None

        yield {
            'status': 'success',
            'message': f'Calendar permissions:\n\n{result.stdout}'
        }

        return result.stdout

    except Exception as e:
        error_msg = f'Exception getting calendar ACL: {str(e)}'
        log_error("Get Calendar ACL", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None


def add_calendar_permission(calendar_ids, user_email, role='reader', send_notifications=False):
    """
    Add permission to calendar(s).

    Args:
        calendar_ids (list): List of calendar IDs
        user_email (str): Email of user/group to grant permission to
        role (str): Permission role (reader, writer, owner)
        send_notifications (bool): Send notification email

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary of results
    """
    gam_cmd = get_gam_command()
    success_count = 0
    error_count = 0

    for i, calendar_id in enumerate(calendar_ids, start=1):
        yield {
            'status': 'progress',
            'current': i,
            'total': len(calendar_ids),
            'message': f'Adding {role} permission for {user_email} to calendar {i} of {len(calendar_ids)}...'
        }

        # Build command
        cmd = [gam_cmd, 'calendar', calendar_id, 'add', role, 'user', user_email]

        # Add sendnotifications parameter
        if send_notifications:
            cmd.extend(['sendnotifications', 'true'])
        else:
            cmd.extend(['sendnotifications', 'false'])

        try:
            result = execute_gam_command(cmd, timeout=30, operation_name="Add Calendar Permission")

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'message': f'✓ Added {role} permission for {user_email} to calendar {calendar_id}'
                }
            else:
                error_count += 1
                error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
                yield {
                    'status': 'error',
                    'message': f'✗ Failed for calendar {calendar_id}: {error_msg}'
                }
                log_error("Add Calendar Permission", f"Calendar {calendar_id}, User {user_email}: {error_msg}")

        except Exception as e:
            error_count += 1
            error_msg = f'Exception: {str(e)}'
            yield {
                'status': 'error',
                'message': f'✗ Failed for calendar {calendar_id}: {error_msg}'
            }
            log_error("Add Calendar Permission", f"Calendar {calendar_id}: {error_msg}")

    # Final summary
    yield {
        'status': 'complete',
        'message': f'Completed: {success_count} successful, {error_count} failed',
        'success_count': success_count,
        'error_count': error_count
    }

    return {'success': success_count, 'errors': error_count}


def remove_calendar_permission(calendar_ids, user_email):
    """
    Remove permission from calendar(s).

    Args:
        calendar_ids (list): List of calendar IDs
        user_email (str): Email of user/group to remove

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary of results
    """
    gam_cmd = get_gam_command()
    success_count = 0
    error_count = 0

    for i, calendar_id in enumerate(calendar_ids, start=1):
        yield {
            'status': 'progress',
            'current': i,
            'total': len(calendar_ids),
            'message': f'Removing permission for {user_email} from calendar {i} of {len(calendar_ids)}...'
        }

        cmd = [gam_cmd, 'calendar', calendar_id, 'delete', 'user', user_email]

        try:
            result = execute_gam_command(cmd, timeout=30, operation_name="Remove Calendar Permission")

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'message': f'✓ Removed permission for {user_email} from calendar {calendar_id}'
                }
            else:
                error_count += 1
                error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
                yield {
                    'status': 'error',
                    'message': f'✗ Failed for calendar {calendar_id}: {error_msg}'
                }
                log_error("Remove Calendar Permission", f"Calendar {calendar_id}, User {user_email}: {error_msg}")

        except Exception as e:
            error_count += 1
            error_msg = f'Exception: {str(e)}'
            yield {
                'status': 'error',
                'message': f'✗ Failed for calendar {calendar_id}: {error_msg}'
            }
            log_error("Remove Calendar Permission", f"Calendar {calendar_id}: {error_msg}")

    # Final summary
    yield {
        'status': 'complete',
        'message': f'Completed: {success_count} successful, {error_count} failed',
        'success_count': success_count,
        'error_count': error_count
    }

    return {'success': success_count, 'errors': error_count}


def create_calendar(user_email, calendar_name, description='', color=None):
    """
    Create a new calendar for a user.

    Args:
        user_email (str): User who will own the calendar
        calendar_name (str): Calendar name
        description (str): Calendar description
        color (str, optional): Color ID (1-24)

    Yields:
        dict: Progress updates

    Returns:
        dict: Result with calendar_id if successful
    """
    gam_cmd = get_gam_command()

    yield {
        'status': 'progress',
        'message': f'Creating calendar "{calendar_name}" for {user_email}...'
    }

    # Build command
    cmd = [gam_cmd, 'user', user_email, 'create', 'calendar', 'name', calendar_name]

    if description:
        cmd.extend(['description', description])

    if color:
        cmd.extend(['color', str(color)])

    try:
        result = execute_gam_command(cmd, timeout=30, operation_name="Create Calendar")

        if result.returncode == 0:
            yield {
                'status': 'success',
                'message': f'✓ Created calendar "{calendar_name}" for {user_email}',
                'data': result.stdout
            }
            return {'success': True, 'output': result.stdout}
        else:
            error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
            yield {
                'status': 'error',
                'message': f'✗ Failed to create calendar: {error_msg}'
            }
            log_error("Create Calendar", f"User {user_email}, Calendar {calendar_name}: {error_msg}")
            return {'success': False, 'error': error_msg}

    except Exception as e:
        error_msg = f'Exception: {str(e)}'
        yield {
            'status': 'error',
            'message': f'✗ Failed to create calendar: {error_msg}'
        }
        log_error("Create Calendar", f"User {user_email}: {error_msg}")
        return {'success': False, 'error': error_msg}


def delete_calendar(user_email, calendar_id):
    """
    Delete a calendar.

    Args:
        user_email (str): User who owns the calendar
        calendar_id (str): Calendar ID to delete

    Yields:
        dict: Progress updates

    Returns:
        dict: Result
    """
    gam_cmd = get_gam_command()

    yield {
        'status': 'progress',
        'message': f'Deleting calendar {calendar_id} for {user_email}...'
    }

    cmd = [gam_cmd, 'user', user_email, 'delete', 'calendar', calendar_id]

    try:
        result = execute_gam_command(cmd, timeout=30, operation_name="Delete Calendar")

        if result.returncode == 0:
            yield {
                'status': 'success',
                'message': f'✓ Deleted calendar {calendar_id}'
            }
            return {'success': True}
        else:
            error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
            yield {
                'status': 'error',
                'message': f'✗ Failed to delete calendar: {error_msg}'
            }
            log_error("Delete Calendar", f"User {user_email}, Calendar {calendar_id}: {error_msg}")
            return {'success': False, 'error': error_msg}

    except Exception as e:
        error_msg = f'Exception: {str(e)}'
        yield {
            'status': 'error',
            'message': f'✗ Failed to delete calendar: {error_msg}'
        }
        log_error("Delete Calendar", f"User {user_email}: {error_msg}")
        return {'success': False, 'error': error_msg}


def import_calendar(user_email, calendar_id, ics_file_path):
    """
    Import calendar events from .ics file.

    Args:
        user_email (str): User who owns the calendar
        calendar_id (str): Target calendar ID
        ics_file_path (str): Path to .ics file

    Yields:
        dict: Progress updates

    Returns:
        dict: Result
    """
    gam_cmd = get_gam_command()

    # Validate file exists
    if not os.path.exists(ics_file_path):
        yield {
            'status': 'error',
            'message': f'✗ File not found: {ics_file_path}'
        }
        return {'success': False, 'error': 'File not found'}

    yield {
        'status': 'progress',
        'message': f'Importing events from {os.path.basename(ics_file_path)} to calendar {calendar_id}...'
    }

    cmd = [gam_cmd, 'user', user_email, 'import', 'calendar', calendar_id, 'file', ics_file_path]

    try:
        result = execute_gam_command(cmd, timeout=120, operation_name="Import Calendar")

        if result.returncode == 0:
            yield {
                'status': 'success',
                'message': f'✓ Imported events to calendar {calendar_id}',
                'data': result.stdout
            }
            return {'success': True, 'output': result.stdout}
        else:
            error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
            yield {
                'status': 'error',
                'message': f'✗ Failed to import calendar: {error_msg}'
            }
            log_error("Import Calendar", f"User {user_email}, Calendar {calendar_id}: {error_msg}")
            return {'success': False, 'error': error_msg}

    except Exception as e:
        error_msg = f'Exception: {str(e)}'
        yield {
            'status': 'error',
            'message': f'✗ Failed to import calendar: {error_msg}'
        }
        log_error("Import Calendar", f"User {user_email}: {error_msg}")
        return {'success': False, 'error': error_msg}


def export_calendar_events(calendar_id, start_date, end_date, output_file):
    """
    Export calendar events to CSV file.

    Args:
        calendar_id (str): Calendar ID
        start_date (str): Start date (YYYY-MM-DD)
        end_date (str): End date (YYYY-MM-DD)
        output_file (str): Output file path

    Yields:
        dict: Progress updates

    Returns:
        dict: Result
    """
    gam_cmd = get_gam_command()

    yield {
        'status': 'progress',
        'message': f'Exporting events from {start_date} to {end_date}...'
    }

    cmd = [gam_cmd, 'calendar', calendar_id, 'print', 'events',
           'after', start_date, 'before', end_date]

    try:
        result = execute_gam_command(cmd, timeout=120, operation_name="Export Calendar Events")

        if result.returncode == 0:
            # Write output to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)

            yield {
                'status': 'success',
                'message': f'✓ Exported events to {output_file}'
            }
            return {'success': True, 'file': output_file}
        else:
            error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
            yield {
                'status': 'error',
                'message': f'✗ Failed to export events: {error_msg}'
            }
            log_error("Export Calendar Events", f"Calendar {calendar_id}: {error_msg}")
            return {'success': False, 'error': error_msg}

    except Exception as e:
        error_msg = f'Exception: {str(e)}'
        yield {
            'status': 'error',
            'message': f'✗ Failed to export events: {error_msg}'
        }
        log_error("Export Calendar Events", f"Calendar {calendar_id}: {error_msg}")
        return {'success': False, 'error': error_msg}


def update_calendar_settings(user_email, calendar_id, **settings):
    """
    Update calendar settings.

    Args:
        user_email (str): User email
        calendar_id (str): Calendar ID
        **settings: Settings to update (selected, hidden, color, etc.)

    Yields:
        dict: Progress updates

    Returns:
        dict: Result
    """
    gam_cmd = get_gam_command()

    yield {
        'status': 'progress',
        'message': f'Updating settings for calendar {calendar_id}...'
    }

    # Build command
    cmd = [gam_cmd, 'user', user_email, 'update', 'calendar', calendar_id]

    # Add settings
    for key, value in settings.items():
        cmd.extend([key, str(value)])

    try:
        result = execute_gam_command(cmd, timeout=30, operation_name="Update Calendar Settings")

        if result.returncode == 0:
            yield {
                'status': 'success',
                'message': f'✓ Updated calendar settings'
            }
            return {'success': True}
        else:
            error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
            yield {
                'status': 'error',
                'message': f'✗ Failed to update settings: {error_msg}'
            }
            log_error("Update Calendar Settings", f"User {user_email}, Calendar {calendar_id}: {error_msg}")
            return {'success': False, 'error': error_msg}

    except Exception as e:
        error_msg = f'Exception: {str(e)}'
        yield {
            'status': 'error',
            'message': f'✗ Failed to update settings: {error_msg}'
        }
        log_error("Update Calendar Settings", f"User {user_email}: {error_msg}")
        return {'success': False, 'error': error_msg}
