# Testing Checklist for GAM Admin Tool

This document provides a comprehensive testing checklist for validating the GAM Admin Tool.

## Pre-Testing Setup

- [ ] GAM7 is installed and in system PATH
- [ ] GAM7 is authenticated (`gam info domain` works)
- [ ] Python 3.8+ is installed
- [ ] All dependencies are installed (`pip install -r requirements.txt`)
- [ ] tkinter is available (GUI support)

## Unit Tests

### Foundation Layer

```bash
python3 test_foundation.py
```

- [ ] All imports successful
- [ ] Logger creates log file
- [ ] CSV handler validates and reads files
- [ ] GAM check detects version/auth status

### Email Backend Module

```bash
python3 test_email_module.py
```

- [ ] All 12 functions exist
- [ ] Function signatures correct
- [ ] All functions documented
- [ ] Module imports successfully

### Email GUI Structure

```bash
python3 test_email_gui.py
```

- [ ] EmailWindow class exists
- [ ] All 6 tab creation methods present
- [ ] All 6 execution methods present
- [ ] Framework methods present
- [ ] All required imports present

## Application Startup Tests

### GAM Version Check

- [ ] Application starts without errors (with GAM7)
- [ ] Error dialog appears if GAM7 not installed
- [ ] Error message shows upgrade link
- [ ] Error dialog appears if GAM not authenticated
- [ ] Error message shows auth instructions

### Main Window

- [ ] Main window opens and displays correctly
- [ ] Title shows "GAM Admin Tool"
- [ ] All 6 category buttons visible
- [ ] Buttons are clickable
- [ ] Window is resizable
- [ ] Close button works

## Placeholder Windows Tests

- [ ] Groups Management window opens
- [ ] Reports window opens
- [ ] Calendar Operations window opens
- [ ] Drive Operations window opens
- [ ] ACL Management window opens
- [ ] All placeholders show "under development" message
- [ ] All placeholder Close buttons work

## Email Operations Window Tests

### Window Opening

- [ ] Email Operations button opens window
- [ ] Window size is appropriate (950x750)
- [ ] All 6 tabs are visible
- [ ] Tab labels are correct
- [ ] Close button works

### Target Selection Tests (All Tabs)

Test on at least one tab (e.g., Delete Messages):

- [ ] Single User radio button works
- [ ] Single User: text entry appears
- [ ] Single User: validation works (requires @)
- [ ] Group radio button works
- [ ] Group: text entry appears
- [ ] All Users radio button works
- [ ] All Users: shows appropriate message
- [ ] CSV File radio button works
- [ ] CSV File: browse button opens file dialog
- [ ] CSV File: validation works (valid CSV)
- [ ] CSV File: validation catches invalid files
- [ ] Select from List radio button works
- [ ] Select from List: Load Users button works
- [ ] Select from List: users populate correctly
- [ ] Select from List: multi-selection works

### Tab 1: Delete Messages

- [ ] Query string input works
- [ ] Date range inputs visible
- [ ] Date format validation works (YYYY/MM/DD)
- [ ] Execute button enabled
- [ ] Form validation prevents empty query
- [ ] Confirmation dialog appears for bulk operations
- [ ] Progress bar starts when executing
- [ ] Results display in text area
- [ ] Success/failure messages appear
- [ ] Progress bar stops when complete

### Tab 2: Manage Delegates

- [ ] Add/Remove radio buttons work
- [ ] Delegate email input works
- [ ] Email validation works (requires @)
- [ ] Execute button enabled
- [ ] Confirmation dialog appears for bulk operations
- [ ] Operation executes correctly
- [ ] Results display properly

### Tab 3: Manage Signatures

- [ ] Set/Remove radio buttons work
- [ ] Enter HTML radio button works
- [ ] Upload File radio button works
- [ ] Text area appears for Enter HTML
- [ ] File browser appears for Upload File
- [ ] Browse button opens file dialog
- [ ] Validation prevents empty signature
- [ ] Execute button works
- [ ] Operation executes correctly

### Tab 4: Manage Forwarding

- [ ] Enable/Disable radio buttons work
- [ ] Forward To input appears when Enable selected
- [ ] Forward To input hides when Disable selected
- [ ] Email validation works
- [ ] Execute button works
- [ ] Operation executes correctly

### Tab 5: Manage Labels

- [ ] Create/Delete radio buttons work
- [ ] Label name input works
- [ ] Validation prevents empty label name
- [ ] Execute button works
- [ ] Operation executes correctly

### Tab 6: Manage Filters

- [ ] Create/Delete radio buttons work
- [ ] Create: all input fields visible (From, To, Subject, Has Words, Label)
- [ ] Delete: Filter ID input visible
- [ ] Validation requires at least one criteria for Create
- [ ] Validation requires Filter ID for Delete
- [ ] Execute button works
- [ ] Operation executes correctly

## Progress and Results Tests

- [ ] Progress bar animates during operations
- [ ] Results text updates in real-time
- [ ] Processing messages show current user
- [ ] Success messages use ✓ symbol
- [ ] Error messages use ✗ symbol
- [ ] Final summary displays correctly
- [ ] Clear Results button works
- [ ] View Error Log button works
- [ ] Error log window opens and displays content

## Threading and Responsiveness Tests

- [ ] GUI remains responsive during operations
- [ ] Can interact with window during operation
- [ ] Cannot start multiple operations simultaneously
- [ ] Warning appears if trying to start second operation
- [ ] Operation completes properly
- [ ] Thread terminates correctly

## Error Handling Tests

### Invalid Input Tests

- [ ] Empty email address rejected
- [ ] Invalid email format rejected
- [ ] Missing required fields rejected
- [ ] Invalid date format rejected
- [ ] Empty CSV file rejected
- [ ] CSV without 'email' header rejected

### GAM Command Errors

- [ ] GAM command failures logged
- [ ] Error messages displayed to user
- [ ] Operations continue for remaining users
- [ ] Final error count accurate
- [ ] Errors viewable in error log

## CSV File Tests

Create test CSV files:

**Valid CSV (test_valid.csv):**
```csv
email
user1@test.com
user2@test.com
```

**Invalid CSV - No Header (test_invalid_header.csv):**
```csv
user1@test.com
user2@test.com
```

**Invalid CSV - Wrong Header (test_wrong_header.csv):**
```csv
username
user1@test.com
```

**Empty CSV (test_empty.csv):**
```csv
email
```

- [ ] Valid CSV accepted and parsed correctly
- [ ] Invalid header CSV rejected with error
- [ ] Wrong header CSV rejected with error
- [ ] Empty CSV rejected with error
- [ ] Error messages are clear and helpful

## Bulk Operation Tests

Test with multiple users (safe operations recommended):

- [ ] Confirmation dialog appears for bulk operations
- [ ] Dialog shows correct user count
- [ ] Can cancel before execution
- [ ] Progress updates for each user
- [ ] Success count accurate
- [ ] Failure count accurate
- [ ] Individual results visible
- [ ] Error log contains failures

## Integration Tests

### Complete Workflow Test

1. Start application
2. Select Email Operations
3. Choose Delete Messages tab
4. Select target: Single User
5. Enter test email
6. Enter query: `from:test@example.com`
7. Execute operation
8. Verify progress displayed
9. Verify results shown
10. Clear results
11. Change to different tab
12. Repeat with different target type

- [ ] Workflow completes without errors
- [ ] All steps work as expected
- [ ] Results accurate

## PyInstaller Build Tests

### Build Process

```bash
pyinstaller build.spec
```

- [ ] Build completes without errors
- [ ] No missing module warnings
- [ ] Executable created in dist/ folder
- [ ] File size reasonable (< 50MB)

### Executable Tests

- [ ] Executable runs on target OS
- [ ] No console window appears (Windows)
- [ ] Application icon displays (if configured)
- [ ] GAM version check works
- [ ] All functionality works same as source
- [ ] No import errors
- [ ] Error logging works

### Distribution Tests

- [ ] Executable works on fresh machine (with GAM7)
- [ ] No Python installation required
- [ ] Executable works without source code
- [ ] All features functional in executable

## Performance Tests

- [ ] Application starts in < 5 seconds
- [ ] Main window opens immediately
- [ ] Email window opens in < 2 seconds
- [ ] User list loads in reasonable time (< 30 seconds for large domains)
- [ ] Single user operations complete quickly
- [ ] Bulk operations show progress for each user
- [ ] Large CSV files (100+ users) process correctly

## Cross-Platform Tests (if applicable)

### Windows

- [ ] Application runs on Windows 10/11
- [ ] Executable builds correctly
- [ ] GUI renders properly
- [ ] File dialogs work
- [ ] GAM integration works

### macOS

- [ ] Application runs on macOS
- [ ] GUI renders properly (may look different)
- [ ] File dialogs work
- [ ] GAM integration works

### Linux

- [ ] Application runs on Linux
- [ ] tkinter available or installed
- [ ] GUI renders properly
- [ ] File dialogs work
- [ ] GAM integration works

## Security Tests

- [ ] No passwords/credentials stored
- [ ] No sensitive data logged
- [ ] Log files don't contain credentials
- [ ] CSV files validated before processing
- [ ] No SQL injection risks (N/A - no database)
- [ ] No command injection in GAM commands
- [ ] File paths validated before use

## Edge Case Tests

- [ ] Very long email lists (1000+ users)
- [ ] Unicode characters in emails
- [ ] Special characters in labels/filters
- [ ] Network timeout during operation
- [ ] GAM command hanging/timeout
- [ ] Disk full during logging
- [ ] Closing app during operation

## Documentation Tests

- [ ] README.md is clear and complete
- [ ] Installation instructions work
- [ ] Usage examples are accurate
- [ ] Troubleshooting section helpful
- [ ] FAQ answers common questions
- [ ] Links work
- [ ] Screenshots accurate (if included)

## Final Checks

- [ ] All test scripts pass
- [ ] No TODO or FIXME comments in code
- [ ] Version number consistent
- [ ] License file present
- [ ] .gitignore properly configured
- [ ] No sensitive data in repository
- [ ] All files have proper headers/docstrings
- [ ] Code follows PEP 8 style
- [ ] No unused imports
- [ ] No debug print statements

## Test Summary

**Date**: ___________
**Tester**: ___________
**Version**: ___________
**Platform**: ___________

**Tests Passed**: _____ / _____
**Tests Failed**: _____ / _____
**Tests Skipped**: _____ / _____

**Critical Issues**: ___________________________________________

**Notes**: ____________________________________________________

---

## Automated Testing Script

For basic validation:

```bash
#!/bin/bash
echo "Running all test scripts..."

python3 test_foundation.py
echo "Foundation tests: $?"

python3 test_email_module.py
echo "Email module tests: $?"

python3 test_email_gui.py
echo "Email GUI tests: $?"

echo "All automated tests complete!"
```

Save as `run_tests.sh` and execute with `bash run_tests.sh`
