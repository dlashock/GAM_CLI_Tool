"""
Reports module for GAM Admin Tool.

Provides functions for generating various Google Workspace reports including
login activity, storage usage, email statistics, and admin audit logs.
"""

import subprocess
import csv
import io
from datetime import datetime, timedelta
from modules.base_operations import get_gam_command
from utils.logger import log_error


def get_login_activity_report(date_range_days=30, include_suspended=False):
    """
    Generate login activity report for all users.

    Fetches last login times for all users and categorizes them by activity level.
    Useful for identifying inactive accounts and verifying license usage.

    Args:
        date_range_days (int): Look back period in days (default: 30)
        include_suspended (bool): Include suspended users in report (default: False)

    Yields:
        dict: Progress updates with status, message, and optional report_data
            - status: 'info', 'success', or 'error'
            - message: Human-readable status message
            - report_data: List of user login data (on success)

    Returns:
        dict: Complete report data structure or None on error
            - report_type: 'login_activity'
            - date_generated: ISO timestamp
            - total_users: Count of users in report
            - data: List of user login records
    """
    gam_cmd = get_gam_command()

    yield {
        'status': 'info',
        'message': 'Fetching user list...'
    }

    # Get all users
    from utils.workspace_data import fetch_users
    users = fetch_users()

    if not users:
        yield {
            'status': 'error',
            'message': 'Failed to fetch users'
        }
        return None

    yield {
        'status': 'info',
        'message': f'Fetching login activity for {len(users)} users...'
    }

    # Get login activity using GAM print users
    # Note: We need lastLoginTime and suspended fields
    cmd = [
        gam_cmd, 'print', 'users',
        'fields', 'primaryemail,lastlogintime,suspended'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            error_msg = f'Failed to fetch login data: {result.stderr}'
            log_error("Login Activity Report", error_msg)
            yield {
                'status': 'error',
                'message': error_msg
            }
            return None

        # Parse CSV output
        reader = csv.DictReader(io.StringIO(result.stdout))
        report_data = []

        for row in reader:
            email = row.get('primaryEmail', row.get('email', ''))
            last_login_str = row.get('lastLoginTime', '')
            suspended_str = row.get('suspended', 'False')
            is_suspended = suspended_str.lower() in ['true', '1', 'yes']

            # Skip suspended users if not including them
            if is_suspended and not include_suspended:
                continue

            # Parse last login time
            if last_login_str and last_login_str not in ['Never logged in', 'Never', '']:
                try:
                    # Try parsing with different formats GAM might return
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                        try:
                            last_login = datetime.strptime(last_login_str, fmt)
                            days_since = (datetime.now() - last_login).days
                            break
                        except ValueError:
                            continue
                    else:
                        # Couldn't parse any format
                        last_login = None
                        days_since = None
                except Exception as e:
                    log_error("Login Activity Report", f"Error parsing date {last_login_str}: {e}")
                    last_login = None
                    days_since = None
            else:
                last_login = None
                days_since = None

            # Determine status
            if days_since is None:
                status = 'Never Logged In'
            elif days_since == 0:
                status = 'Active Today'
            elif days_since <= 7:
                status = 'Active (< 7 days)'
            elif days_since <= 30:
                status = 'Active (< 30 days)'
            elif days_since <= 90:
                status = 'Inactive (< 90 days)'
            else:
                status = 'Inactive (> 90 days)'

            report_data.append({
                'email': email,
                'last_login': last_login_str if last_login_str else 'Never',
                'days_since_login': days_since,
                'status': status
            })

        # Sort by days_since_login (most inactive first)
        report_data.sort(
            key=lambda x: x['days_since_login'] if x['days_since_login'] is not None else 99999,
            reverse=True
        )

        # Calculate statistics
        total_users = len(report_data)
        never_logged_in = sum(1 for u in report_data if u['days_since_login'] is None)
        inactive_90_plus = sum(1 for u in report_data if u['days_since_login'] and u['days_since_login'] > 90)
        active_users = total_users - never_logged_in - inactive_90_plus

        yield {
            'status': 'success',
            'message': f'Generated login activity report for {total_users} users',
            'report_data': report_data,
            'summary': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_90_plus': inactive_90_plus,
                'never_logged_in': never_logged_in
            }
        }

        return {
            'report_type': 'login_activity',
            'date_generated': datetime.now().isoformat(),
            'total_users': total_users,
            'data': report_data,
            'summary': {
                'active_users': active_users,
                'inactive_90_plus': inactive_90_plus,
                'never_logged_in': never_logged_in
            }
        }

    except subprocess.TimeoutExpired:
        error_msg = 'Report generation timed out (120 seconds)'
        log_error("Login Activity Report", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None
    except Exception as e:
        error_msg = f'Exception generating report: {str(e)}'
        log_error("Login Activity Report", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None


def get_storage_usage_report(quota_threshold_percent=80, org_unit=None, user_email=None):
    """
    Generate storage usage report for all users, a specific user, or users in a specific OU.

    Fetches Drive and Gmail storage usage for all users. Useful for capacity
    planning, identifying users over quota, and optimizing storage costs.

    Args:
        quota_threshold_percent (int): Highlight users over this % of quota (default: 80)
        org_unit (str): Optional organizational unit path to filter users (e.g., '/Students')
        user_email (str): Optional specific user email to get storage for

    Yields:
        dict: Progress updates with status, message, and optional report_data
            - status: 'info', 'success', or 'error'
            - message: Human-readable status message
            - report_data: List of user storage data (on success)
            - summary: Aggregate statistics (on success)

    Returns:
        dict: Complete report data structure or None on error
            - report_type: 'storage_usage'
            - date_generated: ISO timestamp
            - total_users: Count of users in report
            - data: List of user storage records
            - summary: Aggregate storage statistics
    """
    gam_cmd = get_gam_command()

    # Determine scope message
    if user_email:
        scope_msg = f'user {user_email}'
        users = [user_email]
    elif org_unit:
        scope_msg = f'users from {org_unit}'
        # Get users from OU
        from utils.workspace_data import fetch_users
        users = fetch_users(org_unit=org_unit)
    else:
        scope_msg = 'all users'
        # Get all users
        from utils.workspace_data import fetch_users
        users = fetch_users()

    yield {
        'status': 'info',
        'message': f'Fetching storage usage for {scope_msg}...'
    }

    # Validate user list
    if not users:
        yield {
            'status': 'error',
            'message': 'Failed to fetch users or invalid user email'
        }
        return None

    total_users = len(users)
    yield {
        'status': 'info',
        'message': f'Fetching storage quota for {total_users} users...'
    }

    report_data = []

    # Fetch storage quota for each user
    for i, user_email in enumerate(users, 1):
        yield {
            'status': 'processing',
            'current': i,
            'total': total_users,
            'message': f'Fetching quota for {user_email}...'
        }

        # Use GAM to get user's Drive quota
        cmd = [
            gam_cmd, 'user', user_email,
            'show', 'filequota'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Parse the output to extract quota information
                output = result.stdout

                # GAM output format example:
                # User: user@domain.com
                # Usage: 1234567890 bytes
                # Limit: 15728640000 bytes

                used_bytes = 0
                total_bytes = 0

                for line in output.split('\n'):
                    line = line.strip()
                    if 'Usage:' in line:
                        # Extract bytes value
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                used_bytes = int(parts[1])
                            except (ValueError, IndexError):
                                pass
                    elif 'Limit:' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                total_bytes = int(parts[1])
                            except (ValueError, IndexError):
                                pass

                # Convert bytes to GB
                bytes_per_gb = 1024 * 1024 * 1024
                total_quota_gb = round(total_bytes / bytes_per_gb, 2) if total_bytes > 0 else 0
                used_quota_gb = round(used_bytes / bytes_per_gb, 2)

                # Calculate percentage
                if total_quota_gb > 0:
                    percent_used = round((used_quota_gb / total_quota_gb) * 100, 1)
                else:
                    percent_used = 0

                # Flag if over threshold
                over_threshold = percent_used >= quota_threshold_percent

                report_data.append({
                    'email': user_email,
                    'total_quota_gb': total_quota_gb,
                    'used_quota_gb': used_quota_gb,
                    'percent_used': percent_used,
                    'over_threshold': over_threshold
                })
            else:
                # If command fails, add user with unknown quota
                report_data.append({
                    'email': user_email,
                    'total_quota_gb': 0,
                    'used_quota_gb': 0,
                    'percent_used': 0,
                    'over_threshold': False
                })

        except subprocess.TimeoutExpired:
            log_error("Storage Usage Report", f"Timeout fetching quota for {user_email}")
            # Add with unknown quota
            report_data.append({
                'email': user_email,
                'total_quota_gb': 0,
                'used_quota_gb': 0,
                'percent_used': 0,
                'over_threshold': False
            })
        except Exception as e:
            log_error("Storage Usage Report", f"Error fetching quota for {user_email}: {str(e)}")
            # Add with unknown quota
            report_data.append({
                'email': user_email,
                'total_quota_gb': 0,
                'used_quota_gb': 0,
                'percent_used': 0,
                'over_threshold': False
            })

    # Sort by percent_used (highest first)
    report_data.sort(key=lambda x: x['percent_used'], reverse=True)

    # Calculate summary statistics
    users_over_threshold = sum(1 for u in report_data if u['over_threshold'])
    total_storage_used = sum(u['used_quota_gb'] for u in report_data)
    total_storage_quota = sum(u['total_quota_gb'] for u in report_data)

    avg_usage_percent = (
        round((total_storage_used / total_storage_quota) * 100, 1)
        if total_storage_quota > 0 else 0
    )

    yield {
        'status': 'success',
        'message': f'Generated storage report for {total_users} users',
        'report_data': report_data,
        'summary': {
            'total_users': total_users,
            'users_over_threshold': users_over_threshold,
            'total_storage_used_gb': round(total_storage_used, 2),
            'total_storage_quota_gb': round(total_storage_quota, 2),
            'avg_usage_percent': avg_usage_percent
        }
    }

    return {
        'report_type': 'storage_usage',
        'date_generated': datetime.now().isoformat(),
        'total_users': total_users,
        'data': report_data,
        'summary': {
            'users_over_threshold': users_over_threshold,
            'total_storage_used_gb': round(total_storage_used, 2),
            'total_storage_quota_gb': round(total_storage_quota, 2),
            'avg_usage_percent': avg_usage_percent
        }
    }


def get_email_usage_report(start_date, end_date=None, scope='all', target=None):
    """
    Generate email usage statistics report.

    Fetches email sending and receiving statistics for all users, a specific user,
    or all members of a group over a date range. Useful for detecting spam senders,
    identifying inactive mailboxes, and understanding communication patterns.

    Args:
        start_date (str): Start date in YYYY-MM-DD format or relative (-7d, -30d)
        end_date (str, optional): End date in YYYY-MM-DD format (default: today)
        scope (str): Report scope - 'all' (domain-wide), 'user', or 'group'
        target (str, optional): Email address of user or group (required if scope is 'user' or 'group')

    Yields:
        dict: Progress updates with status, message, and optional report_data
            - status: 'info', 'success', or 'error'
            - message: Human-readable status message
            - report_data: List of user email usage data (on success)
            - summary: Aggregate statistics (on success)

    Returns:
        dict: Complete report data structure or None on error
            - report_type: 'email_usage'
            - date_generated: ISO timestamp
            - period: Date range of the report
            - data: List of user email usage records
    """
    gam_cmd = get_gam_command()

    scope_msg = {
        'all': 'all users',
        'user': f'user {target}',
        'group': f'group {target}'
    }

    yield {
        'status': 'info',
        'message': f'Fetching email usage statistics for {scope_msg.get(scope, "all users")}...'
    }

    # Build GAM command based on scope
    if scope == 'user':
        # For a specific user, use user-level report
        cmd = [
            gam_cmd, 'user', target,
            'report', 'usage',
            'parameters', 'gmail:num_emails_sent,gmail:num_emails_received',
            'start', start_date
        ]
    elif scope == 'group':
        # For a group, get all members and aggregate their data
        # First, get group members
        yield {
            'status': 'info',
            'message': f'Fetching members of group {target}...'
        }

        # We'll handle group reporting by getting members and then individual reports
        # This will be processed differently below
        cmd = None  # Set to None to handle separately
    else:  # scope == 'all'
        # Domain-wide report
        cmd = [
            gam_cmd, 'report', 'usage', 'customer',
            'parameters', 'gmail:num_emails_sent,gmail:num_emails_received',
            'start', start_date
        ]

    if end_date and cmd:
        cmd.extend(['end', end_date])

    # Handle group scope specially
    if scope == 'group':
        # Get group members first
        try:
            members_cmd = [gam_cmd, 'print', 'group-members', 'group', target]
            members_result = subprocess.run(
                members_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if members_result.returncode != 0:
                error_msg = f'Failed to fetch group members: {members_result.stderr}'
                log_error("Email Usage Report", error_msg)
                yield {
                    'status': 'error',
                    'message': error_msg
                }
                return None

            # Parse group members
            members_reader = csv.DictReader(io.StringIO(members_result.stdout))
            group_members = set()
            for row in members_reader:
                email = row.get('email', row.get('Email', ''))
                if email:
                    group_members.add(email.lower())

            if not group_members:
                yield {
                    'status': 'error',
                    'message': f'No members found in group {target}'
                }
                return None

            yield {
                'status': 'info',
                'message': f'Found {len(group_members)} members in group. Fetching email usage...'
            }

            # Now get domain-wide report and filter for group members
            cmd = [
                gam_cmd, 'report', 'usage', 'customer',
                'parameters', 'gmail:num_emails_sent,gmail:num_emails_received',
                'start', start_date
            ]
            if end_date:
                cmd.extend(['end', end_date])

        except Exception as e:
            error_msg = f'Error fetching group members: {str(e)}'
            log_error("Email Usage Report", error_msg)
            yield {
                'status': 'error',
                'message': error_msg
            }
            return None
    else:
        group_members = None

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            error_msg = f'Failed to fetch email usage: {result.stderr}'
            log_error("Email Usage Report", error_msg)
            yield {
                'status': 'error',
                'message': error_msg
            }
            return None

        # Parse CSV
        reader = csv.DictReader(io.StringIO(result.stdout))
        report_data = []
        user_aggregates = {}

        for row in reader:
            # GAM report usage returns daily data, we need to aggregate by user
            email = row.get('email', row.get('user_email', ''))

            # If group scope, filter to only group members
            if group_members is not None and email.lower() not in group_members:
                continue

            try:
                emails_sent = int(row.get('gmail:num_emails_sent', 0) or 0)
                emails_received = int(row.get('gmail:num_emails_received', 0) or 0)
            except (ValueError, TypeError):
                emails_sent = 0
                emails_received = 0

            date = row.get('date', '')

            # Aggregate by user
            if email not in user_aggregates:
                user_aggregates[email] = {
                    'email': email,
                    'emails_sent': 0,
                    'emails_received': 0,
                    'total_emails': 0
                }

            user_aggregates[email]['emails_sent'] += emails_sent
            user_aggregates[email]['emails_received'] += emails_received
            user_aggregates[email]['total_emails'] += emails_sent + emails_received

        # Convert to list
        report_data = list(user_aggregates.values())

        # Sort by total emails (highest first)
        report_data.sort(key=lambda x: x['total_emails'], reverse=True)

        # Calculate summary
        total_sent = sum(u['emails_sent'] for u in report_data)
        total_received = sum(u['emails_received'] for u in report_data)

        scope_detail = {
            'all': f'{len(report_data)} users (domain-wide)',
            'user': f'user {target}',
            'group': f'{len(report_data)} members of group {target}'
        }

        yield {
            'status': 'success',
            'message': f'Generated email usage report for {scope_detail.get(scope, str(len(report_data)) + " users")}',
            'report_data': report_data,
            'summary': {
                'total_sent': total_sent,
                'total_received': total_received,
                'total_emails': total_sent + total_received,
                'total_users': len(report_data),
                'scope': scope,
                'target': target if scope in ['user', 'group'] else 'all'
            }
        }

        return {
            'report_type': 'email_usage',
            'date_generated': datetime.now().isoformat(),
            'period': f'{start_date} to {end_date or "today"}',
            'data': report_data,
            'summary': {
                'total_sent': total_sent,
                'total_received': total_received,
                'total_emails': total_sent + total_received
            }
        }

    except subprocess.TimeoutExpired:
        error_msg = 'Report generation timed out (120 seconds)'
        log_error("Email Usage Report", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None
    except Exception as e:
        error_msg = f'Exception generating report: {str(e)}'
        log_error("Email Usage Report", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None


def get_admin_activity_report(start_date='-30d', event_type='all'):
    """
    Generate admin activity audit report.

    Fetches administrator actions for compliance auditing, security investigation,
    and accountability tracking.

    Args:
        start_date (str): Start date in YYYY-MM-DD format or relative (-7d, -30d)
        event_type (str): Filter by event type or 'all' for all events
            Common types: 'user_settings', 'group_settings', 'domain_settings'

    Yields:
        dict: Progress updates with status, message, and optional report_data
            - status: 'info', 'success', or 'error'
            - message: Human-readable status message
            - report_data: List of admin activity events (on success)

    Returns:
        dict: Complete report data structure or None on error
            - report_type: 'admin_activity'
            - date_generated: ISO timestamp
            - period: Date range of the report
            - total_events: Count of events
            - data: List of admin activity records
    """
    gam_cmd = get_gam_command()

    yield {
        'status': 'info',
        'message': 'Fetching admin activity logs...'
    }

    # Build command
    cmd = [
        gam_cmd, 'report', 'admin',
        'start', start_date
    ]

    if event_type != 'all':
        cmd.extend(['event', event_type])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            error_msg = f'Failed to fetch admin activity: {result.stderr}'
            log_error("Admin Activity Report", error_msg)
            yield {
                'status': 'error',
                'message': error_msg
            }
            return None

        # Parse CSV
        reader = csv.DictReader(io.StringIO(result.stdout))
        report_data = []
        first_row_fields = None

        for i, row in enumerate(reader):
            # Debug: Capture field names from first row
            if i == 0 and not first_row_fields:
                first_row_fields = list(row.keys())
                yield {
                    'status': 'info',
                    'message': f'CSV fields available: {", ".join(first_row_fields)}'
                }

            # GAM admin report fields - try multiple possible field names
            # Admin/Actor email
            admin_email = (row.get('admin', '') or
                          row.get('actor', '') or
                          row.get('actor_email', '') or
                          row.get('email', '') or
                          row.get('Admin', ''))

            # Event name
            event_name = (row.get('event', '') or
                         row.get('event_name', '') or
                         row.get('eventName', '') or
                         row.get('Event', ''))

            # Event type
            event_type_val = (row.get('type', '') or
                             row.get('event_type', '') or
                             row.get('eventType', '') or
                             row.get('Type', ''))

            # Timestamp
            timestamp = (row.get('time', '') or
                        row.get('timestamp', '') or
                        row.get('date', '') or
                        row.get('Time', ''))

            # Extract all other fields as details (excluding the main ones)
            excluded_keys = {'admin', 'actor', 'actor_email', 'email', 'Admin',
                           'event', 'event_name', 'eventName', 'Event',
                           'type', 'event_type', 'eventType', 'Type',
                           'time', 'timestamp', 'date', 'Time'}

            parameters = []
            for key, value in row.items():
                if key not in excluded_keys and value:  # Only include non-empty values
                    parameters.append(f"{key}={value}")
            details = ', '.join(parameters) if parameters else ''

            # If all main fields are empty, show all row data in details as fallback
            if not admin_email and not event_name and not event_type_val:
                all_data = []
                for key, value in row.items():
                    if value:
                        all_data.append(f"{key}={value}")
                if all_data:
                    details = ', '.join(all_data)
                    # Try to extract any email-like value for admin field
                    for key, value in row.items():
                        if 'email' in key.lower() or '@' in str(value):
                            admin_email = value
                            break

            report_data.append({
                'admin': admin_email,
                'event': event_name,
                'type': event_type_val,
                'timestamp': timestamp,
                'details': details
            })

        # Sort by timestamp (newest first)
        report_data.sort(key=lambda x: x['timestamp'], reverse=True)

        # Calculate event type distribution
        event_types = {}
        for event in report_data:
            event_type_key = event['type']
            event_types[event_type_key] = event_types.get(event_type_key, 0) + 1

        yield {
            'status': 'success',
            'message': f'Generated admin activity report with {len(report_data)} events',
            'report_data': report_data,
            'summary': {
                'total_events': len(report_data),
                'event_types': event_types,
                'unique_admins': len(set(e['admin'] for e in report_data))
            }
        }

        return {
            'report_type': 'admin_activity',
            'date_generated': datetime.now().isoformat(),
            'period': f'{start_date} to today',
            'total_events': len(report_data),
            'data': report_data,
            'summary': {
                'event_types': event_types,
                'unique_admins': len(set(e['admin'] for e in report_data))
            }
        }

    except subprocess.TimeoutExpired:
        error_msg = 'Report generation timed out (120 seconds)'
        log_error("Admin Activity Report", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None
    except Exception as e:
        error_msg = f'Exception generating report: {str(e)}'
        log_error("Admin Activity Report", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None


def get_never_logged_in_report(include_suspended=False):
    """
    Generate report of users who have never logged in.

    Identifies users who have never logged in to their account. Useful for
    identifying unused accounts and potential issues with onboarding.

    Args:
        include_suspended (bool): Include suspended users in report (default: False)

    Yields:
        dict: Progress updates with status, message, and optional report_data
            - status: 'info', 'success', or 'error'
            - message: Human-readable status message
            - report_data: List of users who never logged in (on success)

    Returns:
        dict: Complete report data structure or None on error
            - report_type: 'never_logged_in'
            - date_generated: ISO timestamp
            - total_never_logged_in: Count of users
            - data: List of user records
    """
    # Reuse login activity report with filtering
    yield {
        'status': 'info',
        'message': 'Identifying users who have never logged in...'
    }

    # Get full login activity report
    report_gen = get_login_activity_report(date_range_days=30, include_suspended=include_suspended)

    full_report = None
    for progress in report_gen:
        # Pass through progress updates
        yield progress

        # Capture final result
        if progress.get('status') == 'success':
            full_report = progress

    if not full_report:
        yield {
            'status': 'error',
            'message': 'Failed to generate login activity report'
        }
        return None

    # Filter for users who never logged in
    all_users = full_report.get('report_data', [])
    never_logged_in_users = [
        user for user in all_users
        if user['days_since_login'] is None
    ]

    yield {
        'status': 'success',
        'message': f'Found {len(never_logged_in_users)} users who have never logged in',
        'report_data': never_logged_in_users
    }

    return {
        'report_type': 'never_logged_in',
        'date_generated': datetime.now().isoformat(),
        'total_never_logged_in': len(never_logged_in_users),
        'data': never_logged_in_users
    }


def get_inactive_users_report(inactive_threshold_days=90, min_account_age_days=30, include_suspended=False):
    """
    Generate report of inactive users.

    Identifies users who haven't logged in for a specified period. Useful for
    license reclamation and account cleanup.

    Args:
        inactive_threshold_days (int): Days of inactivity to flag (default: 90)
        min_account_age_days (int): Minimum account age to consider (default: 30)
            Avoids flagging newly created accounts as inactive
        include_suspended (bool): Include suspended users in report (default: False)

    Yields:
        dict: Progress updates with status, message, and optional report_data
            - status: 'info', 'success', or 'error'
            - message: Human-readable status message
            - report_data: List of inactive users (on success)

    Returns:
        dict: Complete report data structure or None on error
            - report_type: 'inactive_users'
            - date_generated: ISO timestamp
            - threshold_days: Inactivity threshold used
            - total_inactive: Count of inactive users
            - data: List of inactive user records
    """
    # Reuse login activity report with filtering
    yield {
        'status': 'info',
        'message': f'Identifying users inactive for {inactive_threshold_days}+ days...'
    }

    # Get full login activity report
    report_gen = get_login_activity_report(date_range_days=inactive_threshold_days, include_suspended=include_suspended)

    full_report = None
    for progress in report_gen:
        # Pass through progress updates
        yield progress

        # Capture final result
        if progress.get('status') == 'success':
            full_report = progress

    if not full_report:
        yield {
            'status': 'error',
            'message': 'Failed to generate login activity report'
        }
        return None

    # Filter for inactive users
    all_users = full_report.get('report_data', [])
    inactive_users = [
        user for user in all_users
        if user['days_since_login'] and user['days_since_login'] >= inactive_threshold_days
    ]

    yield {
        'status': 'success',
        'message': f'Found {len(inactive_users)} inactive users (> {inactive_threshold_days} days)',
        'report_data': inactive_users
    }

    return {
        'report_type': 'inactive_users',
        'date_generated': datetime.now().isoformat(),
        'threshold_days': inactive_threshold_days,
        'total_inactive': len(inactive_users),
        'data': inactive_users
    }


def export_report_to_csv(report_data, output_path):
    """
    Export report data to CSV file.

    Args:
        report_data (dict): Report data structure from any report function
        output_path (str): Path to save CSV file

    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        data = report_data.get('data', [])

        if not data:
            return False

        # Get fieldnames from first record
        fieldnames = list(data[0].keys())

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        return True

    except Exception as e:
        log_error("Export Report", f"Failed to export report: {str(e)}")
        return False
