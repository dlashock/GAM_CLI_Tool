"""
Email operations module for GAM Admin Tool.

This module provides backend functions for executing GAM commands
related to email operations including messages, delegates, signatures,
forwarding, labels, and filters.
"""

import subprocess
import tempfile
import os
import shlex
from utils.logger import log_error
from utils.gam_check import get_gam_path


def _get_gam_command():
    """
    Get the GAM command to use (handles PATH and non-PATH installations).

    Returns:
        str or list: GAM command ('gam' or full path)
    """
    gam_path = get_gam_path()
    return gam_path if gam_path else 'gam'


def delete_messages(users, query, date_from=None, date_to=None, dry_run=False):
    """
    Delete messages for users based on query string.

    Args:
        users (list): List of user email addresses
        query (str): Gmail search query (e.g., "from:sender@example.com")
        date_from (str, optional): Start date for query (YYYY/MM/DD format)
        date_to (str, optional): End date for query (YYYY/MM/DD format)
        dry_run (bool): If True, simulate the operation without executing

    Yields:
        dict: Progress updates with keys: status, email, current, total

    Returns:
        dict: Summary with keys: success_count, failure_count, errors
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    # Build query with date range if provided
    full_query = query
    if date_from:
        full_query += f" after:{date_from}"
    if date_to:
        full_query += f" before:{date_to}"

    for i, user_email in enumerate(users, start=1):
        yield {
            "status": "processing",
            "email": user_email,
            "current": i,
            "total": total,
            "message": f"Deleting messages for {user_email}..."
        }

        try:
            # Dry run mode
            if dry_run:
                success_count += 1
                yield {
                    "status": "dry-run",
                    "email": user_email,
                    "message": f"[DRY RUN] Would delete messages for {user_email} matching query: {full_query}"
                }
                continue

            # Build GAM command
            cmd = [
                _get_gam_command(), 'user', user_email,
                'delete', 'messages',
                'query', full_query,
                'trash', 'excludetrash'
            ]

            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                success_count += 1
                yield {
                    "status": "success",
                    "email": user_email,
                    "message": f"✓ Successfully deleted messages for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Delete Messages", f"Failed for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Failed for {user_email}: {error_msg}"
                }

        except subprocess.TimeoutExpired:
            failure_count += 1
            error_msg = "Command timed out after 60 seconds"
            errors.append((user_email, error_msg))
            log_error("Delete Messages", f"Timeout for {user_email}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Timeout for {user_email}"
            }
        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Delete Messages", f"Exception for {user_email}: {error_msg}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Error for {user_email}: {error_msg}"
            }

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def add_delegate(users, delegate_email):
    """
    Add a delegate to user mailboxes.

    Args:
        users (list): List of user email addresses
        delegate_email (str): Email address of the delegate to add

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
            "status": "processing",
            "email": user_email,
            "current": i,
            "total": total,
            "message": f"Adding delegate {delegate_email} to {user_email}..."
        }

        try:
            cmd = [_get_gam_command(), 'user', user_email, 'delegate', 'to', delegate_email]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    "status": "success",
                    "email": user_email,
                    "message": f"✓ Added delegate for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Add Delegate", f"Failed for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Failed for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Add Delegate", f"Exception for {user_email}: {error_msg}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Error for {user_email}"
            }

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def remove_delegate(users, delegate_email):
    """
    Remove a delegate from user mailboxes.

    Args:
        users (list): List of user email addresses
        delegate_email (str): Email address of the delegate to remove

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
            "status": "processing",
            "email": user_email,
            "current": i,
            "total": total,
            "message": f"Removing delegate {delegate_email} from {user_email}..."
        }

        try:
            cmd = [_get_gam_command(), 'user', user_email, 'delegate', 'delete', delegate_email]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    "status": "success",
                    "email": user_email,
                    "message": f"✓ Removed delegate for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Remove Delegate", f"Failed for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Failed for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Remove Delegate", f"Exception for {user_email}: {error_msg}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Error for {user_email}"
            }

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def set_signature(users, signature_html):
    """
    Set email signature for users.

    Args:
        users (list): List of user email addresses
        signature_html (str): HTML content of the signature

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    # Create temporary file for signature
    temp_fd, temp_path = tempfile.mkstemp(suffix='.html', text=True)
    try:
        # Write signature to temp file
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            f.write(signature_html)

        for i, user_email in enumerate(users, start=1):
            yield {
                "status": "processing",
                "email": user_email,
                "current": i,
                "total": total,
                "message": f"Setting signature for {user_email}..."
            }

            try:
                cmd = [_get_gam_command(), 'user', user_email, 'signature', 'file', temp_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    success_count += 1
                    yield {
                        "status": "success",
                        "email": user_email,
                        "message": f"✓ Set signature for {user_email}"
                    }
                else:
                    failure_count += 1
                    error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                    errors.append((user_email, error_msg))
                    log_error("Set Signature", f"Failed for {user_email}: {error_msg}")
                    yield {
                        "status": "error",
                        "email": user_email,
                        "message": f"✗ Failed for {user_email}"
                    }

            except Exception as e:
                failure_count += 1
                error_msg = str(e)
                errors.append((user_email, error_msg))
                log_error("Set Signature", f"Exception for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Error for {user_email}"
                }

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def remove_signature(users):
    """
    Remove email signature for users.

    Args:
        users (list): List of user email addresses

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
            "status": "processing",
            "email": user_email,
            "current": i,
            "total": total,
            "message": f"Removing signature for {user_email}..."
        }

        try:
            cmd = [_get_gam_command(), 'user', user_email, 'signature', '']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    "status": "success",
                    "email": user_email,
                    "message": f"✓ Removed signature for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Remove Signature", f"Failed for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Failed for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Remove Signature", f"Exception for {user_email}: {error_msg}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Error for {user_email}"
            }

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def enable_forwarding(users, forward_to):
    """
    Enable email forwarding for users.

    Args:
        users (list): List of user email addresses
        forward_to (str): Email address to forward to

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
            "status": "processing",
            "email": user_email,
            "current": i,
            "total": total,
            "message": f"Enabling forwarding for {user_email} to {forward_to}..."
        }

        try:
            cmd = [_get_gam_command(), 'user', user_email, 'forward', 'on', forward_to]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    "status": "success",
                    "email": user_email,
                    "message": f"✓ Enabled forwarding for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Enable Forwarding", f"Failed for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Failed for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Enable Forwarding", f"Exception for {user_email}: {error_msg}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Error for {user_email}"
            }

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def disable_forwarding(users):
    """
    Disable email forwarding for users.

    Args:
        users (list): List of user email addresses

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
            "status": "processing",
            "email": user_email,
            "current": i,
            "total": total,
            "message": f"Disabling forwarding for {user_email}..."
        }

        try:
            cmd = [_get_gam_command(), 'user', user_email, 'forward', 'off']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    "status": "success",
                    "email": user_email,
                    "message": f"✓ Disabled forwarding for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Disable Forwarding", f"Failed for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Failed for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Disable Forwarding", f"Exception for {user_email}: {error_msg}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Error for {user_email}"
            }

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def create_label(users, label_name):
    """
    Create a label for users.

    Args:
        users (list): List of user email addresses
        label_name (str): Name of the label to create

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
            "status": "processing",
            "email": user_email,
            "current": i,
            "total": total,
            "message": f"Creating label '{label_name}' for {user_email}..."
        }

        try:
            cmd = [_get_gam_command(), 'user', user_email, 'label', label_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    "status": "success",
                    "email": user_email,
                    "message": f"✓ Created label for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Create Label", f"Failed for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Failed for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Create Label", f"Exception for {user_email}: {error_msg}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Error for {user_email}"
            }

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def delete_label(users, label_name):
    """
    Delete a label for users.

    Args:
        users (list): List of user email addresses
        label_name (str): Name of the label to delete

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
            "status": "processing",
            "email": user_email,
            "current": i,
            "total": total,
            "message": f"Deleting label '{label_name}' for {user_email}..."
        }

        try:
            cmd = [_get_gam_command(), 'user', user_email, 'delete', 'label', label_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    "status": "success",
                    "email": user_email,
                    "message": f"✓ Deleted label for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Delete Label", f"Failed for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Failed for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Delete Label", f"Exception for {user_email}: {error_msg}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Error for {user_email}"
            }

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def create_filter(users, from_addr=None, to_addr=None, subject=None, has_words=None, action_label=None):
    """
    Create an email filter for users.

    Args:
        users (list): List of user email addresses
        from_addr (str, optional): Filter messages from this address
        to_addr (str, optional): Filter messages to this address
        subject (str, optional): Filter messages with this subject
        has_words (str, optional): Filter messages containing these words
        action_label (str, optional): Apply this label to filtered messages

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    # Build filter criteria
    filter_parts = [_get_gam_command(), 'user', '__USER__', 'filter']

    if from_addr:
        filter_parts.extend(['from', from_addr])
    if to_addr:
        filter_parts.extend(['to', to_addr])
    if subject:
        filter_parts.extend(['subject', subject])
    if has_words:
        filter_parts.extend(['haswords', has_words])
    if action_label:
        filter_parts.extend(['label', action_label])

    for i, user_email in enumerate(users, start=1):
        yield {
            "status": "processing",
            "email": user_email,
            "current": i,
            "total": total,
            "message": f"Creating filter for {user_email}..."
        }

        try:
            # Replace __USER__ placeholder with actual email
            cmd = [user_email if part == '__USER__' else part for part in filter_parts]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    "status": "success",
                    "email": user_email,
                    "message": f"✓ Created filter for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Create Filter", f"Failed for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Failed for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Create Filter", f"Exception for {user_email}: {error_msg}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Error for {user_email}"
            }

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def delete_filter(users, filter_id):
    """
    Delete an email filter for users.

    Args:
        users (list): List of user email addresses
        filter_id (str): ID of the filter to delete

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
            "status": "processing",
            "email": user_email,
            "current": i,
            "total": total,
            "message": f"Deleting filter {filter_id} for {user_email}..."
        }

        try:
            cmd = [_get_gam_command(), 'user', user_email, 'delete', 'filter', filter_id]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                success_count += 1
                yield {
                    "status": "success",
                    "email": user_email,
                    "message": f"✓ Deleted filter for {user_email}"
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                log_error("Delete Filter", f"Failed for {user_email}: {error_msg}")
                yield {
                    "status": "error",
                    "email": user_email,
                    "message": f"✗ Failed for {user_email}"
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Delete Filter", f"Exception for {user_email}: {error_msg}")
            yield {
                "status": "error",
                "email": user_email,
                "message": f"✗ Error for {user_email}"
            }

    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "errors": errors
    }


def list_filters(user_email):
    """
    List all filters for a user.

    This is a helper function for the GUI to populate filter selection.

    Args:
        user_email (str): Email address of the user

    Returns:
        list: List of tuples (filter_id, description) or empty list on error
    """
    try:
        cmd = [_get_gam_command(), 'user', user_email, 'show', 'filters']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            log_error("List Filters", f"Failed for {user_email}: {result.stderr[:200]}")
            return []

        # Parse output to extract filter IDs
        # GAM output format varies, so we'll return raw output for now
        # GUI can parse or display as needed
        filters = []
        lines = result.stdout.split('\n')

        for line in lines:
            # Look for filter ID patterns (typically "Filter ID: xxx" or similar)
            if 'filter' in line.lower() and ':' in line:
                filters.append((line.strip(), line.strip()))

        return filters

    except Exception as e:
        log_error("List Filters", f"Exception for {user_email}: {str(e)}")
        return []
