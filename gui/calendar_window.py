"""
Calendar Operations window for GAM Admin Tool.

Provides GUI for calendar operations including:
- Managing calendar permissions (sharing)
- Creating and deleting calendars
- Viewing calendar information and URLs
- Importing and exporting calendar data
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
import os
from datetime import datetime, timedelta

from gui.base_operation_window import BaseOperationWindow
from modules import calendar as calendar_ops
from utils.workspace_data import fetch_users, fetch_groups


class CalendarWindow(BaseOperationWindow):
    """
    Calendar Operations window.

    Inherits from BaseOperationWindow to provide consistent UI and functionality.
    """

    def __init__(self, parent):
        """
        Initialize the Calendar Operations window.

        Args:
            parent: The parent tkinter widget
        """
        super().__init__(parent, "Calendar Operations", window_size="1000x800")

    def create_operation_tabs(self):
        """Create tabs for calendar operations."""
        # Tab 1: Manage Calendar Permissions
        self.create_permissions_tab()

        # Tab 2: Create/Delete Calendars
        self.create_manage_calendars_tab()

        # Tab 3: View Calendar Information
        self.create_view_info_tab()

        # Tab 4: Import/Export Calendar Data
        self.create_import_export_tab()

    # ==================== TAB 1: MANAGE PERMISSIONS ====================

    def create_permissions_tab(self):
        """Create tab for managing calendar permissions."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Manage Permissions")

        # Create scrollable container
        container, scrollable = self.create_scrollable_frame(tab)
        container.pack(fill=tk.BOTH, expand=True)

        # Operation type (Add or Remove)
        operation_frame = ttk.LabelFrame(scrollable, text="Operation", padding="10")
        operation_frame.pack(fill=tk.X, padx=10, pady=5)

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
        calendar_frame = ttk.LabelFrame(scrollable, text="Calendar Selection", padding="10")
        calendar_frame.pack(fill=tk.X, padx=10, pady=5)

        # User email (calendar owner)
        row = 0
        ttk.Label(calendar_frame, text="Calendar Owner:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.permissions_owner_combo = ttk.Combobox(calendar_frame, width=40)
        self.permissions_owner_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        calendar_frame.columnconfigure(1, weight=1)

        # Load users button
        ttk.Button(
            calendar_frame,
            text="Load Users",
            command=self.load_users_for_permissions_owner
        ).grid(row=row, column=2, padx=5, pady=5)

        # Calendar ID or dropdown
        row += 1
        ttk.Label(calendar_frame, text="Calendar ID:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
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
        permission_user_frame = ttk.LabelFrame(scrollable, text="Share With", padding="10")
        permission_user_frame.pack(fill=tk.X, padx=10, pady=5)

        row = 0
        ttk.Label(permission_user_frame, text="User/Group Email:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.permissions_user_combo = ttk.Combobox(permission_user_frame, width=40)
        self.permissions_user_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        permission_user_frame.columnconfigure(1, weight=1)

        ttk.Button(
            permission_user_frame,
            text="Load Users",
            command=self.load_users_for_permissions_target
        ).grid(row=row, column=2, padx=5, pady=5)

        # Permission Settings Frame (only for Add operation)
        self.permissions_settings_frame = ttk.LabelFrame(scrollable, text="Permission Settings", padding="10")
        self.permissions_settings_frame.pack(fill=tk.X, padx=10, pady=5)

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

        # Role descriptions
        ttk.Label(
            self.permissions_settings_frame,
            text="• reader: Can view events\n• writer: Can view and edit events\n• owner: Full control",
            font=('Arial', 9),
            foreground='gray',
            justify=tk.LEFT
        ).grid(row=row+1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 10))

        # Send notification checkbox
        row += 2
        self.permissions_send_notif_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.permissions_settings_frame,
            text="Send notification email to user",
            variable=self.permissions_send_notif_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        ttk.Label(
            self.permissions_settings_frame,
            text="⚠️ When checked, sends email notification to the user about calendar sharing",
            font=('Arial', 9, 'italic'),
            foreground='orange'
        ).grid(row=row+1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 5))

        # Execute button
        execute_frame = ttk.Frame(scrollable)
        execute_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(
            execute_frame,
            text="Execute",
            command=self.execute_permissions_operation,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        # Progress frame
        self.permissions_progress_frame = self.create_progress_frame(scrollable)

    def toggle_permissions_operation(self):
        """Toggle visibility of permission settings based on operation."""
        if self.permissions_operation_var.get() == "add":
            self.permissions_settings_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            self.permissions_settings_frame.pack_forget()

    def load_users_for_permissions_owner(self):
        """Load users for calendar owner combobox."""
        self.load_combobox_async(self.permissions_owner_combo, fetch_users, enable_fuzzy=True)

    def load_users_for_permissions_target(self):
        """Load users for target user combobox."""
        self.load_combobox_async(self.permissions_user_combo, fetch_users, enable_fuzzy=True)

    def load_calendars_for_permissions(self):
        """Load calendars for selected owner."""
        owner_email = self.permissions_owner_combo.get().strip()
        if not owner_email:
            messagebox.showwarning("Warning", "Please enter calendar owner email first")
            return

        def fetch_calendars():
            calendars = calendar_ops.get_user_calendars(owner_email)
            # Format as "Summary (ID)"
            return [f"{cal['summary']} ({cal['id']})" for cal in calendars]

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
            messagebox.showerror("Error", "Please enter calendar ID")
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
            self.run_async_operation(
                self.permissions_progress_frame,
                calendar_ops.add_calendar_permission,
                [calendar_id],
                target_user,
                role,
                send_notif
            )
        else:
            self.run_async_operation(
                self.permissions_progress_frame,
                calendar_ops.remove_calendar_permission,
                [calendar_id],
                target_user
            )

    # ==================== TAB 2: CREATE/DELETE CALENDARS ====================

    def create_manage_calendars_tab(self):
        """Create tab for creating/deleting calendars."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Create/Delete Calendars")

        # Create scrollable container
        container, scrollable = self.create_scrollable_frame(tab)
        container.pack(fill=tk.BOTH, expand=True)

        # Operation type
        operation_frame = ttk.LabelFrame(scrollable, text="Operation", padding="10")
        operation_frame.pack(fill=tk.X, padx=10, pady=5)

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

        # Create Calendar Frame
        self.create_calendar_frame = ttk.LabelFrame(scrollable, text="Create New Calendar", padding="10")
        self.create_calendar_frame.pack(fill=tk.X, padx=10, pady=5)

        row = 0
        ttk.Label(self.create_calendar_frame, text="Calendar Owner:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.create_calendar_owner_combo = ttk.Combobox(self.create_calendar_frame, width=40)
        self.create_calendar_owner_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        self.create_calendar_frame.columnconfigure(1, weight=1)

        ttk.Button(
            self.create_calendar_frame,
            text="Load Users",
            command=self.load_users_for_create_calendar
        ).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Label(self.create_calendar_frame, text="Calendar Name:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.create_calendar_name_entry = ttk.Entry(self.create_calendar_frame, width=40)
        self.create_calendar_name_entry.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        row += 1
        ttk.Label(self.create_calendar_frame, text="Description:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.create_calendar_desc_entry = ttk.Entry(self.create_calendar_frame, width=40)
        self.create_calendar_desc_entry.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        row += 1
        ttk.Label(self.create_calendar_frame, text="Color (optional):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.create_calendar_color_var = tk.StringVar(value="")
        color_combo = ttk.Combobox(
            self.create_calendar_frame,
            textvariable=self.create_calendar_color_var,
            values=[""] + [str(i) for i in range(1, 25)],
            state="readonly",
            width=10
        )
        color_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        # Delete Calendar Frame
        self.delete_calendar_frame = ttk.LabelFrame(scrollable, text="Delete Calendar", padding="10")

        row = 0
        ttk.Label(self.delete_calendar_frame, text="Calendar Owner:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.delete_calendar_owner_combo = ttk.Combobox(self.delete_calendar_frame, width=40)
        self.delete_calendar_owner_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        self.delete_calendar_frame.columnconfigure(1, weight=1)

        ttk.Button(
            self.delete_calendar_frame,
            text="Load Users",
            command=self.load_users_for_delete_calendar
        ).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Label(self.delete_calendar_frame, text="Calendar ID:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.delete_calendar_id_combo = ttk.Combobox(self.delete_calendar_frame, width=40)
        self.delete_calendar_id_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Button(
            self.delete_calendar_frame,
            text="Load Calendars",
            command=self.load_calendars_for_delete
        ).grid(row=row, column=2, padx=5, pady=5)

        # Execute button
        execute_frame = ttk.Frame(scrollable)
        execute_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(
            execute_frame,
            text="Execute",
            command=self.execute_manage_calendar_operation,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        # Progress frame
        self.manage_calendar_progress_frame = self.create_progress_frame(scrollable)

        # Initial state
        self.toggle_manage_calendar_operation()

    def toggle_manage_calendar_operation(self):
        """Toggle between create and delete frames."""
        if self.manage_calendar_operation_var.get() == "create":
            self.delete_calendar_frame.pack_forget()
            self.create_calendar_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            self.create_calendar_frame.pack_forget()
            self.delete_calendar_frame.pack(fill=tk.X, padx=10, pady=5)

    def load_users_for_create_calendar(self):
        """Load users for create calendar owner."""
        self.load_combobox_async(self.create_calendar_owner_combo, fetch_users, enable_fuzzy=True)

    def load_users_for_delete_calendar(self):
        """Load users for delete calendar owner."""
        self.load_combobox_async(self.delete_calendar_owner_combo, fetch_users, enable_fuzzy=True)

    def load_calendars_for_delete(self):
        """Load calendars for deletion."""
        owner_email = self.delete_calendar_owner_combo.get().strip()
        if not owner_email:
            messagebox.showwarning("Warning", "Please enter calendar owner email first")
            return

        def fetch_calendars():
            calendars = calendar_ops.get_user_calendars(owner_email)
            return [f"{cal['summary']} ({cal['id']})" for cal in calendars]

        self.load_combobox_async(self.delete_calendar_id_combo, fetch_calendars, enable_fuzzy=True)

    def execute_manage_calendar_operation(self):
        """Execute create or delete calendar operation."""
        operation = self.manage_calendar_operation_var.get()

        if operation == "create":
            # Get create values
            owner = self.create_calendar_owner_combo.get().strip()
            name = self.create_calendar_name_entry.get().strip()
            description = self.create_calendar_desc_entry.get().strip()
            color = self.create_calendar_color_var.get()

            # Validate
            if not owner:
                messagebox.showerror("Error", "Please enter calendar owner email")
                return
            if not name:
                messagebox.showerror("Error", "Please enter calendar name")
                return

            # Confirm
            if not messagebox.askyesno("Confirm", f"Create calendar '{name}' for {owner}?"):
                return

            # Clear and execute
            self.clear_results(self.manage_calendar_progress_frame)
            self.run_async_operation(
                self.manage_calendar_progress_frame,
                calendar_ops.create_calendar,
                owner,
                name,
                description,
                color if color else None
            )

        else:  # delete
            # Get delete values
            owner = self.delete_calendar_owner_combo.get().strip()
            calendar_input = self.delete_calendar_id_combo.get().strip()

            # Validate
            if not owner:
                messagebox.showerror("Error", "Please enter calendar owner email")
                return
            if not calendar_input:
                messagebox.showerror("Error", "Please enter calendar ID")
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
            self.run_async_operation(
                self.manage_calendar_progress_frame,
                calendar_ops.delete_calendar,
                owner,
                calendar_id
            )

    # ==================== TAB 3: VIEW CALENDAR INFO ====================

    def create_view_info_tab(self):
        """Create tab for viewing calendar information."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="View Calendar Info")

        # Create scrollable container
        container, scrollable = self.create_scrollable_frame(tab)
        container.pack(fill=tk.BOTH, expand=True)

        # Calendar Selection Frame
        selection_frame = ttk.LabelFrame(scrollable, text="Calendar Selection", padding="10")
        selection_frame.pack(fill=tk.X, padx=10, pady=5)

        row = 0
        ttk.Label(selection_frame, text="Calendar Owner:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.view_info_owner_combo = ttk.Combobox(selection_frame, width=40)
        self.view_info_owner_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        selection_frame.columnconfigure(1, weight=1)

        ttk.Button(
            selection_frame,
            text="Load Users",
            command=self.load_users_for_view_info
        ).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Label(selection_frame, text="Calendar ID:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.view_info_calendar_combo = ttk.Combobox(selection_frame, width=40)
        self.view_info_calendar_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Button(
            selection_frame,
            text="Load Calendars",
            command=self.load_calendars_for_view_info
        ).grid(row=row, column=2, padx=5, pady=5)

        # Buttons Frame
        buttons_frame = ttk.Frame(scrollable)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(
            buttons_frame,
            text="View Calendar Info",
            command=self.view_calendar_info,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame,
            text="View Permissions",
            command=self.view_calendar_permissions,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame,
            text="Clear",
            command=self.clear_view_info_results,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        # Results Frame
        results_frame = ttk.LabelFrame(scrollable, text="Calendar Information", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.view_info_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            height=20,
            font=('Courier', 10)
        )
        self.view_info_text.pack(fill=tk.BOTH, expand=True)

    def load_users_for_view_info(self):
        """Load users for view info."""
        self.load_combobox_async(self.view_info_owner_combo, fetch_users, enable_fuzzy=True)

    def load_calendars_for_view_info(self):
        """Load calendars for view info."""
        owner_email = self.view_info_owner_combo.get().strip()
        if not owner_email:
            messagebox.showwarning("Warning", "Please enter calendar owner email first")
            return

        def fetch_calendars():
            calendars = calendar_ops.get_user_calendars(owner_email)
            return [f"{cal['summary']} ({cal['id']})" for cal in calendars]

        self.load_combobox_async(self.view_info_calendar_combo, fetch_calendars, enable_fuzzy=True)

    def view_calendar_info(self):
        """View calendar information."""
        owner = self.view_info_owner_combo.get().strip()
        calendar_input = self.view_info_calendar_combo.get().strip()

        if not owner:
            messagebox.showerror("Error", "Please enter calendar owner email")
            return
        if not calendar_input:
            messagebox.showerror("Error", "Please enter calendar ID")
            return

        # Extract calendar ID
        if '(' in calendar_input and calendar_input.endswith(')'):
            calendar_id = calendar_input.split('(')[-1].rstrip(')')
        else:
            calendar_id = calendar_input

        # Clear results
        self.view_info_text.delete(1.0, tk.END)
        self.view_info_text.insert(tk.END, f"Retrieving information for calendar {calendar_id}...\n\n")

        # Run in thread
        def fetch_info():
            result_queue = queue.Queue()

            def run():
                try:
                    for progress in calendar_ops.get_calendar_info(calendar_id, owner):
                        result_queue.put(progress)
                    result_queue.put({'status': 'done'})
                except Exception as e:
                    result_queue.put({'status': 'error', 'message': str(e)})

            thread = threading.Thread(target=run, daemon=True)
            thread.start()

            def check_queue():
                try:
                    while True:
                        progress = result_queue.get_nowait()
                        if progress['status'] == 'done':
                            return
                        elif progress['status'] == 'success':
                            self.view_info_text.delete(1.0, tk.END)
                            self.view_info_text.insert(tk.END, progress.get('data', ''))
                        elif progress['status'] == 'error':
                            self.view_info_text.insert(tk.END, f"\nError: {progress['message']}\n")
                except queue.Empty:
                    self.after(100, check_queue)

            check_queue()

        fetch_info()

    def view_calendar_permissions(self):
        """View calendar permissions."""
        calendar_input = self.view_info_calendar_combo.get().strip()

        if not calendar_input:
            messagebox.showerror("Error", "Please enter calendar ID")
            return

        # Extract calendar ID
        if '(' in calendar_input and calendar_input.endswith(')'):
            calendar_id = calendar_input.split('(')[-1].rstrip(')')
        else:
            calendar_id = calendar_input

        # Clear results
        self.view_info_text.delete(1.0, tk.END)
        self.view_info_text.insert(tk.END, f"Retrieving permissions for calendar {calendar_id}...\n\n")

        # Run in thread
        def fetch_acl():
            result_queue = queue.Queue()

            def run():
                try:
                    for progress in calendar_ops.get_calendar_acl(calendar_id):
                        result_queue.put(progress)
                    result_queue.put({'status': 'done'})
                except Exception as e:
                    result_queue.put({'status': 'error', 'message': str(e)})

            thread = threading.Thread(target=run, daemon=True)
            thread.start()

            def check_queue():
                try:
                    while True:
                        progress = result_queue.get_nowait()
                        if progress['status'] == 'done':
                            return
                        elif progress['status'] == 'success':
                            self.view_info_text.delete(1.0, tk.END)
                            self.view_info_text.insert(tk.END, progress.get('data', ''))
                        elif progress['status'] == 'error':
                            self.view_info_text.insert(tk.END, f"\nError: {progress['message']}\n")
                except queue.Empty:
                    self.after(100, check_queue)

            check_queue()

        fetch_acl()

    def clear_view_info_results(self):
        """Clear view info results."""
        self.view_info_text.delete(1.0, tk.END)

    # ==================== TAB 4: IMPORT/EXPORT ====================

    def create_import_export_tab(self):
        """Create tab for importing/exporting calendar data."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Import/Export")

        # Create scrollable container
        container, scrollable = self.create_scrollable_frame(tab)
        container.pack(fill=tk.BOTH, expand=True)

        # Import Section
        import_frame = ttk.LabelFrame(scrollable, text="Import Calendar (.ics file)", padding="10")
        import_frame.pack(fill=tk.X, padx=10, pady=5)

        row = 0
        ttk.Label(import_frame, text="Calendar Owner:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.import_owner_combo = ttk.Combobox(import_frame, width=40)
        self.import_owner_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        import_frame.columnconfigure(1, weight=1)

        ttk.Button(
            import_frame,
            text="Load Users",
            command=self.load_users_for_import
        ).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Label(import_frame, text="Target Calendar:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.import_calendar_combo = ttk.Combobox(import_frame, width=40)
        self.import_calendar_combo.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Button(
            import_frame,
            text="Load Calendars",
            command=self.load_calendars_for_import
        ).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Label(import_frame, text=".ics File:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.import_file_entry = ttk.Entry(import_frame, width=40)
        self.import_file_entry.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Button(
            import_frame,
            text="Browse...",
            command=self.browse_import_file
        ).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Button(
            import_frame,
            text="Import",
            command=self.execute_import,
            width=15
        ).grid(row=row, column=1, sticky=tk.W, padx=5, pady=10)

        # Export Section
        export_frame = ttk.LabelFrame(scrollable, text="Export Calendar Events", padding="10")
        export_frame.pack(fill=tk.X, padx=10, pady=5)

        row = 0
        ttk.Label(export_frame, text="Calendar ID:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_calendar_entry = ttk.Entry(export_frame, width=40)
        self.export_calendar_entry.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        export_frame.columnconfigure(1, weight=1)

        row += 1
        ttk.Label(export_frame, text="Start Date:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_start_date_entry = ttk.Entry(export_frame, width=20)
        self.export_start_date_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        # Set default to 30 days ago
        default_start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.export_start_date_entry.insert(0, default_start)

        ttk.Label(export_frame, text="(YYYY-MM-DD)", font=('Arial', 9), foreground='gray').grid(
            row=row, column=2, sticky=tk.W, padx=5, pady=5
        )

        row += 1
        ttk.Label(export_frame, text="End Date:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_end_date_entry = ttk.Entry(export_frame, width=20)
        self.export_end_date_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        # Set default to 30 days from now
        default_end = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.export_end_date_entry.insert(0, default_end)

        ttk.Label(export_frame, text="(YYYY-MM-DD)", font=('Arial', 9), foreground='gray').grid(
            row=row, column=2, sticky=tk.W, padx=5, pady=5
        )

        row += 1
        ttk.Label(export_frame, text="Output File:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.export_file_entry = ttk.Entry(export_frame, width=40)
        self.export_file_entry.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Button(
            export_frame,
            text="Browse...",
            command=self.browse_export_file
        ).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Button(
            export_frame,
            text="Export",
            command=self.execute_export,
            width=15
        ).grid(row=row, column=1, sticky=tk.W, padx=5, pady=10)

        # Progress frame
        self.import_export_progress_frame = self.create_progress_frame(scrollable)

    def load_users_for_import(self):
        """Load users for import."""
        self.load_combobox_async(self.import_owner_combo, fetch_users, enable_fuzzy=True)

    def load_calendars_for_import(self):
        """Load calendars for import."""
        owner_email = self.import_owner_combo.get().strip()
        if not owner_email:
            messagebox.showwarning("Warning", "Please enter calendar owner email first")
            return

        def fetch_calendars():
            calendars = calendar_ops.get_user_calendars(owner_email)
            return [f"{cal['summary']} ({cal['id']})" for cal in calendars]

        self.load_combobox_async(self.import_calendar_combo, fetch_calendars, enable_fuzzy=True)

    def browse_import_file(self):
        """Browse for import .ics file."""
        file_path = filedialog.askopenfilename(
            title="Select .ics File",
            filetypes=[("iCalendar files", "*.ics"), ("All files", "*.*")]
        )
        if file_path:
            self.import_file_entry.delete(0, tk.END)
            self.import_file_entry.insert(0, file_path)

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

    def execute_import(self):
        """Execute calendar import."""
        owner = self.import_owner_combo.get().strip()
        calendar_input = self.import_calendar_combo.get().strip()
        ics_file = self.import_file_entry.get().strip()

        # Validate
        if not owner:
            messagebox.showerror("Error", "Please enter calendar owner email")
            return
        if not calendar_input:
            messagebox.showerror("Error", "Please select target calendar")
            return
        if not ics_file:
            messagebox.showerror("Error", "Please select .ics file")
            return

        if not os.path.exists(ics_file):
            messagebox.showerror("Error", f"File not found: {ics_file}")
            return

        # Extract calendar ID
        if '(' in calendar_input and calendar_input.endswith(')'):
            calendar_id = calendar_input.split('(')[-1].rstrip(')')
        else:
            calendar_id = calendar_input

        # Confirm
        if not messagebox.askyesno("Confirm", f"Import events from {os.path.basename(ics_file)} to calendar {calendar_id}?"):
            return

        # Clear and execute
        self.clear_results(self.import_export_progress_frame)
        self.run_async_operation(
            self.import_export_progress_frame,
            calendar_ops.import_calendar,
            owner,
            calendar_id,
            ics_file
        )

    def execute_export(self):
        """Execute calendar export."""
        calendar_id = self.export_calendar_entry.get().strip()
        start_date = self.export_start_date_entry.get().strip()
        end_date = self.export_end_date_entry.get().strip()
        output_file = self.export_file_entry.get().strip()

        # Validate
        if not calendar_id:
            messagebox.showerror("Error", "Please enter calendar ID")
            return
        if not start_date or not end_date:
            messagebox.showerror("Error", "Please enter date range")
            return
        if not output_file:
            messagebox.showerror("Error", "Please select output file")
            return

        # Validate date format (basic)
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
        self.run_async_operation(
            self.import_export_progress_frame,
            calendar_ops.export_calendar_events,
            calendar_id,
            start_date,
            end_date,
            output_file
        )
