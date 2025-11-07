"""
User Management Window for GAM Admin Tool.

Provides a tabbed interface for all user-related operations including
creating users, deleting, suspending, resetting passwords, updating info,
managing organizational units, and managing aliases.

Inherits from BaseOperationWindow for common functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import csv

from gui.base_operation_window import BaseOperationWindow
from modules import users as users_module
from utils.csv_handler import validate_csv


class UsersWindow(BaseOperationWindow):
    """
    User Management window with tabbed interface.

    Provides 7 tabs for different user operations:
    - Create Users
    - Delete Users
    - Suspend/Restore Users
    - Reset Passwords
    - Update User Info
    - Manage Organizational Units
    - Manage Aliases
    """

    def __init__(self, parent):
        """
        Initialize the User Management window.

        Args:
            parent: The parent tkinter widget
        """
        super().__init__(parent, "User Management", "900x750", (800, 600))

    def create_operation_tabs(self):
        """Create all user management operation tabs."""
        self.create_create_users_tab()
        self.create_delete_users_tab()
        self.create_suspend_restore_tab()
        self.create_reset_password_tab()
        self.create_update_info_tab()
        self.create_manage_ou_tab()
        self.create_manage_aliases_tab()

    # ==================== TAB 1: CREATE USERS ====================

    def create_create_users_tab(self):
        """Create the Create Users tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Create Users")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Create new user accounts. Choose single user or CSV for bulk creation.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Mode selection
        mode_frame = ttk.Frame(tab)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.create_users_mode = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="Single User",
            variable=self.create_users_mode,
            value="single",
            command=self.toggle_create_users_mode
        ).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(
            mode_frame,
            text="CSV Bulk Import",
            variable=self.create_users_mode,
            value="csv",
            command=self.toggle_create_users_mode
        ).pack(side=tk.LEFT)

        # Container for mode-specific content (keeps layout stable)
        mode_container = ttk.Frame(tab)
        mode_container.pack(fill=tk.X, pady=(0, 10))

        # Single user input frame
        self.create_users_single_frame = ttk.LabelFrame(mode_container, text="User Details", padding="10")

        # Email (required)
        ttk.Label(self.create_users_single_frame, text="Email*:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.create_user_email = ttk.Entry(self.create_users_single_frame, width=40)
        self.create_user_email.grid(row=0, column=1, sticky=tk.EW, pady=5)

        # First Name (required)
        ttk.Label(self.create_users_single_frame, text="First Name*:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.create_user_firstname = ttk.Entry(self.create_users_single_frame, width=40)
        self.create_user_firstname.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # Last Name (required)
        ttk.Label(self.create_users_single_frame, text="Last Name*:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.create_user_lastname = ttk.Entry(self.create_users_single_frame, width=40)
        self.create_user_lastname.grid(row=2, column=1, sticky=tk.EW, pady=5)

        # Password (required)
        ttk.Label(self.create_users_single_frame, text="Password*:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.create_user_password = ttk.Entry(self.create_users_single_frame, width=40, show="*")
        self.create_user_password.grid(row=3, column=1, sticky=tk.EW, pady=5)

        # Org Unit (optional)
        ttk.Label(self.create_users_single_frame, text="Org Unit:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.create_user_orgunit = ttk.Entry(self.create_users_single_frame, width=40)
        self.create_user_orgunit.insert(0, "/")
        self.create_user_orgunit.grid(row=4, column=1, sticky=tk.EW, pady=5)

        # Title (optional)
        ttk.Label(self.create_users_single_frame, text="Title:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.create_user_title = ttk.Entry(self.create_users_single_frame, width=40)
        self.create_user_title.grid(row=5, column=1, sticky=tk.EW, pady=5)

        # Phone (optional)
        ttk.Label(self.create_users_single_frame, text="Phone:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.create_user_phone = ttk.Entry(self.create_users_single_frame, width=40)
        self.create_user_phone.grid(row=6, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.create_users_single_frame, text="* Required fields", font=('Arial', 8), foreground='gray').grid(row=7, column=1, sticky=tk.W, pady=(5, 0))

        self.create_users_single_frame.grid_columnconfigure(1, weight=1)

        # CSV selection frame
        self.create_users_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.create_users_csv_frame, text="CSV Format: email,firstName,lastName,password,orgUnit,title,phone").pack(anchor=tk.W)
        ttk.Label(self.create_users_csv_frame, text="Required: email, firstName, lastName, password. Optional: orgUnit (default /), title, phone").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(self.create_users_csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.create_users_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.create_users_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_for_create_users()
        ).pack(side=tk.LEFT)

        # Progress frame
        self.create_users_progress = self.create_progress_frame(tab)
        self.create_users_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Create User(s)",
            command=self.execute_create_users,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.create_users_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.create_users_dry_run
        ).pack(side=tk.LEFT)

        # Initial toggle
        self.toggle_create_users_mode()

    def toggle_create_users_mode(self):
        """Toggle between single and CSV mode for create users."""
        if self.create_users_mode.get() == "single":
            self.create_users_csv_frame.pack_forget()
            self.create_users_single_frame.pack(fill=tk.X, expand=True)
        else:
            self.create_users_single_frame.pack_forget()
            self.create_users_csv_frame.pack(fill=tk.X, expand=True)

    def browse_csv_for_create_users(self):
        """Browse for CSV file for create users."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.create_users_csv_entry.delete(0, tk.END)
            self.create_users_csv_entry.insert(0, file_path)

    def execute_create_users(self):
        """Execute create users operation."""
        mode = self.create_users_mode.get()

        if mode == "single":
            # Single user mode
            email = self.create_user_email.get().strip()
            firstname = self.create_user_firstname.get().strip()
            lastname = self.create_user_lastname.get().strip()
            password = self.create_user_password.get().strip()
            orgunit = self.create_user_orgunit.get().strip() or "/"
            title = self.create_user_title.get().strip()
            phone = self.create_user_phone.get().strip()

            # Validate required fields
            if not email:
                messagebox.showerror("Validation Error", "Email is required.")
                return
            if not firstname:
                messagebox.showerror("Validation Error", "First Name is required.")
                return
            if not lastname:
                messagebox.showerror("Validation Error", "Last Name is required.")
                return
            if not password:
                messagebox.showerror("Validation Error", "Password is required.")
                return

            # Create user data dict
            users_data = [{
                'email': email,
                'firstName': firstname,
                'lastName': lastname,
                'password': password,
                'orgUnit': orgunit,
                'title': title,
                'phone': phone
            }]

        else:
            # CSV mode
            csv_file = self.create_users_csv_entry.get().strip()
            if not csv_file:
                messagebox.showerror("Validation Error", "Please select a CSV file.")
                return

            # Read CSV
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    users_data = list(reader)

                if not users_data:
                    messagebox.showerror("Error", "CSV file is empty.")
                    return

                # Validate required fields
                required = ['email', 'firstName', 'lastName', 'password']
                for user_data in users_data:
                    for field in required:
                        if field not in user_data or not user_data[field]:
                            messagebox.showerror("Validation Error", f"Missing required field '{field}' in CSV.")
                            return

                # Confirm bulk operation
                if not self.confirm_bulk_operation(len(users_data), "create users"):
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
                return

        # Execute
        dry_run = self.create_users_dry_run.get()
        self.run_operation(
            users_module.create_user,
            self.create_users_progress,
            users_data,
            dry_run=dry_run
        )

    # ==================== TAB 2: DELETE USERS ====================

    def create_delete_users_tab(self):
        """Create the Delete Users tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Delete Users")

        # Warning
        warning = ttk.Label(
            tab,
            text="⚠ WARNING: This permanently deletes user accounts. This action cannot be undone!",
            foreground='red',
            font=('Arial', 10, 'bold')
        )
        warning.pack(pady=(0, 10), anchor=tk.W)

        # Target selection (simplified - no "All Users" or "Group" for safety)
        self.delete_users_target = self.create_single_user_target_selection_frame(tab, 'delete_users')
        self.delete_users_target.pack(fill=tk.X, pady=(0, 10))

        # Progress frame
        self.delete_users_progress = self.create_progress_frame(tab)
        self.delete_users_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Delete Users",
            command=self.execute_delete_users,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.delete_users_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.delete_users_dry_run
        ).pack(side=tk.LEFT)

    def execute_delete_users(self):
        """Execute delete users operation."""
        users = self.get_target_users('delete_users')
        if users is None:
            return

        # Extra confirmation for delete
        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you absolutely sure you want to DELETE {len(users)} user(s)?\n\n"
            "This action CANNOT be undone!",
            icon='warning'
        )
        if not response:
            return

        dry_run = self.delete_users_dry_run.get()
        self.run_operation(
            users_module.delete_user,
            self.delete_users_progress,
            users,
            dry_run=dry_run
        )

    # ==================== TAB 3: SUSPEND/RESTORE USERS ====================

    def create_suspend_restore_tab(self):
        """Create the Suspend/Restore Users tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Suspend/Restore")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Suspend or restore user accounts. Suspended users cannot sign in.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Action selection
        action_frame = ttk.LabelFrame(tab, text="Action", padding="10")
        action_frame.pack(fill=tk.X, pady=(0, 10))

        self.suspend_restore_action = tk.StringVar(value="suspend")
        ttk.Radiobutton(
            action_frame,
            text="Suspend Users",
            variable=self.suspend_restore_action,
            value="suspend"
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            action_frame,
            text="Restore Users",
            variable=self.suspend_restore_action,
            value="restore"
        ).pack(side=tk.LEFT)

        # Target selection (simplified - no "All Users" or "Group" for safety)
        self.suspend_restore_target = self.create_single_user_target_selection_frame(tab, 'suspend_restore')
        self.suspend_restore_target.pack(fill=tk.X, pady=(0, 10))

        # Progress frame
        self.suspend_restore_progress = self.create_progress_frame(tab)
        self.suspend_restore_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Execute",
            command=self.execute_suspend_restore,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.suspend_restore_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.suspend_restore_dry_run
        ).pack(side=tk.LEFT)

    def execute_suspend_restore(self):
        """Execute suspend/restore operation."""
        users = self.get_target_users('suspend_restore')
        if users is None:
            return

        action = self.suspend_restore_action.get()
        dry_run = self.suspend_restore_dry_run.get()

        if action == 'suspend':
            self.run_operation(
                users_module.suspend_user,
                self.suspend_restore_progress,
                users,
                dry_run=dry_run
            )
        else:
            self.run_operation(
                users_module.restore_user,
                self.suspend_restore_progress,
                users,
                dry_run=dry_run
            )

    # ==================== TAB 4: RESET PASSWORDS ====================

    def create_reset_password_tab(self):
        """Create the Reset Password tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Reset Passwords")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Reset user passwords. Choose single user or CSV for bulk resets.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Mode selection
        mode_frame = ttk.Frame(tab)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.reset_password_mode = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="Single User",
            variable=self.reset_password_mode,
            value="single",
            command=self.toggle_reset_password_mode
        ).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(
            mode_frame,
            text="CSV Bulk Import",
            variable=self.reset_password_mode,
            value="csv",
            command=self.toggle_reset_password_mode
        ).pack(side=tk.LEFT)

        # Container for mode-specific content
        mode_container = ttk.Frame(tab)
        mode_container.pack(fill=tk.X, pady=(0, 10))

        # Single user input frame
        self.reset_password_single_frame = ttk.LabelFrame(mode_container, text="Password Reset", padding="10")

        ttk.Label(self.reset_password_single_frame, text="User Email*:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.reset_password_email = ttk.Entry(self.reset_password_single_frame, width=40)
        self.reset_password_email.grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.reset_password_single_frame, text="New Password*:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.reset_password_new = ttk.Entry(self.reset_password_single_frame, width=40, show="*")
        self.reset_password_new.grid(row=1, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.reset_password_single_frame, text="* Required fields", font=('Arial', 8), foreground='gray').grid(row=2, column=1, sticky=tk.W, pady=(5, 0))

        self.reset_password_single_frame.grid_columnconfigure(1, weight=1)

        # CSV selection frame
        self.reset_password_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.reset_password_csv_frame, text="CSV Format: email,password").pack(anchor=tk.W, pady=(0, 10))

        csv_input_frame = ttk.Frame(self.reset_password_csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.reset_password_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.reset_password_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_for_reset_password()
        ).pack(side=tk.LEFT)

        # Progress frame
        self.reset_password_progress = self.create_progress_frame(tab)
        self.reset_password_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Reset Password(s)",
            command=self.execute_reset_password,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.reset_password_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.reset_password_dry_run
        ).pack(side=tk.LEFT)

        # Initial toggle
        self.toggle_reset_password_mode()

    def toggle_reset_password_mode(self):
        """Toggle between single and CSV mode for reset password."""
        if self.reset_password_mode.get() == "single":
            self.reset_password_csv_frame.pack_forget()
            self.reset_password_single_frame.pack(fill=tk.X, expand=True)
        else:
            self.reset_password_single_frame.pack_forget()
            self.reset_password_csv_frame.pack(fill=tk.X, expand=True)

    def browse_csv_for_reset_password(self):
        """Browse for CSV file for reset password."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.reset_password_csv_entry.delete(0, tk.END)
            self.reset_password_csv_entry.insert(0, file_path)

    def execute_reset_password(self):
        """Execute reset password operation."""
        mode = self.reset_password_mode.get()

        if mode == "single":
            # Single user mode
            email = self.reset_password_email.get().strip()
            password = self.reset_password_new.get().strip()

            # Validate required fields
            if not email:
                messagebox.showerror("Validation Error", "User email is required.")
                return
            if not password:
                messagebox.showerror("Validation Error", "New password is required.")
                return

            # Create user data dict
            users_data = [{
                'email': email,
                'password': password
            }]

        else:
            # CSV mode
            csv_file = self.reset_password_csv_entry.get().strip()
            if not csv_file:
                messagebox.showerror("Validation Error", "Please select a CSV file.")
                return

            # Read CSV
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
                    if 'password' not in user_data or not user_data['password']:
                        messagebox.showerror("Validation Error", "Missing 'password' field in CSV.")
                        return

                # Confirm
                if not self.confirm_bulk_operation(len(users_data), "reset passwords"):
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
                return

        # Execute
        dry_run = self.reset_password_dry_run.get()
        self.run_operation(
            users_module.reset_password,
            self.reset_password_progress,
            users_data,
            dry_run=dry_run
        )

    # ==================== TAB 5: UPDATE USER INFO ====================

    def create_update_info_tab(self):
        """Create the Update User Info tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Update Info")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Update user information. Choose single user or CSV for bulk updates.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Mode selection
        mode_frame = ttk.Frame(tab)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.update_info_mode = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="Single User",
            variable=self.update_info_mode,
            value="single",
            command=self.toggle_update_info_mode
        ).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(
            mode_frame,
            text="CSV Bulk Import",
            variable=self.update_info_mode,
            value="csv",
            command=self.toggle_update_info_mode
        ).pack(side=tk.LEFT)

        # Container for mode-specific content
        mode_container = ttk.Frame(tab)
        mode_container.pack(fill=tk.X, pady=(0, 10))

        # Single user input frame
        self.update_info_single_frame = ttk.LabelFrame(mode_container, text="Update User Details", padding="10")

        ttk.Label(self.update_info_single_frame, text="User Email*:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_email = ttk.Entry(self.update_info_single_frame, width=40)
        self.update_info_email.grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.update_info_single_frame, text="First Name:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_firstname = ttk.Entry(self.update_info_single_frame, width=40)
        self.update_info_firstname.grid(row=1, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.update_info_single_frame, text="Last Name:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_lastname = ttk.Entry(self.update_info_single_frame, width=40)
        self.update_info_lastname.grid(row=2, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.update_info_single_frame, text="Title:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_title = ttk.Entry(self.update_info_single_frame, width=40)
        self.update_info_title.grid(row=3, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.update_info_single_frame, text="Phone:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_phone = ttk.Entry(self.update_info_single_frame, width=40)
        self.update_info_phone.grid(row=4, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.update_info_single_frame, text="Address:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_address = ttk.Entry(self.update_info_single_frame, width=40)
        self.update_info_address.grid(row=5, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.update_info_single_frame, text="* Required. Leave other fields blank to keep unchanged.",
                 font=('Arial', 8), foreground='gray').grid(row=6, column=1, sticky=tk.W, pady=(5, 0))

        self.update_info_single_frame.grid_columnconfigure(1, weight=1)

        # CSV selection frame
        self.update_info_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.update_info_csv_frame, text="CSV Format: email,firstName,lastName,title,phone,address").pack(anchor=tk.W)
        ttk.Label(self.update_info_csv_frame, text="Required: email. Optional: firstName, lastName, title, phone, address").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(self.update_info_csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.update_info_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.update_info_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_for_update_info()
        ).pack(side=tk.LEFT)

        # Progress frame
        self.update_info_progress = self.create_progress_frame(tab)
        self.update_info_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Update User Info",
            command=self.execute_update_info,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.update_info_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.update_info_dry_run
        ).pack(side=tk.LEFT)

        # Initial toggle
        self.toggle_update_info_mode()

    def toggle_update_info_mode(self):
        """Toggle between single and CSV mode for update info."""
        if self.update_info_mode.get() == "single":
            self.update_info_csv_frame.pack_forget()
            self.update_info_single_frame.pack(fill=tk.X, expand=True)
        else:
            self.update_info_single_frame.pack_forget()
            self.update_info_csv_frame.pack(fill=tk.X, expand=True)

    def browse_csv_for_update_info(self):
        """Browse for CSV file for update info."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.update_info_csv_entry.delete(0, tk.END)
            self.update_info_csv_entry.insert(0, file_path)

    def execute_update_info(self):
        """Execute update user info operation."""
        mode = self.update_info_mode.get()

        if mode == "single":
            # Single user mode
            email = self.update_info_email.get().strip()

            if not email:
                messagebox.showerror("Validation Error", "User email is required.")
                return

            # Build user data dict with only non-empty fields
            user_data = {'email': email}

            firstname = self.update_info_firstname.get().strip()
            if firstname:
                user_data['firstName'] = firstname

            lastname = self.update_info_lastname.get().strip()
            if lastname:
                user_data['lastName'] = lastname

            title = self.update_info_title.get().strip()
            if title:
                user_data['title'] = title

            phone = self.update_info_phone.get().strip()
            if phone:
                user_data['phone'] = phone

            address = self.update_info_address.get().strip()
            if address:
                user_data['address'] = address

            users_data = [user_data]

        else:
            # CSV mode
            csv_file = self.update_info_csv_entry.get().strip()
            if not csv_file:
                messagebox.showerror("Validation Error", "Please select a CSV file.")
                return

            # Read CSV
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    users_data = list(reader)

                if not users_data:
                    messagebox.showerror("Error", "CSV file is empty.")
                    return

                # Validate email field
                for user_data in users_data:
                    if 'email' not in user_data or not user_data['email']:
                        messagebox.showerror("Validation Error", "Missing 'email' field in CSV.")
                        return

                # Confirm
                if not self.confirm_bulk_operation(len(users_data), "update user info"):
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
                return

        # Execute
        dry_run = self.update_info_dry_run.get()
        self.run_operation(
            users_module.update_user_info,
            self.update_info_progress,
            users_data,
            dry_run=dry_run
        )

    # ==================== TAB 6: MANAGE ORGANIZATIONAL UNITS ====================

    def create_manage_ou_tab(self):
        """Create the Manage Organizational Units tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage OUs")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Move users to different organizational units. Use CSV for bulk moves.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # CSV selection frame
        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(csv_frame, text="CSV Format: email,orgUnit").pack(anchor=tk.W)
        ttk.Label(csv_frame, text="Example: john@domain.com,/Staff/Engineering").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.manage_ou_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.manage_ou_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_for_manage_ou()
        ).pack(side=tk.LEFT)

        # Progress frame
        self.manage_ou_progress = self.create_progress_frame(tab)
        self.manage_ou_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Move Users",
            command=self.execute_manage_ou,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.manage_ou_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.manage_ou_dry_run
        ).pack(side=tk.LEFT)

    def browse_csv_for_manage_ou(self):
        """Browse for CSV file for manage OU."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.manage_ou_csv_entry.delete(0, tk.END)
            self.manage_ou_csv_entry.insert(0, file_path)

    def execute_manage_ou(self):
        """Execute manage OU operation."""
        csv_file = self.manage_ou_csv_entry.get().strip()
        if not csv_file:
            messagebox.showerror("Validation Error", "Please select a CSV file.")
            return

        # Read CSV
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
                if 'orgUnit' not in user_data or not user_data['orgUnit']:
                    messagebox.showerror("Validation Error", "Missing 'orgUnit' field in CSV.")
                    return

            # Confirm
            if not self.confirm_bulk_operation(len(users_data), "move users"):
                return

            # Execute
            dry_run = self.manage_ou_dry_run.get()
            self.run_operation(
                users_module.change_org_unit,
                self.manage_ou_progress,
                users_data,
                dry_run=dry_run
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")

    # ==================== TAB 7: MANAGE ALIASES ====================

    def create_manage_aliases_tab(self):
        """Create the Manage Aliases tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Aliases")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Add or remove email aliases. Use CSV for bulk alias management.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Action selection
        action_frame = ttk.LabelFrame(tab, text="Action", padding="10")
        action_frame.pack(fill=tk.X, pady=(0, 10))

        self.manage_aliases_action = tk.StringVar(value="add")
        ttk.Radiobutton(
            action_frame,
            text="Add Aliases",
            variable=self.manage_aliases_action,
            value="add"
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            action_frame,
            text="Remove Aliases",
            variable=self.manage_aliases_action,
            value="remove"
        ).pack(side=tk.LEFT)

        # CSV selection frame
        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(csv_frame, text="For Add: email,alias (where email is primary, alias is the new alias to add)").pack(anchor=tk.W)
        ttk.Label(csv_frame, text="For Remove: Just list one alias per line (header: alias)").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.manage_aliases_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.manage_aliases_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_for_manage_aliases()
        ).pack(side=tk.LEFT)

        # Progress frame
        self.manage_aliases_progress = self.create_progress_frame(tab)
        self.manage_aliases_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Execute",
            command=self.execute_manage_aliases,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.manage_aliases_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.manage_aliases_dry_run
        ).pack(side=tk.LEFT)

    def browse_csv_for_manage_aliases(self):
        """Browse for CSV file for manage aliases."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.manage_aliases_csv_entry.delete(0, tk.END)
            self.manage_aliases_csv_entry.insert(0, file_path)

    def execute_manage_aliases(self):
        """Execute manage aliases operation."""
        csv_file = self.manage_aliases_csv_entry.get().strip()
        if not csv_file:
            messagebox.showerror("Validation Error", "Please select a CSV file.")
            return

        action = self.manage_aliases_action.get()
        dry_run = self.manage_aliases_dry_run.get()

        # Read CSV
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)

            if not data:
                messagebox.showerror("Error", "CSV file is empty.")
                return

            if action == 'add':
                # Validate add format
                for row in data:
                    if 'email' not in row or not row['email']:
                        messagebox.showerror("Validation Error", "Missing 'email' field in CSV for add action.")
                        return
                    if 'alias' not in row or not row['alias']:
                        messagebox.showerror("Validation Error", "Missing 'alias' field in CSV for add action.")
                        return

                # Confirm
                if not self.confirm_bulk_operation(len(data), "add aliases"):
                    return

                # Execute
                self.run_operation(
                    users_module.add_alias,
                    self.manage_aliases_progress,
                    data,
                    dry_run=dry_run
                )
            else:
                # Remove - just need list of aliases
                if 'alias' not in data[0]:
                    messagebox.showerror("Validation Error", "Missing 'alias' field in CSV for remove action.")
                    return

                aliases = [row['alias'] for row in data if row.get('alias')]

                # Confirm
                if not self.confirm_bulk_operation(len(aliases), "remove aliases"):
                    return

                # Execute
                self.run_operation(
                    users_module.remove_alias,
                    self.manage_aliases_progress,
                    aliases,
                    dry_run=dry_run
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
