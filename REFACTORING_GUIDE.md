# GAM Admin Tool - Refactoring Guide

## Overview

This guide documents the refactored utility methods in `BaseOperationWindow` that eliminate code duplication and provide standard patterns for new features.

**Date:** 2025-11-13
**Status:** Infrastructure complete, gradual migration in progress

---

## New Utility Methods in BaseOperationWindow

### 1. `load_combobox_async()` - Async Combobox Loading

**Purpose:** Eliminates ~270 lines of duplicated combobox loading code.

**Old Pattern (18 lines, repeated 15+ times):**
```python
def load_users_for_manage_ou(self):
    self.manage_ou_email['values'] = ["Loading..."]
    self.manage_ou_email.set("Loading...")

    def fetch_and_populate():
        from utils.workspace_data import fetch_users
        users = fetch_users()
        if users:
            self.after(0, lambda: self.manage_ou_email.configure(values=sorted(users)))
            self.after(0, lambda: self.manage_ou_email.set(""))
            self.after(0, lambda: self.enable_standalone_fuzzy_search(self.manage_ou_email, sorted(users)))
        else:
            self.after(0, lambda: self.manage_ou_email.configure(values=[]))
            self.after(0, lambda: self.manage_ou_email.set(""))

    import threading
    threading.Thread(target=fetch_and_populate, daemon=True).start()
```

**New Pattern (1 line):**
```python
def load_users_for_manage_ou(self):
    from utils.workspace_data import fetch_users
    self.load_combobox_async(self.manage_ou_email, fetch_users, enable_fuzzy=True)
```

**Parameters:**
- `combobox`: The combobox widget to populate
- `fetch_function`: Function that returns list of items (e.g., `fetch_users`, `fetch_groups`)
- `tab_id`: Optional tab ID for fuzzy search with getattr/setattr pattern
- `enable_fuzzy`: Enable fuzzy search (default: True)
- `default_value`: Value to set after loading (default: "")
- `loading_text`: Loading message (default: "Loading...")
- `sort`: Sort results alphabetically (default: True)

**Example Usage:**
```python
# With tab_id (uses self.enable_fuzzy_search from base)
self.load_combobox_async(
    self.combobox_widget,
    fetch_users,
    tab_id='delete_user',
    enable_fuzzy=True
)

# Without tab_id (uses standalone fuzzy search)
self.load_combobox_async(
    self.email_combobox,
    fetch_users,
    enable_fuzzy=True
)

# Disable fuzzy search
self.load_combobox_async(
    self.simple_combobox,
    fetch_groups,
    enable_fuzzy=False
)
```

---

### 2. `browse_csv_file()` - CSV File Browser

**Purpose:** Eliminates ~30 lines of duplicated file browsing code.

**Old Pattern (8 lines, repeated 7+ times):**
```python
def browse_csv_for_create_users(self):
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if file_path:
        self.create_users_csv_entry.delete(0, tk.END)
        self.create_users_csv_entry.insert(0, file_path)
```

**New Pattern (1 line):**
```python
def browse_csv_for_create_users(self):
    self.browse_csv_file(self.create_users_csv_entry, "Select Users CSV File")
```

**Parameters:**
- `entry_widget`: Entry or Combobox widget to populate with file path
- `title`: Dialog title (default: "Select CSV File")

**Returns:** File path string, or None if canceled

**Example Usage:**
```python
# Simple usage
self.browse_csv_file(self.csv_entry_widget)

# With custom title
self.browse_csv_file(self.csv_entry_widget, "Select User Import CSV")

# Check if file was selected
file_path = self.browse_csv_file(self.csv_entry_widget, "Select CSV")
if file_path:
    print(f"Selected: {file_path}")
```

---

### 3. `read_and_validate_csv()` - CSV Reading & Validation

**Purpose:** Eliminates ~100 lines of duplicated CSV handling code.

**Old Pattern (25 lines, repeated 8+ times):**
```python
csv_file = self.create_users_csv_entry.get().strip()
if not csv_file:
    messagebox.showerror("Error", "Please select a CSV file.")
    return

try:
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users_data = list(reader)

    if not users_data:
        messagebox.showerror("Error", "CSV file is empty.")
        return

    # Validate required fields
    for user_data in users_data:
        if 'email' not in user_data or not user_data['email']:
            messagebox.showerror("Validation Error", "Missing 'email' field in CSV.")
            return

    if not self.confirm_bulk_operation(len(users_data), "create users"):
        return

except Exception as e:
    messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
    return

# Now process users_data...
```

**New Pattern (6 lines):**
```python
csv_file = self.create_users_csv_entry.get().strip()
if not csv_file:
    self.show_error("Please select a CSV file.")
    return

users_data = self.read_and_validate_csv(
    csv_file,
    required_fields=['email', 'firstname', 'lastname'],
    operation_name='create users'
)

if not users_data:
    return  # Error already shown to user

# Now process users_data...
```

**Parameters:**
- `file_path`: Path to CSV file
- `required_fields`: List of required column headers (e.g., `['email', 'firstname']`)
- `operation_name`: Operation description for messages (e.g., `'create users'`)

**Returns:** List of dictionaries (CSV rows), or None on error/cancel

**Features:**
- UTF-8 encoding support
- Empty file detection
- Required field validation (checks all rows)
- User confirmation for bulk operations
- Comprehensive error handling (file not found, permissions, etc.)

**Example Usage:**
```python
# Basic usage
data = self.read_and_validate_csv(
    csv_path,
    required_fields=['email'],
    operation_name='delete users'
)
if data:
    # Process data
    for row in data:
        email = row['email']
        # ...

# Multiple required fields
data = self.read_and_validate_csv(
    csv_path,
    required_fields=['email', 'firstname', 'lastname', 'ou'],
    operation_name='create users'
)

# For operations with optional fields
data = self.read_and_validate_csv(
    csv_path,
    required_fields=['email'],  # Only email required
    operation_name='update users'
)
if data:
    # Optional fields may or may not exist
    for row in data:
        email = row['email']
        firstname = row.get('firstname', '')  # Optional
        lastname = row.get('lastname', '')    # Optional
```

---

### 4. `create_mode_toggle()` - Single/CSV Mode Toggle

**Purpose:** Eliminates ~40 lines of duplicated mode toggle code.

**Old Pattern (20 lines per tab):**
```python
# Mode selection
self.create_users_mode = tk.StringVar(value="single")
mode_frame = ttk.Frame(tab)
mode_frame.pack(fill=tk.X, pady=(0, 10))

ttk.Radiobutton(
    mode_frame,
    text="Create Single User",
    variable=self.create_users_mode,
    value="single",
    command=self.toggle_create_users_mode
).pack(side=tk.LEFT, padx=(0, 20))

ttk.Radiobutton(
    mode_frame,
    text="Bulk Create from CSV",
    variable=self.create_users_mode,
    value="csv",
    command=self.toggle_create_users_mode
).pack(side=tk.LEFT)

# Create frames
self.create_users_single_frame = ttk.LabelFrame(tab, text="Create Single User", padding="10")
self.create_users_csv_frame = ttk.LabelFrame(tab, text="Bulk Create from CSV", padding="10")
self.create_users_single_frame.pack(fill=tk.X, expand=True)

# Toggle method
def toggle_create_users_mode(self):
    if self.create_users_mode.get() == "single":
        self.create_users_csv_frame.pack_forget()
        self.create_users_single_frame.pack(fill=tk.X, expand=True)
    else:
        self.create_users_single_frame.pack_forget()
        self.create_users_csv_frame.pack(fill=tk.X, expand=True)
```

**New Pattern (5 lines + widget additions):**
```python
# Create mode toggle
mode_frame, single_frame, csv_frame, mode_var = self.create_mode_toggle(
    tab,
    tab_id='create_user',
    single_label="Create Single User",
    csv_label="Bulk Create from CSV"
)

# Add widgets to single_frame
ttk.Label(single_frame, text="Email:").grid(row=0, column=0)
ttk.Entry(single_frame).grid(row=0, column=1)

# Add widgets to csv_frame
ttk.Label(csv_frame, text="CSV File:").pack()
csv_entry = ttk.Entry(csv_frame)
csv_entry.pack()
ttk.Button(csv_frame, text="Browse",
           command=lambda: self.browse_csv_file(csv_entry)).pack()
```

**Parameters:**
- `parent`: Parent widget (usually the tab)
- `tab_id`: Tab identifier for storing mode variable
- `single_label`: Label for single mode radio button
- `csv_label`: Label for CSV mode radio button
- `default_mode`: Default mode (`'single'` or `'csv'`, default: `'single'`)

**Returns:** Tuple of `(mode_frame, single_frame, csv_frame, mode_var)`

**Features:**
- Automatically creates and manages mode variable (`self.{tab_id}_mode`)
- Handles frame visibility toggling
- Returns frames for customization
- Mode variable can be accessed via `getattr(self, f'{tab_id}_mode').get()`

**Example Usage:**
```python
# Basic usage
mode_frame, single_frame, csv_frame, mode_var = self.create_mode_toggle(
    parent_tab,
    tab_id='delete_user'
)

# Check current mode
current_mode = mode_var.get()  # 'single' or 'csv'
# OR
current_mode = self.delete_user_mode.get()

# Custom labels
mode_frame, single_frame, csv_frame, mode_var = self.create_mode_toggle(
    parent_tab,
    tab_id='import_data',
    single_label="Manual Entry",
    csv_label="Import from File",
    default_mode='csv'
)
```

---

### 5. Fuzzy Search - Standardized

**Purpose:** Eliminates ~105 lines of duplicated fuzzy search code.

**Changes:**
- `BaseOperationWindow.enable_fuzzy_search()` - For comboboxes with tab_id
- `BaseOperationWindow._enable_standalone_fuzzy_search()` - For comboboxes without tab_id
- Both are now called automatically by `load_combobox_async()` when `enable_fuzzy=True`

**Old Pattern:**
```python
def enable_standalone_fuzzy_search(self, combobox, all_values):
    """35 lines of code..."""
    combobox._all_values = all_values
    def on_keyrelease(event):
        # ... filtering logic ...
    combobox.bind('<KeyRelease>', on_keyrelease)
```

**New Pattern:**
```python
# Automatically handled by load_combobox_async!
self.load_combobox_async(combobox, fetch_function, enable_fuzzy=True)

# Or manually if needed:
self._enable_standalone_fuzzy_search(combobox, all_values)
```

**Note:** You generally don't need to call fuzzy search methods directly anymore - `load_combobox_async()` handles it.

---

## Migration Strategy

### For Existing Code

**Gradual migration recommended:**
1. New code should use refactored methods immediately
2. Existing code can be migrated incrementally
3. Priority: Migrate when touching a file for other reasons

**No urgent need to migrate all existing code** - it works fine as-is. The refactored methods are primarily for:
- New features (Calendar, Drive, Reporting)
- Future maintenance
- Code clarity

### For New Features (Calendar, Drive, Reporting)

**MUST use refactored methods:**
- ✅ Use `load_combobox_async()` for all combobox loading
- ✅ Use `browse_csv_file()` for CSV file selection
- ✅ Use `read_and_validate_csv()` for CSV processing
- ✅ Use `create_mode_toggle()` for single/CSV mode tabs
- ✅ Fuzzy search is automatic with `load_combobox_async()`

---

## Complete Example: Creating a New Feature Tab

```python
def create_new_feature_tab(self, notebook):
    """Example of creating a tab using refactored methods."""
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="New Feature")

    # Create scrollable container
    container, scrollable = self.create_scrollable_frame(tab)

    # Create mode toggle
    mode_frame, single_frame, csv_frame, mode_var = self.create_mode_toggle(
        scrollable,
        tab_id='new_feature',
        single_label="Single Entry",
        csv_label="Bulk Import from CSV"
    )

    # === Single Mode Widgets ===
    ttk.Label(single_frame, text="User Email:").grid(row=0, column=0, sticky=tk.W)
    user_combobox = ttk.Combobox(single_frame, width=40)
    user_combobox.grid(row=0, column=1, sticky=tk.EW)

    # Load users with fuzzy search
    from utils.workspace_data import fetch_users
    self.load_combobox_async(user_combobox, fetch_users, enable_fuzzy=True)

    # === CSV Mode Widgets ===
    ttk.Label(csv_frame, text="CSV File:").pack(anchor=tk.W)
    csv_entry = ttk.Entry(csv_frame, width=50)
    csv_entry.pack(fill=tk.X, pady=5)

    ttk.Button(
        csv_frame,
        text="Browse...",
        command=lambda: self.browse_csv_file(csv_entry, "Select Feature CSV")
    ).pack()

    # === Execute Button ===
    def execute_operation():
        mode = mode_var.get()

        if mode == 'single':
            user_email = user_combobox.get().strip()
            if not user_email:
                self.show_error("Please select a user.")
                return
            # Process single user...

        else:  # CSV mode
            csv_file = csv_entry.get().strip()
            if not csv_file:
                self.show_error("Please select a CSV file.")
                return

            # Read and validate CSV
            data = self.read_and_validate_csv(
                csv_file,
                required_fields=['email'],
                operation_name='process users'
            )

            if not data:
                return  # Error already shown

            # Process CSV data...
            for row in data:
                user_email = row['email']
                # ...

    ttk.Button(
        scrollable,
        text="Execute",
        command=execute_operation
    ).pack(pady=20)
```

---

## Benefits Summary

### Code Reduction
- **~270 lines** eliminated from combobox loading duplication
- **~105 lines** eliminated from fuzzy search duplication
- **~40 lines** eliminated from mode toggle duplication
- **~100 lines** eliminated from CSV handling duplication
- **~30 lines** eliminated from file browsing duplication

**Total: ~545 lines of duplication eliminated**

### Developer Experience
- ✅ Consistent patterns across all features
- ✅ Less code to write for new features
- ✅ Fewer bugs (shared, tested code)
- ✅ Easier maintenance
- ✅ Better documentation

### Future Features
- Calendar Operations can use these patterns immediately
- Drive Operations can use these patterns immediately
- Reporting can use these patterns immediately
- Any future features benefit automatically

---

## Testing Checklist

When using refactored methods, verify:

- [ ] Comboboxes load data correctly
- [ ] Fuzzy search filters as you type
- [ ] Focus stays in combobox while typing (not stolen by dropdown)
- [ ] CSV file browser opens and populates entry widget
- [ ] CSV validation catches empty files
- [ ] CSV validation catches missing required fields
- [ ] Bulk operation confirmation appears for CSV imports
- [ ] Mode toggle switches frames correctly
- [ ] Single mode shows single entry widgets
- [ ] CSV mode shows CSV entry widgets

---

## Questions?

If you have questions about using these refactored methods, refer to:
1. This guide for usage patterns
2. `gui/base_operation_window.py` for method documentation
3. Existing window files for examples (users_window.py, email_window.py, groups_window.py)

---

**Last Updated:** 2025-11-13
**Version:** 1.0
**Status:** Ready for use in new features
