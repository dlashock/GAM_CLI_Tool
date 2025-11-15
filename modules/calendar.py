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
        log_info("Get User Calendars", f"Fetching calendars for {user_email}")
        result = execute_gam_command(cmd, timeout=60, operation_name="Get User Calendars")

        if result.returncode != 0:
            error_msg = f"Failed for {user_email}: {result.stderr}"
            log_error("Get User Calendars", error_msg)
            print(f"ERROR loading calendars: {error_msg}")  # Debug output
            return []

        # Parse CSV output
        calendars = []
        if result.stdout:
            log_info("Get User Calendars", f"Parsing calendar data for {user_email}")
            reader = csv.DictReader(io.StringIO(result.stdout))
            for row in reader:
                cal = {
                    'id': row.get('calendarId', ''),  # GAM uses 'calendarId' not 'id'
                    'summary': row.get('summary', ''),
                    'accessRole': row.get('accessRole', '')
                }
                calendars.append(cal)

        log_info("Get User Calendars", f"Loaded {len(calendars)} calendars for {user_email}")
        return calendars

    except Exception as e:
        error_msg = f"Exception for {user_email}: {str(e)}"
        log_error("Get User Calendars", error_msg)
        print(f"EXCEPTION loading calendars: {error_msg}")  # Debug output
        import traceback
        traceback.print_exc()
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

    # Build command - GAM requires 'summary' parameter for calendar name
    cmd = [gam_cmd, 'user', user_email, 'create', 'calendar', 'summary', calendar_name]

    if description:
        cmd.extend(['description', description])

    if color:
        # Note: GAM uses colorid for calendar creation
        cmd.extend(['colorid', str(color)])

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


def import_calendar_events(calendar_id, csv_file_path, timezone):
    """
    Import calendar events from CSV file in Google Calendar format.
    Creates each event individually using GAM commands.

    Args:
        calendar_id (str): Target calendar ID
        csv_file_path (str): Path to CSV file in Google Calendar format
        timezone (str): Timezone for events (e.g., 'America/New_York')

    Yields:
        dict: Progress updates

    Returns:
        dict: Result with success/failure counts
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo

    gam_cmd = get_gam_command()

    # Validate file exists
    if not os.path.exists(csv_file_path):
        yield {
            'status': 'error',
            'message': f'✗ File not found: {csv_file_path}'
        }
        return {'success': False, 'error': 'File not found'}

    yield {
        'status': 'progress',
        'message': f'Reading events from {os.path.basename(csv_file_path)}...'
    }

    try:
        # Read and parse CSV file
        events = []
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                events.append(row)

        if not events:
            yield {
                'status': 'error',
                'message': '✗ No events found in CSV file'
            }
            return {'success': False, 'error': 'No events in file'}

        yield {
            'status': 'progress',
            'message': f'Found {len(events)} events. Starting import...'
        }

        # Import each event
        success_count = 0
        failure_count = 0

        for idx, event in enumerate(events, 1):
            try:
                # Extract event data
                subject = event.get('Subject', '').strip()
                if not subject:
                    yield {
                        'status': 'progress',
                        'message': f'⊘ Event {idx}/{len(events)}: Skipped (no subject)'
                    }
                    failure_count += 1
                    continue

                # Parse dates and times
                start_date = event.get('Start Date', '').strip()
                start_time = event.get('Start Time', '').strip()
                end_date = event.get('End Date', '').strip()
                end_time = event.get('End Time', '').strip()
                is_all_day = event.get('All Day Event', '').strip().lower() == 'true'
                description = event.get('Description', '').strip()
                location = event.get('Location', '').strip()

                # Convert to ISO format for GAM
                tz = ZoneInfo(timezone)

                if is_all_day:
                    # All-day event
                    start_dt = datetime.strptime(start_date, '%m/%d/%Y')
                    start_iso = start_dt.strftime('%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%m/%d/%Y') if end_date else start_dt
                    end_iso = end_dt.strftime('%Y-%m-%d')
                else:
                    # Timed event - make timezone-aware and include offset
                    start_datetime = f"{start_date} {start_time}"
                    start_dt = datetime.strptime(start_datetime, '%m/%d/%Y %I:%M %p')
                    start_dt_tz = start_dt.replace(tzinfo=tz)
                    start_iso = start_dt_tz.isoformat()

                    if end_date and end_time:
                        end_datetime = f"{end_date} {end_time}"
                        end_dt = datetime.strptime(end_datetime, '%m/%d/%Y %I:%M %p')
                    else:
                        # Default to 1 hour duration
                        end_dt = start_dt
                    end_dt_tz = end_dt.replace(tzinfo=tz)
                    end_iso = end_dt_tz.isoformat()

                # Build GAM command
                cmd = [gam_cmd, 'calendar', calendar_id, 'add', 'event',
                       'start', start_iso, 'end', end_iso,
                       'summary', subject]

                if is_all_day:
                    cmd.append('allday')

                if description:
                    cmd.extend(['description', description])

                if location:
                    cmd.extend(['location', location])

                # Execute command
                yield {
                    'status': 'progress',
                    'message': f'⏳ Importing event {idx}/{len(events)}: {subject[:50]}...'
                }

                result = execute_gam_command(cmd, timeout=30, operation_name="Import Event")

                if result.returncode == 0:
                    success_count += 1
                    yield {
                        'status': 'progress',
                        'message': f'✓ Event {idx}/{len(events)}: {subject[:50]}'
                    }
                else:
                    failure_count += 1
                    error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
                    yield {
                        'status': 'progress',
                        'message': f'✗ Event {idx}/{len(events)}: {subject[:50]} - {error_msg[:50]}'
                    }
                    log_error("Import Event", f"Calendar {calendar_id}, Event '{subject}': {error_msg}")

            except Exception as e:
                failure_count += 1
                yield {
                    'status': 'progress',
                    'message': f'✗ Event {idx}/{len(events)}: Error parsing - {str(e)[:50]}'
                }
                log_error("Import Event", f"Calendar {calendar_id}: {str(e)}")
                continue

        # Final summary
        if success_count > 0:
            yield {
                'status': 'success',
                'message': f'✓ Import complete: {success_count} succeeded, {failure_count} failed'
            }
            return {
                'success': True,
                'imported': success_count,
                'failed': failure_count
            }
        else:
            yield {
                'status': 'error',
                'message': f'✗ Import failed: 0 succeeded, {failure_count} failed'
            }
            return {
                'success': False,
                'imported': 0,
                'failed': failure_count
            }

    except Exception as e:
        error_msg = f'Exception: {str(e)}'
        yield {
            'status': 'error',
            'message': f'✗ Failed to import events: {error_msg}'
        }
        log_error("Import Calendar Events", f"Calendar {calendar_id}: {error_msg}")
        return {'success': False, 'error': error_msg}


def export_calendar_events(calendar_id, start_date, end_date, output_file):
    """
    Export calendar events to CSV file in Google Calendar import format.

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

    # Build GAM command
    cmd = [gam_cmd, 'calendar', calendar_id, 'print', 'events',
           'after', start_date, 'before', end_date]

    try:
        result = execute_gam_command(cmd, timeout=120, operation_name="Export Calendar Events")

        if result.returncode == 0:
            yield {
                'status': 'progress',
                'message': 'Converting to Google Calendar import format...'
            }

            # Convert GAM CSV to Google Calendar format
            converted_csv = _convert_to_google_calendar_format(result.stdout)

            # Write converted CSV to file
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                f.write(converted_csv)

            yield {
                'status': 'success',
                'message': f'✓ Exported events to {output_file} (Google Calendar import format)'
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


def _convert_to_google_calendar_format(gam_csv_output):
    """
    Convert GAM's CSV output to Google Calendar import format.

    Google Calendar expects these columns:
    - Subject (required)
    - Start Date (required) - MM/DD/YYYY format
    - Start Time (optional)
    - End Date (optional) - MM/DD/YYYY format
    - End Time (optional)
    - All Day Event (optional) - True/False
    - Description (optional)
    - Location (optional)

    Args:
        gam_csv_output (str): CSV output from GAM

    Returns:
        str: Converted CSV in Google Calendar format
    """
    from datetime import datetime

    # Parse GAM CSV
    reader = csv.DictReader(io.StringIO(gam_csv_output))

    # Prepare output
    output = io.StringIO()
    writer = csv.writer(output)

    # Write Google Calendar headers
    writer.writerow(['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time',
                     'All Day Event', 'Description', 'Location'])

    # Convert each event
    for row in reader:
        try:
            # Extract fields from GAM output
            subject = row.get('summary', '')
            description = row.get('description', '')
            location = row.get('location', '')

            # Parse start date/time
            start_datetime_str = row.get('start.dateTime', '')
            start_date_str = row.get('start.date', '')

            # Parse end date/time
            end_datetime_str = row.get('end.dateTime', '')
            end_date_str = row.get('end.date', '')

            # Determine if all-day event
            is_all_day = bool(start_date_str and not start_datetime_str)

            # Format start date/time
            if start_datetime_str:
                # Parse datetime (format: 2024-01-15T10:00:00-05:00)
                start_dt = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
                start_date = start_dt.strftime('%m/%d/%Y')
                start_time = start_dt.strftime('%I:%M %p').lstrip('0')  # Remove leading zero
            elif start_date_str:
                # All-day event with just date
                start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
                start_date = start_dt.strftime('%m/%d/%Y')
                start_time = ''
            else:
                # No start date found, skip this event
                continue

            # Format end date/time
            if end_datetime_str:
                end_dt = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
                end_date = end_dt.strftime('%m/%d/%Y')
                end_time = end_dt.strftime('%I:%M %p').lstrip('0')
            elif end_date_str:
                end_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_date = end_dt.strftime('%m/%d/%Y')
                end_time = ''
            else:
                end_date = start_date
                end_time = start_time

            # Write row in Google Calendar format
            writer.writerow([
                subject,
                start_date,
                start_time,
                end_date,
                end_time,
                'True' if is_all_day else 'False',
                description,
                location
            ])

        except Exception as e:
            # Log error but continue with other events
            log_error("CSV Conversion", f"Failed to convert event: {str(e)}")
            continue

    return output.getvalue()


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
