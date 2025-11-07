"""
Base Operations Module for GAM Admin Tool.

Provides common backend functionality for all GAM operations including:
- GAM command execution wrappers
- Bulk operation handling
- Progress yielding patterns
- Error handling and logging
- Input validation

All operation modules should use these functions for consistency.
"""

import subprocess
import time
import re
from utils.logger import log_error
from utils.gam_check import get_gam_path


def get_gam_command():
    """
    Get the GAM command to use (handles PATH and non-PATH installations).

    Returns:
        str: GAM command ('gam' or full path)
    """
    gam_path = get_gam_path()
    return gam_path if gam_path else 'gam'


def execute_gam_command(command_args, timeout=30, operation_name="GAM Operation"):
    """
    Execute a GAM command and return the result.

    Args:
        command_args (list): GAM command arguments (including 'gam' or path)
        timeout (int): Timeout in seconds (default: 30)
        operation_name (str): Name of operation for logging

    Returns:
        subprocess.CompletedProcess: Command result

    Raises:
        subprocess.TimeoutExpired: If command times out
        Exception: For other execution errors
    """
    try:
        result = subprocess.run(
            command_args,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # Log errors if command failed
        if result.returncode != 0 and result.stderr:
            log_error(operation_name, f"Command failed: {result.stderr[:200]}")

        return result

    except subprocess.TimeoutExpired as e:
        error_msg = f"Command timed out after {timeout} seconds"
        log_error(operation_name, error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Command execution failed: {str(e)}"
        log_error(operation_name, error_msg)
        raise


def execute_gam_command_with_retry(command_args, max_retries=3, backoff_factor=2,
                                   timeout=30, operation_name="GAM Operation"):
    """
    Execute GAM command with retry logic for rate limiting.

    Implements exponential backoff for handling API rate limits.

    Args:
        command_args (list): GAM command as list
        max_retries (int): Maximum retry attempts (default: 3)
        backoff_factor (int): Exponential backoff multiplier (default: 2)
        timeout (int): Timeout in seconds (default: 30)
        operation_name (str): Name for logging

    Returns:
        subprocess.CompletedProcess: Command result

    Raises:
        Exception: If all retries exhausted
    """
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                command_args,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Check for rate limiting
            if result.stderr and 'rate limit' in result.stderr.lower():
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** attempt
                    time.sleep(sleep_time)
                    continue

            # Check for quota exceeded
            if result.stderr and 'quota exceeded' in result.stderr.lower():
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** attempt
                    time.sleep(sleep_time)
                    continue

            return result

        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                sleep_time = backoff_factor ** attempt
                time.sleep(sleep_time)
                continue
            error_msg = f"Command timed out after {max_retries} attempts"
            log_error(operation_name, error_msg)
            raise Exception(error_msg)

    error_msg = f"Command failed after {max_retries} attempts"
    log_error(operation_name, error_msg)
    raise Exception(error_msg)


def execute_bulk_operation(operation_name, users, operation_func, *args, dry_run=False, **kwargs):
    """
    Execute an operation for multiple users with progress tracking.

    This is a generic wrapper for bulk operations that provides:
    - Progress yielding for GUI updates
    - Success/failure tracking
    - Error logging
    - Dry-run support

    Args:
        operation_name (str): Name of operation for logging/display
        users (list): List of user emails to process
        operation_func (callable): Function to execute for each user
                                  Should accept (user_email, *args, **kwargs)
                                  Should return (success, message)
        *args: Additional arguments to pass to operation_func
        dry_run (bool): If True, preview without executing
        **kwargs: Additional keyword arguments for operation_func

    Yields:
        dict: Progress updates with keys:
            - status: 'processing', 'success', 'error', or 'dry-run'
            - email: Current user email
            - current: Current iteration number
            - total: Total number of users
            - message: Status message

    Returns:
        dict: Summary with keys:
            - success_count: Number of successful operations
            - failure_count: Number of failed operations
            - errors: List of (email, error_message) tuples
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
            'message': f"Processing {user_email}... ({i}/{total})"
        }

        try:
            if dry_run:
                # Dry run - just show what would happen
                yield {
                    'status': 'dry-run',
                    'email': user_email,
                    'current': i,
                    'total': total,
                    'message': f"[DRY RUN] Would process {user_email}"
                }
                success_count += 1
            else:
                # Execute actual operation
                success, message = operation_func(user_email, *args, **kwargs)

                if success:
                    success_count += 1
                    yield {
                        'status': 'success',
                        'email': user_email,
                        'current': i,
                        'total': total,
                        'message': f"✓ {message}"
                    }
                else:
                    failure_count += 1
                    errors.append((user_email, message))
                    yield {
                        'status': 'error',
                        'email': user_email,
                        'current': i,
                        'total': total,
                        'message': f"✗ {message}"
                    }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error(operation_name, f"Exception for {user_email}: {error_msg}")
            yield {
                'status': 'error',
                'email': user_email,
                'current': i,
                'total': total,
                'message': f"✗ Error for {user_email}: {error_msg[:100]}"
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def build_gam_command(base_parts, user_email=None, additional_parts=None):
    """
    Build a complete GAM command with proper formatting.

    Args:
        base_parts (list): Base command parts (e.g., ['user', 'EMAIL', 'delete', 'messages'])
        user_email (str): User email to substitute for 'EMAIL' placeholder
        additional_parts (list): Additional command parts to append

    Returns:
        list: Complete command ready for subprocess.run()
    """
    gam_cmd = get_gam_command()
    command = [gam_cmd]

    # Add base parts, substituting email if provided
    for part in base_parts:
        if part == 'EMAIL' or part == '__USER__':
            if user_email:
                command.append(user_email)
            else:
                command.append(part)  # Keep placeholder if no email provided
        else:
            command.append(part)

    # Add additional parts
    if additional_parts:
        command.extend(additional_parts)

    return command


def validate_email(email):
    """
    Validate email address format.

    Args:
        email (str): Email address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_date(date_str, format='YYYY/MM/DD'):
    """
    Validate date string format.

    Args:
        date_str (str): Date string to validate
        format (str): Expected format (default: 'YYYY/MM/DD')

    Returns:
        bool: True if valid, False otherwise
    """
    if format == 'YYYY/MM/DD':
        pattern = r'^\d{4}/\d{2}/\d{2}$'
        if re.match(pattern, date_str):
            try:
                year, month, day = map(int, date_str.split('/'))
                # Basic validation
                if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                    return True
            except:
                pass

    elif format == 'YYYY-MM-DD':
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if re.match(pattern, date_str):
            try:
                year, month, day = map(int, date_str.split('-'))
                if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                    return True
            except:
                pass

    return False


def get_user_friendly_error(gam_error):
    """
    Convert GAM error to user-friendly message.

    Based on common GAM error patterns, provides helpful messages and
    potential solutions.

    Args:
        gam_error (str): Raw GAM error message

    Returns:
        tuple: (user_message, help_link or None)
    """
    error_lower = gam_error.lower()

    # OAuth/Authentication errors
    if any(keyword in error_lower for keyword in ['oauth', 'credentials', 'authentication', 'not authorized']):
        return (
            'GAM is not authenticated. Please run "gam oauth create".',
            'https://github.com/GAM-team/GAM/wiki/Authorization'
        )

    # Permission errors
    if any(keyword in error_lower for keyword in ['insufficient', 'permission denied']):
        return (
            'Insufficient permissions. Check admin role settings in Google Workspace.',
            'https://support.google.com/a/answer/2405986'
        )

    # Rate limiting
    if any(keyword in error_lower for keyword in ['rate limit', 'quota exceeded']):
        return (
            'Rate limit exceeded. Please wait a few minutes and try again.',
            'https://developers.google.com/admin-sdk/directory/v1/limits'
        )

    # Resource not found
    if any(keyword in error_lower for keyword in ['not found', 'does not exist']):
        return (
            'Resource not found. Verify the email address or ID is correct.',
            None
        )

    # Invalid parameters
    if any(keyword in error_lower for keyword in ['invalid', 'bad request']):
        return (
            'Invalid parameter. Check your input and try again.',
            None
        )

    # Fallback - show truncated error
    return (f"Operation failed: {gam_error[:200]}", None)


def format_progress_message(operation, email, current, total, status='processing'):
    """
    Format a standardized progress message.

    Args:
        operation (str): Operation name (e.g., "Deleting messages")
        email (str): User email
        current (int): Current iteration
        total (int): Total iterations
        status (str): Status ('processing', 'success', 'error')

    Returns:
        str: Formatted message
    """
    percentage = (current / total * 100) if total > 0 else 0

    if status == 'processing':
        return f"{operation} for {email}... ({current}/{total}, {percentage:.1f}%)"
    elif status == 'success':
        return f"✓ {operation} completed for {email} ({current}/{total})"
    elif status == 'error':
        return f"✗ {operation} failed for {email} ({current}/{total})"
    else:
        return f"{operation} - {email} ({current}/{total})"


def parse_gam_user_info(gam_output):
    """
    Parse GAM user info output into a dictionary.

    Args:
        gam_output (str): Output from 'gam info user' command

    Returns:
        dict: Parsed user information
    """
    user_info = {}

    # Parse line by line
    for line in gam_output.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            user_info[key.strip()] = value.strip()

    return user_info


def chunk_list(items, chunk_size):
    """
    Split a list into chunks of specified size.

    Useful for batch operations where processing all items at once
    would be too slow or hit API limits.

    Args:
        items (list): List to chunk
        chunk_size (int): Size of each chunk

    Yields:
        list: Chunks of the original list
    """
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]


def estimate_operation_time(count, seconds_per_item=1.0):
    """
    Estimate operation completion time.

    Args:
        count (int): Number of items to process
        seconds_per_item (float): Average seconds per item

    Returns:
        str: Human-readable time estimate (e.g., "5 minutes", "2 hours")
    """
    total_seconds = count * seconds_per_item

    if total_seconds < 60:
        return f"{int(total_seconds)} seconds"
    elif total_seconds < 3600:
        minutes = int(total_seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = int(total_seconds / 3600)
        minutes = int((total_seconds % 3600) / 60)
        if minutes > 0:
            return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours != 1 else ''}"
