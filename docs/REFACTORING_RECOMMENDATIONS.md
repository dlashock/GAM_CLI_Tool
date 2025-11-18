# Refactoring Recommendations

**Purpose:** Improve code maintainability, testability, and extensibility
**Priority:** MEDIUM (after critical features implemented)
**Estimated Total Effort:** 15-20 hours

---

## Current Code Quality Assessment

### Strengths ✅
- Excellent separation of concerns (GUI/modules/utils)
- Comprehensive error handling
- Good code reuse through BaseOperationWindow
- Consistent naming conventions
- Well-documented functions

### Areas for Improvement ⚠️
- Large window files (800-1200 lines)
- No automated testing
- Some code duplication in window creation
- Hardcoded configuration values
- No dependency injection

---

## Refactoring Priority Matrix

```
High Impact, Low Effort:
├── Add basic tests (4h)
├── Extract configuration (2h)
└── Split large window files (6h)

High Impact, High Effort:
├── Comprehensive test suite (15h)
└── Implement dependency injection (8h)

Low Impact, Low Effort:
├── Type hints (3h)
└── Docstring improvements (2h)

Low Impact, High Effort:
└── Complete architectural rewrite (avoid)
```

---

## 1. Split Large Window Files
**Effort:** 6 hours | **Impact:** HIGH | **Priority:** HIGH

### Problem
Some GUI windows exceed 1000 lines, making them hard to navigate and maintain.

**Example:** `users_window.py` has 10+ tabs, each 80-120 lines

### Solution: Extract Tab Classes

**Before:**
```
users_window.py (1200 lines)
└── UsersWindow class
    ├── create_create_user_tab() (100 lines)
    ├── create_delete_user_tab() (100 lines)
    ├── create_password_tab() (120 lines)
    ├── ... 7 more tabs ...
    └── execute_*() methods (500 lines)
```

**After:**
```
gui/users/
├── users_window.py (200 lines) - Main coordinator
├── create_user_tab.py (150 lines) - User creation
├── delete_user_tab.py (120 lines) - User deletion
├── password_tab.py (150 lines) - Password management
├── user_info_tab.py (100 lines) - Update user info
└── ... other tabs ...
```

**Implementation Pattern:**

```python
# gui/users/users_window.py
from gui.users.create_user_tab import CreateUserTab
from gui.users.delete_user_tab import DeleteUserTab
# ... more imports ...

class UsersWindow(BaseOperationWindow):
    def create_operation_tabs(self):
        # Create tab instances
        self.create_user_tab = CreateUserTab(self.notebook, self)
        self.delete_user_tab = DeleteUserTab(self.notebook, self)
        # ... more tabs ...

        # Add to notebook
        self.notebook.add(self.create_user_tab, text="Create User")
        self.notebook.add(self.delete_user_tab, text="Delete User")
        # ... more tabs ...

# gui/users/create_user_tab.py
class CreateUserTab(ttk.Frame):
    """User creation tab component."""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.create_widgets()

    def create_widgets(self):
        """Create tab UI."""
        # Mode toggle
        mode_frame, single_frame, csv_frame, mode_var = \
            self.main_window.create_mode_toggle(
                self, 'create_user',
                single_label="Create Single User",
                csv_label="Bulk Create from CSV"
            )

        # ... rest of UI ...

        execute_btn = ttk.Button(
            self,
            text="Create User(s)",
            command=self.execute_create_users
        )
        execute_btn.pack()

    def execute_create_users(self):
        """Execute user creation."""
        # ... validation and execution ...
        from modules.users import create_user
        self.main_window.run_operation(
            create_user,
            self.progress_frame,
            users_data
        )
```

**Benefits:**
- Each file <200 lines
- Easier to find and modify specific functionality
- Can test tabs independently
- Reduces merge conflicts in version control

---

## 2. Add Configuration System
**Effort:** 2 hours | **Impact:** MEDIUM | **Priority:** HIGH

### Problem
Settings hardcoded throughout codebase:
- Bulk operation threshold (50 users)
- Timeout values (30, 60, 120 seconds)
- Window sizes ("950x750")
- Cache TTL (30 minutes)
- Log file max size

### Solution: Centralized Configuration

**Create `config.py`:**
```python
# config.py
import json
import os

DEFAULT_CONFIG = {
    # Operations
    "bulk_operation_warning_threshold": 50,
    "default_timeout_seconds": 60,
    "long_timeout_seconds": 120,
    "max_retry_attempts": 3,

    # UI
    "main_window_size": "800x600",
    "operation_window_size": "950x750",
    "min_window_size": [800, 600],
    "theme": "default",  # or "dark"

    # Performance
    "cache_expiry_minutes": 30,
    "max_concurrent_operations": 5,

    # Logging
    "log_file": "gam_tool_errors.log",
    "log_max_size_mb": 10,
    "log_backup_count": 5,
    "log_level": "ERROR",

    # Advanced
    "enable_dry_run": True,
    "auto_export_results": False,
    "export_directory": "./exports"
}

class Config:
    """Application configuration manager."""

    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        """Load config from file if exists."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        """Save current config to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key, default=None):
        """Get config value."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set config value."""
        self.config[key] = value

# Global config instance
config = Config()
```

**Usage Throughout Codebase:**
```python
# Instead of:
if len(users) > 50:
    confirm = messagebox.askyesno(...)

# Use:
from config import config
if len(users) > config.get('bulk_operation_warning_threshold'):
    confirm = messagebox.askyesno(...)

# Instead of:
result = subprocess.run(cmd, timeout=60)

# Use:
result = subprocess.run(cmd, timeout=config.get('default_timeout_seconds'))
```

**Add Settings UI:**
```python
# gui/settings_window.py
class SettingsWindow(tk.Toplevel):
    """Settings configuration window."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")

        # Create settings UI
        self.create_widgets()

    def create_widgets(self):
        """Create settings interface."""
        # General settings
        general_frame = ttk.LabelFrame(self, text="General", padding="10")
        general_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(general_frame, text="Bulk Operation Warning:").grid(row=0, column=0)
        threshold_var = tk.IntVar(value=config.get('bulk_operation_warning_threshold'))
        ttk.Spinbox(general_frame, from_=10, to=500, textvariable=threshold_var).grid(row=0, column=1)

        # Save button
        ttk.Button(self, text="Save", command=self.save_settings).pack(pady=10)

    def save_settings(self):
        """Save settings to config."""
        config.set('bulk_operation_warning_threshold', threshold_var.get())
        config.save()
        messagebox.showinfo("Settings", "Settings saved successfully")
        self.destroy()
```

---

## 3. Add Basic Testing Infrastructure
**Effort:** 4 hours | **Impact:** HIGH | **Priority:** HIGH

### Current State
- Zero automated tests
- All testing is manual
- Refactoring is risky

### Solution: pytest + pytest-mock

**Setup:**
```bash
pip install pytest pytest-cov pytest-mock
```

**Create Test Structure:**
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_modules/
│   ├── test_email.py        # Email operations tests
│   ├── test_users.py        # User operations tests
│   ├── test_groups.py       # Group operations tests
│   └── test_drive.py        # Drive operations tests
├── test_utils/
│   ├── test_logger.py       # Logger tests
│   ├── test_csv_handler.py  # CSV handling tests
│   └── test_workspace_data.py
└── test_gui/
    └── test_base_window.py  # GUI tests (harder)
```

**Example Test File:**
```python
# tests/test_modules/test_email.py
import pytest
from modules.email import delete_messages

@pytest.fixture
def mock_subprocess(mocker):
    """Mock subprocess.run for testing."""
    return mocker.patch('modules.email.subprocess.run')

@pytest.fixture
def mock_gam_command(mocker):
    """Mock GAM command path."""
    mocker.patch('modules.email.get_gam_command', return_value='gam')

def test_delete_messages_success(mock_subprocess, mock_gam_command):
    """Test successful message deletion."""
    # Mock successful GAM response
    mock_subprocess.return_value.returncode = 0
    mock_subprocess.return_value.stdout = "Messages deleted"
    mock_subprocess.return_value.stderr = ""

    # Execute function
    users = ['test@example.com']
    query = 'from:spam@example.com'

    results = list(delete_messages(users, query))

    # Assertions
    assert any(r['status'] == 'success' for r in results)
    mock_subprocess.assert_called_once()

def test_delete_messages_dry_run(mock_subprocess, mock_gam_command):
    """Test dry-run mode doesn't execute."""
    users = ['test@example.com']
    query = 'test query'

    results = list(delete_messages(users, query, dry_run=True))

    # Should yield dry-run status
    assert any(r['status'] == 'dry-run' for r in results)
    # Should NOT call subprocess
    mock_subprocess.assert_not_called()

def test_delete_messages_with_date_range(mock_subprocess, mock_gam_command):
    """Test query construction with date range."""
    mock_subprocess.return_value.returncode = 0

    users = ['test@example.com']
    query = 'from:sender'
    date_from = '2025/01/01'
    date_to = '2025/12/31'

    list(delete_messages(users, query, date_from, date_to))

    # Verify command includes date parameters
    call_args = mock_subprocess.call_args[0][0]
    assert 'after:2025/01/01' in ' '.join(call_args)
    assert 'before:2025/12/31' in ' '.join(call_args)

def test_delete_messages_handles_timeout(mock_subprocess, mock_gam_command):
    """Test timeout handling."""
    from subprocess import TimeoutExpired
    mock_subprocess.side_effect = TimeoutExpired('gam', 60)

    users = ['test@example.com']
    query = 'test'

    results = list(delete_messages(users, query))

    # Should yield error status
    assert any(r['status'] == 'error' for r in results)
```

**Run Tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=modules --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_modules/test_email.py

# Run specific test
pytest tests/test_modules/test_email.py::test_delete_messages_success
```

**Target Coverage:**
- **Phase 1:** 40% coverage (utilities and simple functions)
- **Phase 2:** 60% coverage (all backend modules)
- **Phase 3:** 70%+ coverage (include GUI logic)

---

## 4. Add Type Hints
**Effort:** 3 hours | **Impact:** LOW | **Priority:** LOW

### Benefits
- Better IDE autocomplete
- Catch type errors early with mypy
- Self-documenting code

### Implementation
```python
# Before
def delete_messages(users, query, date_from=None, date_to=None, dry_run=False):
    """Delete messages..."""

# After
from typing import List, Optional, Generator, Dict, Any

def delete_messages(
    users: List[str],
    query: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    dry_run: bool = False
) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
    """
    Delete messages for users based on query string.

    Args:
        users: List of user email addresses
        query: Gmail search query
        date_from: Start date for query (YYYY/MM/DD format)
        date_to: End date for query (YYYY/MM/DD format)
        dry_run: If True, simulate without executing

    Yields:
        Progress updates with status, email, current, total, message

    Returns:
        Summary with success_count, failure_count, errors
    """
```

**Setup mypy:**
```bash
pip install mypy

# Run type checking
mypy modules/ utils/ gui/
```

---

## 5. Improve Error Recovery
**Effort:** 3 hours | **Impact:** MEDIUM | **Priority:** MEDIUM

### Problem
Operations fail entirely on first error, requiring manual restart

### Solution: Skip-and-Continue with Retry

```python
# Add to modules/base_operations.py

from functools import wraps
import time

def retry_on_failure(max_attempts=3, delay=2):
    """Decorator for retrying failed operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)
                    if result.returncode == 0:
                        return result

                    # Retry on certain errors
                    if 'rate limit' in result.stderr.lower():
                        if attempt < max_attempts - 1:
                            time.sleep(delay * (2 ** attempt))  # Exponential backoff
                            continue

                    return result  # Don't retry other errors

                except subprocess.TimeoutExpired:
                    if attempt < max_attempts - 1:
                        continue
                    raise

            return result  # Final attempt

        return wrapper
    return decorator

@retry_on_failure(max_attempts=3)
def execute_gam_command(cmd, **kwargs):
    """Execute GAM command with retry logic."""
    return subprocess.run(cmd, **kwargs)
```

---

## 6. Extract Constants
**Effort:** 1 hour | **Impact:** LOW | **Priority:** LOW

### Create Constants File

```python
# constants.py

# Window sizes
MAIN_WINDOW_SIZE = "800x600"
OPERATION_WINDOW_SIZE = "950x750"
MIN_WINDOW_SIZE = (800, 600)

# Timeouts (seconds)
SHORT_TIMEOUT = 30
MEDIUM_TIMEOUT = 60
LONG_TIMEOUT = 120
VERY_LONG_TIMEOUT = 300

# Bulk operation thresholds
BULK_WARNING_THRESHOLD = 50
VERY_LARGE_BULK_THRESHOLD = 100

# CSV requirements
CSV_ENCODING = 'utf-8'
REQUIRED_CSV_FIELD = 'email'

# GAM command defaults
DEFAULT_GAM_FIELDS = ['id', 'name', 'email']
MAX_RESULTS_DEFAULT = 100

# UI text
APP_TITLE = "GAM Admin Tool"
VERSION = "0.9.0"

# Error messages
ERROR_NO_GAM = "GAM not found. Please install GAM7 first."
ERROR_NO_AUTH = "GAM not authenticated. Run: gam oauth create"
ERROR_INVALID_EMAIL = "Please enter a valid email address."
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2, 12 hours)
1. Add configuration system (2h)
2. Extract constants (1h)
3. Setup testing infrastructure (4h)
4. Write first 20 unit tests (5h)

### Phase 2: Refactoring (Week 3-4, 15 hours)
5. Split users_window.py (3h)
6. Split email_window.py (2h)
7. Split groups_window.py (2h)
8. Split calendar_window.py (2h)
9. Add error recovery (3h)
10. Add type hints to critical functions (3h)

### Phase 3: Testing (Week 5-6, 10 hours)
11. Write comprehensive module tests (5h)
12. Add integration tests (3h)
13. Achieve 60% code coverage (2h)

---

## Metrics for Success

### Code Quality
- Lines per file: < 500 (currently some > 1000)
- Code coverage: > 60% (currently 0%)
- Type hint coverage: > 50% (currently 0%)
- Duplicate code: < 5% (currently good)

### Maintainability
- Time to find bug: < 5 minutes (varies)
- Time to add feature: < 2 hours (varies)
- Merge conflicts: Minimal (improve with split files)

---

**End of Refactoring Recommendations**
**Next:** See `IMPLEMENTATION_ROADMAP.md` for complete action plan
