"""
Calendar Operations Window for GAM Admin Tool.

Provides a tabbed interface for all calendar-related operations including
managing permissions, creating/deleting calendars, viewing information,
and importing/exporting calendar data.

Inherits from BaseOperationWindow for common functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime, timedelta

from gui.base_operation_window import BaseOperationWindow
from modules import calendar as calendar_ops
from utils.workspace_data import fetch_users, fetch_groups


# Calendar color mapping (GAM color IDs to names)
CALENDAR_COLORS = {
    "": "Default",
    "1": "Lavender",
    "2": "Sage",
    "3": "Grape",
    "4": "Flamingo",
    "5": "Banana",
    "6": "Tangerine",
    "7": "Peacock",
    "8": "Graphite",
    "9": "Blueberry",
    "10": "Basil",
    "11": "Tomato"
}


class CalendarWindow(BaseOperationWindow):
    """
    Calendar Operations window with tabbed interface.

    Provides 4 tabs for different calendar operations:
    - Manage Permissions
    - Create/Delete Calendars
    - View Calendar Info
    - Import/Export Data
    """

    def __init__(self, parent):
        """
        Initialize the Calendar Operations window.

        Args:
            parent: The parent tkinter widget
        """
        super().__init__(parent, "Calendar Operations", "900x750", (800, 600))

    def create_operation_tabs(self):
        """Create all calendar operation tabs."""
        self.create_permissions_tab()
        self.create_manage_calendars_tab()
        self.create_view_info_tab()
        self.create_import_export_tab()

        # Auto-load comboboxes on window initialization
        self.after(100, self.initialize_comboboxes)

    def initialize_comboboxes(self):
        """Auto-load all comboboxes on window initialization."""
        # Tab 1: Manage Permissions
        self.load_combobox_async(self.permissions_owner_combo, fetch_users, enable_fuzzy=True)
        self.load_combobox_async(self.permissions_user_combo, fetch_users, enable_fuzzy=True)

        # Tab 2: Create/Delete Calendars
        self.load_combobox_async(self.manage_calendar_owner_combo, fetch_users, enable_fuzzy=True)

        # Tab 3: View Info
        self.load_combobox_async(self.view_info_owner_combo, fetch_users, enable_fuzzy=True)

        # Tab 4: Import/Export
        self.load_combobox_async(self.import_export_owner_combo, fetch_users, enable_fuzzy=True)

    # ==================== TAB 1: MANAGE PERMISSIONS ====================

    def create_permissions_tab(self):
        """Create tab for managing calendar permissions."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Permissions")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Share or unshare calendars with users/groups. Choose permission level and optionally send notifications.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Operation type (Add or Remove)
        operation_frame = ttk.LabelFrame(tab, text="Operation", padding="10")
        operation_frame.pack(fill=tk.X, pady=(0, 10))

        self.permissions_operation_var = tk.StringVar(value="add")
        ttk.Radiobutton(
            operation_frame,
            text="Add Permission (Share Calendar)",
            variable=self.permissions_operation_var,
            value="add",
            command=self.toggle_permissions_operation
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            operation_frame,
            text="Remove Permission (Unshare Calendar)",
            variable=self.permissions_operation_var,
            value="remove",
            command=self.toggle_permissions_operation
        ).pack(side=tk.LEFT)

        # Calendar Selection Frame
        calendar_frame = ttk.LabelFrame(tab, text="Calendar Selection", padding="10")
        calendar_frame.pack(fill=tk.X, pady=(0, 10))

        # Calendar Owner
        row = 0
        ttk.Label(calendar_frame, text="Calendar Owner:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.permissions_owner_combo = ttk.Combobox(calendar_frame, width=40)
        self.permissions_owner_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        calendar_frame.columnconfigure(1, weight=1)

        # Calendar ID
        row += 1
        ttk.Label(calendar_frame, text="Calendar Name:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.permissions_calendar_combo = ttk.Combobox(calendar_frame, width=40)
        self.permissions_calendar_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Button(
            calendar_frame,
            text="Load Calendars",
            command=self.load_calendars_for_permissions
        ).grid(row=row, column=2, padx=5, pady=5)

        ttk.Label(
            calendar_frame,
            text="Tip: Use 'primary' for user's main calendar, or select from dropdown",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        ).grid(row=row+1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(0, 5))

        # User/Group to share with
        permission_user_frame = ttk.LabelFrame(tab, text="Share With", padding="10")
        permission_user_frame.pack(fill=tk.X, pady=(0, 10))

        row = 0
        ttk.Label(permission_user_frame, text="User/Group Email:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.permissions_user_combo = ttk.Combobox(permission_user_frame, width=40)
        self.permissions_user_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        permission_user_frame.columnconfigure(1, weight=1)

        # Permission Settings Frame (only for Add operation)
        self.permissions_settings_frame = ttk.LabelFrame(tab, text="Permission Settings", padding="10")
        self.permissions_settings_frame.pack(fill=tk.X, pady=(0, 10))

        row = 0
        ttk.Label(self.permissions_settings_frame, text="Permission Level:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.permissions_role_var = tk.StringVar(value="reader")
        role_combo = ttk.Combobox(
            self.permissions_settings_frame,
            textvariable=self.permissions_role_var,
            values=["reader", "writer", "owner"],
            state="readonly",
            width=20
        )
        role_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        # Role descriptions inline
        ttk.Label(
            self.permissions_settings_frame,
            text="(reader: view only | writer: view & edit | owner: full control)",
            font=('Arial', 9),
            foreground='gray'
        ).grid(row=row, column=2, sticky=tk.W, padx=(10, 5), pady=5)

        # Send notification checkbox
        row += 1
        self.permissions_send_notif_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.permissions_settings_frame,
            text="Send notification email",
            variable=self.permissions_send_notif_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        ttk.Label(
            self.permissions_settings_frame,
            text="(sends email notification about calendar sharing)",
            font=('Arial', 9),
            foreground='gray'
        ).grid(row=row, column=2, sticky=tk.W, padx=(10, 5), pady=5)

        # Progress frame
        self.permissions_progress_frame = self.create_progress_frame(tab)
        self.permissions_progress_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        execute_frame = ttk.Frame(tab)
        execute_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            execute_frame,
            text="Execute",
            command=self.execute_permissions_operation,
            width=20
        ).pack(side=tk.LEFT)

    def toggle_permissions_operation(self):
        """Toggle visibility of permission settings based on operation."""
        if self.permissions_operation_var.get() == "add":
            # Show permission settings
            self.permissions_settings_frame.pack(fill=tk.X, pady=(0, 10), before=self.permissions_progress_frame)
        else:
            # Hide permission settings (so layout doesn't shift)
            self.permissions_settings_frame.pack_forget()

    def load_calendars_for_permissions(self):
        """Load calendars for selected owner."""
        owner_email = self.permissions_owner_combo.get().strip()
        if not owner_email:
            messagebox.showwarning("Warning", "Please enter calendar owner email first")
            return

        def fetch_calendars():
            calendars = calendar_ops.get_user_calendars(owner_email)
            return [f"{cal['summary']} ({cal['id']})" for cal in calendars if cal.get('id')]

        self.load_combobox_async(self.permissions_calendar_combo, fetch_calendars, enable_fuzzy=True)

    def execute_permissions_operation(self):
        """Execute permission add/remove operation."""
        # Get values
        owner_email = self.permissions_owner_combo.get().strip()
        calendar_input = self.permissions_calendar_combo.get().strip()
        target_user = self.permissions_user_combo.get().strip()
        operation = self.permissions_operation_var.get()

        # Validate inputs
        if not owner_email:
            messagebox.showerror("Error", "Please enter calendar owner email")
            return
        if not calendar_input:
            messagebox.showerror("Error", "Please enter calendar name")
            return
        if not target_user:
            messagebox.showerror("Error", "Please enter user/group email to share with")
            return

        # Extract calendar ID if format is "Summary (ID)"
        if '(' in calendar_input and calendar_input.endswith(')'):
            calendar_id = calendar_input.split('(')[-1].rstrip(')')
        else:
            calendar_id = calendar_input

        # Confirmation
        action_text = "add permission for" if operation == "add" else "remove permission for"
        if not messagebox.askyesno(
            "Confirm",
            f"Are you sure you want to {action_text} {target_user} on calendar {calendar_id}?"
        ):
            return

        # Clear previous results
        self.clear_results(self.permissions_progress_frame)

        # Execute operation
        if operation == "add":
            role = self.permissions_role_var.get()
            send_notif = self.permissions_send_notif_var.get()
            self.run_operation(
                calendar_ops.add_calendar_permission,
                self.permissions_progress_frame,
                [calendar_id],
                target_user,
                role,
                send_notif
            )
        else:
            self.run_operation(
                calendar_ops.remove_calendar_permission,
                self.permissions_progress_frame,
                [calendar_id],
                target_user
            )

    # ==================== TAB 2: CREATE/DELETE CALENDARS ====================

    def create_manage_calendars_tab(self):
        """Create tab for creating/deleting calendars."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Create/Delete Calendars")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Create new calendars or delete existing ones.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Operation type
        operation_frame = ttk.LabelFrame(tab, text="Operation", padding="10")
        operation_frame.pack(fill=tk.X, pady=(0, 10))

        self.manage_calendar_operation_var = tk.StringVar(value="create")
        ttk.Radiobutton(
            operation_frame,
            text="Create Calendar",
            variable=self.manage_calendar_operation_var,
            value="create",
            command=self.toggle_manage_calendar_operation
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            operation_frame,
            text="Delete Calendar",
            variable=self.manage_calendar_operation_var,
            value="delete",
            command=self.toggle_manage_calendar_operation
        ).pack(side=tk.LEFT)

        # Shared Calendar Details Frame
        details_frame = ttk.LabelFrame(tab, text="Calendar Details", padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 10))

        # Calendar Owner (shared)
        row = 0
        ttk.Label(details_frame, text="Calendar Owner:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.manage_calendar_owner_combo = ttk.Combobox(details_frame, width=40)
        self.manage_calendar_owner_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        details_frame.columnconfigure(1, weight=1)

        # Bind owner selection to load calendars
        self.manage_calendar_owner_combo.bind('<<ComboboxSelected>>', lambda e: self.load_calendars_for_manage())

        # Calendar Name - different widgets for create vs delete
        row += 1
        ttk.Label(details_frame, text="Calendar Name:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)

        # Entry widget for create mode
        self.manage_calendar_name_entry = ttk.Entry(details_frame, width=40)
        self.manage_calendar_name_entry.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        # Combobox for delete mode (initially hidden)
        self.manage_calendar_name_combo = ttk.Combobox(details_frame, width=40, state='readonly')
        self.manage_calendar_name_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        self.manage_calendar_name_combo.grid_remove()  # Hide initially

        # Load button (for delete mode)
        self.manage_calendar_load_btn = ttk.Button(
            details_frame,
            text="Load Calendars",
            command=self.load_calendars_for_manage
        )
        self.manage_calendar_load_btn.grid(row=row, column=2, padx=5, pady=5)
        self.manage_calendar_load_btn.grid_remove()  # Hide initially

        # Create-specific fields frame
        self.create_calendar_frame = ttk.Frame(details_frame)
        self.create_calendar_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=(10, 0))

        # Description (create only)
        ttk.Label(self.create_calendar_frame, text="Description (Optional):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.create_calendar_desc_entry = ttk.Entry(self.create_calendar_frame, width=40)
        self.create_calendar_desc_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.create_calendar_frame.columnconfigure(1, weight=1)

        # Progress frame
        self.manage_calendar_progress_frame = self.create_progress_frame(tab)
        self.manage_calendar_progress_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        execute_frame = ttk.Frame(tab)
        execute_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            execute_frame,
            text="Execute",
            command=self.execute_manage_calendar_operation,
            width=20
        ).pack(side=tk.LEFT)

        # Initial state
        self.toggle_manage_calendar_operation()

    def toggle_manage_calendar_operation(self):
        """Toggle between create and delete modes."""
        if self.manage_calendar_operation_var.get() == "create":
            # Create mode: show entry, hide combobox and load button, show create fields
            self.manage_calendar_name_entry.grid()
            self.manage_calendar_name_combo.grid_remove()
            self.manage_calendar_load_btn.grid_remove()
            self.create_calendar_frame.grid()
        else:
            # Delete mode: show combobox and load button, hide entry, hide create fields
            self.manage_calendar_name_entry.grid_remove()
            self.manage_calendar_name_combo.grid()
            self.manage_calendar_load_btn.grid()
            self.create_calendar_frame.grid_remove()

    def load_calendars_for_manage(self):
        """Load calendars for selected owner."""
        owner_email = self.manage_calendar_owner_combo.get().strip()
        if not owner_email:
            messagebox.showwarning("Warning", "Please enter calendar owner email first")
            return

        def fetch_calendars():
            calendars = calendar_ops.get_user_calendars(owner_email)
            return [f"{cal['summary']} ({cal['id']})" for cal in calendars if cal.get('id')]

        self.load_combobox_async(self.manage_calendar_name_combo, fetch_calendars, enable_fuzzy=True)

    def execute_manage_calendar_operation(self):
        """Execute create or delete calendar operation."""
        operation = self.manage_calendar_operation_var.get()
        owner = self.manage_calendar_owner_combo.get().strip()

        # Validate common fields
        if not owner:
            messagebox.showerror("Error", "Please enter calendar owner email")
            return

        if operation == "create":
            # Create mode - get from entry widget
            calendar_input = self.manage_calendar_name_entry.get().strip()
            if not calendar_input:
                messagebox.showerror("Error", "Please enter calendar name")
                return
            name = calendar_input
            description = self.create_calendar_desc_entry.get().strip()

            # Confirm
            if not messagebox.askyesno("Confirm", f"Create calendar '{name}' for {owner}?"):
                return

            # Clear and execute
            self.clear_results(self.manage_calendar_progress_frame)
            self.run_operation(
                calendar_ops.create_calendar,
                self.manage_calendar_progress_frame,
                owner,
                name,
                description
            )

        else:
            # Delete mode - get from combobox widget
            calendar_input = self.manage_calendar_name_combo.get().strip()
            if not calendar_input:
                messagebox.showerror("Error", "Please select a calendar to delete")
                return

            # Extract calendar ID
            if '(' in calendar_input and calendar_input.endswith(')'):
                calendar_id = calendar_input.split('(')[-1].rstrip(')')
            else:
                calendar_id = calendar_input

            # Confirm
            if not messagebox.askyesno("Confirm", f"⚠️ Delete calendar {calendar_id}?\n\nThis action cannot be undone!"):
                return

            # Clear and execute
            self.clear_results(self.manage_calendar_progress_frame)
            self.run_operation(
                calendar_ops.delete_calendar,
                self.manage_calendar_progress_frame,
                owner,
                calendar_id
            )

    # ==================== TAB 3: VIEW CALENDAR INFO ====================

    def create_view_info_tab(self):
        """Create tab for viewing calendar information."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="View Calendar Info")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="View calendar information, URLs, and permissions.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Calendar Selection Frame
        selection_frame = ttk.LabelFrame(tab, text="Calendar Selection", padding="10")
        selection_frame.pack(fill=tk.X, pady=(0, 10))

        row = 0
        ttk.Label(selection_frame, text="Calendar Owner:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.view_info_owner_combo = ttk.Combobox(selection_frame, width=40)
        self.view_info_owner_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        selection_frame.columnconfigure(1, weight=1)

        row += 1
        ttk.Label(selection_frame, text="Calendar Name:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.view_info_calendar_combo = ttk.Combobox(selection_frame, width=40)
        self.view_info_calendar_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Button(
            selection_frame,
            text="Load Calendars",
            command=self.load_calendars_for_view_info
        ).grid(row=row, column=2, padx=5, pady=5)

        # Buttons Frame
        buttons_frame = ttk.Frame(tab)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            buttons_frame,
            text="View Calendar Info",
            command=self.view_calendar_info,
            width=20
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            buttons_frame,
            text="View Permissions",
            command=self.view_calendar_permissions,
            width=20
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            buttons_frame,
            text="Clear",
            command=lambda: self.clear_results(self.view_info_progress_frame),
            width=15
        ).pack(side=tk.LEFT)

        # Progress frame (repurposed as results display)
        self.view_info_progress_frame = self.create_progress_frame(tab)
        self.view_info_progress_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    def load_calendars_for_view_info(self):
        """Load calendars for view info."""
        owner_email = self.view_info_owner_combo.get().strip()
        if not owner_email:
            messagebox.showwarning("Warning", "Please enter calendar owner email first")
            return

        def fetch_calendars():
            calendars = calendar_ops.get_user_calendars(owner_email)
            return [f"{cal['summary']} ({cal['id']})" for cal in calendars if cal.get('id')]

        self.load_combobox_async(self.view_info_calendar_combo, fetch_calendars, enable_fuzzy=True)

    def view_calendar_info(self):
        """View calendar information."""
        owner = self.view_info_owner_combo.get().strip()
        calendar_input = self.view_info_calendar_combo.get().strip()

        if not owner:
            messagebox.showerror("Error", "Please enter calendar owner email")
            return
        if not calendar_input:
            messagebox.showerror("Error", "Please enter calendar name")
            return

        # Extract calendar ID
        if '(' in calendar_input and calendar_input.endswith(')'):
            calendar_id = calendar_input.split('(')[-1].rstrip(')')
        else:
            calendar_id = calendar_input

        # Validate calendar_id is not empty
        if not calendar_id:
            messagebox.showerror("Error", "Invalid calendar selection. Please select a valid calendar or enter 'primary'")
            return

        # Clear and run
        self.clear_results(self.view_info_progress_frame)
        self.run_operation(
            calendar_ops.get_calendar_info,
            self.view_info_progress_frame,
            calendar_id,
            owner
        )

    def view_calendar_permissions(self):
        """View calendar permissions."""
        calendar_input = self.view_info_calendar_combo.get().strip()

        if not calendar_input:
            messagebox.showerror("Error", "Please enter calendar name")
            return

        # Extract calendar ID
        if '(' in calendar_input and calendar_input.endswith(')'):
            calendar_id = calendar_input.split('(')[-1].rstrip(')')
        else:
            calendar_id = calendar_input

        # Validate calendar_id is not empty
        if not calendar_id:
            messagebox.showerror("Error", "Invalid calendar selection. Please select a valid calendar or enter 'primary'")
            return

        # Clear and run
        self.clear_results(self.view_info_progress_frame)
        self.run_operation(
            calendar_ops.get_calendar_acl,
            self.view_info_progress_frame,
            calendar_id
        )

    # ==================== TAB 4: IMPORT/EXPORT ====================

    def create_import_export_tab(self):
        """Create tab for exporting calendar data."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Export Calendar")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Export calendar events to CSV format.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Shared Calendar Selection Frame
        calendar_frame = ttk.LabelFrame(tab, text="Calendar Selection", padding="10")
        calendar_frame.pack(fill=tk.X, pady=(0, 10))

        # Calendar Owner
        row = 0
        ttk.Label(calendar_frame, text="Calendar Owner:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.import_export_owner_combo = ttk.Combobox(calendar_frame, width=40)
        self.import_export_owner_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        calendar_frame.columnconfigure(1, weight=1)

        # Calendar Name
        row += 1
        ttk.Label(calendar_frame, text="Calendar Name:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.import_export_calendar_combo = ttk.Combobox(calendar_frame, width=40)
        self.import_export_calendar_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Button(
            calendar_frame,
            text="Load Calendars",
            command=self.load_calendars_for_import_export
        ).grid(row=row, column=2, padx=5, pady=5)

        # Export settings frame
        self.export_frame = ttk.LabelFrame(tab, text="Export Settings", padding="10")
        self.export_frame.pack(fill=tk.X, pady=(0, 10))

        # Date range
        ttk.Label(self.export_frame, text="Start Date:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_start_date_entry = ttk.Entry(self.export_frame, width=20)
        self.export_start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        default_start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.export_start_date_entry.insert(0, default_start)

        ttk.Label(self.export_frame, text="(YYYY-MM-DD)", font=('Arial', 9), foreground='gray').grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=5
        )

        ttk.Label(self.export_frame, text="End Date:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_end_date_entry = ttk.Entry(self.export_frame, width=20)
        self.export_end_date_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        default_end = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.export_end_date_entry.insert(0, default_end)

        ttk.Label(self.export_frame, text="(YYYY-MM-DD)", font=('Arial', 9), foreground='gray').grid(
            row=1, column=2, sticky=tk.W, padx=5, pady=5
        )

        ttk.Label(self.export_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_file_entry = ttk.Entry(self.export_frame, width=40)
        self.export_file_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.export_frame.columnconfigure(1, weight=1)

        ttk.Button(
            self.export_frame,
            text="Browse...",
            command=self.browse_export_file
        ).grid(row=2, column=2, padx=5, pady=5)

        # Progress frame
        self.import_export_progress_frame = self.create_progress_frame(tab)
        self.import_export_progress_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        execute_frame = ttk.Frame(tab)
        execute_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            execute_frame,
            text="Execute",
            command=self.execute_export_operation,
            width=20
        ).pack(side=tk.LEFT)

    def load_calendars_for_import_export(self):
        """Load calendars for export."""
        owner_email = self.import_export_owner_combo.get().strip()
        if not owner_email:
            messagebox.showwarning("Warning", "Please enter calendar owner email first")
            return

        def fetch_calendars():
            calendars = calendar_ops.get_user_calendars(owner_email)
            return [f"{cal['summary']} ({cal['id']})" for cal in calendars if cal.get('id')]

        self.load_combobox_async(self.import_export_calendar_combo, fetch_calendars, enable_fuzzy=True)

    def browse_export_file(self):
        """Browse for export file location."""
        file_path = filedialog.asksaveasfilename(
            title="Save Events As",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.export_file_entry.delete(0, tk.END)
            self.export_file_entry.insert(0, file_path)

    def execute_export_operation(self):
        """Execute calendar export operation."""
        owner = self.import_export_owner_combo.get().strip()
        calendar_input = self.import_export_calendar_combo.get().strip()
        start_date = self.export_start_date_entry.get().strip()
        end_date = self.export_end_date_entry.get().strip()
        output_file = self.export_file_entry.get().strip()

        # Validate fields
        if not owner:
            messagebox.showerror("Error", "Please enter calendar owner email")
            return
        if not calendar_input:
            messagebox.showerror("Error", "Please select calendar")
            return
        if not start_date or not end_date:
            messagebox.showerror("Error", "Please enter date range")
            return
        if not output_file:
            messagebox.showerror("Error", "Please select output file")
            return

        # Extract calendar ID
        if '(' in calendar_input and calendar_input.endswith(')'):
            calendar_id = calendar_input.split('(')[-1].rstrip(')')
        else:
            calendar_id = calendar_input

        # Validate date format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return

        # Confirm
        if not messagebox.askyesno("Confirm", f"Export events from {start_date} to {end_date}?"):
            return

        # Clear and execute
        self.clear_results(self.import_export_progress_frame)
        self.run_operation(
            calendar_ops.export_calendar_events,
            self.import_export_progress_frame,
            calendar_id,
            start_date,
            end_date,
            output_file
        )
