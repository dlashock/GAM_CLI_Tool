"""
Drive Operations Module for GAM Admin Tool.

This module provides backend functions for Google Drive operations including:
- Security scanning (non-domain ACL detection)
- File operations (search, transfer, delete)
- Permission management
- Drive cleanup operations

All functions yield progress updates for GUI display.
"""

import subprocess
import json
import csv
import io
from datetime import datetime
from modules.base_operations import get_gam_command
from utils.logger import log_error, log_info


def scan_non_domain_acls(users, domain, include_anyone_links=True, dry_run=False):
    """
    Scan users' Drive files for non-domain ACLs (external sharing).

    This is a CRITICAL security function for K-12 environments to identify
    files shared outside the organization.

    Args:
        users (list): List of user email addresses to scan
        domain (str): Organization domain (e.g., 'school.edu')
        include_anyone_links (bool): Include 'anyone with link' permissions
        dry_run (bool): If True, only report without taking action

    Yields:
        dict: Progress updates with keys:
            - status: 'processing' | 'found_external' | 'clean' | 'error'
            - user: User email being scanned
            - file_id: File ID if external ACL found
            - file_name: File name if external ACL found
            - external_emails: List of external emails with access
            - permission_type: 'user' | 'group' | 'anyone' | 'domain'
            - role: 'reader' | 'writer' | 'owner'
            - current: Current user number
            - total: Total users to scan
            - message: Human-readable status message

    Returns:
        dict: Summary with keys:
            - users_scanned: Number of users scanned
            - files_scanned: Total files scanned
            - files_with_external_acls: Count of files with external sharing
            - external_shares_found: Total external permissions found
            - findings: List of dicts with detailed findings
    """
    total = len(users)
    users_scanned = 0
    files_scanned = 0
    files_with_external_acls = 0
    external_shares_found = 0
    findings = []

    gam_cmd = get_gam_command()

    for i, user_email in enumerate(users, start=1):
        yield {
            'status': 'processing',
            'user': user_email,
            'current': i,
            'total': total,
            'message': f'Scanning Drive files for {user_email}...'
        }

        try:
            # Get all files with permissions information
            # Using GAM command to print file list with permissions
            cmd = [
                gam_cmd, 'user', user_email,
                'print', 'filelist',
                'fields', 'id,name,permissions,owners'
            ]

            log_info("Drive ACL Scan", f"Scanning files for {user_email}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for large drives
            )

            if result.returncode != 0:
                error_msg = result.stderr[:500] if result.stderr else "Unknown error"
                yield {
                    'status': 'error',
                    'user': user_email,
                    'message': f'✗ Failed to scan {user_email}: {error_msg}'
                }
                log_error("Drive ACL Scan", f"Failed for {user_email}: {error_msg}")
                continue

            # Parse CSV output from GAM
            reader = csv.DictReader(io.StringIO(result.stdout))

            user_external_files = []
            user_files_count = 0

            for row in reader:
                user_files_count += 1
                file_id = row.get('id', '')
                file_name = row.get('name', '')
                permissions_str = row.get('permissions', '')

                # Skip if no permissions data
                if not permissions_str:
                    continue

                # Parse permissions JSON
                try:
                    # GAM returns permissions as JSON string
                    permissions = json.loads(permissions_str)
                except (json.JSONDecodeError, TypeError):
                    # If it's not JSON, skip this file
                    continue

                # Check each permission for external sharing
                external_perms = []

                # Handle both list and single permission formats
                if isinstance(permissions, dict):
                    permissions = [permissions]
                elif not isinstance(permissions, list):
                    continue

                for perm in permissions:
                    perm_type = perm.get('type', '')
                    email = perm.get('emailAddress', '')
                    role = perm.get('role', '')
                    perm_domain = perm.get('domain', '')

                    is_external = False

                    if perm_type == 'anyone':
                        # Anyone with the link
                        if include_anyone_links:
                            is_external = True
                            external_perms.append({
                                'type': 'anyone',
                                'email': 'Anyone with the link',
                                'role': role
                            })

                    elif perm_type in ['user', 'group']:
                        # Check if email is external to domain
                        if email and not email.endswith(f'@{domain}'):
                            is_external = True
                            external_perms.append({
                                'type': perm_type,
                                'email': email,
                                'role': role
                            })

                    elif perm_type == 'domain':
                        # Check if different domain
                        if perm_domain and perm_domain != domain:
                            is_external = True
                            external_perms.append({
                                'type': 'domain',
                                'email': f'{perm_domain} (entire domain)',
                                'role': role
                            })

                # If external permissions found, record it
                if external_perms:
                    finding = {
                        'user': user_email,
                        'file_id': file_id,
                        'file_name': file_name,
                        'external_permissions': external_perms
                    }
                    findings.append(finding)
                    user_external_files.append(file_name)
                    files_with_external_acls += 1
                    external_shares_found += len(external_perms)

                    # Yield individual finding
                    external_emails = [p['email'] for p in external_perms]
                    yield {
                        'status': 'found_external',
                        'user': user_email,
                        'file_id': file_id,
                        'file_name': file_name,
                        'external_emails': external_emails,
                        'message': f'⚠️  {user_email}: "{file_name}" shared with {len(external_perms)} external parties'
                    }

            files_scanned += user_files_count
            users_scanned += 1

            # Summary for this user
            if user_external_files:
                yield {
                    'status': 'complete_with_findings',
                    'user': user_email,
                    'message': f'✓ {user_email}: {len(user_external_files)} files with external sharing (out of {user_files_count} files)'
                }
            else:
                yield {
                    'status': 'clean',
                    'user': user_email,
                    'message': f'✓ {user_email}: No external sharing detected ({user_files_count} files scanned)'
                }

        except subprocess.TimeoutExpired:
            yield {
                'status': 'error',
                'user': user_email,
                'message': f'✗ Timeout scanning {user_email} (drive too large or slow network)'
            }
            log_error("Drive ACL Scan", f"Timeout for {user_email}")

        except Exception as e:
            error_msg = str(e)
            yield {
                'status': 'error',
                'user': user_email,
                'message': f'✗ Error scanning {user_email}: {error_msg}'
            }
            log_error("Drive ACL Scan", f"Exception for {user_email}: {error_msg}")

    return {
        'users_scanned': users_scanned,
        'files_scanned': files_scanned,
        'files_with_external_acls': files_with_external_acls,
        'external_shares_found': external_shares_found,
        'findings': findings
    }


def transfer_ownership(transfer_data, dry_run=False):
    """
    Transfer file ownership in bulk.

    Args:
        transfer_data (list): List of dicts with keys:
            - file_id (required): Google Drive file ID
            - current_owner (required): Current owner email
            - new_owner (required): New owner email
            - send_email (optional): Notify new owner (default: False)
        dry_run (bool): Preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(transfer_data)
    success_count = 0
    failure_count = 0
    errors = []

    gam_cmd = get_gam_command()

    for i, transfer in enumerate(transfer_data, start=1):
        file_id = transfer.get('file_id', '').strip()
        current_owner = transfer.get('current_owner', '').strip()
        new_owner = transfer.get('new_owner', '').strip()
        send_email = transfer.get('send_email', False)

        yield {
            'status': 'processing',
            'current': i,
            'total': total,
            'message': f'Transferring file {file_id} from {current_owner} to {new_owner}...'
        }

        # Validation
        if not file_id or not current_owner or not new_owner:
            failure_count += 1
            errors.append((file_id, "Missing required fields"))
            yield {
                'status': 'error',
                'file_id': file_id,
                'message': f'✗ Missing required fields for file {file_id}'
            }
            continue

        if '@' not in current_owner or '@' not in new_owner:
            failure_count += 1
            errors.append((file_id, "Invalid email address"))
            yield {
                'status': 'error',
                'file_id': file_id,
                'message': f'✗ Invalid email address'
            }
            continue

        try:
            # Build GAM command for ownership transfer
            cmd = [
                gam_cmd, 'user', current_owner,
                'transfer', 'ownership', file_id,
                new_owner
            ]

            if send_email:
                cmd.extend(['sendemailemail', 'true'])
            else:
                cmd.extend(['sendemailemail', 'false'])

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'file_id': file_id,
                    'message': f'[DRY RUN] Would transfer {file_id}: {current_owner} → {new_owner}'
                }
                success_count += 1
                continue

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'file_id': file_id,
                    'message': f'✓ Transferred ownership: {current_owner} → {new_owner}'
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((file_id, error_msg))
                log_error("Transfer Ownership", f"Failed for {file_id}: {error_msg}")
                yield {
                    'status': 'error',
                    'file_id': file_id,
                    'message': f'✗ Failed to transfer {file_id}: {error_msg[:100]}'
                }

        except subprocess.TimeoutExpired:
            failure_count += 1
            errors.append((file_id, "Timeout"))
            yield {
                'status': 'error',
                'file_id': file_id,
                'message': f'✗ Timeout transferring {file_id}'
            }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((file_id, error_msg))
            log_error("Transfer Ownership", f"Exception for {file_id}: {error_msg}")
            yield {
                'status': 'error',
                'file_id': file_id,
                'message': f'✗ Error transferring {file_id}'
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def remove_external_permissions(removal_data, dry_run=False):
    """
    Remove external permissions from files.

    Args:
        removal_data (list): List of dicts with keys:
            - file_id (required): Google Drive file ID
            - owner (required): File owner email
            - permission_email (required): Email to remove
        dry_run (bool): Preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(removal_data)
    success_count = 0
    failure_count = 0
    errors = []

    gam_cmd = get_gam_command()

    for i, removal in enumerate(removal_data, start=1):
        file_id = removal.get('file_id', '').strip()
        owner = removal.get('owner', '').strip()
        permission_email = removal.get('permission_email', '').strip()

        yield {
            'status': 'processing',
            'current': i,
            'total': total,
            'message': f'Removing {permission_email} from file {file_id}...'
        }

        try:
            cmd = [
                gam_cmd, 'user', owner,
                'delete', 'drivefileacl', file_id,
                permission_email
            ]

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'file_id': file_id,
                    'message': f'[DRY RUN] Would remove {permission_email} from {file_id}'
                }
                success_count += 1
                continue

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'file_id': file_id,
                    'message': f'✓ Removed {permission_email} from {file_id}'
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((file_id, error_msg))
                yield {
                    'status': 'error',
                    'file_id': file_id,
                    'message': f'✗ Failed to remove permission from {file_id}'
                }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((file_id, error_msg))
            log_error("Remove Permission", f"Exception for {file_id}: {error_msg}")
            yield {
                'status': 'error',
                'file_id': file_id,
                'message': f'✗ Error for {file_id}'
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def search_files(users, query, max_results=100):
    """
    Search for files matching query across users.

    Args:
        users (list): List of user emails to search
        query (str): Drive search query (e.g., "name contains 'budget'")
        max_results (int): Maximum results per user

    Yields:
        dict: Progress updates and search results

    Returns:
        dict: Summary with total files found
    """
    total = len(users)
    total_files_found = 0
    all_results = []

    gam_cmd = get_gam_command()

    for i, user_email in enumerate(users, start=1):
        yield {
            'status': 'processing',
            'user': user_email,
            'current': i,
            'total': total,
            'message': f'Searching Drive for {user_email}...'
        }

        try:
            cmd = [
                gam_cmd, 'user', user_email,
                'print', 'filelist',
                'query', query,
                'fields', 'id,name,createdtime,mimetype,size',
                'maxresults', str(max_results)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                # Parse CSV output
                reader = csv.DictReader(io.StringIO(result.stdout))
                user_files = list(reader)

                total_files_found += len(user_files)
                all_results.extend(user_files)

                yield {
                    'status': 'success',
                    'user': user_email,
                    'files_found': len(user_files),
                    'files': user_files,
                    'message': f'✓ {user_email}: Found {len(user_files)} file(s)'
                }
            else:
                yield {
                    'status': 'error',
                    'user': user_email,
                    'message': f'✗ Search failed for {user_email}'
                }

        except Exception as e:
            yield {
                'status': 'error',
                'user': user_email,
                'message': f'✗ Error searching {user_email}'
            }
            log_error("Search Files", f"Exception for {user_email}: {str(e)}")

    return {
        'total_files_found': total_files_found,
        'results': all_results
    }


def empty_trash(users, dry_run=False):
    """
    Empty Drive trash for users.

    Args:
        users (list): List of user emails
        dry_run (bool): Preview without executing

    Yields:
        dict: Progress updates

    Returns:
        dict: Summary with success/failure counts
    """
    total = len(users)
    success_count = 0
    failure_count = 0
    errors = []

    gam_cmd = get_gam_command()

    for i, user_email in enumerate(users, start=1):
        yield {
            'status': 'processing',
            'user': user_email,
            'current': i,
            'total': total,
            'message': f'Emptying trash for {user_email}...'
        }

        try:
            cmd = [gam_cmd, 'user', user_email, 'empty', 'drivetrash']

            if dry_run:
                yield {
                    'status': 'dry-run',
                    'user': user_email,
                    'message': f'[DRY RUN] Would empty trash for {user_email}'
                }
                success_count += 1
                continue

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # Can take time for large trash
            )

            if result.returncode == 0:
                success_count += 1
                yield {
                    'status': 'success',
                    'user': user_email,
                    'message': f'✓ Emptied trash for {user_email}'
                }
            else:
                failure_count += 1
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                errors.append((user_email, error_msg))
                yield {
                    'status': 'error',
                    'user': user_email,
                    'message': f'✗ Failed for {user_email}'
                }

        except subprocess.TimeoutExpired:
            failure_count += 1
            yield {
                'status': 'error',
                'user': user_email,
                'message': f'✗ Timeout for {user_email} (very large trash)'
            }

        except Exception as e:
            failure_count += 1
            error_msg = str(e)
            errors.append((user_email, error_msg))
            log_error("Empty Trash", f"Exception for {user_email}: {error_msg}")
            yield {
                'status': 'error',
                'user': user_email,
                'message': f'✗ Error for {user_email}'
            }

    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'errors': errors
    }


def get_file_info(user_email, file_id):
    """
    Get detailed information about a specific file.

    Args:
        user_email (str): Owner's email address
        file_id (str): Google Drive file ID

    Returns:
        tuple: (success: bool, data: dict or error_message: str)
    """
    gam_cmd = get_gam_command()

    try:
        cmd = [gam_cmd, 'user', user_email, 'show', 'fileinfo', file_id]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # Parse the output into a dictionary
            file_info = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    file_info[key.strip()] = value.strip()

            return (True, file_info)
        else:
            error_msg = result.stderr[:500] if result.stderr else "Unknown error"
            log_error("Get File Info", f"Failed for {file_id}: {error_msg}")
            return (False, error_msg)

    except Exception as e:
        error_msg = str(e)
        log_error("Get File Info", f"Exception for {file_id}: {error_msg}")
        return (False, error_msg)
