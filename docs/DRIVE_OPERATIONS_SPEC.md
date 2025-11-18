# Drive Operations Module - Complete Specification

**Priority:** 🔴 CRITICAL
**Estimated Effort:** 10-12 hours
**Target Release:** v1.1
**Dependencies:** None (uses existing infrastructure)

---

## Table of Contents

1. [Overview](#overview)
2. [GAM Commands Reference](#gam-commands-reference)
3. [Module Structure](#module-structure)
4. [Backend Operations](#backend-operations)
5. [GUI Design](#gui-design)
6. [Security Features](#security-features)
7. [CSV Formats](#csv-formats)
8. [Implementation Plan](#implementation-plan)
9. [Testing Strategy](#testing-strategy)

---

## Overview

The Drive Operations module provides comprehensive Google Drive management capabilities with a strong focus on **security and compliance** for K-12 environments.

### Key Features

| Category | Operations | Priority |
|----------|-----------|----------|
| **File Operations** | Search, Transfer Ownership, Delete, Share | HIGH |
| **Security** | Non-Domain ACL Scanner, External Sharing Audit | **CRITICAL** |
| **Bulk Operations** | CSV-based file management | HIGH |
| **Drive Management** | Empty Trash, Storage Reports | MEDIUM |
| **Folder Operations** | Create, Move Files, Organize | MEDIUM |

### Critical Security Need

**Problem:** Schools inadvertently share files with external parties
- Students share assignments with personal accounts
- Staff share sensitive documents outside organization
- No visibility into external sharing patterns
- Manual auditing is impossible at scale

**Solution:** Automated scanning and remediation tools

---

## GAM Commands Reference

### Core GAM7 Commands Used

```bash
# File Listing & Search
gam user <email> show filelist query "<query>" [fields <fields>]
gam user <email> show filelist select <drivefilename> <name>

# Ownership Transfer
gam user <email> transfer ownership <fileid> <newemail> [sendemailemail true|false]

# Permissions Management
gam user <email> add drivefileacl <fileid> user|group <email> role reader|writer|owner
gam user <email> delete drivefileacl <fileid> <email>
gam user <email> show drivefileacl <fileid>
gam user <email> update drivefileacl <fileid> <email> role <role>

# File Operations
gam user <email> delete drivefile <fileid> [purge]
gam user <email> update drivefile <fileid> [mimetype <mimetype>] [parentid <folderid>]
gam user <email> create drivefile drivefilename <name> mimetype gfolder

# Drive Management
gam user <email> empty drivetrash
gam user <email> show fileinfo <fileid>
gam user <email> show driveactivity [fileid <fileid>]

# Security Scanning (Custom logic using multiple commands)
gam user <email> show filelist fields id,name,permissions
# Parse output to find non-domain shares
```

### Important Notes

- **Rate Limits:** Google Drive API has quota limits (typically 1000 requests/100 seconds per user)
- **Batch Operations:** Use `gam csv` for bulk operations
- **File IDs:** Persistent across renames, use as primary identifier
- **Trash:** Files can be recovered from trash unless purged

---

## Module Structure

### File Organization

```
modules/
└── drive.py (NEW - ~800 lines)
    ├── File Operations
    │   ├── search_files()
    │   ├── transfer_ownership()
    │   ├── delete_files()
    │   └── share_files()
    ├── Security Operations
    │   ├── scan_non_domain_acls()
    │   ├── audit_external_sharing()
    │   └── remove_external_permissions()
    ├── Drive Management
    │   ├── empty_trash()
    │   ├── get_storage_usage()
    │   └── get_file_info()
    └── Folder Operations
        ├── create_folder()
        └── move_files_to_folder()

gui/
└── drive_window.py (REWRITE - ~900 lines)
    └── Inherits from BaseOperationWindow
        ├── Security Scanner Tab
        ├── File Operations Tab
        ├── Ownership Transfer Tab
        ├── Permissions Tab
        └── Drive Cleanup Tab
```

---

## Backend Operations

### 1. Non-Domain ACL Scanner (CRITICAL)

**Purpose:** Identify files shared with external (non-domain) users

**Pseudo-code:**

```python
def scan_non_domain_acls(users, domain, include_anyone_links=True, dry_run=False):
    """
    Scan users' Drive files for non-domain ACLs (external sharing).

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
            cmd = [
                gam_cmd, 'user', user_email,
                'show', 'filelist',
                'fields', 'id,name,permissions,owners'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for large drives
            )

            if result.returncode != 0:
                yield {
                    'status': 'error',
                    'user': user_email,
                    'message': f'✗ Failed to scan {user_email}: {result.stderr}'
                }
                log_error("Drive ACL Scan", f"Failed for {user_email}: {result.stderr}")
                continue

            # Parse CSV output
            import csv
            import io
            reader = csv.DictReader(io.StringIO(result.stdout))

            user_external_files = []
            user_files_count = 0

            for row in reader:
                user_files_count += 1
                file_id = row.get('id', '')
                file_name = row.get('name', '')
                permissions_str = row.get('permissions', '')

                # Parse permissions JSON
                if not permissions_str:
                    continue

                import json
                try:
                    permissions = json.loads(permissions_str)
                except json.JSONDecodeError:
                    continue

                # Check each permission for external sharing
                external_perms = []
                for perm in permissions:
                    perm_type = perm.get('type', '')  # 'user', 'group', 'domain', 'anyone'
                    email = perm.get('emailAddress', '')
                    role = perm.get('role', '')

                    # Identify external sharing
                    is_external = False

                    if perm_type == 'anyone':
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
                        perm_domain = perm.get('domain', '')
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
                'message': f'✗ Timeout scanning {user_email} (drive too large)'
            }
            log_error("Drive ACL Scan", f"Timeout for {user_email}")

        except Exception as e:
            yield {
                'status': 'error',
                'user': user_email,
                'message': f'✗ Error scanning {user_email}: {str(e)}'
            }
            log_error("Drive ACL Scan", f"Exception for {user_email}: {str(e)}")

    return {
        'users_scanned': users_scanned,
        'files_scanned': files_scanned,
        'files_with_external_acls': files_with_external_acls,
        'external_shares_found': external_shares_found,
        'findings': findings
    }
```

**Output Format:**
```python
findings = [
    {
        'user': 'student@school.edu',
        'file_id': '1abc123',
        'file_name': 'Homework Assignment.docx',
        'external_permissions': [
            {'type': 'user', 'email': 'parent@gmail.com', 'role': 'reader'},
            {'type': 'anyone', 'email': 'Anyone with the link', 'role': 'reader'}
        ]
    },
    # ... more findings
]
```

---

### 2. Transfer File Ownership

**Purpose:** Bulk transfer file ownership (e.g., when staff leaves)

**Pseudo-code:**

```python
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

        if not validate_email(current_owner) or not validate_email(new_owner):
            failure_count += 1
            errors.append((file_id, "Invalid email address"))
            yield {
                'status': 'error',
                'file_id': file_id,
                'message': f'✗ Invalid email address'
            }
            continue

        try:
            # Build GAM command
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
                    'message': f'✗ Failed to transfer {file_id}'
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
```

---

### 3. Remove External Permissions

**Purpose:** Bulk remove external sharing from files

**Pseudo-code:**

```python
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
```

---

### 4. Search Files

**Purpose:** Find files matching criteria

**Pseudo-code:**

```python
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
                'show', 'filelist',
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
                import csv, io
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
```

---

### 5. Empty Trash

**Purpose:** Empty Drive trash for users

**Pseudo-code:**

```python
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
```

---

## GUI Design

### DriveWindow Class Structure

```python
class DriveWindow(BaseOperationWindow):
    """
    Drive Operations window.

    Inherits from BaseOperationWindow to leverage:
    - Standard target selection framework
    - Progress tracking and threading
    - Error logging
    - Utility methods
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            title="Drive Operations",
            window_size="1100x800",
            min_size=(900, 700)
        )

    def create_operation_tabs(self):
        """Create Drive-specific operation tabs."""
        # Tab 1: Security Scanner (CRITICAL)
        self.create_security_scanner_tab()

        # Tab 2: File Search
        self.create_file_search_tab()

        # Tab 3: Ownership Transfer
        self.create_ownership_transfer_tab()

        # Tab 4: Permissions Management
        self.create_permissions_tab()

        # Tab 5: Drive Cleanup
        self.create_cleanup_tab()
```

### Tab 1: Security Scanner

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Security Scanner - Find External Sharing                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Target Users:                                                │
│  ( ) Select User  ( ) Group  ( ) All Users  (*) CSV File     │
│                                                               │
│  Scan Options:                                                │
│  ☑ Include "Anyone with link" sharing                        │
│  ☑ Include external domain sharing                           │
│  ☐ Auto-remove external permissions (DANGEROUS!)             │
│                                                               │
│  Your Domain: [school.edu          ]                         │
│                                                               │
│  [🔍 Scan for External Sharing]  [Export Results]            │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  Progress and Results                                         │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░ 60%                                  │
│                                                               │
│  ✓ john@school.edu: No external sharing (45 files scanned)   │
│  ⚠️  mary@school.edu: "Budget.xlsx" shared with outsider     │
│  ⚠️  mary@school.edu: "Grades.doc" - anyone with link        │
│  ✓ tom@school.edu: No external sharing (12 files scanned)    │
│  ✗ Error scanning alice@school.edu: Permission denied        │
│                                                               │
│  [Clear Results]  [View Error Log]  [Export to CSV]          │
└─────────────────────────────────────────────────────────────┘
```

**Pseudo-code for Execute Button:**

```python
def execute_security_scan(self):
    """Execute security scan for external sharing."""
    # Get target users
    users = self.get_target_users('security_scan')
    if not users:
        return

    # Get domain
    domain = self.domain_entry.get().strip()
    if not domain:
        messagebox.showerror("Error", "Please enter your organization domain")
        return

    # Get options
    include_anyone = self.include_anyone_var.get()
    auto_remove = self.auto_remove_var.get()

    # Warn if auto-remove enabled
    if auto_remove:
        response = messagebox.askyesno(
            "Confirm Auto-Remove",
            "WARNING: This will automatically remove ALL external permissions!\n\n"
            "This action cannot be undone.\n\n"
            "Are you absolutely sure?",
            icon='warning'
        )
        if not response:
            return

    # Import backend function
    from modules.drive import scan_non_domain_acls

    # Run operation
    self.run_operation(
        scan_non_domain_acls,
        self.security_scan_progress_frame,
        users,
        domain,
        include_anyone,
        dry_run=(not auto_remove)
    )
```

---

## CSV Formats

### Security Scan Results Export

```csv
user,file_id,file_name,external_email,permission_type,role
student1@school.edu,1abc123,Homework.docx,parent@gmail.com,user,reader
student1@school.edu,1abc123,Homework.docx,Anyone with link,anyone,reader
teacher@school.edu,2def456,Grades.xlsx,admin@external.com,user,writer
```

### Ownership Transfer Import

```csv
file_id,current_owner,new_owner,send_email
1abc123,retiring.teacher@school.edu,new.teacher@school.edu,true
2def456,retiring.teacher@school.edu,new.teacher@school.edu,false
3ghi789,student@school.edu,teacher@school.edu,true
```

### Permission Removal Import

```csv
file_id,owner,permission_email
1abc123,student@school.edu,parent@gmail.com
2def456,teacher@school.edu,external.user@gmail.com
```

---

## Implementation Plan

### Phase 1: Backend Module (4-5 hours)

1. **Create `modules/drive.py`** (2 hours)
   - Implement `scan_non_domain_acls()`
   - Implement `transfer_ownership()`
   - Implement `remove_external_permissions()`
   - Add error handling and logging

2. **Test Backend Functions** (1 hour)
   - Manual testing with test domain
   - Verify GAM command construction
   - Test CSV parsing

3. **Add Additional Operations** (2 hours)
   - `search_files()`
   - `empty_trash()`
   - `share_files()`
   - `delete_files()`

### Phase 2: GUI Implementation (5-6 hours)

1. **Rewrite `gui/drive_window.py`** (3 hours)
   - Inherit from BaseOperationWindow
   - Create Security Scanner tab
   - Create File Operations tab
   - Create Ownership Transfer tab

2. **Add Remaining Tabs** (2 hours)
   - Permissions Management tab
   - Drive Cleanup tab

3. **Testing & Refinement** (1 hour)
   - End-to-end testing
   - UI/UX improvements
   - Error message refinement

### Phase 3: Documentation (1 hour)

1. Update README.md with Drive features
2. Create CSV format examples
3. Add security scanner usage guide
4. Update roadmap

---

## Testing Strategy

### Unit Tests (Not Yet Implemented)

```python
# tests/test_drive.py

def test_scan_non_domain_acls_identifies_external():
    """Test that external sharing is correctly identified."""
    # Mock GAM output with external sharing
    # Assert that external permission is flagged

def test_scan_non_domain_acls_ignores_internal():
    """Test that internal sharing is not flagged."""
    # Mock GAM output with only internal sharing
    # Assert no external permissions found

def test_transfer_ownership_validates_emails():
    """Test email validation in ownership transfer."""
    # Pass invalid emails
    # Assert validation error

def test_empty_trash_handles_timeout():
    """Test timeout handling for very large trash."""
    # Mock timeout
    # Assert graceful error handling
```

### Manual Testing Checklist

- [ ] Security scanner detects "anyone with link" sharing
- [ ] Security scanner detects external user sharing
- [ ] Security scanner detects external domain sharing
- [ ] Security scanner ignores internal sharing correctly
- [ ] Ownership transfer works for single file
- [ ] Ownership transfer works for bulk CSV
- [ ] Permission removal works correctly
- [ ] Empty trash completes successfully
- [ ] Error handling works for permission denied
- [ ] Progress tracking updates correctly
- [ ] CSV export includes all findings
- [ ] Large drives (1000+ files) complete without timeout

---

## Security Considerations

### Rate Limiting
- Google Drive API has quotas
- Implement delays between users if needed
- Show warning for bulk operations on many users

### Permissions
- Verify GAM has necessary scopes
- Handle permission denied errors gracefully
- Don't expose file contents in logs

### Data Privacy
- Don't log file names that might be sensitive
- Sanitize error messages
- Secure CSV exports (recommend encryption)

### User Communication
- Clearly warn about destructive operations
- Show preview before removing permissions
- Require confirmation for auto-remove feature

---

## Performance Optimization

### For Large Environments (1000+ users)

```python
# Optional: Parallel scanning (use with caution - rate limits!)
from concurrent.futures import ThreadPoolExecutor

def scan_non_domain_acls_parallel(users, domain, max_workers=3):
    """
    Parallel version for large user bases.

    NOTE: Set max_workers conservatively to avoid rate limits.
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scan_single_user, user, domain): user
            for user in users
        }

        for future in as_completed(futures):
            user = futures[future]
            try:
                result = future.result()
                yield result
            except Exception as e:
                yield {'status': 'error', 'user': user, 'error': str(e)}
```

---

## Future Enhancements

### v1.2+
- **Scheduled Scanning:** Automatic weekly security scans
- **Email Alerts:** Notify admins of external sharing violations
- **Policy Enforcement:** Auto-remove external shares based on rules
- **Drive Quota Management:** Identify users over quota
- **File Activity Monitoring:** Track file access patterns
- **Duplicate File Detection:** Find and merge duplicates
- **Shared Drive Support:** Extend to Team/Shared Drives

---

## Success Metrics

### Implementation Success
- All 5 tabs functional
- Security scanner completes for 100+ users in < 5 minutes
- Zero false positives on internal sharing detection
- < 5% error rate on bulk operations

### User Adoption
- 80%+ of admins use security scanner monthly
- Average 50+ external permissions removed per month
- Positive user feedback on ease of use

---

## Appendix: GAM Command Examples

### Find files shared with anyone
```bash
gam user student@school.edu show filelist query "visibility='anyoneWithLink'"
```

### Find files shared externally
```bash
gam user teacher@school.edu show filelist fields id,name,permissions | grep -v '@school.edu'
```

### Transfer ownership
```bash
gam user old.owner@school.edu transfer ownership 1abc123 new.owner@school.edu
```

### Remove specific permission
```bash
gam user owner@school.edu delete drivefileacl 1abc123 external@gmail.com
```

### Empty trash
```bash
gam user student@school.edu empty drivetrash
```

### Create folder
```bash
gam user teacher@school.edu create drivefile drivefilename "Class Resources" mimetype gfolder
```

---

**End of Drive Operations Specification**
**Next:** See `REPORTS_SPEC.md` for Reports Module specification
