# GAM Admin Tool - Development Roadmap

## Current Project Status

**Version:** 0.9.0 (Pre-Release)
**Last Updated:** 2025-11-13

### ✅ Implemented Features

#### Foundation Layer
- ✅ GAM7 version and authentication checking
- ✅ Error logging system (`gam_tool_errors.log`)
- ✅ CSV file handling and validation
- ✅ Workspace data fetching with session caching
- ✅ Base operation window with reusable utilities
- ✅ Async combobox loading with fuzzy search
- ✅ Progress tracking and threading framework

#### Email Operations (6 Operations)
- ✅ Delete Messages (with query and date range)
- ✅ Manage Delegates (add/remove)
- ✅ Manage Signatures (set/remove HTML signatures)
- ✅ Manage Forwarding (enable/disable)
- ✅ Manage Labels (create/delete)
- ✅ Manage Filters (create/delete with flexible criteria)

#### User Management (7+ Operations)
- ✅ Create Users (single and bulk from CSV)
- ✅ Update User Info (name, title, phone, etc.)
- ✅ Suspend/Unsuspend Users
- ✅ Reset Passwords (with optional generation)
- ✅ Move Users to Organizational Units
- ✅ Manage Aliases (add/remove)
- ✅ Change Primary Email

#### Group Management (6+ Operations)
- ✅ Create/Delete Groups
- ✅ Add/Remove Members
- ✅ Manage Member Roles (Member, Manager, Owner)
- ✅ Update Group Settings
- ✅ Manage Group Aliases
- ✅ Change Group Owners

#### UI/UX Features
- ✅ Multi-tab interface for each module
- ✅ Single user, group, all users, CSV file, and list selection modes
- ✅ Fuzzy search in all comboboxes
- ✅ Real-time progress tracking
- ✅ Comprehensive error reporting
- ✅ Bulk operation confirmations
- ✅ Password generator utility

**Total Lines of Code:** ~10,500+
**Implementation Status:** Core features complete, ~60% of planned functionality

---

## 🚀 Future Development Phases

### Phase 1: Reports Module (HIGH PRIORITY)
**Estimated Time:** 6-8 hours
**Status:** Placeholder exists, needs full implementation

#### Planned Features

**User Reports:**
- User login activity and last login times
- User storage usage (Gmail, Drive)
- Suspended users list
- Inactive users report

**Admin Reports:**
- Admin activity audit trail
- Password change events
- User creation/deletion history

**Email Reports:**
- Email usage statistics (sent/received)
- Users with forwarding enabled
- Top email senders/receivers

**Drive Reports:**
- Drive activity and file sharing
- External sharing report
- Storage usage by user

**Calendar Reports:**
- Calendar usage statistics
- Meeting frequency reports

#### GAM Commands Required
```bash
gam report users parameters accounts:last_login_time
gam report usage customer parameters gmail:num_emails_sent
gam report admin parameters account_warning_event
gam report drive parameters doc_title,owner
```

#### GUI Design
- Multiple report type tabs
- Date range selection with presets
- Export to CSV functionality
- Basic data visualization (charts/graphs)
- Scheduled reports (optional)

---

### Phase 2: Drive Operations (HIGH PRIORITY)
**Estimated Time:** 10-12 hours
**Status:** Placeholder exists, needs full implementation

#### Planned Features

**File Operations:**
- Search files by query
- Transfer ownership
- Delete files (with excludetrash)
- Share/unshare files
- List and update permissions

**Folder Operations:**
- Create folders
- Move files to folders
- Organize bulk files from CSV

**Drive Management:**
- Get drive usage/quotas
- Empty trash for users
- Bulk cleanup operations

**Security Features (Critical):**
- **Non-Domain ACL Detection** - Scan for files shared outside domain
- External sharing audit reports
- Bulk permission removal
- Security compliance reports

#### GAM Commands Required
```bash
gam user EMAIL show filelist query "QUERY"
gam user EMAIL transfer ownership FILE_ID to NEW_OWNER
gam user EMAIL add drivefileacl FILE_ID user USER role ROLE
gam user EMAIL delete drivefileacl FILE_ID user USER
gam user EMAIL empty drivetrash
```

#### CSV Formats
```csv
# Transfer ownership
file_id,current_owner,new_owner
abc123,john@domain.com,jane@domain.com

# Share files
file_id,user,role
abc123,partner@external.com,reader
```

---

### Phase 3: Calendar Operations (MEDIUM PRIORITY)
**Estimated Time:** 6-8 hours
**Status:** Placeholder exists, needs full implementation

#### Planned Features

**Calendar Management:**
- Create/delete calendars
- List user calendars
- Share/unshare calendars
- Get calendar permissions

**Event Management:**
- Create events (single and recurring)
- Delete events by query
- List events in date range
- Bulk event creation from CSV

**Resource Calendars:**
- Create resource calendars (rooms, equipment)
- List all resources
- Manage resource access

#### GAM Commands Required
```bash
gam user EMAIL create calendar "NAME" description "DESC"
gam calendar CALENDAR_ID add reader user EMAIL
gam calendar CALENDAR_ID create event "TITLE" start START end END
gam calendar CALENDAR_ID delete events query "QUERY"
```

#### CSV Formats
```csv
# Create events
calendar,title,start,end,description,recurring
cal123,Team Meeting,2025-01-15T10:00:00,2025-01-15T11:00:00,Weekly sync,WEEKLY
```

---

### Phase 4: Advanced Features (MEDIUM PRIORITY)
**Estimated Time:** 8-10 hours

#### 4.1 Dry-Run Mode
- Preview operations without executing
- Show GAM commands that would run
- Display affected users/groups/files
- "Execute For Real" button after preview

#### 4.2 Operation History & Undo
- Store last N operations with details
- Provide undo for reversible operations
- Warn when operation cannot be undone
- History viewer in GUI

**Undo Examples:**
- Add Delegate → Remove Delegate
- Enable Forwarding → Disable Forwarding
- Add Group Member → Remove Group Member

**Cannot Undo:**
- Delete Messages (permanent)
- Delete User (data loss)

#### 4.3 Operation Templates
- Save common workflows as templates
- Template variables ({{email}}, {{firstName}}, etc.)
- Load and execute templates
- Share templates (export/import JSON)

**Example Templates:**
- New Employee Setup
- Employee Offboarding
- Department Transfer

#### 4.4 Enhanced UX
- Better progress indicators with ETA
- Export all results to CSV
- Dark mode toggle
- Cancel long-running operations
- Searchable dropdown improvements

---

### Phase 5: Team Drives Module (LOW PRIORITY)
**Estimated Time:** 4-6 hours

#### Planned Features
- Create/delete team drives
- List all team drives
- Add/remove members
- Manage team drive permissions
- Search files in team drives

---

### Phase 6: Security & Compliance (ONGOING)
**Priority:** Critical for production use

#### Security Checklist
- [ ] No passwords stored in logs
- [ ] No credentials in error messages
- [ ] CSV files validated before parsing
- [ ] No command injection vulnerabilities
- [ ] File paths validated (no directory traversal)
- [ ] All user input sanitized
- [ ] Dry-run mode doesn't leak sensitive data

#### Security Tools
```bash
# Static analysis
pip install bandit
bandit -r . -ll

# Dependency audit
pip install pip-audit
pip-audit
```

---

### Phase 7: Distribution & Packaging (BEFORE v1.0)
**Estimated Time:** 8 hours

#### Multi-Platform Builds
- Windows executable (.exe)
- macOS application (.app bundle)
- Linux binary or AppImage
- Code signing certificates (optional)

#### Auto-Update System
- Check for updates on startup
- Download new version
- Install and restart
- Changelog display

#### Installation
- Platform-specific installers
- Homebrew formula (macOS)
- Chocolatey package (Windows)
- Snap/Flatpak (Linux)

---

### Phase 8: Documentation (ONGOING)

#### User Documentation
- Complete user guide with screenshots
- Video tutorials (3-5 minutes each)
- Troubleshooting guide
- FAQ expansion

#### Developer Documentation
- Architecture overview
- Adding new modules guide
- API reference (auto-generated from docstrings)
- Contributing guidelines

---

## Long-Term Vision (Post-1.0)

### Web Interface
- Convert to web application (Flask/FastAPI + React)
- Multi-user support
- Role-based access control
- Hosted service option

### API Access
- REST API for all operations
- Webhook support
- API authentication
- Rate limiting

### Workflow Automation
- Visual workflow builder (drag-and-drop)
- Conditional logic (if-then-else)
- Scheduled workflows
- Event-triggered actions

### AI Integration
- Natural language queries
- Anomaly detection
- Recommendations (suggest users to suspend, groups to clean up)
- Chatbot assistant

---

## Implementation Priority

**Immediate (v0.9 → v1.0):**
1. Fix any remaining bugs in existing features
2. Security audit
3. Build system and distribution

**Next Release (v1.1):**
1. Reports Module
2. Drive Operations (including security scanning)

**Future Releases (v1.2+):**
1. Calendar Operations
2. Advanced Features (templates, history, dry-run)
3. Team Drives

**Long-Term:**
- Web interface
- API access
- Advanced automation

---

## Contributing

This is an open-source project welcoming contributions. Priority areas:
- Bug fixes in existing features
- Test coverage
- Documentation improvements
- New features (follow phases above)

See REFACTORING_GUIDE.md for information on the base utility methods available for new features.

---

## Resources

### GAM Resources
- **GAM7 GitHub:** https://github.com/GAM-team/GAM
- **GAM Documentation:** https://github.com/GAM-team/GAM/wiki
- **GAM Command Reference:** https://github.com/GAM-team/GAM/wiki/GAM-Command-Reference

### Development
- **Python:** https://www.python.org/
- **tkinter Documentation:** https://docs.python.org/3/library/tkinter.html
- **PyInstaller:** https://pyinstaller.org/

---

## Success Metrics

**Features:**
- ✅ Email operations (6)
- ✅ User management (7+)
- ✅ Group management (6+)
- ⏳ Reports (0)
- ⏳ Drive operations (0)
- ⏳ Calendar operations (0)

**Quality:**
- Responsive GUI (<100ms)
- Comprehensive error handling
- Complete documentation
- Cross-platform builds

---

**Last Updated:** 2025-11-13
**Project Status:** Active development, pre-release
