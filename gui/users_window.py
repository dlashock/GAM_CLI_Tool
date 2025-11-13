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
from gui.password_generator import PasswordGeneratorDialog
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
        self.create_mfa_tab()

        # Auto-load comboboxes on window initialization
        self.after(100, self.initialize_comboboxes)

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

        password_frame = ttk.Frame(self.create_users_single_frame)
        password_frame.grid(row=3, column=1, sticky=tk.EW, pady=5)

        self.create_user_password = ttk.Entry(password_frame, width=30, show="*")
        self.create_user_password.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            password_frame,
            text="Generate",
            command=lambda: self.open_password_generator(self.create_user_password),
            width=10
        ).pack(side=tk.LEFT)

        # Org Unit (optional) - with dropdown
        ttk.Label(self.create_users_single_frame, text="Org Unit:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=(0, 5))

        orgunit_frame = ttk.Frame(self.create_users_single_frame)
        orgunit_frame.grid(row=4, column=1, sticky=tk.EW, pady=5)

        self.create_user_orgunit = ttk.Combobox(orgunit_frame, values=["/"])
        self.create_user_orgunit.set("/")
        self.create_user_orgunit.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            orgunit_frame,
            text="Load OUs",
            command=self.load_org_units_for_create_user
        ).pack(side=tk.LEFT)

        ttk.Label(self.create_users_single_frame, text="* Required fields", font=('Arial', 8), foreground='gray').grid(row=5, column=1, sticky=tk.W, pady=(5, 0))

        self.create_users_single_frame.grid_columnconfigure(1, weight=1)

        # CSV selection frame
        self.create_users_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.create_users_csv_frame, text="CSV Format: email,firstName,lastName,password,orgUnit").pack(anchor=tk.W)
        ttk.Label(self.create_users_csv_frame, text="Required: email, firstName, lastName, password. Optional: orgUnit (default /)").pack(anchor=tk.W, pady=(5, 10))

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

    def load_org_units_for_create_user(self):
        """Load organizational units into combobox for create user."""
        # Set loading indicator
        self.create_user_orgunit['values'] = ["Loading..."]
        self.create_user_orgunit.set("Loading...")

        def fetch_and_populate():
            from utils.workspace_data import fetch_org_units
            orgs = fetch_org_units()
            if orgs:
                # Update combobox in main thread
                self.after(0, lambda: self.create_user_orgunit.configure(values=sorted(orgs)))
                self.after(0, lambda: self.create_user_orgunit.set("/"))
            else:
                # Fallback to root if no OUs found
                self.after(0, lambda: self.create_user_orgunit.configure(values=["/", "No OUs found"]))
                self.after(0, lambda: self.create_user_orgunit.set("/"))

        # Run in background thread
        import threading
        threading.Thread(target=fetch_and_populate, daemon=True).start()

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
                'orgUnit': orgunit
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

        # Prepare success callback to clear fields (only for single mode and not dry run)
        on_success = None
        if mode == "single" and not dry_run:
            on_success = lambda: self.clear_fields(
                self.create_user_email,
                self.create_user_firstname,
                self.create_user_lastname,
                self.create_user_password
            )

        self.run_operation(
            users_module.create_user,
            self.create_users_progress,
            users_data,
            dry_run=dry_run,
            on_success=on_success
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
        self.delete_users_target = self.create_combobox_user_target_selection_frame(tab, 'delete_users')
        self.delete_users_target.pack(fill=tk.X, pady=(0, 10))

        # Drive transfer option
        drive_frame = ttk.LabelFrame(tab, text="Drive Ownership Transfer (Optional)", padding="10")
        drive_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(drive_frame, text="Transfer Drive files to:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))

        target_email_frame = ttk.Frame(drive_frame)
        target_email_frame.grid(row=0, column=1, sticky=tk.EW, pady=5)

        self.delete_drive_target = ttk.Combobox(target_email_frame)
        self.delete_drive_target.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            target_email_frame,
            text="Load Users",
            command=self.load_users_for_delete_drive
        ).pack(side=tk.LEFT)

        ttk.Label(drive_frame, text="(Leave blank to skip Drive transfer)", font=('Arial', 8), foreground='gray').grid(row=1, column=1, sticky=tk.W)

        drive_frame.grid_columnconfigure(1, weight=1)

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

    def load_users_for_delete_drive(self):
        """Load users for the delete Drive transfer dropdown."""
        from utils.workspace_data import fetch_users
        self.load_combobox_async(self.delete_drive_target, fetch_users, enable_fuzzy=True)

    def execute_delete_users(self):
        """Execute delete users operation."""
        users = self.get_target_users('delete_users')
        if users is None:
            return

        # Get Drive transfer target if specified
        drive_target = self.delete_drive_target.get().strip()

        # Extra confirmation for delete
        confirm_msg = f"Are you absolutely sure you want to DELETE {len(users)} user(s)?\n\n"
        if drive_target:
            confirm_msg += f"Drive files will be transferred to: {drive_target}\n\n"
        confirm_msg += "This action CANNOT be undone!"

        response = messagebox.askyesno(
            "Confirm Deletion",
            confirm_msg,
            icon='warning'
        )
        if not response:
            return

        dry_run = self.delete_users_dry_run.get()
        self.run_operation(
            users_module.delete_user,
            self.delete_users_progress,
            users,
            dry_run=dry_run,
            drive_target=drive_target if drive_target else None
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
        self.suspend_restore_target = self.create_combobox_user_target_selection_frame(tab, 'suspend_restore')
        self.suspend_restore_target.pack(fill=tk.X, pady=(0, 10))

        # Suspend options frame (only visible when suspending)
        self.suspend_options_frame = ttk.LabelFrame(tab, text="Suspend Options (Optional)", padding="10")
        self.suspend_options_frame.pack(fill=tk.X, pady=(0, 10))

        # Drive transfer option
        ttk.Label(self.suspend_options_frame, text="Transfer Drive files to:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))

        drive_email_frame = ttk.Frame(self.suspend_options_frame)
        drive_email_frame.grid(row=0, column=1, sticky=tk.EW, pady=5)

        self.suspend_drive_target = ttk.Combobox(drive_email_frame)
        self.suspend_drive_target.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            drive_email_frame,
            text="Load Users",
            command=self.load_users_for_suspend_drive
        ).pack(side=tk.LEFT)

        ttk.Label(self.suspend_options_frame, text="(Leave blank to skip Drive transfer)", font=('Arial', 8), foreground='gray').grid(row=1, column=1, sticky=tk.W)

        # OU move option
        ttk.Label(self.suspend_options_frame, text="Move to OU:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5), padx=(0, 5))

        ou_frame = ttk.Frame(self.suspend_options_frame)
        ou_frame.grid(row=2, column=1, sticky=tk.EW, pady=(10, 5))

        self.suspend_target_ou = ttk.Combobox(ou_frame, values=["/"])
        self.suspend_target_ou.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            ou_frame,
            text="Load OUs",
            command=self.load_ous_for_suspend
        ).pack(side=tk.LEFT)

        ttk.Label(self.suspend_options_frame, text="(Leave blank to keep current OU)", font=('Arial', 8), foreground='gray').grid(row=3, column=1, sticky=tk.W)

        self.suspend_options_frame.grid_columnconfigure(1, weight=1)

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

    def load_users_for_suspend_drive(self):
        """Load users for the suspend Drive transfer dropdown."""
        from utils.workspace_data import fetch_users
        self.load_combobox_async(self.suspend_drive_target, fetch_users, enable_fuzzy=True)

    def load_ous_for_suspend(self):
        """Load OUs for the suspend OU move dropdown."""
        from utils.workspace_data import fetch_org_units
        self.load_combobox_async(self.suspend_target_ou, fetch_org_units,
                                default_value="/", enable_fuzzy=True)

    def execute_suspend_restore(self):
        """Execute suspend/restore operation."""
        users = self.get_target_users('suspend_restore')
        if users is None:
            return

        action = self.suspend_restore_action.get()
        dry_run = self.suspend_restore_dry_run.get()

        if action == 'suspend':
            # Get optional parameters for suspend
            drive_target = self.suspend_drive_target.get().strip()
            target_ou = self.suspend_target_ou.get().strip()

            self.run_operation(
                users_module.suspend_user,
                self.suspend_restore_progress,
                users,
                dry_run=dry_run,
                drive_target=drive_target if drive_target else None,
                target_ou=target_ou if target_ou and target_ou != "/" else None
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
        self.reset_password_email = ttk.Combobox(self.reset_password_single_frame, width=37)
        self.reset_password_email.grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.reset_password_single_frame, text="New Password*:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))

        password_frame = ttk.Frame(self.reset_password_single_frame)
        password_frame.grid(row=1, column=1, sticky=tk.EW, pady=5)

        self.reset_password_new = ttk.Entry(password_frame, width=30, show="*")
        self.reset_password_new.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            password_frame,
            text="Generate",
            command=lambda: self.open_password_generator(self.reset_password_new),
            width=10
        ).pack(side=tk.LEFT)

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

        # Single user input frame (2 columns side by side layout)
        self.update_info_single_frame = ttk.LabelFrame(mode_container, text="Update User Details", padding="10")

        # Row 0: User Email | First Name
        ttk.Label(self.update_info_single_frame, text="User Email*:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_email = ttk.Combobox(self.update_info_single_frame, width=17)
        self.update_info_email.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(0, 15))

        ttk.Label(self.update_info_single_frame, text="First Name:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_firstname = ttk.Entry(self.update_info_single_frame, width=20)
        self.update_info_firstname.grid(row=0, column=3, sticky=tk.EW, pady=5)

        # Row 1: Last Name | Employee ID
        ttk.Label(self.update_info_single_frame, text="Last Name:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_lastname = ttk.Entry(self.update_info_single_frame, width=20)
        self.update_info_lastname.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(0, 15))

        ttk.Label(self.update_info_single_frame, text="Employee ID:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_employee_id = ttk.Entry(self.update_info_single_frame, width=20)
        self.update_info_employee_id.grid(row=1, column=3, sticky=tk.EW, pady=5)

        # Row 2: Job Title | Manager's Email
        ttk.Label(self.update_info_single_frame, text="Job Title:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_job_title = ttk.Entry(self.update_info_single_frame, width=20)
        self.update_info_job_title.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(0, 15))

        ttk.Label(self.update_info_single_frame, text="Manager's Email:").grid(row=2, column=2, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_manager = ttk.Entry(self.update_info_single_frame, width=20)
        self.update_info_manager.grid(row=2, column=3, sticky=tk.EW, pady=5)

        # Row 3: Department | Cost Center
        ttk.Label(self.update_info_single_frame, text="Department:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_department = ttk.Entry(self.update_info_single_frame, width=20)
        self.update_info_department.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=(0, 15))

        ttk.Label(self.update_info_single_frame, text="Cost Center:").grid(row=3, column=2, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_cost_center = ttk.Entry(self.update_info_single_frame, width=20)
        self.update_info_cost_center.grid(row=3, column=3, sticky=tk.EW, pady=5)

        # Row 4: Building ID | Address
        ttk.Label(self.update_info_single_frame, text="Building ID:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_building_id = ttk.Entry(self.update_info_single_frame, width=20)
        self.update_info_building_id.grid(row=4, column=1, sticky=tk.EW, pady=5, padx=(0, 15))

        ttk.Label(self.update_info_single_frame, text="Address:").grid(row=4, column=2, sticky=tk.W, pady=5, padx=(0, 5))
        self.update_info_address = ttk.Entry(self.update_info_single_frame, width=20)
        self.update_info_address.grid(row=4, column=3, sticky=tk.EW, pady=5)

        # Row 5: GAL visibility checkbox
        self.update_info_hide_from_gal = tk.BooleanVar()
        ttk.Checkbutton(
            self.update_info_single_frame,
            text="Hide from Global Address List (GAL)",
            variable=self.update_info_hide_from_gal
        ).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(self.update_info_single_frame, text="* Required. Leave other fields blank to keep unchanged.",
                 font=('Arial', 8), foreground='gray').grid(row=5, column=2, columnspan=2, sticky=tk.W, pady=5)

        # Configure column weights for proper expansion
        self.update_info_single_frame.grid_columnconfigure(1, weight=1)
        self.update_info_single_frame.grid_columnconfigure(3, weight=1)

        # CSV selection frame
        self.update_info_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.update_info_csv_frame, text="CSV Format: email,firstName,lastName,employeeId,jobTitle,manager,department,costCenter,buildingId,address,galHidden").pack(anchor=tk.W)
        ttk.Label(self.update_info_csv_frame, text="Required: email. Optional: All other fields. galHidden: true/false").pack(anchor=tk.W, pady=(5, 10))

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

            employee_id = self.update_info_employee_id.get().strip()
            if employee_id:
                user_data['employeeId'] = employee_id

            job_title = self.update_info_job_title.get().strip()
            if job_title:
                user_data['jobTitle'] = job_title

            manager = self.update_info_manager.get().strip()
            if manager:
                user_data['manager'] = manager

            department = self.update_info_department.get().strip()
            if department:
                user_data['department'] = department

            cost_center = self.update_info_cost_center.get().strip()
            if cost_center:
                user_data['costCenter'] = cost_center

            building_id = self.update_info_building_id.get().strip()
            if building_id:
                user_data['buildingId'] = building_id

            address = self.update_info_address.get().strip()
            if address:
                user_data['address'] = address

            # GAL visibility - always include if checkbox is checked
            if self.update_info_hide_from_gal.get():
                user_data['galHidden'] = True

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
            text="Move users to different organizational units. Choose single entry or CSV for bulk moves.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Mode selection
        mode_frame = ttk.LabelFrame(tab, text="Input Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.manage_ou_mode = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="Single Entry",
            variable=self.manage_ou_mode,
            value="single",
            command=self.toggle_manage_ou_mode
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            mode_frame,
            text="CSV Bulk",
            variable=self.manage_ou_mode,
            value="csv",
            command=self.toggle_manage_ou_mode
        ).pack(side=tk.LEFT)

        # Container for mode-specific frames
        mode_container = ttk.Frame(tab)
        mode_container.pack(fill=tk.X, pady=(0, 10))

        # Single entry frame
        self.manage_ou_single_frame = ttk.LabelFrame(mode_container, text="User Details", padding="10")

        # User Email with dropdown
        ttk.Label(self.manage_ou_single_frame, text="User Email: *").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        email_frame = ttk.Frame(self.manage_ou_single_frame)
        email_frame.grid(row=0, column=1, sticky=tk.EW, pady=5)

        self.manage_ou_email = ttk.Combobox(email_frame)
        self.manage_ou_email.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            email_frame,
            text="Load Users",
            command=self.load_users_for_manage_ou
        ).pack(side=tk.LEFT)

        # Organizational Unit with dropdown
        ttk.Label(self.manage_ou_single_frame, text="Organizational Unit: *").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        ou_frame = ttk.Frame(self.manage_ou_single_frame)
        ou_frame.grid(row=1, column=1, sticky=tk.EW, pady=5)

        self.manage_ou_orgunit = ttk.Combobox(ou_frame, values=["/"])
        self.manage_ou_orgunit.set("/")
        self.manage_ou_orgunit.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            ou_frame,
            text="Load OUs",
            command=self.load_org_units_for_manage_ou
        ).pack(side=tk.LEFT)

        ttk.Label(self.manage_ou_single_frame, text="* Required fields", font=('Arial', 8), foreground='gray').grid(row=2, column=1, sticky=tk.W, pady=(5, 0))

        self.manage_ou_single_frame.grid_columnconfigure(1, weight=1)

        # CSV selection frame
        self.manage_ou_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.manage_ou_csv_frame, text="CSV Format: email,orgUnit").pack(anchor=tk.W)
        ttk.Label(self.manage_ou_csv_frame, text="Example: john@domain.com,/Staff/Engineering").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(self.manage_ou_csv_frame)
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
            text="Move User(s)",
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

        # Initial mode
        self.toggle_manage_ou_mode()

    def toggle_manage_ou_mode(self):
        """Toggle between single and CSV mode for Manage OUs."""
        if self.manage_ou_mode.get() == "single":
            self.manage_ou_single_frame.pack(fill=tk.X, expand=True)
            self.manage_ou_csv_frame.pack_forget()
        else:
            self.manage_ou_single_frame.pack_forget()
            self.manage_ou_csv_frame.pack(fill=tk.X, expand=True)

    def load_users_for_manage_ou(self):
        """Load users for the manage OU user email dropdown."""
        from utils.workspace_data import fetch_users
        self.load_combobox_async(self.manage_ou_email, fetch_users, enable_fuzzy=True)

    def load_org_units_for_manage_ou(self):
        """Load organizational units for the manage OU dropdown."""
        import modules.users as users_module
        self.load_combobox_async(self.manage_ou_orgunit, users_module.list_org_units,
                                default_value="/", enable_fuzzy=True)

    def browse_csv_for_manage_ou(self):
        """Browse for CSV file for manage OU."""
        self.browse_csv_file(self.manage_ou_csv_entry, "Select OU Management CSV File")

    def execute_manage_ou(self):
        """Execute manage OU operation."""
        mode = self.manage_ou_mode.get()

        if mode == "single":
            # Single entry mode
            email = self.manage_ou_email.get().strip()
            orgunit = self.manage_ou_orgunit.get().strip()

            # Validate required fields
            if not email:
                messagebox.showerror("Validation Error", "Email is required.")
                return
            if not orgunit:
                messagebox.showerror("Validation Error", "Organizational Unit is required.")
                return

            # Create user data
            users_data = [{
                'email': email,
                'orgUnit': orgunit
            }]

        else:
            # CSV mode
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

                # Confirm bulk operation
                if not self.confirm_bulk_operation(len(users_data), "move users"):
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
                return

        # Execute
        dry_run = self.manage_ou_dry_run.get()

        # Prepare success callback to clear fields (only for single mode and not dry run)
        on_success = None
        if mode == "single" and not dry_run:
            on_success = lambda: self.clear_fields(self.manage_ou_email)

        self.run_operation(
            users_module.change_org_unit,
            self.manage_ou_progress,
            users_data,
            dry_run=dry_run,
            on_success=on_success
        )

    # ==================== TAB 7: MANAGE ALIASES ====================

    def create_manage_aliases_tab(self):
        """Create the Manage Aliases tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Aliases")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Add or remove email aliases. Choose single entry or CSV for bulk operations.",
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

        # Mode selection
        mode_frame = ttk.Frame(tab)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.manage_aliases_mode = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="Single Entry",
            variable=self.manage_aliases_mode,
            value="single",
            command=self.toggle_manage_aliases_mode
        ).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(
            mode_frame,
            text="CSV Bulk Import",
            variable=self.manage_aliases_mode,
            value="csv",
            command=self.toggle_manage_aliases_mode
        ).pack(side=tk.LEFT)

        # Container for mode-specific content
        mode_container = ttk.Frame(tab)
        mode_container.pack(fill=tk.X, pady=(0, 10))

        # Single entry frame
        self.manage_aliases_single_frame = ttk.LabelFrame(mode_container, text="Alias Details", padding="10")

        ttk.Label(self.manage_aliases_single_frame, text="User Email*:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.manage_aliases_email = ttk.Combobox(self.manage_aliases_single_frame, width=37)
        self.manage_aliases_email.grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.manage_aliases_single_frame, text="Alias*:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.manage_aliases_alias = ttk.Entry(self.manage_aliases_single_frame, width=40)
        self.manage_aliases_alias.grid(row=1, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.manage_aliases_single_frame, text="* Required fields", font=('Arial', 8), foreground='gray').grid(row=2, column=1, sticky=tk.W, pady=(5, 0))

        self.manage_aliases_single_frame.grid_columnconfigure(1, weight=1)

        # CSV selection frame
        self.manage_aliases_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.manage_aliases_csv_frame, text="For Add: email,alias").pack(anchor=tk.W)
        ttk.Label(self.manage_aliases_csv_frame, text="For Remove: alias (one per line)").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(self.manage_aliases_csv_frame)
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

        # Initial toggle
        self.toggle_manage_aliases_mode()

    def toggle_manage_aliases_mode(self):
        """Toggle between single and CSV mode for manage aliases."""
        if self.manage_aliases_mode.get() == "single":
            self.manage_aliases_csv_frame.pack_forget()
            self.manage_aliases_single_frame.pack(fill=tk.X, expand=True)
        else:
            self.manage_aliases_single_frame.pack_forget()
            self.manage_aliases_csv_frame.pack(fill=tk.X, expand=True)

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
        mode = self.manage_aliases_mode.get()
        action = self.manage_aliases_action.get()
        dry_run = self.manage_aliases_dry_run.get()

        if mode == "single":
            # Single entry mode
            if action == 'add':
                email = self.manage_aliases_email.get().strip()
                alias = self.manage_aliases_alias.get().strip()

                if not email:
                    messagebox.showerror("Validation Error", "User email is required.")
                    return
                if not alias:
                    messagebox.showerror("Validation Error", "Alias is required.")
                    return

                data = [{'email': email, 'alias': alias}]
            else:  # remove
                alias = self.manage_aliases_alias.get().strip()
                if not alias:
                    messagebox.showerror("Validation Error", "Alias is required.")
                    return

                data = [{'alias': alias}]

        else:
            # CSV mode
            csv_file = self.manage_aliases_csv_entry.get().strip()
            if not csv_file:
                messagebox.showerror("Validation Error", "Please select a CSV file.")
                return

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
                else:
                    # Validate remove format
                    for row in data:
                        if 'alias' not in row or not row['alias']:
                            messagebox.showerror("Validation Error", "Missing 'alias' field in CSV for remove action.")
                            return

                # Confirm
                if not self.confirm_bulk_operation(len(data), f"{action} aliases"):
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
                return

        # Prepare success callback to clear fields (only for single mode and not dry run)
        on_success = None
        if mode == "single" and not dry_run:
            if action == 'add':
                # For add action, clear both email and alias
                on_success = lambda: self.clear_fields(
                    self.manage_aliases_email,
                    self.manage_aliases_alias
                )
            else:
                # For remove action, only clear alias
                on_success = lambda: self.clear_fields(
                    self.manage_aliases_alias
                )

        # Execute
        if action == 'add':
            self.run_operation(
                users_module.add_alias,
                self.manage_aliases_progress,
                data,
                dry_run=dry_run,
                on_success=on_success
            )
        else:  # remove
            self.run_operation(
                users_module.remove_alias,
                self.manage_aliases_progress,
                data,
                dry_run=dry_run,
                on_success=on_success
            )

    # ==================== TAB 8: MFA MANAGEMENT ====================

    def create_mfa_tab(self):
        """Create the MFA Management tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="MFA Management")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Manage Multi-Factor Authentication (MFA) for users.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Action selection
        action_frame = ttk.LabelFrame(tab, text="MFA Action", padding="10")
        action_frame.pack(fill=tk.X, pady=(0, 10))

        self.mfa_action = tk.StringVar(value="disable")

        ttk.Radiobutton(
            action_frame,
            text="Disable MFA",
            variable=self.mfa_action,
            value="disable"
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            action_frame,
            text="Retrieve Backup Codes",
            variable=self.mfa_action,
            value="backup_codes"
        ).pack(side=tk.LEFT, padx=(0, 20))

        # Info label about enabling MFA
        info_label = ttk.Label(
            action_frame,
            text="Note: To enable MFA, configure enforcement at OU/Domain level via Google Admin Console",
            font=('Arial', 9),
            foreground='#666666'
        )
        info_label.pack(side=tk.LEFT, padx=(20, 0))

        # Target selection (simplified - no "All Users" or "Group" for safety)
        self.mfa_target = self.create_combobox_user_target_selection_frame(tab, 'mfa')
        self.mfa_target.pack(fill=tk.X, pady=(0, 10))

        # Progress frame
        self.mfa_progress = self.create_progress_frame(tab)
        self.mfa_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Execute",
            command=self.execute_mfa,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

    def execute_mfa(self):
        """Execute MFA operation."""
        users = self.get_target_users('mfa')
        if users is None:
            return

        action = self.mfa_action.get()

        # Confirmation for multiple users
        if len(users) > 1:
            action_text = {
                'disable': 'disable MFA for',
                'backup_codes': 'retrieve backup codes for'
            }.get(action, 'perform MFA action on')

            if not messagebox.askyesno(
                "Confirm Operation",
                f"You are about to {action_text} {len(users)} users.\n\nProceed?"
            ):
                return

        # Execute appropriate action
        if action == 'disable':
            self.run_operation(
                users_module.disable_mfa,
                self.mfa_progress,
                users
            )
        else:  # backup_codes
            self.run_operation(
                users_module.get_backup_codes,
                self.mfa_progress,
                users
            )

    # ==================== PASSWORD GENERATOR ====================

    def open_password_generator(self, password_entry):
        """
        Open password generator dialog and set generated password to entry field.

        Args:
            password_entry: The entry widget to populate with generated password
        """
        def set_password(password):
            # Temporarily show the password field
            password_entry.config(show="")
            password_entry.delete(0, tk.END)
            password_entry.insert(0, password)
            # Hide it again after 3 seconds
            self.after(3000, lambda: password_entry.config(show="*"))

        PasswordGeneratorDialog(self, set_password)

    # ==================== COMBOBOX INITIALIZATION ====================

    def initialize_comboboxes(self):
        """Auto-load all comboboxes on window initialization."""
        # Load users for target selection comboboxes
        self.load_users_combobox('delete_users')
        self.load_users_combobox('suspend_restore')
        self.load_users_combobox('mfa')

        # Load users for custom comboboxes
        self.load_users_for_reset_password()
        self.load_users_for_update_info()
        self.load_users_for_manage_aliases()

        # Load users for delete drive transfer combobox
        self.load_users_for_delete_drive()
        # Load users for suspend drive transfer combobox
        self.load_users_for_suspend_drive()
        # Load users for manage OU combobox
        self.load_users_for_manage_ou()

    def load_users_for_reset_password(self):
        """Load users for reset password combobox."""
        from utils.workspace_data import fetch_users
        self.load_combobox_async(self.reset_password_email, fetch_users, enable_fuzzy=True)

    def load_users_for_update_info(self):
        """Load users for update info combobox."""
        from utils.workspace_data import fetch_users
        self.load_combobox_async(self.update_info_email, fetch_users, enable_fuzzy=True)

    def load_users_for_manage_aliases(self):
        """Load users for manage aliases combobox."""
        from utils.workspace_data import fetch_users
        self.load_combobox_async(self.manage_aliases_email, fetch_users, enable_fuzzy=True)

