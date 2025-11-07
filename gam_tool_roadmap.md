# GAM Admin Tool - Complete Implementation Roadmap

## Project Status

**Current State:**
- ✓ Foundation layer complete (utils, logging, CSV handling, GAM checks)
- ✓ Main window and navigation complete
- ✓ Email operations fully implemented (6 operations, ~1,100 lines)
- ✓ Email backend module complete (12 functions, ~995 lines)
- ✓ Build system and documentation complete
- ⚠ Email filter creation bug (line 826 in modules/email.py)

**Total Lines of Code:** ~3,300
**Project Structure:** Modular, well-documented, ready for expansion

---

## Appendix A: Detailed Base Class Architecture

### BaseOperationWindow Class Diagram

```
BaseOperationWindow (Abstract)
├── __init__(parent, title, window_size)
├── create_widgets()
│   ├── create_title()
│   ├── create_notebook()
│   ├── create_operation_tabs() [ABSTRACT]
│   └── create_bottom_buttons()
├── Target Selection Methods
│   ├── create_target_selection_frame(parent, tab_id)
│   ├── update_target_input(tab_id)
│   ├── browse_csv(tab_id)
│   ├── load_users_list(tab_id)
│   ├── populate_listbox(tab_id, users)
│   └── get_target_users(tab_id) → list[str]
├── Progress Methods
│   ├── create_progress_frame(parent)
│   ├── clear_results(progress_frame)
│   ├── view_error_log()
│   └── export_results(results, operation_name)
├── Operation Execution
│   ├── run_operation(func, progress_frame, *args)
│   ├── check_operation_queue(progress_frame, queue)
│   └── cancel_operation()
└── Utility Methods
    ├── confirm_bulk_operation(count, operation_name) → bool
    ├── validate_email(email) → bool
    ├── validate_date(date_str) → bool
    └── show_error(message)

EmailWindow(BaseOperationWindow)
├── create_operation_tabs()
│   ├── create_delete_messages_tab()
│   ├── create_delegates_tab()
│   ├── create_signatures_tab()
│   ├── create_forwarding_tab()
│   ├── create_labels_tab()
│   └── create_filters_tab()
└── Execution Methods
    ├── execute_delete_messages()
    ├── execute_delegates()
    ├── execute_signatures()
    ├── execute_forwarding()
    ├── execute_labels()
    └── execute_filters()

UsersWindow(BaseOperationWindow)
├── create_operation_tabs()
│   ├── create_create_users_tab()
│   ├── create_delete_users_tab()
│   ├── create_suspend_restore_tab()
│   ├── create_reset_password_tab()
│   ├── create_update_info_tab()
│   ├── create_manage_ou_tab()
│   └── create_manage_aliases_tab()
└── Execution Methods
    ├── execute_create_users()
    ├── execute_delete_users()
    └── ... (etc)

[Similar structure for GroupsWindow, DriveWindow, ReportsWindow, CalendarWindow]
```

---

## Appendix B: CSV Template Library

### All CSV Formats Reference

**Email Operations:**
```csv
# Delete messages - target users
email
user1@domain.com
user2@domain.com
```

**User Operations:**
```csv
# Create users
email,firstName,lastName,password,orgUnit,title,phone
john.doe@domain.com,John,Doe,TempPass123!,/Staff,Developer,555-1234
jane.smith@domain.com,Jane,Smith,TempPass456!,/Management,Manager,555-5678

# Update users
email,title,phone,address
john.doe@domain.com,Senior Developer,555-1234,123 Main St
jane.smith@domain.com,Project Manager,555-5678,456 Oak Ave

# Reset passwords
email,newPassword
john.doe@domain.com,NewPass123!
jane.smith@domain.com,NewPass456!

# Manage aliases
email,alias,action
john.doe@domain.com,j.doe@domain.com,add
jane.smith@domain.com,jsmith@domain.com,add
```

**Group Operations:**
```csv
# Create groups
email,name,description
sales@domain.com,Sales Team,Sales department group
support@domain.com,Support Team,Customer support group

# Add members
group,member,role
sales@domain.com,john@domain.com,MEMBER
sales@domain.com,jane@domain.com,MANAGER
support@domain.com,john@domain.com,MEMBER

# Sync membership (exact membership)
group,member,role
sales@domain.com,john@domain.com,MEMBER
sales@domain.com,jane@domain.com,MANAGER
sales@domain.com,bob@domain.com,MEMBER
```

**Drive Operations:**
```csv
# Transfer ownership
file_id,current_owner,new_owner
abc123xyz,john@domain.com,jane@domain.com
def456uvw,john@domain.com,jane@domain.com

# Share files
file_id,user,role
abc123xyz,partner@external.com,reader
def456uvw,contractor@external.com,commenter

# Move files
file_id,target_folder_id
abc123xyz,folder_xyz_123
def456uvw,folder_xyz_123
```

**Calendar Operations:**
```csv
# Create events
calendar,title,start,end,description,recurring
cal_123,Team Meeting,2025-01-15T10:00:00,2025-01-15T11:00:00,Weekly team sync,WEEKLY
cal_456,Project Review,2025-01-20T14:00:00,2025-01-20T15:00:00,Monthly review,MONTHLY

# Share calendars
calendar,user,role
cal_123,john@domain.com,writer
cal_456,jane@domain.com,reader
```

---

## Appendix C: GAM Command Reference Quick Guide

### Essential GAM Commands by Category

**Users:**
```bash
# Create
gam create user EMAIL firstname FIRST lastname LAST password PASS ou OU

# Update
gam update user EMAIL [password|firstname|lastname|title|phone|ou] VALUE

# Delete
gam delete user EMAIL

# Suspend/Restore
gam update user EMAIL suspended [on|off]

# Info
gam info user EMAIL

# List
gam print users [query QUERY] [ou OU]

# Aliases
gam create alias ALIAS user EMAIL
gam delete alias ALIAS
```

**Groups:**
```bash
# Create
gam create group EMAIL name NAME description DESC

# Delete
gam delete group EMAIL

# Add members
gam update group GROUP add [member|manager|owner] user EMAIL

# Remove members
gam update group GROUP remove member user EMAIL

# List members
gam print group-members group GROUP

# Settings
gam update group GROUP [whocanpostmessage|whocanviewgroup|...] VALUE
```

**Email:**
```bash
# Delete messages
gam user EMAIL delete messages query "QUERY" trash excludetrash

# Delegates
gam user EMAIL delegate to DELEGATE
gam user EMAIL delegate delete DELEGATE

# Signature
gam user EMAIL signature file FILE

# Forwarding
gam user EMAIL forward on FORWARD_TO
gam user EMAIL forward off

# Labels
gam user EMAIL label LABEL_NAME
gam user EMAIL delete label LABEL_NAME

# Filters
gam user EMAIL filter from SENDER label LABEL
gam user EMAIL delete filter FILTER_ID
```

**Drive:**
```bash
# Search
gam user EMAIL show filelist query "QUERY"

# Transfer
gam user EMAIL transfer ownership FILE_ID to NEW_OWNER

# Share
gam user EMAIL add drivefileacl FILE_ID user USER role [reader|writer|owner]

# Unshare
gam user EMAIL delete drivefileacl FILE_ID user USER

# Permissions
gam user EMAIL show drivefileacl FILE_ID

# Usage
gam user EMAIL show driveusage
```

**Calendar:**
```bash
# Create calendar
gam user EMAIL create calendar NAME description DESC

# Delete calendar
gam user EMAIL delete calendar CALENDAR_ID

# Share
gam calendar CALENDAR_ID add [reader|writer|owner] user EMAIL

# Events
gam calendar CALENDAR_ID create event "TITLE" start START end END
gam calendar CALENDAR_ID delete events query "QUERY"
```

**Reports:**
```bash
# User reports
gam report users parameters accounts:last_login_time

# Usage reports
gam report usage customer parameters gmail:num_emails_sent

# Admin reports
gam report admin parameters account_warning_event

# Drive reports
gam report drive parameters doc_title,owner
```

---

## Appendix D: Error Handling Best Practices

### Common GAM Errors and Solutions

**Error Categories:**

1. **Authentication Errors**
   ```
   Error: OAuth2 credentials not configured
   Solution: Run 'gam oauth create'
   ```

2. **Permission Errors**
   ```
   Error: Insufficient permissions
   Solution: Check admin role permissions
   ```

3. **Rate Limiting**
   ```
   Error: User rate limit exceeded
   Solution: Implement exponential backoff
   ```

4. **Resource Not Found**
   ```
   Error: User not found
   Solution: Verify email address exists
   ```

5. **Invalid Parameters**
   ```
   Error: Invalid query
   Solution: Validate query syntax before execution
   ```

### Implementation in Code

```python
def execute_with_retry(gam_command, max_retries=3, backoff_factor=2):
    """
    Execute GAM command with retry logic for rate limiting.
    
    Args:
        gam_command (list): GAM command as list
        max_retries (int): Maximum retry attempts
        backoff_factor (int): Exponential backoff multiplier
        
    Returns:
        subprocess.CompletedProcess: Command result
        
    Raises:
        Exception: If all retries exhausted
    """
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                gam_command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check for rate limiting
            if 'rate limit' in result.stderr.lower():
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** attempt
                    time.sleep(sleep_time)
                    continue
            
            return result
            
        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                continue
            raise
    
    raise Exception(f"Command failed after {max_retries} attempts")
```

### Error Message Mapping

```python
ERROR_MESSAGES = {
    'oauth': {
        'pattern': r'oauth|credentials|authentication',
        'user_message': 'GAM is not authenticated. Please run "gam oauth create".',
        'help_link': 'https://github.com/GAM-team/GAM/wiki/Authorization'
    },
    'permissions': {
        'pattern': r'insufficient|permission denied|not authorized',
        'user_message': 'Insufficient permissions. Check admin role settings.',
        'help_link': 'https://support.google.com/a/answer/2405986'
    },
    'rate_limit': {
        'pattern': r'rate limit|quota exceeded',
        'user_message': 'Rate limit exceeded. Please wait and try again.',
        'help_link': 'https://developers.google.com/admin-sdk/directory/v1/limits'
    },
    'not_found': {
        'pattern': r'not found|does not exist',
        'user_message': 'Resource not found. Verify the email/ID is correct.',
        'help_link': None
    },
    'invalid_parameter': {
        'pattern': r'invalid|bad request',
        'user_message': 'Invalid parameter. Check your input and try again.',
        'help_link': None
    }
}

def get_user_friendly_error(gam_error):
    """
    Convert GAM error to user-friendly message.
    
    Args:
        gam_error (str): Raw GAM error message
        
    Returns:
        tuple: (user_message, help_link)
    """
    for error_type, config in ERROR_MESSAGES.items():
        if re.search(config['pattern'], gam_error, re.IGNORECASE):
            return (config['user_message'], config['help_link'])
    
    # Fallback
    return (f"Operation failed: {gam_error[:200]}", None)
```

---

## Appendix E: Performance Optimization Tips

### Optimization Strategies

**1. Batch Operations**
```python
# BAD: Individual API calls
for user in users:
    gam_command = ['gam', 'user', user, 'info']
    subprocess.run(gam_command)

# GOOD: Batch with GAM's batch capabilities
gam_command = ['gam', 'all', 'users', 'print', 'users']
subprocess.run(gam_command)  # Single call, all users
```

**2. Caching**
```python
# Cache user list for session
_user_cache = None
_cache_timestamp = None
CACHE_DURATION = 300  # 5 minutes

def get_users(force_refresh=False):
    global _user_cache, _cache_timestamp
    
    now = time.time()
    if not force_refresh and _user_cache and (now - _cache_timestamp < CACHE_DURATION):
        return _user_cache
    
    _user_cache = fetch_users()
    _cache_timestamp = now
    return _user_cache
```

**3. Parallel Processing**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_users_parallel(users, operation_func, max_workers=5):
    """
    Process users in parallel with thread pool.
    
    Args:
        users (list): Users to process
        operation_func (callable): Function to call per user
        max_workers (int): Max concurrent threads
        
    Yields:
        dict: Progress updates
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_user = {
            executor.submit(operation_func, user): user 
            for user in users
        }
        
        # Process as they complete
        completed = 0
        for future in as_completed(future_to_user):
            user = future_to_user[future]
            try:
                result = future.result()
                completed += 1
                yield {
                    'status': 'success',
                    'user': user,
                    'current': completed,
                    'total': len(users)
                }
            except Exception as e:
                yield {
                    'status': 'error',
                    'user': user,
                    'error': str(e)
                }
```

**4. Memory Management**
```python
# BAD: Load all results into memory
all_files = []
for user in users:
    files = get_user_files(user)
    all_files.extend(files)  # Memory grows linearly

# GOOD: Stream results
def stream_user_files(users):
    for user in users:
        files = get_user_files(user)
        for file in files:
            yield file  # Constant memory usage
```

**5. GUI Responsiveness**
```python
# Update GUI every N items to avoid too many redraws
UPDATE_FREQUENCY = 10

for i, item in enumerate(items):
    process_item(item)
    
    if i % UPDATE_FREQUENCY == 0:
        self.update_gui(i, len(items))
        self.update_idletasks()  # Let GUI breathe
```

### Performance Benchmarks

**Target Performance:**
- GUI startup: < 2 seconds
- Load user list (1000 users): < 10 seconds
- Single operation: < 1 second
- Bulk operation (100 users): < 2 minutes
- Memory usage: < 200 MB for typical operations

**Profiling:**
```python
import cProfile
import pstats

def profile_operation():
    """Profile an operation to find bottlenecks."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run operation
    execute_operation()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
```

---

## Appendix F: Security Checklist

### Pre-Release Security Audit

**Code Security:**
- [ ] No hardcoded passwords or API keys
- [ ] All user input validated and sanitized
- [ ] No SQL injection vulnerabilities (not applicable, but check if DB added)
- [ ] No command injection in subprocess calls
- [ ] File paths validated (no directory traversal)
- [ ] CSV parsing uses safe libraries
- [ ] No eval() or exec() usage
- [ ] All exceptions caught and logged safely

**Data Security:**
- [ ] Passwords never logged
- [ ] Credentials not in error messages
- [ ] Log files don't contain sensitive data
- [ ] CSV files validated before parsing
- [ ] Temporary files cleaned up
- [ ] User data not transmitted to third parties
- [ ] Telemetry is anonymous and opt-in

**Authentication:**
- [ ] GAM authentication properly checked
- [ ] No authentication bypass possible
- [ ] Session management secure (if applicable)
- [ ] Credentials stored securely by GAM

**Access Control:**
- [ ] Only authorized operations allowed
- [ ] Bulk operation confirmations required
- [ ] Dry-run mode doesn't leak data
- [ ] File permissions set correctly

**Dependencies:**
- [ ] All dependencies from trusted sources
- [ ] No known vulnerabilities in dependencies
- [ ] Dependencies pinned to specific versions
- [ ] Regular security updates planned

**Build Security:**
- [ ] Build process reproducible
- [ ] Executables signed (code signing certificate)
- [ ] No malware in distribution
- [ ] Checksum verification available

### Security Tools

**Static Analysis:**
```bash
# Install security scanners
pip install bandit safety

# Run Bandit (Python security scanner)
bandit -r . -ll -f json -o bandit_report.json

# Check for known vulnerabilities
safety check --json
```

**Dependency Audit:**
```bash
# Check for outdated packages
pip list --outdated

# Audit with pip-audit
pip install pip-audit
pip-audit
```

---

## Appendix G: Contribution Guidelines

### How to Contribute

**Getting Started:**
1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Run tests
6. Submit pull request

**Code Standards:**
- Follow PEP 8 style guide
- Maximum line length: 100 characters
- Use type hints where appropriate
- Write docstrings for all functions
- Add unit tests for new features
- Update documentation

**Commit Messages:**
```
Format: <type>(<scope>): <subject>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Examples:
feat(users): Add bulk password reset
fix(email): Correct filter creation command
docs(readme): Update installation instructions
```

**Pull Request Process:**
1. Update README.md with details of changes
2. Update CHANGELOG.md
3. Ensure all tests pass
4. Request review from maintainers
5. Address review feedback
6. Squash commits before merge

**What to Contribute:**
- Bug fixes
- New features (modules, operations)
- Documentation improvements
- Test coverage
- Performance optimizations
- UI/UX enhancements

**What Not to Contribute:**
- Breaking changes without discussion
- Features without documentation
- Code without tests
- Anything violating security best practices

---

## Appendix H: Troubleshooting Guide

### Common Issues and Solutions

**Issue: GAM not found**
```
Error: GAM is not installed or not found in PATH

Solutions:
1. Install GAM7: pip install gam7
2. Add GAM to PATH:
   - Mac/Linux: export PATH="$HOME/bin/gam7:$PATH"
   - Windows: Add GAM folder to system PATH
3. Verify: gam version
```

**Issue: Authentication failure**
```
Error: GAM is not authenticated

Solutions:
1. Run: gam oauth create
2. Follow browser prompts to authorize
3. Verify: gam info domain
4. Check admin permissions in Google Workspace
```

**Issue: Slow operations**
```
Problem: Bulk operations taking too long

Solutions:
1. Check network connection
2. Reduce batch size
3. Use filters to limit scope
4. Consider running during off-peak hours
5. Check GAM API quotas
```

**Issue: CSV import fails**
```
Error: CSV file invalid or unreadable

Solutions:
1. Verify file encoding is UTF-8
2. Check header row matches expected format
3. Remove blank rows
4. Validate email addresses
5. Use sample CSV template
```

**Issue: GUI freezes**
```
Problem: Application becomes unresponsive

Solutions:
1. Wait for operation to complete
2. Check if operation is running (look at logs)
3. Restart application
4. Report bug with details
5. Use smaller batch sizes
```

**Issue: Executable won't run (Windows)**
```
Error: Windows Defender or antivirus blocks execution

Solutions:
1. Add exception for executable
2. Right-click → Properties → Unblock
3. Run as administrator
4. Download from official source only
5. Verify checksum
```

**Issue: Operation fails silently**
```
Problem: No error shown but operation doesn't work

Solutions:
1. Check error log (View Error Log button)
2. Verify GAM command manually in terminal
3. Check user permissions
4. Look for rate limiting
5. Report bug with log file
```

---

## Appendix I: Feature Request Template

### How to Request New Features

**Use this template when requesting features:**

```markdown
## Feature Request

**Feature Name:** [Short descriptive name]

**Problem Statement:**
What problem does this feature solve? Why is it needed?

**Proposed Solution:**
Describe your proposed solution in detail.

**Alternative Solutions:**
Have you considered alternatives? What are they?

**GAM Commands:**
Which GAM commands would be used? Provide examples.

**User Interface:**
How should users interact with this feature?

**Use Cases:**
Provide 2-3 real-world scenarios where this would be useful.

**Priority:**
- [ ] Critical (can't do my job without it)
- [ ] High (would significantly improve workflow)
- [ ] Medium (nice to have)
- [ ] Low (minor improvement)

**Additional Context:**
Screenshots, mockups, or other relevant information.
```

**Examples of Good Feature Requests:**

1. **Bulk License Management**
   - Problem: Need to assign/remove licenses for many users
   - GAM commands: `gam user EMAIL add license`, etc.
   - UI: New tab in Users window
   - Use case: Onboarding 50 new employees

2. **Custom Report Builder**
   - Problem: Need to combine multiple report types
   - GAM commands: Multiple report commands
   - UI: Custom report tab with checkboxes
   - Use case: Monthly compliance report

---

## Appendix J: Release Checklist Template

### Pre-Release Checklist

**Version: X.Y.Z**
**Release Date: YYYY-MM-DD**

**Code:**
- [ ] All features complete
- [ ] All tests passing
- [ ] No critical bugs
- [ ] No TODO/FIXME in production code
- [ ] Code reviewed
- [ ] Security audit passed

**Documentation:**
- [ ] README.md updated
- [ ] CHANGELOG.md updated
- [ ] USER_GUIDE.md updated
- [ ] API documentation updated
- [ ] Version number updated in code
- [ ] Screenshots current

**Testing:**
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing complete
- [ ] Performance benchmarks met
- [ ] Cross-platform testing done
- [ ] Fresh install tested

**Build:**
- [ ] Windows executable builds
- [ ] Mac executable builds
- [ ] Linux executable builds
- [ ] All executables tested
- [ ] File sizes reasonable
- [ ] Icons included

**Distribution:**
- [ ] GitHub release created
- [ ] Executables uploaded
- [ ] Checksums provided
- [ ] Release notes complete
- [ ] Download links work
- [ ] Auto-updater configured

**Communication:**
- [ ] Blog post written
- [ ] Social media posts ready
- [ ] Email announcement prepared
- [ ] Community notified
- [ ] Support channels ready

**Post-Release:**
- [ ] Monitor for issues
- [ ] Respond to feedback
- [ ] Plan hotfix if needed
- [ ] Update project board
- [ ] Thank contributors

---

## Final Notes

This comprehensive roadmap provides everything needed to transform the GAM Admin Tool into a world-class Google Workspace administration platform.

**Key Success Factors:**
1. Follow the phases in order
2. Don't skip testing or documentation
3. Get user feedback early and often
4. Keep security top of mind
5. Build incrementally, release frequently

**Remember:**
- Quality > Speed
- User experience is paramount
- Security cannot be compromised
- Documentation is not optional
- Community contributions are valuable

**Getting Help:**
- GitHub Issues for bugs
- GitHub Discussions for questions
- GAM Google Group for GAM questions
- Stack Overflow for Python/tkinter help

**Stay Updated:**
- Follow GAM7 releases
- Monitor Google Workspace API changes
- Track Python updates
- Review security advisories

---

**Let's build something amazing together!**

Good luck with implementation! 🚀

## Phase 0: Critical Fixes and Refactoring

### 0.1: Bug Fixes (IMMEDIATE)

**File:** `modules/email.py`

**Issue:** Line 826 in `create_filter()` function
```python
# WRONG (current):
filter_parts = ['gam', 'user', '__USER__', 'filter']

# CORRECT:
filter_parts = [_get_gam_command(), 'user', '__USER__', 'filter']
```

**Action:** Fix this bug before proceeding with any new features.

**Test:** Create a filter for a single user and verify the GAM command executes correctly.

---

### 0.2: Base Classes Refactoring (HIGH PRIORITY)

**Goal:** Extract common patterns from email_window.py to avoid code duplication in future modules.

**New Files to Create:**

#### `gui/base_operation_window.py` (~500 lines)

Abstract base class that all operation windows inherit from.

**Features:**
- Target selection frame (single, group, all, CSV, list)
- Progress tracking frame (progress bar, results text, buttons)
- Common helper methods (browse CSV, load users, get target users)
- Threading framework for operations
- Confirmation dialogs for bulk operations
- Error log viewer

**Methods to Extract:**
```python
class BaseOperationWindow(tk.Toplevel):
    """Abstract base class for operation windows."""
    
    def __init__(self, parent, title):
        """Initialize window with title."""
        
    # TARGET SELECTION
    def create_target_selection_frame(self, parent, tab_id)
    def update_target_input(self, tab_id)
    def browse_csv(self, tab_id)
    def load_users_list(self, tab_id)
    def populate_listbox(self, tab_id, users)
    def get_target_users(self, tab_id)
    
    # PROGRESS AND RESULTS
    def create_progress_frame(self, parent)
    def clear_results(self, progress_frame)
    def view_error_log(self)
    
    # OPERATION EXECUTION
    def run_operation(self, operation_func, progress_frame, *args)
    def check_operation_queue(self, progress_frame, result_queue)
    
    # ABSTRACT METHODS (must be implemented by subclasses)
    @abstractmethod
    def create_operation_tabs(self):
        """Create operation-specific tabs."""
        pass
```

**Benefits:**
- Reduces code duplication by ~400 lines per module
- Ensures consistent UX across all modules
- Makes new modules faster to implement
- Centralizes bug fixes (fix once, applies everywhere)

**Implementation Steps:**
1. Create `gui/base_operation_window.py`
2. Copy common methods from `email_window.py`
3. Make methods generic (remove email-specific references)
4. Add abstract methods for subclass customization
5. Refactor `email_window.py` to inherit from base class
6. Test that email operations still work correctly
7. Document the base class for future developers

---

#### `modules/base_operations.py` (~300 lines)

Common backend functionality for all GAM operations.

**Features:**
- GAM command execution wrapper
- Progress yielding pattern
- Error handling and logging
- Success/failure tracking
- Timeout management

**Functions:**
```python
def execute_gam_command(command_args, timeout=30):
    """Execute a GAM command and return result."""
    
def execute_bulk_operation(operation_name, users, command_builder, *args):
    """
    Execute operation for multiple users with progress tracking.
    
    Args:
        operation_name (str): Name for logging
        users (list): List of user emails
        command_builder (callable): Function that builds GAM command
        *args: Arguments to pass to command_builder
        
    Yields:
        dict: Progress updates
        
    Returns:
        dict: Success/failure summary
    """
    
def build_gam_command(base_cmd, user_email, *args):
    """Build GAM command list with proper formatting."""
    
def validate_email(email):
    """Validate email address format."""
    
def validate_date(date_string):
    """Validate date format (YYYY/MM/DD)."""
```

**Implementation Steps:**
1. Create `modules/base_operations.py`
2. Extract common patterns from `modules/email.py`
3. Refactor email.py to use base operations
4. Test all email operations still work
5. Document for future module developers

---

## Phase 1: User Management Module

**Priority:** HIGH (Most frequently needed operations)
**Estimated Complexity:** Medium
**Estimated Time:** 6-8 hours

### Files to Create:

#### `modules/users.py` (~800 lines)

**Functions:**
1. `create_user(users_data, password, org_unit=None)`
   - Create new user accounts
   - Set initial password
   - Place in specific OU

2. `delete_user(users)`
   - Delete user accounts
   - Option to transfer data first

3. `suspend_user(users)`
   - Suspend user accounts

4. `restore_user(users)`
   - Restore suspended users

5. `reset_password(users, new_password=None)`
   - Reset user passwords
   - Generate random password if none provided

6. `update_user_info(users, **attributes)`
   - Update user attributes (name, title, phone, etc.)
   - Supports: givenName, familyName, title, phone, address

7. `change_org_unit(users, org_unit)`
   - Move users to different organizational unit

8. `rename_user(old_email, new_email)`
   - Rename user email address

9. `get_user_info(user_email)`
   - Retrieve detailed user information
   - For display in GUI

10. `list_user_aliases(user_email)`
    - List all aliases for a user

11. `add_alias(users, alias_email)`
    - Add email alias to users

12. `remove_alias(users, alias_email)`
    - Remove email alias from users

**GAM Command Examples:**
```bash
# Create user
gam create user johndoe@domain.com firstname John lastname Doe password TempPass123! ou /Staff

# Delete user
gam delete user johndoe@domain.com

# Suspend user
gam update user johndoe@domain.com suspended on

# Reset password
gam update user johndoe@domain.com password NewPass123!

# Update info
gam update user johndoe@domain.com title "Senior Manager" phone "555-1234"

# Move OU
gam update user johndoe@domain.com ou /Management

# Rename
gam update user oldname@domain.com email newname@domain.com

# Get info
gam info user johndoe@domain.com

# Add alias
gam create alias john.doe@domain.com user johndoe@domain.com
```

---

#### `gui/users_window.py` (~900 lines)

Inherits from `BaseOperationWindow`.

**Tabs:**
1. **Create Users**
   - CSV upload for bulk creation
   - Fields: email, firstName, lastName, password, orgUnit
   - Option to generate random passwords
   - Option to send welcome email

2. **Delete Users**
   - Target selection
   - Confirmation with user count
   - Option to transfer data to another user first

3. **Suspend/Restore Users**
   - Toggle between suspend and restore
   - Target selection
   - Bulk operation support

4. **Reset Passwords**
   - Target selection
   - Password input (or auto-generate)
   - Option to require password change on next login
   - Option to email new password to user

5. **Update User Info**
   - Target selection
   - Checkboxes for which fields to update
   - Fields: First Name, Last Name, Title, Phone, Address
   - Bulk update from CSV

6. **Manage Org Units**
   - Target selection
   - Dropdown or text entry for OU path
   - Show current OU (for single user)

7. **Manage Aliases**
   - Target selection
   - Add or Remove toggle
   - Alias email input
   - List existing aliases button (for single user)

**CSV Format Examples:**

Create Users CSV:
```csv
email,firstName,lastName,password,orgUnit
john.doe@domain.com,John,Doe,TempPass123!,/Staff
jane.smith@domain.com,Jane,Smith,TempPass456!,/Management
```

Update Users CSV:
```csv
email,title,phone
john.doe@domain.com,Senior Developer,555-1234
jane.smith@domain.com,Project Manager,555-5678
```

**Special Features:**
- Password generator button (creates secure random passwords)
- "Test create" mode (validates but doesn't create)
- Export results to CSV (list of created users, passwords)

---

### Testing Checklist for User Management:

- [ ] Create single user works
- [ ] Create users from CSV works
- [ ] Delete user with confirmation works
- [ ] Suspend user works
- [ ] Restore suspended user works
- [ ] Reset password works
- [ ] Auto-generate password works
- [ ] Update user info (all fields) works
- [ ] Move user to different OU works
- [ ] Add alias works
- [ ] Remove alias works
- [ ] Get user info displays correctly
- [ ] Bulk operations show progress
- [ ] Errors are logged and displayed
- [ ] CSV validation works for all formats

---

## Phase 2: Group Management Module

**Priority:** HIGH (Second most requested)
**Estimated Complexity:** Medium
**Estimated Time:** 6-8 hours

### Files to Create:

#### `modules/groups.py` (~700 lines)

**Functions:**
1. `create_group(groups_data)`
   - Create new groups
   - Set name, description, settings

2. `delete_group(groups)`
   - Delete groups

3. `add_members(groups, members, role='MEMBER')`
   - Add members to groups
   - Support roles: MEMBER, MANAGER, OWNER

4. `remove_members(groups, members)`
   - Remove members from groups

5. `list_members(group_email)`
   - List all members of a group
   - Include roles

6. `update_group_settings(groups, **settings)`
   - Update group settings
   - Who can post, join, view members, etc.

7. `get_group_info(group_email)`
   - Retrieve group details

8. `list_user_groups(user_email)`
   - List all groups a user belongs to

9. `add_group_alias(groups, alias_email)`
   - Add alias to group

10. `remove_group_alias(groups, alias_email)`
    - Remove alias from group

11. `sync_group_members(group_email, members_list)`
    - Sync group membership to exact list
    - Add missing, remove extra

**GAM Command Examples:**
```bash
# Create group
gam create group sales@domain.com name "Sales Team" description "Sales department group"

# Delete group
gam delete group sales@domain.com

# Add members
gam update group sales@domain.com add member user john@domain.com
gam update group sales@domain.com add manager user jane@domain.com

# Remove members
gam update group sales@domain.com remove member user john@domain.com

# List members
gam print group-members group sales@domain.com

# Update settings
gam update group sales@domain.com whocanpostmessage ALL_IN_DOMAIN_CAN_POST

# Get info
gam info group sales@domain.com

# List user's groups
gam user john@domain.com print groups

# Add alias
gam create group-alias salesteam@domain.com group sales@domain.com
```

---

#### `gui/groups_window.py` (~800 lines)

Replace the current placeholder with full implementation.

**Tabs:**
1. **Create Groups**
   - Single group or CSV
   - Fields: email, name, description
   - Advanced settings (who can post, join, etc.)

2. **Delete Groups**
   - Target selection
   - Confirmation

3. **Manage Members**
   - Select groups (single, CSV, list)
   - Add or Remove toggle
   - Member selection (single, CSV, list)
   - Role selection (Member, Manager, Owner)
   - Sync option (make membership exactly match CSV)

4. **List Members**
   - Select group
   - Display members with roles
   - Export to CSV button

5. **Group Settings**
   - Select groups
   - Update settings (dropdown/toggle for each setting)
   - Settings: who can post, join, view members, etc.

6. **Group Aliases**
   - Select groups
   - Add or Remove toggle
   - Alias input

7. **User's Groups**
   - Enter user email
   - Display all groups user belongs to
   - Show role in each group
   - Quick remove button for each group

**CSV Format Examples:**

Create Groups CSV:
```csv
email,name,description
sales@domain.com,Sales Team,Sales department group
support@domain.com,Support Team,Customer support group
```

Add Members CSV:
```csv
group,member,role
sales@domain.com,john@domain.com,MEMBER
sales@domain.com,jane@domain.com,MANAGER
support@domain.com,john@domain.com,MEMBER
```

**Special Features:**
- Nested group support (groups as members of groups)
- Bulk membership sync (CSV defines exact membership)
- Export group membership reports

---

### Testing Checklist for Group Management:

- [ ] Create single group works
- [ ] Create groups from CSV works
- [ ] Delete group with confirmation works
- [ ] Add members (single, bulk) works
- [ ] Remove members works
- [ ] Add managers/owners works
- [ ] List members displays correctly
- [ ] Update group settings works
- [ ] Add group alias works
- [ ] List user's groups works
- [ ] Sync membership works (adds and removes)
- [ ] Nested groups work
- [ ] Export membership to CSV works

---

## Phase 3: Drive Operations Module

**Priority:** HIGH (Security and data management)
**Estimated Complexity:** High (Drive API is complex)
**Estimated Time:** 10-12 hours

### Files to Create:

#### `modules/drive.py` (~1000 lines)

**Functions:**

**File Operations:**
1. `search_files(users, query, owned_by_user=True)`
   - Search for files by query
   - Return file IDs, names, owners

2. `transfer_ownership(files, new_owner)`
   - Transfer file ownership

3. `delete_files(users, file_ids)`
   - Delete files (moves to trash unless excludetrash)

4. `share_file(files, users, role='reader')`
   - Share files with users
   - Roles: reader, commenter, writer, owner

5. `unshare_file(files, users)`
   - Remove user access from files

6. `list_permissions(file_id)`
   - List all permissions for a file

7. `update_permissions(files, user, role)`
   - Update existing permission role

**Folder Operations:**
8. `create_folder(users, folder_name, parent_folder=None)`
   - Create folders in user drives

9. `move_file(files, target_folder)`
   - Move files to different folder

**Drive Management:**
10. `get_drive_usage(users)`
    - Get storage quota and usage

11. `empty_trash(users)`
    - Empty trash for users

**Non-Domain ACL Detection (HIGH PRIORITY SECURITY FEATURE):**
12. `find_non_domain_acls(users, domain)`
    - Scan for files shared outside domain
    - Based on: https://github.com/taers232c/GAM-Scripts3/blob/master/GetNonDomainDriveACLs.py
    - Return detailed report

**GAM Command Examples:**
```bash
# Search files
gam user john@domain.com show filelist query "name contains 'budget'"

# Transfer ownership
gam user john@domain.com transfer ownership file_id to jane@domain.com

# Delete files
gam user john@domain.com delete drivefile id file_id purge excludetrash

# Share file
gam user john@domain.com add drivefileacl file_id user jane@domain.com role reader

# Unshare file
gam user john@domain.com delete drivefileacl file_id user jane@domain.com

# List permissions
gam user john@domain.com show drivefileacl file_id

# Create folder
gam user john@domain.com create drivefile drivefilename "Projects" mimetype gfolder

# Get usage
gam user john@domain.com show driveusage

# Empty trash
gam user john@domain.com empty drivetrash
```

---

#### `gui/drive_window.py` (~1000 lines)

Replace the current placeholder with full implementation.

**Tabs:**
1. **Search Files**
   - Select users
   - Query builder (name, type, modified date, shared with)
   - Show results in table
   - Export results to CSV
   - Actions: Transfer, Delete, Share, Unshare (on selected results)

2. **Transfer Ownership**
   - Select users (current owners)
   - File ID input or search
   - New owner selection
   - Bulk transfer from CSV

3. **Share/Unshare Files**
   - Select files (ID, search, CSV)
   - Add or Remove toggle
   - User/group selection
   - Role selection (for sharing)
   - Bulk operation support

4. **Manage Permissions**
   - File ID input
   - List current permissions (table)
   - Add, Remove, Update buttons
   - Shows: user, role, type, inherited

5. **Folder Operations**
   - Create folders
   - Move files to folders
   - Organize bulk files from CSV

6. **Drive Cleanup**
   - Select users
   - Empty trash
   - Show storage usage before/after
   - Bulk operation

7. **Security Audit (Non-Domain ACLs)**
   - Select users or all users
   - Domain input (to check against)
   - Run scan (can take long time)
   - Display results in table:
     - File name
     - Owner
     - Shared with (external emails)
     - Permission level
   - Export to CSV
   - Bulk unshare option

**CSV Format Examples:**

Transfer Ownership CSV:
```csv
file_id,current_owner,new_owner
abc123xyz,john@domain.com,jane@domain.com
def456uvw,john@domain.com,jane@domain.com
```

Share Files CSV:
```csv
file_id,user,role
abc123xyz,partner@external.com,reader
def456uvw,contractor@external.com,commenter
```

**Special Features:**
- File preview (if possible via GAM)
- Storage usage dashboard (pie chart showing usage by user)
- Scheduled scans for external sharing (save config)
- Non-domain ACL report with filters (by user, by date, by domain)

---

### Non-Domain ACL Detection Implementation

Based on the GAM-Scripts3 implementation, this is the algorithm:

```python
def find_non_domain_acls(users, domain):
    """
    Scan user drives for files shared outside the domain.
    
    This is a critical security feature to detect data leakage.
    
    Args:
        users (list): Users to scan
        domain (str): Your domain (e.g., "company.com")
        
    Yields:
        dict: Progress and results
        
    Returns:
        list: List of dicts with file info and external shares
    """
    
    results = []
    
    for user in users:
        # Get all files owned by user
        # gam user john@domain.com print filelist allfields
        
        for file in files:
            # Get permissions
            # gam user john@domain.com show drivefileacl file_id
            
            for permission in permissions:
                email = permission.get('emailAddress', '')
                
                # Check if external
                if '@' in email and not email.endswith(f'@{domain}'):
                    results.append({
                        'owner': user,
                        'file_name': file['name'],
                        'file_id': file['id'],
                        'external_email': email,
                        'role': permission['role'],
                        'type': permission['type']
                    })
                    
                    yield {
                        'status': 'found',
                        'message': f"Found: {file['name']} shared with {email}"
                    }
    
    return results
```

**GUI Features:**
- Start/Stop scan button
- Real-time progress (files scanned, external shares found)
- Results table with sorting and filtering
- Export to CSV
- Bulk actions: Remove access, Transfer ownership, Email owner

---

### Testing Checklist for Drive Operations:

- [ ] File search works with various queries
- [ ] Search results display correctly
- [ ] Transfer ownership works
- [ ] Delete files works (uses excludetrash)
- [ ] Share file with user/group works
- [ ] Unshare file works
- [ ] List permissions shows all access
- [ ] Update permission role works
- [ ] Create folder works
- [ ] Move file to folder works
- [ ] Get drive usage displays correctly
- [ ] Empty trash works
- [ ] Non-domain ACL scan works
- [ ] ACL scan can be stopped
- [ ] ACL results export to CSV
- [ ] Bulk operations from CSV work
- [ ] All operations show progress

---

## Phase 4: Reports Module

**Priority:** MEDIUM (Visibility and auditing)
**Estimated Complexity:** Medium
**Estimated Time:** 6-8 hours

### Files to Create:

#### `modules/reports.py` (~600 lines)

**Functions:**

**User Reports:**
1. `get_user_login_report(start_date, end_date, users=None)`
   - User login activity
   - Last login time
   - Login locations

2. `get_user_usage_report(date, users=None)`
   - Gmail storage usage
   - Drive storage usage
   - Active/inactive accounts

3. `get_suspended_users()`
   - List all suspended users

**Admin Reports:**
4. `get_admin_actions_report(start_date, end_date, admin=None)`
   - Admin activity audit
   - User creation/deletion
   - Settings changes

5. `get_password_changes_report(start_date, end_date)`
   - Password change events
   - Who changed passwords

**Email Reports:**
6. `get_email_usage_report(date, users=None)`
   - Emails sent/received
   - Top senders/receivers

7. `get_gmail_forwarding_report()`
   - Users with forwarding enabled
   - Forwarding destinations

**Drive Reports:**
8. `get_drive_activity_report(start_date, end_date, users=None)`
   - File creation/modification/sharing
   - Most active users

9. `get_external_sharing_report()`
   - Files shared externally
   - By user, by file

**Calendar Reports:**
10. `get_calendar_usage_report(start_date, end_date, users=None)`
    - Calendar events created
    - Meeting statistics

**GAM Command Examples:**
```bash
# User login report
gam report users parameters accounts:last_login_time

# User usage
gam report usage customer parameters gmail:num_emails_received,drive:num_files

# Admin actions
gam report admin parameters account_warning_event,user_creation

# Email usage
gam report usage user parameters gmail:num_emails_sent

# Drive activity
gam report drive parameters doc_title,owner
```

---

#### `gui/reports_window.py` (~700 lines)

Replace the current placeholder with full implementation.

**Tabs:**
1. **User Reports**
   - Report type dropdown (Login, Usage, Suspended)
   - Date range selection
   - User filter (all, single, CSV)
   - Generate Report button
   - Display results in table
   - Export to CSV
   - Charts (if possible): login frequency, storage usage

2. **Admin Reports**
   - Report type dropdown (Admin Actions, Password Changes)
   - Date range selection
   - Admin filter (optional)
   - Generate Report button
   - Display audit trail
   - Export to CSV

3. **Email Reports**
   - Report type dropdown (Usage, Forwarding)
   - Date range selection
   - User filter
   - Generate Report button
   - Display results
   - Charts: top senders, top receivers

4. **Drive Reports**
   - Report type dropdown (Activity, External Sharing)
   - Date range selection
   - User filter
   - Generate Report button
   - Display results
   - Charts: most active users, sharing stats

5. **Calendar Reports**
   - Date range selection
   - User filter
   - Generate Report button
   - Display meeting statistics

6. **Custom Reports**
   - Select multiple report types
   - Combine data
   - Custom filters
   - Scheduled reports (save config)

**Special Features:**
- Date range presets (Today, This Week, This Month, Last 30 Days)
- Report templates (save common report configs)
- Scheduled reports (run automatically, email results)
- Data visualization (basic charts using tkinter canvas or matplotlib)
- Compare periods (this month vs last month)

---

### Testing Checklist for Reports:

- [ ] User login report generates
- [ ] User usage report shows storage
- [ ] Suspended users list works
- [ ] Admin actions audit works
- [ ] Password changes report works
- [ ] Email usage report works
- [ ] Forwarding report lists all
- [ ] Drive activity report works
- [ ] External sharing report works
- [ ] Calendar usage report works
- [ ] All reports export to CSV
- [ ] Date range filtering works
- [ ] User filtering works
- [ ] Charts display correctly (if implemented)
- [ ] Report templates save/load

---

## Phase 5: Calendar Operations Module

**Priority:** MEDIUM
**Estimated Complexity:** Medium
**Estimated Time:** 6-8 hours

### Files to Create:

#### `modules/calendar.py` (~600 lines)

**Functions:**

**Calendar Management:**
1. `create_calendar(users, calendar_name, description=None)`
   - Create new calendars

2. `delete_calendar(users, calendar_id)`
   - Delete calendars

3. `list_calendars(user_email)`
   - List all calendars for user

**Sharing:**
4. `share_calendar(calendars, users, role='reader')`
   - Share calendar with users
   - Roles: reader, writer, owner

5. `unshare_calendar(calendars, users)`
   - Remove access

6. `get_calendar_acl(calendar_id)`
   - List all permissions

**Events:**
7. `create_event(calendars, event_data)`
   - Create calendar events
   - Support recurring events

8. `delete_events(calendars, query)`
   - Delete events by query

9. `list_events(calendar_id, start_date, end_date)`
   - List events in date range

**Resource Calendars:**
10. `create_resource_calendar(resource_data)`
    - Create resource calendars (conference rooms, equipment)

11. `list_resources()`
    - List all resource calendars

**GAM Command Examples:**
```bash
# Create calendar
gam user john@domain.com create calendar "Project Calendar" description "Team project calendar"

# Delete calendar
gam user john@domain.com delete calendar calendar_id

# List calendars
gam user john@domain.com print calendars

# Share calendar
gam calendar calendar_id add reader user jane@domain.com

# Create event
gam calendar calendar_id create event "Team Meeting" start "2025-01-15T10:00:00" end "2025-01-15T11:00:00"

# Delete events
gam calendar calendar_id delete events query "Team Meeting"

# List events
gam calendar calendar_id show events after "2025-01-01" before "2025-01-31"
```

---

#### `gui/calendar_window.py` (~700 lines)

Replace the current placeholder with full implementation.

**Tabs:**
1. **Manage Calendars**
   - Create calendars
   - Delete calendars
   - List user's calendars

2. **Share Calendars**
   - Select calendars
   - Add or Remove access
   - User selection
   - Role selection
   - Bulk operations

3. **Manage Events**
   - Create events (single or recurring)
   - Delete events by query
   - List events in date range
   - Bulk event creation from CSV

4. **Resource Calendars**
   - Create resources (rooms, equipment)
   - List resources
   - Manage resource access

**CSV Format Examples:**

Create Events CSV:
```csv
calendar,title,start,end,description,recurring
cal123,Team Meeting,2025-01-15T10:00:00,2025-01-15T11:00:00,Weekly team sync,WEEKLY
cal456,Project Review,2025-01-20T14:00:00,2025-01-20T15:00:00,Monthly review,MONTHLY
```

**Special Features:**
- Calendar picker (visual date/time selection)
- Recurring event builder (RRULE generator)
- Bulk event creation (CSV template provided)
- Calendar overlay view (if feasible)

---

### Testing Checklist for Calendar:

- [ ] Create calendar works
- [ ] Delete calendar works
- [ ] List calendars displays all
- [ ] Share calendar with user works
- [ ] Unshare calendar works
- [ ] Get calendar ACL shows all
- [ ] Create single event works
- [ ] Create recurring event works
- [ ] Delete events by query works
- [ ] List events shows correctly
- [ ] Create resource calendar works
- [ ] Bulk operations work
- [ ] CSV import works

---

## Phase 6: Advanced Features

**Priority:** LOW (Nice to have)
**Estimated Complexity:** Varies
**Estimated Time:** Variable

### 6.1: Configuration System

**File:** `config.py` (~200 lines)

**Features:**
- Default timeout values
- Max bulk operation sizes (e.g., confirm if >100 users)
- CSV header templates for each operation
- GAM command templates
- User preferences (theme, default CSV directory)
- Recent operations history (last 10)

**Implementation:**
```python
# config.py

# Timeouts (seconds)
GAM_COMMAND_TIMEOUT = 30
GAM_LONG_COMMAND_TIMEOUT = 60
GAM_REPORT_TIMEOUT = 120

# Bulk operation limits
BULK_CONFIRM_THRESHOLD = 50  # Confirm if affecting >50 users
MAX_BULK_OPERATION = 1000    # Hard limit

# CSV Templates
CSV_HEADERS = {
    'create_users': ['email', 'firstName', 'lastName', 'password', 'orgUnit'],
    'update_users': ['email', 'title', 'phone'],
    'add_group_members': ['group', 'member', 'role'],
    'transfer_ownership': ['file_id', 'current_owner', 'new_owner'],
}

# Default values
DEFAULT_PASSWORD_LENGTH = 16
DEFAULT_ORG_UNIT = '/Users'
DEFAULT_USER_ROLE = 'MEMBER'

# UI Settings
WINDOW_DEFAULT_SIZE = {
    'main': (800, 600),
    'email': (950, 750),
    'users': (900, 700),
    'groups': (900, 700),
    'drive': (1000, 800),
}

# Operation history
MAX_HISTORY_ITEMS = 10
HISTORY_FILE = 'operation_history.json'
```

**GUI Integration:**
- Add Settings menu to main window
- Settings dialog to modify config
- Save/load user preferences

---

### 6.2: Dry-Run Mode

**Implementation:** Modify all backend functions to accept `dry_run=False` parameter.

**Features:**
- Preview what would happen without executing
- Show GAM commands that would be run
- Display affected users/groups/files
- No actual changes made

**Implementation in Backend:**
```python
def delete_messages(users, query, date_from=None, date_to=None, dry_run=False):
    """
    Delete messages with optional dry-run mode.
    
    Args:
        dry_run (bool): If True, only show what would happen
    """
    for i, user_email in enumerate(users, start=1):
        # Build command
        cmd = [_get_gam_command(), 'user', user_email, 'delete', 'messages', ...]
        
        if dry_run:
            yield {
                'status': 'dry-run',
                'message': f"Would execute: {' '.join(cmd)}"
            }
            continue
        
        # Execute for real
        result = subprocess.run(cmd, ...)
```

**GUI Changes:**
- Add "Dry Run" checkbox to all operation tabs
- Change "Execute" button text to "Preview" when dry-run enabled
- Show commands in results area
- Add "Execute For Real" button after dry-run preview

---

### 6.3: Undo Last Operation

**File:** `utils/operation_history.py` (~300 lines)

**Features:**
- Store last N operations with details
- Provide undo commands for reversible operations
- Warn when operation cannot be undone

**Implementation:**
```python
import json
from datetime import datetime

HISTORY_FILE = 'operation_history.json'

def log_operation(operation_type, details, undo_possible=True, undo_commands=None):
    """
    Log an operation to history.
    
    Args:
        operation_type (str): Type of operation (e.g., "Delete Messages")
        details (dict): Operation details
        undo_possible (bool): Whether operation can be undone
        undo_commands (list): List of GAM commands to undo (if possible)
    """
    
def get_operation_history(limit=10):
    """Get recent operations."""
    
def undo_operation(operation_id):
    """
    Undo a specific operation by running undo commands.
    
    Returns:
        tuple: (success, message)
    """
```

**Undo Examples:**
- Add Delegate → Remove Delegate
- Enable Forwarding → Disable Forwarding
- Add Group Member → Remove Group Member
- Share File → Unshare File

**Cannot Undo:**
- Delete Messages (permanently deleted)
- Delete User (some data lost)
- Transfer Ownership (reversible but not automatic)

**GUI Integration:**
- Add "History" menu item to main window
- Show operation history dialog
- Each item has "Undo" button (if applicable)
- Show undo status after execution

---

### 6.4: Operation Templates

**File:** `utils/templates.py` (~200 lines)

**Features:**
- Save common workflows as templates
- Load and execute templates
- Share templates (export/import JSON)

**Template Structure:**
```json
{
  "name": "New Employee Setup",
  "description": "Create user, add to groups, share calendars",
  "operations": [
    {
      "module": "users",
      "function": "create_user",
      "parameters": {
        "email": "{{email}}",
        "firstName": "{{firstName}}",
        "lastName": "{{lastName}}",
        "password": "{{password}}",
        "orgUnit": "/Staff"
      }
    },
    {
      "module": "groups",
      "function": "add_members",
      "parameters": {
        "groups": ["all-staff@domain.com", "team-sales@domain.com"],
        "members": ["{{email}}"],
        "role": "MEMBER"
      }
    },
    {
      "module": "calendar",
      "function": "share_calendar",
      "parameters": {
        "calendars": ["company-events@domain.com"],
        "users": ["{{email}}"],
        "role": "reader"
      }
    }
  ]
}
```

**Template Variables:**
- {{email}}, {{firstName}}, {{lastName}}, {{password}}
- User prompted for values when running template

**GUI Integration:**
- Add "Templates" menu to main window
- Template manager dialog:
  - List saved templates
  - Create/Edit/Delete buttons
  - Run button (prompts for variables)
- Template editor with JSON or form-based interface

**Common Templates to Include:**
- New Employee Setup
- Employee Offboarding
- Department Transfer
- Shared Drive Setup
- Group Communication Setup

---

### 6.5: Scheduled Operations

**File:** `utils/scheduler.py` (~300 lines)

**Features:**
- Schedule operations to run at specific times
- Recurring schedules (daily, weekly, monthly)
- Email notifications when complete
- Requires background process or OS scheduler integration

**Implementation:**
- Save operation configs with schedule
- On startup, check for pending operations
- Option 1: Background thread (runs while app open)
- Option 2: Generate cron job / Windows Task (runs independently)

**GUI Integration:**
- Add "Schedule" tab to each operation window
- Schedule configurator:
  - Date/time picker
  - Recurrence options
  - Notification email
- "Scheduled Operations" menu item shows pending jobs

**Use Cases:**
- Weekly external sharing audit
- Monthly inactive user report
- Daily drive usage report
- Quarterly group membership audit

---

### 6.6: Enhanced User Experience Features

#### Search/Filter in Dropdowns

**Problem:** Loading 1000+ users into dropdown is slow and hard to navigate.

**Solution:**
```python
class SearchableListbox(tk.Frame):
    """
    Listbox with search/filter capability.
    
    Features:
    - Search as you type
    - Filter list in real-time
    - Multi-select support
    - Clear search button
    """
    
    def __init__(self, parent, items):
        # Search entry at top
        # Filtered listbox below
        # Status label showing "X of Y items"
```

**Implementation:**
- Replace all Listbox widgets with SearchableListbox
- Add search entry above listbox
- Filter items as user types
- Show count of filtered vs total items

---

#### Progress Percentage

**Current:** Shows "Processing user 5 of 100..."

**Enhanced:** 
```
Processing user 5 of 100... (5%)
[████░░░░░░░░░░░░░░] 5%
Estimated time remaining: 3 minutes
```

**Implementation:**
```python
def run_operation(self, operation_func, progress_frame, *args):
    """Enhanced with percentage and time estimate."""
    
    start_time = time.time()
    
    for progress in operation_func(*args):
        current = progress.get('current', 0)
        total = progress.get('total', 0)
        
        if total > 0:
            percentage = (current / total) * 100
            progress_frame.progress_bar['value'] = percentage
            
            # Estimate time remaining
            elapsed = time.time() - start_time
            if current > 0:
                avg_time_per_item = elapsed / current
                remaining_items = total - current
                eta_seconds = avg_time_per_item * remaining_items
                eta_str = format_time(eta_seconds)
                
                message = f"{progress['message']} ({percentage:.1f}%) - ETA: {eta_str}"
            else:
                message = progress['message']
                
            # Update display
            ...
```

---

#### Export Results to CSV

**Add to all result displays:**
- "Export Results" button
- Saves current results to CSV
- Includes timestamp in filename
- Opens save dialog for user to choose location

**Implementation:**
```python
def export_results_to_csv(self, results, operation_name):
    """
    Export operation results to CSV.
    
    Args:
        results (list): List of result dicts
        operation_name (str): Name for filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    default_filename = f"{operation_name}_{timestamp}.csv"
    
    filename = filedialog.asksaveasfilename(
        defaultextension='.csv',
        initialfile=default_filename,
        filetypes=[('CSV files', '*.csv')]
    )
    
    if filename:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
```

---

#### Dark Mode Toggle

**Implementation:**
- Add "Dark Mode" toggle to Settings
- Use ttk themes: 'clam' (light), 'alt' (dark)
- Save preference in config

```python
def toggle_dark_mode(enabled):
    """Switch between light and dark themes."""
    style = ttk.Style()
    if enabled:
        style.theme_use('alt')
        # Additional color configuration
    else:
        style.theme_use('clam')
```

---

#### Cancel Long-Running Operations

**Current:** Operations run to completion, no way to stop.

**Enhanced:**
- Add "Cancel" button during operations
- Set cancellation flag
- Backend checks flag between iterations
- Clean shutdown with partial results

**Implementation:**
```python
class BaseOperationWindow:
    def __init__(self):
        self.cancel_flag = False
    
    def run_operation(self, operation_func, progress_frame, *args):
        self.cancel_flag = False
        
        # Show Cancel button
        cancel_btn.config(state=tk.NORMAL)
        
        for progress in operation_func(*args, cancel_flag=self.cancel_flag):
            if self.cancel_flag:
                progress_frame.results_text.insert("Operation cancelled by user")
                break
            # ... process progress
    
    def cancel_operation(self):
        self.cancel_flag = True
```

**Backend Support:**
```python
def delete_messages(users, query, cancel_flag=None):
    for i, user in enumerate(users):
        # Check cancellation
        if cancel_flag and cancel_flag.is_set():
            yield {'status': 'cancelled'}
            break
        
        # Continue operation
        ...
```

---

### 6.7: Data Visualization

**Library:** Use matplotlib (already supported by PyInstaller)

**Features:**
- Storage usage pie charts (Drive Reports)
- Login activity bar charts (User Reports)
- Group membership growth over time (Group Reports)
- External sharing trends (Drive Security)

**Implementation:**
```python
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def show_storage_chart(data):
    """
    Display storage usage pie chart in tkinter window.
    
    Args:
        data (dict): {user: storage_bytes}
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
    ax.set_title('Storage Usage by User')
    
    # Embed in tkinter
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
```

**Charts to Add:**
- Drive Reports: Storage usage pie chart
- User Reports: Login frequency bar chart
- Group Reports: Membership size comparison
- Email Reports: Email volume over time (line chart)

---

## Phase 7: Team Drives Module

**Priority:** MEDIUM
**Estimated Complexity:** Medium
**Estimated Time:** 4-6 hours

### Files to Create:

#### `modules/team_drives.py` (~500 lines)

**Functions:**
1. `create_team_drive(name, org_unit=None)`
   - Create shared/team drives

2. `delete_team_drive(drive_ids)`
   - Delete team drives

3. `list_team_drives()`
   - List all team drives

4. `add_team_drive_member(drive_ids, users, role='reader')`
   - Add members to team drives

5. `remove_team_drive_member(drive_ids, users)`
   - Remove members

6. `get_team_drive_members(drive_id)`
   - List all members

7. `transfer_team_drive_ownership(drive_id, new_owner)`
   - Change organizer

8. `search_team_drive_files(drive_ids, query)`
   - Search files in team drives

**GAM Commands:**
```bash
# Create team drive
gam create teamdrive "Marketing Team Drive"

# Delete team drive
gam delete teamdrive drive_id

# List team drives
gam print teamdrives

# Add member
gam add drivefileacl drive_id user john@domain.com role writer teamdrive drive_id

# Remove member
gam delete drivefileacl drive_id user john@domain.com teamdrive drive_id
```

---

#### `gui/team_drives_window.py` (~600 lines)

**Tabs:**
1. **Manage Team Drives**
   - Create team drives
   - Delete team drives
   - List all team drives

2. **Manage Members**
   - Select team drives
   - Add or Remove members
   - Role selection
   - Bulk operations

3. **Team Drive Files**
   - Search files
   - Manage permissions
   - Similar to Drive Operations but scoped to team drives

**Special Note:** Replace the placeholder acls_window.py with this, or create separate team_drives_window.py.

---

## Phase 8: Testing and Quality Assurance

### 8.1: Comprehensive Test Suite

**Files to Create:**

#### `tests/test_all_modules.py` (~500 lines)

**Test Categories:**
1. **Unit Tests**
   - Test each backend function with mock GAM commands
   - Test input validation
   - Test error handling

2. **Integration Tests**
   - Test GUI + Backend integration
   - Test CSV import/export
   - Test bulk operations

3. **End-to-End Tests**
   - Test complete workflows
   - Test with actual GAM (optional, requires test domain)

**Framework:** Use Python's `unittest` module

**Example:**
```python
import unittest
from unittest.mock import patch, MagicMock
from modules.users import create_user

class TestUserModule(unittest.TestCase):
    
    @patch('modules.users.subprocess.run')
    def test_create_user_success(self, mock_run):
        """Test successful user creation."""
        mock_run.return_value = MagicMock(returncode=0)
        
        users_data = [{
            'email': 'test@domain.com',
            'firstName': 'Test',
            'lastName': 'User',
            'password': 'TempPass123!'
        }]
        
        results = list(create_user(users_data))
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'success')
        mock_run.assert_called_once()
```

---

#### `tests/test_gui.py` (~300 lines)

**GUI Tests:**
- Test window creation
- Test widget layout
- Test validation logic
- Test user input handling

**Note:** GUI tests are limited without actual GUI interaction, but can test logic.

---

### 8.2: Performance Testing

**File:** `tests/benchmark.py` (~200 lines)

**Tests:**
- Bulk operation performance (100, 500, 1000 users)
- CSV parsing performance (large files)
- GUI responsiveness during operations
- Memory usage during large operations

**Benchmarks to Establish:**
- Operations per second
- Memory usage per 1000 users
- GUI freeze time (should be 0)

---

### 8.3: Security Audit

**Checklist:**
- [ ] No passwords stored in logs
- [ ] No credentials in error messages
- [ ] CSV files validated before parsing
- [ ] No command injection vulnerabilities in GAM commands
- [ ] File paths validated (no directory traversal)
- [ ] All user input sanitized
- [ ] Dry-run mode doesn't leak sensitive data

**Tool:** Use `bandit` for Python security linting
```bash
pip install bandit
bandit -r . -ll
```

---

## Phase 9: Documentation

### 9.1: User Documentation

**Files to Create:**

#### `docs/USER_GUIDE.md` (~2000 lines)

**Sections:**
1. **Getting Started**
   - Installation
   - First-time setup
   - Authentication

2. **Email Operations**
   - Complete guide for each operation
   - Screenshots
   - Common scenarios
   - Troubleshooting

3. **User Management**
   - Creating users
   - Bulk operations
   - CSV formats
   - Examples

4. **Group Management**
   - Creating groups
   - Managing members
   - Best practices

5. **Drive Operations**
   - File management
   - Security scanning
   - Bulk operations

6. **Reports**
   - Available reports
   - Interpreting results
   - Exporting data

7. **Calendar Operations**
   - Calendar management
   - Event creation
   - Sharing

8. **Advanced Features**
   - Templates
   - Scheduling
   - Dry-run mode
   - History and undo

9. **Troubleshooting**
   - Common errors
   - GAM issues
   - Performance tips

10. **FAQ**
    - 50+ common questions

---

#### `docs/ADMIN_GUIDE.md` (~1000 lines)

**Sections:**
1. **Deployment**
   - Building executable
   - Distribution
   - Updates

2. **Configuration**
   - Config file options
   - User preferences
   - Customization

3. **Security**
   - Access control
   - Audit logging
   - Best practices

4. **Backup and Recovery**
   - Operation history
   - Undo operations
   - Data export

5. **Integration**
   - Scheduled operations
   - API access (future)
   - External tools

---

### 9.2: Developer Documentation

**Files to Create:**

#### `docs/DEVELOPER_GUIDE.md` (~1500 lines)

**Sections:**
1. **Architecture Overview**
   - Project structure
   - Design patterns
   - Module dependencies

2. **Adding New Modules**
   - Step-by-step guide
   - BaseOperationWindow usage
   - Base operations usage
   - Testing requirements

3. **Backend Development**
   - GAM command patterns
   - Error handling
   - Progress reporting
   - Generator pattern

4. **GUI Development**
   - tkinter patterns
   - Tab creation
   - Form validation
   - Threading

5. **Testing**
   - Unit testing
   - Integration testing
   - Mocking GAM commands

6. **Contributing**
   - Code style guide
   - Git workflow
   - Pull request process
   - Code review checklist

---

#### `docs/API_REFERENCE.md` (~1000 lines)

**Auto-generated from docstrings:**
- All module functions
- Parameters and return values
- Examples
- GAM commands used

**Generation:**
Use `pydoc` or `sphinx` to generate from code docstrings.

---

### 9.3: Video Tutorials

**Create short video tutorials (~3-5 minutes each):**
1. Installation and Setup
2. Email Operations Walkthrough
3. User Management Basics
4. Bulk Operations with CSV
5. Security Scanning (Non-Domain ACLs)
6. Creating Operation Templates
7. Scheduling Reports
8. Troubleshooting Common Issues

**Tools:** 
- Screen recording: OBS Studio (free)
- Video editing: DaVinci Resolve (free)
- Host on: YouTube, link from README

---

## Phase 10: Distribution and Maintenance

### 10.1: Multi-Platform Builds

**Build Process:**

**Windows:**
```bash
# On Windows machine
pyinstaller build.spec

# Test executable
dist\GAM_Admin_Tool.exe
```

**macOS:**
```bash
# On Mac machine
pyinstaller build_mac.spec

# Create .app bundle
# Sign with Apple Developer certificate (optional)

# Create DMG installer
hdiutil create -volname "GAM Admin Tool" -srcfolder dist/GAM_Admin_Tool.app -ov -format UDZO GAM_Admin_Tool.dmg
```

**Linux:**
```bash
# On Linux machine
pyinstaller build_linux.spec

# Create AppImage or .deb package
# Or provide source + requirements.txt
```

**Create Platform-Specific build.spec files:**
- `build_windows.spec`
- `build_mac.spec`
- `build_linux.spec`

---

### 10.2: Auto-Update System

**File:** `utils/updater.py` (~300 lines)

**Features:**
- Check for updates on startup
- Download new version
- Install and restart
- Changelog display

**Implementation:**
```python
import requests
import json

UPDATE_URL = "https://api.github.com/repos/user/repo/releases/latest"

def check_for_updates(current_version):
    """
    Check if newer version available.
    
    Returns:
        tuple: (update_available, latest_version, download_url, changelog)
    """
    response = requests.get(UPDATE_URL)
    data = response.json()
    
    latest_version = data['tag_name']
    if version_greater_than(latest_version, current_version):
        return (True, latest_version, data['assets'][0]['browser_download_url'], data['body'])
    
    return (False, None, None, None)

def download_update(url, destination):
    """Download update file."""
    
def install_update(update_file):
    """Install update and restart application."""
```

**GUI Integration:**
- Show update notification on startup
- "Check for Updates" in Help menu
- Download progress dialog
- Changelog viewer

---

### 10.3: Telemetry (Optional)

**File:** `utils/telemetry.py` (~200 lines)

**Anonymous usage statistics:**
- Feature usage frequency
- Operation success/failure rates
- Performance metrics
- Error reports (anonymized)

**Privacy:**
- Make opt-in during first run
- No personal data collected
- No user emails or domain names
- No file names or content

**Implementation:**
```python
def log_event(event_type, metadata):
    """
    Log anonymous event.
    
    Args:
        event_type (str): Type of event (e.g., "operation_completed")
        metadata (dict): Anonymous metadata
    """
    if not user_consented():
        return
    
    event = {
        'type': event_type,
        'timestamp': datetime.now().isoformat(),
        'version': APP_VERSION,
        'platform': sys.platform,
        **metadata
    }
    
    # Send to analytics endpoint (if online)
    try:
        requests.post(ANALYTICS_URL, json=event, timeout=5)
    except:
        pass  # Silent fail
```

**Use Cases:**
- Understand which features are most used
- Identify which operations fail most often
- Prioritize bug fixes
- Guide future development

---

### 10.4: GitHub Repository Setup

**Repository Structure:**
```
GAM_Admin_Tool/
├── .github/
│   ├── workflows/
│   │   ├── build.yml          # CI/CD for builds
│   │   ├── test.yml           # Automated testing
│   │   └── release.yml        # Release automation
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── question.md
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
├── gui/
├── modules/
├── utils/
├── tests/
├── .gitignore
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
└── requirements.txt
```

**GitHub Actions Workflows:**

**`.github/workflows/test.yml`:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m unittest discover tests/
```

**`.github/workflows/build.yml`:**
```yaml
name: Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Windows executable
        run: pyinstaller build_windows.spec
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: GAM_Admin_Tool_Windows
          path: dist/GAM_Admin_Tool.exe
  
  build-mac:
    runs-on: macos-latest
    # Similar steps for Mac
  
  build-linux:
    runs-on: ubuntu-latest
    # Similar steps for Linux
```

---

### 10.5: Release Process

**Version Numbering:**
- Use Semantic Versioning: MAJOR.MINOR.PATCH
- Example: 1.0.0 → 1.1.0 (new features) → 1.1.1 (bug fixes)

**Release Checklist:**
1. [ ] Update version in code
2. [ ] Update CHANGELOG.md
3. [ ] Run all tests
4. [ ] Build for all platforms
5. [ ] Test executables
6. [ ] Create GitHub release
7. [ ] Upload executables
8. [ ] Update documentation
9. [ ] Announce release

**CHANGELOG.md Format:**
```markdown
# Changelog

## [1.2.0] - 2025-02-15

### Added
- User Management module with 12 operations
- Group Management module with 11 operations
- Operation templates feature
- Dry-run mode for all operations

### Changed
- Improved progress tracking with ETA
- Enhanced error messages

### Fixed
- Email filter creation bug (#42)
- CSV parsing issue with UTF-8 BOM (#45)

### Security
- Fixed command injection vulnerability
```

---

## Implementation Timeline

### Estimated Total Time: 80-100 hours

**Week 1-2: Foundation (16 hours)**
- Phase 0: Bug fixes and refactoring
- Base classes implementation
- Testing and documentation

**Week 3-4: Core Modules (24 hours)**
- Phase 1: User Management
- Phase 2: Group Management
- Testing and documentation

**Week 5-6: Advanced Modules (24 hours)**
- Phase 3: Drive Operations (including ACL detection)
- Phase 4: Reports Module
- Testing and documentation

**Week 7: Additional Modules (12 hours)**
- Phase 5: Calendar Operations
- Phase 7: Team Drives
- Testing and documentation

**Week 8: Polish (16 hours)**
- Phase 6: Advanced features (templates, scheduling, UX enhancements)
- Phase 8: Comprehensive testing
- Phase 9: Documentation completion

**Week 9: Distribution (8 hours)**
- Phase 10: Multi-platform builds
- GitHub setup
- Release process

---

## Success Metrics

**Features:**
- [ ] 50+ GAM operations accessible via GUI
- [ ] All 6 placeholder windows implemented
- [ ] Dry-run mode for all operations
- [ ] Operation templates system
- [ ] Comprehensive reporting
- [ ] Security audit features

**Quality:**
- [ ] 90%+ test coverage
- [ ] Zero critical bugs
- [ ] <100ms GUI response time
- [ ] Successful builds for Windows, Mac, Linux
- [ ] Complete user documentation

**Adoption:**
- [ ] 100+ downloads in first month
- [ ] 10+ GitHub stars
- [ ] Active community contributions
- [ ] Positive user feedback

---

## Maintenance Plan

### Ongoing Tasks:

**Monthly:**
- Check for GAM7 updates and compatibility
- Review and merge pull requests
- Address bug reports
- Update dependencies

**Quarterly:**
- Add new features based on user requests
- Performance optimization
- Security audit
- Documentation updates

**Annually:**
- Major version release
- Comprehensive testing
- Refactoring as needed
- User survey for priorities

---

## Future Enhancements (Post-1.0)

### Phase 11: Web Interface

Convert to web application:
- Replace tkinter with Flask/FastAPI backend
- React or Vue.js frontend
- Multi-user support
- Role-based access control
- Hosted service option

### Phase 12: API Access

Provide REST API:
- Programmatic access to all operations
- Webhook support
- API authentication
- Rate limiting
- Documentation with Swagger/OpenAPI

### Phase 13: Workflow Automation

Advanced automation:
- Visual workflow builder (drag-and-drop)
- Conditional logic (if-then-else)
- Loops and variables
- Scheduled workflows
- Event-triggered workflows

### Phase 14: AI Integration

Intelligent features:
- Natural language queries ("Show me users who haven't logged in this month")
- Anomaly detection (unusual file sharing, login patterns)
- Recommendations (suggest users to suspend, groups to clean up)
- Chatbot assistant for common tasks

### Phase 15: Mobile App

Mobile companion:
- View reports on mobile
- Approve pending operations
- Emergency actions (suspend user, revoke access)
- Push notifications for alerts

---

## Resources and Links

### GAM Resources:
- **GAM7 GitHub:** https://github.com/GAM-team/GAM
- **GAM Documentation:** https://github.com/GAM-team/GAM/wiki
- **GAM Community:** https://groups.google.com/g/google-apps-manager
- **GAM Command Reference:** https://github.com/GAM-team/GAM/wiki/GAM-Command-Reference

### Development Tools:
- **Python:** https://www.python.org/
- **tkinter Documentation:** https://docs.python.org/3/library/tkinter.html
- **PyInstaller:** https://pyinstaller.org/
- **GitHub Actions:** https://docs.github.com/en/actions

### Design Resources:
- **tkinter Themes:** https://github.com/rdbende/Sun-Valley-ttk-theme
- **Icons:** https://iconscout.com/ or https://fontawesome.com/

### Testing:
- **unittest:** https://docs.python.org/3/library/unittest.html
- **pytest:** https://pytest.org/ (alternative)
- **coverage.py:** https://coverage.readthedocs.io/

---

## Conclusion

This roadmap provides a comprehensive plan to transform the GAM Admin Tool from a solid email operations tool into a complete Google Workspace administration platform.

**Key Principles:**
1. **Modular Development:** Each phase is independent and can be completed separately
2. **User-Centric:** Focus on features that save admins the most time
3. **Quality First:** Testing and documentation are not optional
4. **Security-Focused:** Protect user data and credentials at all times
5. **Community-Driven:** Open source and welcoming contributions

**Next Steps:**
1. Fix the email filter bug (Phase 0.1)
2. Create base classes (Phase 0.2)
3. Implement User Management (Phase 1)
4. Continue through phases in order

**Success Factors:**
- Clear architecture with base classes prevents code duplication
- Comprehensive testing catches bugs early
- Good documentation enables community contributions
- Iterative releases provide value quickly
- User feedback guides priority

This tool has the potential to save Google Workspace administrators hundreds of hours per year. Let's build something amazing!

---

## Quick Reference: Implementation Order

1. ✅ Email Operations (COMPLETE)
2. 🔧 Fix email filter bug (IMMEDIATE)
3. 🏗️ Base classes refactoring (HIGH PRIORITY)
4. 👥 User Management (NEXT)
5. 👥 Group Management
6. 📁 Drive Operations + ACL Detection
7. 📊 Reports Module
8. 📅 Calendar Operations
9. 🚀 Advanced Features (Templates, Scheduling, UX)
10. 🧪 Comprehensive Testing
11. 📚 Complete Documentation
12. 📦 Multi-Platform Distribution

---