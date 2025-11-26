# Reports Module - Complete Specification

**Priority:** 🔴 HIGH
**Estimated Effort:** 6-8 hours
**Target Release:** v1.1
**Dependencies:** None (uses existing infrastructure)

---

## Table of Contents

1. [Overview](#overview)
2. [GAM Commands Reference](#gam-commands-reference)
3. [Module Structure](#module-structure)
4. [Report Types](#report-types)
5. [Backend Operations](#backend-operations)
6. [GUI Design](#gui-design)
7. [Implementation Plan](#implementation-plan)
8. [Testing Strategy](#testing-strategy)

---

## Overview

The Reports module provides visibility into Google Workspace usage, activity, and compliance metrics for administrative oversight and decision-making.

### Key Features

| Category | Reports | Priority |
|----------|---------|----------|
| **User Reports** | Login Activity, Storage Usage, Inactive Users | HIGH |
| **Email Reports** | Email Statistics, Forwarding Audit | HIGH |
| **Admin Reports** | Admin Activity, Password Changes | MEDIUM |
| **Drive Reports** | Storage Usage, File Sharing Patterns | MEDIUM |
| **Calendar Reports** | Meeting Statistics, Calendar Usage | LOW |

### Business Value

**For K-12 Administrators:**
- Identify inactive accounts (save licenses)
- Monitor storage usage (plan capacity)
- Audit admin actions (compliance)
- Track email usage (detect abuse)
- Understand adoption patterns

---

## GAM Commands Reference

### Core Reporting Commands

```bash
# User Reports
gam report users parameters accounts:last_login_time fields email,accounts:last_login_time
gam report users parameters accounts:is_disabled fields email,accounts:is_disabled
gam show users suspended

# Usage Reports
gam report usage customer parameters gmail:num_emails_sent,gmail:num_emails_received
gam report usage customer parameters drive:num_items_created
gam report usage user <email> parameters gmail:num_emails_sent date <date>

# Admin Activity
gam report admin parameters account_warning_event fields actor:email,event:name,event:type
gam report admin start -7d parameters delegated_admin_settings_event

# Drive/Storage Reports
gam report usage customer parameters drive:total_file_size
gam user <email> show filecount

# Login/Security
gam report logins start -30d
gam report users parameters security:is_2sv_enrolled fields email,security:is_2sv_enrolled
```

### Important Notes

- Reports use Admin SDK Reports API
- Historical data available for 180 days (Google limitation)
- Date format: YYYY-MM-DD or relative (-7d, -30d)
- Large reports may take time to generate
- Rate limits apply (use delays for bulk)

---

## Module Structure

```
modules/
└── reports.py (NEW - ~600 lines)
    ├── User Reports
    │   ├── get_login_activity_report()
    │   ├── get_inactive_users_report()
    │   ├── get_storage_usage_report()
    │   └── get_suspended_users_report()
    ├── Email Reports
    │   ├── get_email_usage_report()
    │   └── get_forwarding_audit_report()
    ├── Admin Reports
    │   ├── get_admin_activity_report()
    │   └── get_password_change_report()
    ├── Drive Reports
    │   ├── get_drive_storage_report()
    │   └── get_file_sharing_report()
    └── Utilities
        ├── parse_report_csv()
        ├── calculate_inactive_days()
        └── export_report_to_csv()

gui/
└── reports_window.py (REWRITE - ~700 lines)
    └── Inherits from BaseOperationWindow
        ├── User Activity Tab
        ├── Email Usage Tab
        ├── Admin Audit Tab
        ├── Storage Reports Tab
        └── Custom Report Tab
```

---

## Report Types

### 1. User Login Activity Report

**Purpose:** Track last login times for all users

**Data Points:**
- User email
- Last login time
- Days since last login
- Status (Active/Inactive/Suspended)

**Use Cases:**
- Identify inactive accounts for cleanup
- Verify license usage
- Detect compromised accounts (unusual login patterns)

**Output Sample:**
```csv
email,last_login,days_since_login,status
student1@school.edu,2025-11-15 14:32:00,3,Active
teacher1@school.edu,2025-09-01 09:15:00,78,Inactive
admin@school.edu,2025-11-18 08:00:00,0,Active
suspended@school.edu,2025-08-30 10:00:00,80,Suspended
```

---

### 2. Storage Usage Report

**Purpose:** Monitor Drive and Gmail storage usage

**Data Points:**
- User email
- Drive storage used (GB)
- Gmail storage used (GB)
- Total storage used (GB)
- Storage quota (GB)
- Percentage used
- Over quota flag

**Use Cases:**
- Plan storage capacity
- Identify users over quota
- Optimize storage costs
- Enforce cleanup policies

**Output Sample:**
```csv
email,drive_gb,gmail_gb,total_gb,quota_gb,percent_used,over_quota
teacher1@school.edu,12.5,3.2,15.7,15,104.7%,true
student1@school.edu,2.1,0.8,2.9,5,58.0%,false
admin@school.edu,45.3,8.7,54.0,100,54.0%,false
```

---

### 3. Email Usage Statistics

**Purpose:** Track email sending and receiving patterns

**Data Points:**
- User email or department
- Emails sent (count)
- Emails received (count)
- Date range
- Average per day

**Use Cases:**
- Detect spam senders
- Identify inactive mailboxes
- Understand communication patterns
- Capacity planning

**Output Sample:**
```csv
user,emails_sent,emails_received,date_range,avg_per_day
teacher1@school.edu,245,892,2025-10-18 to 2025-11-18,7.9
student1@school.edu,12,156,2025-10-18 to 2025-11-18,0.4
admin@school.edu,1580,3240,2025-10-18 to 2025-11-18,51.0
```

---

### 4. Admin Activity Audit

**Purpose:** Track administrator actions for compliance

**Data Points:**
- Admin email
- Action performed
- Target user/resource
- Timestamp
- Event type
- IP address (if available)

**Use Cases:**
- Compliance auditing
- Security investigation
- Change tracking
- Accountability

**Output Sample:**
```csv
admin,action,target,timestamp,event_type,ip_address
admin@school.edu,User created,newstudent@school.edu,2025-11-18 09:15:00,account_management,192.168.1.50
admin@school.edu,Password reset,teacher@school.edu,2025-11-18 10:30:00,account_management,192.168.1.50
super.admin@school.edu,Admin role assigned,newadmin@school.edu,2025-11-17 14:00:00,delegated_admin,10.0.0.5
```

---

### 5. Inactive Users Report

**Purpose:** Identify users who haven't logged in recently

**Parameters:**
- Inactive threshold (days): 30, 60, 90, 180
- Include suspended: Yes/No
- Minimum days since creation: 30 (ignore new accounts)

**Data Points:**
- User email
- Last login date
- Days inactive
- Creation date
- Status
- Organizational Unit

**Output Sample:**
```csv
email,last_login,days_inactive,created_date,status,org_unit
former.student@school.edu,2024-06-15,156,2021-09-01,Active,/Students/Graduated
unused.account@school.edu,Never,365,2024-01-15,Active,/Students
leftover.test@school.edu,2024-03-10,253,2024-03-01,Active,/Test Accounts
```

---

## Backend Operations

### 1. Get Login Activity Report

**Pseudo-code:**

```python
def get_login_activity_report(date_range_days=30, include_suspended=False):
    """
    Generate login activity report for all users.

    Args:
        date_range_days (int): Look back period in days
        include_suspended (bool): Include suspended users

    Yields:
        dict: Progress updates and report data

    Returns:
        dict: Report data with user login information
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

    # Get login activity using GAM report
    cmd = [
        gam_cmd, 'report', 'users',
        'parameters', 'accounts:last_login_time',
        'fields', 'email,accounts:last_login_time'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            yield {
                'status': 'error',
                'message': f'Failed to fetch login report: {result.stderr}'
            }
            return None

        # Parse CSV output
        import csv, io
        from datetime import datetime, timedelta

        reader = csv.DictReader(io.StringIO(result.stdout))
        report_data = []

        for row in reader:
            email = row.get('email', '')
            last_login_str = row.get('accounts:last_login_time', '')

            # Parse last login time
            if last_login_str and last_login_str != 'Never logged in':
                try:
                    last_login = datetime.strptime(last_login_str, '%Y-%m-%d %H:%M:%S')
                    days_since = (datetime.now() - last_login).days
                except:
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
                'last_login': last_login_str,
                'days_since_login': days_since,
                'status': status
            })

        # Sort by days_since_login (most inactive first)
        report_data.sort(key=lambda x: x['days_since_login'] if x['days_since_login'] is not None else 99999, reverse=True)

        yield {
            'status': 'success',
            'message': f'Generated login activity report for {len(report_data)} users',
            'report_data': report_data
        }

        return {
            'report_type': 'login_activity',
            'date_generated': datetime.now().isoformat(),
            'total_users': len(report_data),
            'data': report_data
        }

    except Exception as e:
        error_msg = f'Exception generating report: {str(e)}'
        log_error("Login Activity Report", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None
```

---

### 2. Get Storage Usage Report

**Pseudo-code:**

```python
def get_storage_usage_report(quota_threshold_percent=80):
    """
    Generate storage usage report for all users.

    Args:
        quota_threshold_percent (int): Highlight users over this % of quota

    Yields:
        dict: Progress updates and report data

    Returns:
        dict: Report data with storage usage
    """
    gam_cmd = get_gam_command()

    yield {
        'status': 'info',
        'message': 'Fetching storage usage data...'
    }

    # Get usage report from GAM
    cmd = [
        gam_cmd, 'report', 'usage', 'customer',
        'parameters', 'accounts:total_quota_in_mb,accounts:used_quota_in_mb,accounts:drive_used_quota_in_mb,accounts:gmail_used_quota_in_mb'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180
        )

        if result.returncode != 0:
            yield {
                'status': 'error',
                'message': f'Failed to fetch storage report: {result.stderr}'
            }
            return None

        # Parse CSV
        import csv, io
        reader = csv.DictReader(io.StringIO(result.stdout))
        report_data = []

        for row in reader:
            email = row.get('email', '')
            total_quota_mb = float(row.get('accounts:total_quota_in_mb', 0) or 0)
            used_quota_mb = float(row.get('accounts:used_quota_in_mb', 0) or 0)
            drive_used_mb = float(row.get('accounts:drive_used_quota_in_mb', 0) or 0)
            gmail_used_mb = float(row.get('accounts:gmail_used_quota_in_mb', 0) or 0)

            # Convert MB to GB
            total_quota_gb = round(total_quota_mb / 1024, 2)
            used_quota_gb = round(used_quota_mb / 1024, 2)
            drive_used_gb = round(drive_used_mb / 1024, 2)
            gmail_used_gb = round(gmail_used_mb / 1024, 2)

            # Calculate percentage
            if total_quota_gb > 0:
                percent_used = round((used_quota_gb / total_quota_gb) * 100, 1)
            else:
                percent_used = 0

            # Flag if over threshold
            over_threshold = percent_used >= quota_threshold_percent

            report_data.append({
                'email': email,
                'total_quota_gb': total_quota_gb,
                'used_quota_gb': used_quota_gb,
                'drive_used_gb': drive_used_gb,
                'gmail_used_gb': gmail_used_gb,
                'percent_used': percent_used,
                'over_threshold': over_threshold
            })

        # Sort by percent_used (highest first)
        report_data.sort(key=lambda x: x['percent_used'], reverse=True)

        # Calculate summary statistics
        total_users = len(report_data)
        users_over_threshold = sum(1 for u in report_data if u['over_threshold'])
        total_storage_used = sum(u['used_quota_gb'] for u in report_data)
        total_storage_quota = sum(u['total_quota_gb'] for u in report_data)

        yield {
            'status': 'success',
            'message': f'Generated storage report for {total_users} users',
            'report_data': report_data,
            'summary': {
                'total_users': total_users,
                'users_over_threshold': users_over_threshold,
                'total_storage_used_gb': round(total_storage_used, 2),
                'total_storage_quota_gb': round(total_storage_quota, 2)
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
                'total_storage_quota_gb': round(total_storage_quota, 2)
            }
        }

    except Exception as e:
        error_msg = f'Exception generating report: {str(e)}'
        log_error("Storage Usage Report", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None
```

---

### 3. Get Email Usage Report

**Pseudo-code:**

```python
def get_email_usage_report(start_date, end_date=None):
    """
    Generate email usage statistics report.

    Args:
        start_date (str): Start date (YYYY-MM-DD or -Nd format)
        end_date (str, optional): End date (YYYY-MM-DD)

    Yields:
        dict: Progress updates and report data

    Returns:
        dict: Report data with email usage statistics
    """
    gam_cmd = get_gam_command()

    yield {
        'status': 'info',
        'message': 'Fetching email usage statistics...'
    }

    # Build GAM command
    cmd = [
        gam_cmd, 'report', 'usage', 'customer',
        'parameters', 'gmail:num_emails_sent,gmail:num_emails_received',
        'start', start_date
    ]

    if end_date:
        cmd.extend(['end', end_date])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            yield {
                'status': 'error',
                'message': f'Failed to fetch email usage: {result.stderr}'
            }
            return None

        # Parse CSV
        import csv, io
        from datetime import datetime

        reader = csv.DictReader(io.StringIO(result.stdout))
        report_data = []

        for row in reader:
            email = row.get('email', '')
            emails_sent = int(row.get('gmail:num_emails_sent', 0) or 0)
            emails_received = int(row.get('gmail:num_emails_received', 0) or 0)
            date = row.get('date', '')

            report_data.append({
                'email': email,
                'date': date,
                'emails_sent': emails_sent,
                'emails_received': emails_received,
                'total_emails': emails_sent + emails_received
            })

        # Sort by total emails (highest first)
        report_data.sort(key=lambda x: x['total_emails'], reverse=True)

        # Calculate summary
        total_sent = sum(u['emails_sent'] for u in report_data)
        total_received = sum(u['emails_received'] for u in report_data)

        yield {
            'status': 'success',
            'message': f'Generated email usage report',
            'report_data': report_data,
            'summary': {
                'total_sent': total_sent,
                'total_received': total_received,
                'total_emails': total_sent + total_received
            }
        }

        return {
            'report_type': 'email_usage',
            'date_generated': datetime.now().isoformat(),
            'period': f'{start_date} to {end_date or "today"}',
            'data': report_data
        }

    except Exception as e:
        error_msg = f'Exception generating report: {str(e)}'
        log_error("Email Usage Report", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None
```

---

### 4. Get Admin Activity Report

**Pseudo-code:**

```python
def get_admin_activity_report(start_date='-30d', event_type='all'):
    """
    Generate admin activity audit report.

    Args:
        start_date (str): Start date (YYYY-MM-DD or -Nd format)
        event_type (str): Filter by event type or 'all'

    Yields:
        dict: Progress updates and report data

    Returns:
        dict: Report data with admin actions
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
        cmd.extend(['parameters', event_type])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            yield {
                'status': 'error',
                'message': f'Failed to fetch admin activity: {result.stderr}'
            }
            return None

        # Parse CSV
        import csv, io
        reader = csv.DictReader(io.StringIO(result.stdout))
        report_data = []

        for row in reader:
            admin_email = row.get('actor:email', '')
            event_name = row.get('event:name', '')
            event_type = row.get('event:type', '')
            timestamp = row.get('id:time', '')
            parameters = row.get('event:parameters', '')

            report_data.append({
                'admin': admin_email,
                'event': event_name,
                'type': event_type,
                'timestamp': timestamp,
                'details': parameters
            })

        # Sort by timestamp (newest first)
        report_data.sort(key=lambda x: x['timestamp'], reverse=True)

        yield {
            'status': 'success',
            'message': f'Generated admin activity report with {len(report_data)} events',
            'report_data': report_data
        }

        return {
            'report_type': 'admin_activity',
            'date_generated': datetime.now().isoformat(),
            'period': f'{start_date} to today',
            'total_events': len(report_data),
            'data': report_data
        }

    except Exception as e:
        error_msg = f'Exception generating report: {str(e)}'
        log_error("Admin Activity Report", error_msg)
        yield {
            'status': 'error',
            'message': error_msg
        }
        return None
```

---

## GUI Design

### ReportsWindow Class Structure

```python
class ReportsWindow(BaseOperationWindow):
    """
    Reports window for generating workspace reports.

    Inherits from BaseOperationWindow for standard infrastructure.
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            title="Google Workspace Reports",
            window_size="1000x750",
            min_size=(900, 650)
        )

    def create_operation_tabs(self):
        """Create report type tabs."""
        # Tab 1: User Activity Reports
        self.create_user_activity_tab()

        # Tab 2: Storage Reports
        self.create_storage_tab()

        # Tab 3: Email Usage
        self.create_email_usage_tab()

        # Tab 4: Admin Audit
        self.create_admin_audit_tab()

        # Tab 5: Custom Reports
        self.create_custom_report_tab()
```

### Tab 1: User Activity Reports

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  User Activity Reports                                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Report Type:                                                 │
│  (*) Login Activity  ( ) Inactive Users  ( ) Suspended Users │
│                                                               │
│  Inactive Threshold: [90▼] days    (for Inactive Users)      │
│                                                               │
│  ☐ Include suspended users                                   │
│  ☐ Include never-logged-in users                             │
│                                                               │
│  [📊 Generate Report]  [📥 Export to CSV]                    │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  Report Results                                               │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ Complete                              │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ Email               │ Last Login    │ Days │ Status    │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │ inactive@sch.edu    │ 2024-06-01    │ 170  │ Inactive  │   │
│  │ oldacct@sch.edu     │ Never         │ N/A  │ Never     │   │
│  │ active@sch.edu      │ 2025-11-18    │ 0    │ Active    │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  Summary: 245 users scanned, 23 inactive (> 90 days)          │
│                                                               │
│  [Copy to Clipboard]  [Clear Results]                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Backend Module (3-4 hours)

1. **Create `modules/reports.py`** (2 hours)
   - `get_login_activity_report()`
   - `get_storage_usage_report()`
   - `get_email_usage_report()`
   - `get_admin_activity_report()`

2. **Test Backend** (1 hour)
   - Verify GAM commands
   - Test CSV parsing
   - Validate calculations

3. **Add Export Functions** (1 hour)
   - Export to CSV
   - Export to Excel (optional)
   - Pretty print for display

### Phase 2: GUI Implementation (3-4 hours)

1. **Rewrite `gui/reports_window.py`** (2 hours)
   - Inherit from BaseOperationWindow
   - Create User Activity tab
   - Create Storage tab
   - Create Email Usage tab

2. **Add Report Viewing** (1 hour)
   - Scrollable table view
   - Summary statistics
   - Export buttons

3. **Testing & Polish** (1 hour)
   - End-to-end testing
   - UI improvements

---

## Testing Strategy

### Manual Testing Checklist

- [ ] Login activity report generates correctly
- [ ] Inactive users identified accurately
- [ ] Storage usage calculations correct
- [ ] Email statistics accurate
- [ ] Admin activity log retrieved
- [ ] CSV export works
- [ ] Date range filtering works
- [ ] Large datasets (1000+ users) complete
- [ ] Error handling works
- [ ] Summary statistics accurate

---

## Future Enhancements

### v1.2+
- **Scheduled Reports:** Email reports automatically
- **Charts/Graphs:** Visual representations using matplotlib
- **Trend Analysis:** Compare periods
- **Alerts:** Notify on thresholds exceeded
- **Custom Dashboards:** Save favorite report combinations
- **Data Retention:** Store historical reports

---

**End of Reports Specification**
**Next:** See `QUICK_WINS.md` for easy implementation opportunities
