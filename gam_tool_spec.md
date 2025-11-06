# GAM Admin Tool Project Specification

## Project Overview
Build a modular Python GUI application for GAMADV-XTD3/GAM7 that provides an intuitive, graphical interface for common Google Workspace administrative tasks. The application will be packaged as a standalone executable for easy distribution.

## Project Structure
```
gam-tool/
├── main.py
├── gui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── email_window.py
│   ├── groups_window.py
│   ├── reports_window.py
│   ├── calendar_window.py
│   ├── drive_window.py
│   └── acls_window.py
├── modules/
│   ├── __init__.py
│   ├── email.py
│   ├── groups.py
│   ├── reports.py
│   ├── calendar.py
│   ├── drive.py
│   └── acls.py
├── utils/
│   ├── __init__.py
│   ├── gam_check.py
│   ├── csv_handler.py
│   ├── workspace_data.py
│   └── logger.py
├── assets/
│   └── icon.ico
├── requirements.txt
├── build.spec
└── README.md
```

## Core Requirements

### 1. Entry Point (main.py)
- Initialize the GUI application using tkinter
- On startup, verify GAM7 is installed and authenticated (use utils/gam_check.py)
- If GAM7 check fails, display error dialog with upgrade instructions
- If auth check fails, display error dialog with authentication instructions
- Launch main_window.py if all checks pass
- Handle application close gracefully

### 2. Version & Authentication Check (utils/gam_check.py)
- Run `gam version` and verify it's GAM7 (not GAMADV-XTD3)
- If not GAM7, display message: "Please upgrade to GAM7. Visit: https://github.com/GAM-team/GAM"
- Test authentication by running a simple GAM command (e.g., `gam info domain`)
- If auth fails, display: "GAM is not authenticated. Please run 'gam oauth create' or visit: https://github.com/GAM-team/GAM/wiki/Authorization"
- Return True/False for version check and auth check

### 3. CSV Handler (utils/csv_handler.py)
- Function to validate CSV exists and has required header
- Function to read CSV and return list of email addresses
- Expected header: `email`
- Handle file not found, invalid format, empty file errors

### 4. Workspace Data Fetcher (utils/workspace_data.py)
- Function to fetch all users: `gam print users`
- Function to fetch all groups: `gam print groups`
- Cache results for the session to avoid repeated API calls
- Return lists of email addresses for populating dropdown menus
- Handle errors if GAM commands fail
- Log errors to both console and `gam_tool_errors.log` file
- Include timestamp, operation attempted, error message
- Format: `[YYYY-MM-DD HH:MM:SS] [OPERATION] ERROR: message`

### 7. Email Operations Window (gui/email_window.py)
Create a window with tabbed interface for different email operations:

#### Tabs:
1. Delete Messages
2. Manage Delegates
3. Manage Signatures
4. Manage Forwarding
5. Manage Labels
6. Manage Filters

#### Common Elements in Each Tab:

**Target Selection Frame:**
- Radio buttons:
  - ( ) Single User
  - ( ) Group
  - ( ) All Users
  - ( ) CSV File
  - ( ) Select from List
- Input field/dropdown that changes based on selection:
  - Single User: Text entry field
  - Group: Text entry field
  - All Users: Disabled (shows count)
  - CSV File: File browser button
  - Select from List: Multi-select dropdown populated from workspace_data.py

**Operation-Specific Parameters Frame:**

*Delete Messages Tab:*
- Label: "Query String"
- Text entry: (e.g., "from:sender@example.com")
- Label: "Date Range (Optional)"
- Date picker: From date
- Date picker: To date
- Execute button

*Manage Delegates Tab:*
- Radio buttons: ( ) Add Delegate  ( ) Remove Delegate
- Label: "Delegate Email"
- Text entry or dropdown (from workspace users)
- Execute button

*Manage Signatures Tab:*
- Radio buttons: ( ) Set Signature  ( ) Remove Signature
- Label: "Signature HTML File" (if Set is selected)
- File browser button
- OR
- Text area for inline HTML entry
- Execute button

*Manage Forwarding Tab:*
- Radio buttons: ( ) Enable  ( ) Disable
- Label: "Forward To" (if Enable is selected)
- Text entry field
- Execute button

*Manage Labels Tab:*
- Radio buttons: ( ) Create Label  ( ) Delete Label
- Label: "Label Name"
- Text entry field
- Execute button

*Manage Filters Tab:*
- Radio buttons: ( ) Create Filter  ( ) Delete Filter
- If Create:
  - Label: "From"
  - Text entry
  - Label: "To"
  - Text entry
  - Label: "Subject"
  - Text entry
  - Label: "Has Words"
  - Text entry
  - Label: "Action (Label Name)"
  - Text entry
- If Delete:
  - Button: "List Existing Filters"
  - Dropdown: populated with filter IDs
- Execute button

**Progress and Results Frame:**
- Progress bar (shows during bulk operations)
- Text area showing:
  - "Processing user X of Y..."
  - Success/failure messages
  - Summary: "Completed for X users, Failed for Y users"
- Button: "View Error Log" (opens logger output)

**Button Row:**
- [Execute] [Clear Form] [Close]

#### Behavior:
- When "Select from List" is chosen, button says "Load Users/Groups" and populates multi-select
- Before executing bulk operations, show confirmation dialog: "You are about to [OPERATION] for [COUNT] users. Proceed?"
- Disable form controls during execution
- Show progress bar and real-time status updates
- Re-enable form controls when complete
- Display success/error summary
### 8. Email Module Backend (modules/email.py)
Functions to execute GAM commands based on GUI inputs:

#### Functions:
- `delete_messages(users, query, date_from=None, date_to=None)`
- `add_delegate(users, delegate_email)`
- `remove_delegate(users, delegate_email)`
- `set_signature(users, signature_html)`
- `remove_signature(users)`
- `enable_forwarding(users, forward_to)`
- `disable_forwarding(users)`
- `create_label(users, label_name)`
- `delete_label(users, label_name)`
- `create_filter(users, from_addr, to_addr, subject, has_words, action_label)`
- `delete_filter(users, filter_id)`

#### Implementation Details:
- Each function accepts a list of users (even if single user)
- Construct GAM command string
- Use subprocess to execute
- Yield progress updates for GUI to display
- Return success/failure counts
- Log all errors using utils/logger.py

#### GAM Command Examples:
```python
# Delete messages
f"gam user {email} delete messages query '{query}' trash excludetrash"

# Add delegate
f"gam user {email} delegate to {delegate_email}"

# Set signature
f"gam user {email} signature file {signature_file}"

# Enable forwarding
f"gam user {email} forward on {forward_to}"

# Create label
f"gam user {email} label '{label_name}'"

# Create filter
f"gam user {email} filter from {from_addr} label '{action_label}'"
```

### 9. Placeholder Windows for Future Modules
Create basic placeholder windows for:
- gui/groups_window.py
- gui/reports_window.py
- gui/calendar_window.py
- gui/drive_window.py
- gui/acls_window.py

Each should display: "This module is under development. Check back in a future release!"
With a [Close] button.

This allows the main menu to be complete while focusing development on email operations.

### 10. Error Handling
- Wrap all GAM command executions in try/except
- Log failures with utils/logger.py
- Display user-friendly error messages
- Continue processing remaining users on bulk operations (don't stop on first error)

### 11. Confirmation Dialogs
Before executing commands that affect multiple users:
```
You are about to [OPERATION] for [COUNT] users.
Proceed? (y/n):
```

## Technical Specifications

### Python Version
- Python 3.8+

### Dependencies (requirements.txt)
```
# GUI framework (built into Python, no external dependency)
# tkinter - standard library

# For building executable
pyinstaller==6.3.0

# Standard library modules used:
# subprocess - GAM command execution
# csv - CSV file handling
# datetime - logging timestamps
# os - file operations
# threading - keeping GUI responsive during operations
```

### Code Style
- Clear variable names
- Comments explaining GAM command construction
- Docstrings for each function
- Handle edge cases (empty inputs, invalid files, network errors)
- Use threading for long-running operations to keep GUI responsive
- Follow PEP 8 style guidelines

### GUI Design Principles
- Clean, professional appearance using ttk themed widgets
- Consistent padding and spacing (10px standard)
- Clear visual hierarchy (headers, sections, buttons)
- Helpful placeholder text in input fields
- Tooltips on hover for complex options
- Disable controls during operations to prevent double-clicks
- Use color sparingly (red for errors, green for success)
- Responsive layout that works at different window sizes

### User Experience
- Loading spinner/message during workspace data fetching
- Progress indicators for bulk operations: "Processing user 5 of 100..."
- Success notifications: "Operation completed successfully for [COUNT] users"
- Failure summaries: "Failed for [COUNT] users. Click 'View Error Log' for details"
- Clear error messages in dialogs (not just console output)
- Form validation before allowing execution (e.g., email format checks)
- Ability to cancel long-running operations
- Remember window positions and sizes between sessions (optional enhancement)

## Implementation Priority
1. Build utils/gam_check.py (critical for startup validation)
2. Build utils/logger.py
3. Build utils/workspace_data.py
4. Build utils/csv_handler.py
5. Create main.py (entry point with startup checks)
6. Build gui/main_window.py (main menu interface)
7. Build placeholder windows for future modules
8. Implement modules/email.py backend fully (all 6 operations)
9. Build gui/email_window.py with all tabs and functionality
10. Test thoroughly with single user, CSV, and bulk operations
11. Create application icon (assets/icon.ico)
12. Write build.spec for PyInstaller
13. Build executable and test
14. Write README.md with installation and usage instructions

## Building the Executable

### PyInstaller Configuration (build.spec)
Create a spec file for building the standalone executable:

```python
# build.spec
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/icon.ico', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GAM_Admin_Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
```

### Build Commands
```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller build.spec

# Output will be in dist/GAM_Admin_Tool.exe
```

### Distribution
- Executable will be in `dist/` folder
- Single file, no installation required
- Users must have GAM7 installed and configured separately
- Works on Windows (create separate builds for Mac/Linux if needed)
- modules/groups.py - Group management operations
- modules/reports.py - Google Workspace reports
- modules/calendar.py - Calendar operations
- modules/drive.py - Drive operations (always use excludetrash)
- modules/acls.py - Non-domain Drive ACL detection (based on GetNonDomainDriveACLs.py)

## Testing Checklist
- [ ] GAM7 version check works and shows error dialog for older versions
- [ ] GAM7 upgrade message displays correctly for GAMADV-XTD3
- [ ] Authentication check works and shows error dialog if not authenticated
- [ ] Main window opens with all category buttons
- [ ] Placeholder windows display for Groups, Reports, Calendar, Drive, ACLs
- [ ] Email operations window opens and displays all tabs
- [ ] Workspace data fetch populates dropdowns correctly
- [ ] Single user operations work for all email functions
- [ ] CSV file selection and validation works (valid and invalid files)
- [ ] Multi-select from list works correctly
- [ ] All users confirmation dialog appears and respects cancel
- [ ] Progress bar updates during bulk operations
- [ ] Operations can be cancelled mid-execution
- [ ] Errors log to file and display in GUI
- [ ] Success/failure summary displays correctly
- [ ] "View Error Log" button opens log viewer
- [ ] Form validation prevents invalid submissions
- [ ] GUI remains responsive during long operations (threading works)
- [ ] Application closes cleanly without errors
- [ ] PyInstaller build creates working executable
- [ ] Executable runs on fresh Windows machine with GAM7 installed
- [ ] Application icon displays correctly in executable

## Notes
- Always use `excludetrash` flag for delete operations
- GAM commands should be constructed as strings and executed via subprocess
- Use threading to prevent GUI freezing during GAM operations
- Keep code modular so additional GUI windows can be added easily
- Focus on completing email module fully before expanding to other categories
- tkinter is chosen because it's included with Python (no external dependencies for users)
- PyInstaller packages everything into a single executable
- Application requires GAM7 to be installed separately (not bundled)
- Test on target OS (Windows primarily, Mac/Linux if needed)

## README.md Contents
Should include:
- Project description and purpose
- Prerequisites (GAM7 installation and configuration)
- How to download and run the executable
- How to run from source (for developers)
- Screenshots of main window and email operations
- Link to GAM7 documentation
- Troubleshooting section
- Contributing guidelines (for future modules)
- License information