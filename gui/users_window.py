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
            text="Create new user accounts. Use CSV for bulk creation.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # CSV selection frame
        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(csv_frame, text="CSV Format: email,firstName,lastName,password,orgUnit,title,phone").pack(anchor=tk.W)
        ttk.Label(csv_frame, text="Required: email, firstName, lastName, password. Optional: orgUnit (default /), title, phone").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(csv_frame)
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
            text="Create Users",
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

            # Confirm
            if not self.confirm_bulk_operation(len(users_data), "create users"):
                return

            # Execute
            dry_run = self.create_users_dry_run.get()
            self.run_operation(
                users_module.create_user,
                self.create_users_progress,
                users_data,
                dry_run=dry_run
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")

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

        # Target selection
        self.delete_users_target = self.create_target_selection_frame(tab, 'delete_users')
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

        # Target selection
        self.suspend_restore_target = self.create_target_selection_frame(tab, 'suspend_restore')
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
            text="Reset user passwords. Use CSV for bulk password resets.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # CSV selection frame
        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(csv_frame, text="CSV Format: email,password").pack(anchor=tk.W, pady=(0, 10))

        csv_input_frame = ttk.Frame(csv_frame)
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
            text="Reset Passwords",
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

            # Execute
            dry_run = self.reset_password_dry_run.get()
            self.run_operation(
                users_module.reset_password,
                self.reset_password_progress,
                users_data,
                dry_run=dry_run
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")

    # ==================== TAB 5: UPDATE USER INFO ====================

    def create_update_info_tab(self):
        """Create the Update User Info tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Update Info")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Update user information (name, title, phone, etc.). Use CSV for bulk updates.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # CSV selection frame
        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(csv_frame, text="CSV Format: email,firstName,lastName,title,phone,address").pack(anchor=tk.W)
        ttk.Label(csv_frame, text="Required: email. Optional: firstName, lastName, title, phone, address (include only fields to update)").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(csv_frame)
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

            # Execute
            dry_run = self.update_info_dry_run.get()
            self.run_operation(
                users_module.update_user_info,
                self.update_info_progress,
                users_data,
                dry_run=dry_run
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")

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
