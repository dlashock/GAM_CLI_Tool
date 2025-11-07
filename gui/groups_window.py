"""
Group Management Window for GAM Admin Tool.

Provides a tabbed interface for all group-related operations including
creating groups, deleting, managing members, group settings, and aliases.

Inherits from BaseOperationWindow for common functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

from gui.base_operation_window import BaseOperationWindow
from modules import groups as groups_module


class GroupsWindow(BaseOperationWindow):
    """
    Group Management window with tabbed interface.

    Provides 7 tabs for different group operations:
    - Create Groups
    - Delete Groups
    - Manage Members
    - List Members
    - Group Settings
    - Group Aliases
    - User's Groups
    """

    def __init__(self, parent):
        """
        Initialize the Group Management window.

        Args:
            parent: The parent tkinter widget
        """
        super().__init__(parent, "Group Management", "900x750", (800, 600))

    def create_operation_tabs(self):
        """Create all group management operation tabs."""
        self.create_create_groups_tab()
        self.create_delete_groups_tab()
        self.create_manage_members_tab()
        self.create_list_members_tab()
        self.create_group_settings_tab()
        self.create_group_aliases_tab()
        self.create_user_groups_tab()

    # ==================== TAB 1: CREATE GROUPS ====================

    def create_create_groups_tab(self):
        """Create the Create Groups tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Create Groups")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Create new groups. Use CSV for bulk creation.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # CSV selection frame
        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(csv_frame, text="CSV Format: email,name,description").pack(anchor=tk.W)
        ttk.Label(csv_frame, text="Required: email, name. Optional: description").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.create_groups_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.create_groups_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_file(self.create_groups_csv_entry)
        ).pack(side=tk.LEFT)

        # Progress frame
        self.create_groups_progress = self.create_progress_frame(tab)
        self.create_groups_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Create Groups",
            command=self.execute_create_groups,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.create_groups_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.create_groups_dry_run
        ).pack(side=tk.LEFT)

    def execute_create_groups(self):
        """Execute create groups operation."""
        csv_file = self.create_groups_csv_entry.get().strip()
        if not csv_file:
            messagebox.showerror("Validation Error", "Please select a CSV file.")
            return

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                groups_data = list(reader)

            if not groups_data:
                messagebox.showerror("Error", "CSV file is empty.")
                return

            # Validate required fields
            for group_data in groups_data:
                if 'email' not in group_data or not group_data['email']:
                    messagebox.showerror("Validation Error", "Missing 'email' field in CSV.")
                    return
                if 'name' not in group_data or not group_data['name']:
                    messagebox.showerror("Validation Error", "Missing 'name' field in CSV.")
                    return

            if not self.confirm_bulk_operation(len(groups_data), "create groups"):
                return

            dry_run = self.create_groups_dry_run.get()
            self.run_operation(
                groups_module.create_group,
                self.create_groups_progress,
                groups_data,
                dry_run=dry_run
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")

    # ==================== TAB 2: DELETE GROUPS ====================

    def create_delete_groups_tab(self):
        """Create the Delete Groups tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Delete Groups")

        # Warning
        warning = ttk.Label(
            tab,
            text="⚠ WARNING: This permanently deletes groups!",
            foreground='red',
            font=('Arial', 10, 'bold')
        )
        warning.pack(pady=(0, 10), anchor=tk.W)

        # Target selection
        self.delete_groups_target = self.create_target_selection_frame(tab, 'delete_groups')
        self.delete_groups_target.pack(fill=tk.X, pady=(0, 10))

        # Progress frame
        self.delete_groups_progress = self.create_progress_frame(tab)
        self.delete_groups_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Delete Groups",
            command=self.execute_delete_groups,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.delete_groups_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.delete_groups_dry_run
        ).pack(side=tk.LEFT)

    def execute_delete_groups(self):
        """Execute delete groups operation."""
        groups = self.get_target_users('delete_groups')  # Reuses target selection
        if groups is None:
            return

        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to DELETE {len(groups)} group(s)?",
            icon='warning'
        )
        if not response:
            return

        dry_run = self.delete_groups_dry_run.get()
        self.run_operation(
            groups_module.delete_group,
            self.delete_groups_progress,
            groups,
            dry_run=dry_run
        )

    # ==================== TAB 3: MANAGE MEMBERS ====================

    def create_manage_members_tab(self):
        """Create the Manage Members tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Members")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Add or remove members from groups. Use CSV for bulk operations.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Action selection
        action_frame = ttk.LabelFrame(tab, text="Action", padding="10")
        action_frame.pack(fill=tk.X, pady=(0, 10))

        self.manage_members_action = tk.StringVar(value="add")
        ttk.Radiobutton(
            action_frame,
            text="Add Members",
            variable=self.manage_members_action,
            value="add"
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            action_frame,
            text="Remove Members",
            variable=self.manage_members_action,
            value="remove"
        ).pack(side=tk.LEFT)

        # CSV selection frame
        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(csv_frame, text="For Add: group,member,role (role: MEMBER, MANAGER, or OWNER)").pack(anchor=tk.W)
        ttk.Label(csv_frame, text="For Remove: group,member").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.manage_members_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.manage_members_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_file(self.manage_members_csv_entry)
        ).pack(side=tk.LEFT)

        # Progress frame
        self.manage_members_progress = self.create_progress_frame(tab)
        self.manage_members_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Execute",
            command=self.execute_manage_members,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.manage_members_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.manage_members_dry_run
        ).pack(side=tk.LEFT)

    def execute_manage_members(self):
        """Execute manage members operation."""
        csv_file = self.manage_members_csv_entry.get().strip()
        if not csv_file:
            messagebox.showerror("Validation Error", "Please select a CSV file.")
            return

        action = self.manage_members_action.get()
        dry_run = self.manage_members_dry_run.get()

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)

            if not data:
                messagebox.showerror("Error", "CSV file is empty.")
                return

            # Validate fields
            for row in data:
                if 'group' not in row or not row['group']:
                    messagebox.showerror("Validation Error", "Missing 'group' field in CSV.")
                    return
                if 'member' not in row or not row['member']:
                    messagebox.showerror("Validation Error", "Missing 'member' field in CSV.")
                    return

            if not self.confirm_bulk_operation(len(data), f"{action} members"):
                return

            if action == 'add':
                self.run_operation(
                    groups_module.add_members,
                    self.manage_members_progress,
                    data,
                    dry_run=dry_run
                )
            else:
                self.run_operation(
                    groups_module.remove_members,
                    self.manage_members_progress,
                    data,
                    dry_run=dry_run
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")

    # ==================== TAB 4: LIST MEMBERS ====================

    def create_list_members_tab(self):
        """Create the List Members tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="List Members")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="List all members of a group.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Group selection
        group_frame = ttk.LabelFrame(tab, text="Group Email", padding="10")
        group_frame.pack(fill=tk.X, pady=(0, 10))

        self.list_members_entry = ttk.Entry(group_frame, width=50)
        self.list_members_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            group_frame,
            text="List Members",
            command=self.execute_list_members
        ).pack(side=tk.LEFT)

        # Results frame
        results_frame = ttk.LabelFrame(tab, text="Members", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Scrolled text widget
        scroll = ttk.Scrollbar(results_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.list_members_text = tk.Text(results_frame, height=15, width=60, yscrollcommand=scroll.set)
        self.list_members_text.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.list_members_text.yview)

    def execute_list_members(self):
        """Execute list members operation."""
        group_email = self.list_members_entry.get().strip()
        if not group_email:
            messagebox.showerror("Validation Error", "Please enter a group email.")
            return

        self.list_members_text.delete("1.0", tk.END)
        self.list_members_text.insert(tk.END, "Fetching members...\n")
        self.update_idletasks()

        success, result = groups_module.list_members(group_email)

        self.list_members_text.delete("1.0", tk.END)
        if success:
            if result:
                self.list_members_text.insert(tk.END, f"Group: {group_email}\n")
                self.list_members_text.insert(tk.END, f"Total members: {len(result)}\n\n")
                self.list_members_text.insert(tk.END, f"{'Email':<40} {'Role':<15}\n")
                self.list_members_text.insert(tk.END, "="*55 + "\n")
                for member in result:
                    self.list_members_text.insert(tk.END, f"{member['email']:<40} {member['role']:<15}\n")
            else:
                self.list_members_text.insert(tk.END, "No members found.")
        else:
            self.list_members_text.insert(tk.END, f"Error: {result}")

    # ==================== TAB 5: GROUP SETTINGS ====================

    def create_group_settings_tab(self):
        """Create the Group Settings tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Group Settings")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Update group settings. Use CSV for bulk updates.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # CSV selection frame
        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(csv_frame, text="CSV Format: group,whoCanPostMessage,whoCanViewGroup,whoCanJoin").pack(anchor=tk.W)
        ttk.Label(csv_frame, text="Values: ALL_IN_DOMAIN_CAN_POST, ALL_MEMBERS_CAN_POST, OWNERS_ONLY, etc.").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.group_settings_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.group_settings_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_file(self.group_settings_csv_entry)
        ).pack(side=tk.LEFT)

        # Progress frame
        self.group_settings_progress = self.create_progress_frame(tab)
        self.group_settings_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Update Settings",
            command=self.execute_group_settings,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.group_settings_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.group_settings_dry_run
        ).pack(side=tk.LEFT)

    def execute_group_settings(self):
        """Execute group settings operation."""
        csv_file = self.group_settings_csv_entry.get().strip()
        if not csv_file:
            messagebox.showerror("Validation Error", "Please select a CSV file.")
            return

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                settings_data = list(reader)

            if not settings_data:
                messagebox.showerror("Error", "CSV file is empty.")
                return

            # Validate group field
            for data in settings_data:
                if 'group' not in data or not data['group']:
                    messagebox.showerror("Validation Error", "Missing 'group' field in CSV.")
                    return

            if not self.confirm_bulk_operation(len(settings_data), "update group settings"):
                return

            dry_run = self.group_settings_dry_run.get()
            self.run_operation(
                groups_module.update_group_settings,
                self.group_settings_progress,
                settings_data,
                dry_run=dry_run
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")

    # ==================== TAB 6: GROUP ALIASES ====================

    def create_group_aliases_tab(self):
        """Create the Group Aliases tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Group Aliases")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Add or remove group aliases. Use CSV for bulk operations.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Action selection
        action_frame = ttk.LabelFrame(tab, text="Action", padding="10")
        action_frame.pack(fill=tk.X, pady=(0, 10))

        self.group_aliases_action = tk.StringVar(value="add")
        ttk.Radiobutton(
            action_frame,
            text="Add Aliases",
            variable=self.group_aliases_action,
            value="add"
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            action_frame,
            text="Remove Aliases",
            variable=self.group_aliases_action,
            value="remove"
        ).pack(side=tk.LEFT)

        # CSV selection frame
        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(csv_frame, text="For Add: group,alias").pack(anchor=tk.W)
        ttk.Label(csv_frame, text="For Remove: Just list aliases (header: alias)").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.group_aliases_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.group_aliases_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_file(self.group_aliases_csv_entry)
        ).pack(side=tk.LEFT)

        # Progress frame
        self.group_aliases_progress = self.create_progress_frame(tab)
        self.group_aliases_progress.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Execute button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Execute",
            command=self.execute_group_aliases,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Dry run checkbox
        self.group_aliases_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.group_aliases_dry_run
        ).pack(side=tk.LEFT)

    def execute_group_aliases(self):
        """Execute group aliases operation."""
        csv_file = self.group_aliases_csv_entry.get().strip()
        if not csv_file:
            messagebox.showerror("Validation Error", "Please select a CSV file.")
            return

        action = self.group_aliases_action.get()
        dry_run = self.group_aliases_dry_run.get()

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
                    if 'group' not in row or not row['group']:
                        messagebox.showerror("Validation Error", "Missing 'group' field in CSV.")
                        return
                    if 'alias' not in row or not row['alias']:
                        messagebox.showerror("Validation Error", "Missing 'alias' field in CSV.")
                        return

                if not self.confirm_bulk_operation(len(data), "add group aliases"):
                    return

                self.run_operation(
                    groups_module.add_group_alias,
                    self.group_aliases_progress,
                    data,
                    dry_run=dry_run
                )
            else:
                # Remove - just need list of aliases
                if 'alias' not in data[0]:
                    messagebox.showerror("Validation Error", "Missing 'alias' field in CSV.")
                    return

                aliases = [row['alias'] for row in data if row.get('alias')]

                if not self.confirm_bulk_operation(len(aliases), "remove group aliases"):
                    return

                self.run_operation(
                    groups_module.remove_group_alias,
                    self.group_aliases_progress,
                    aliases,
                    dry_run=dry_run
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")

    # ==================== TAB 7: USER'S GROUPS ====================

    def create_user_groups_tab(self):
        """Create the User's Groups tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="User's Groups")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="List all groups a user belongs to.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # User selection
        user_frame = ttk.LabelFrame(tab, text="User Email", padding="10")
        user_frame.pack(fill=tk.X, pady=(0, 10))

        self.user_groups_entry = ttk.Entry(user_frame, width=50)
        self.user_groups_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            user_frame,
            text="List Groups",
            command=self.execute_user_groups
        ).pack(side=tk.LEFT)

        # Results frame
        results_frame = ttk.LabelFrame(tab, text="Groups", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Scrolled text widget
        scroll = ttk.Scrollbar(results_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.user_groups_text = tk.Text(results_frame, height=15, width=60, yscrollcommand=scroll.set)
        self.user_groups_text.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.user_groups_text.yview)

    def execute_user_groups(self):
        """Execute user groups operation."""
        user_email = self.user_groups_entry.get().strip()
        if not user_email:
            messagebox.showerror("Validation Error", "Please enter a user email.")
            return

        self.user_groups_text.delete("1.0", tk.END)
        self.user_groups_text.insert(tk.END, "Fetching groups...\n")
        self.update_idletasks()

        success, result = groups_module.list_user_groups(user_email)

        self.user_groups_text.delete("1.0", tk.END)
        if success:
            if result:
                self.user_groups_text.insert(tk.END, f"User: {user_email}\n")
                self.user_groups_text.insert(tk.END, f"Total groups: {len(result)}\n\n")
                for group in result:
                    self.user_groups_text.insert(tk.END, f"{group}\n")
            else:
                self.user_groups_text.insert(tk.END, "User is not a member of any groups.")
        else:
            self.user_groups_text.insert(tk.END, f"Error: {result}")

    # ==================== HELPER METHODS ====================

    def browse_csv_file(self, entry_widget):
        """Browse for CSV file and update entry widget."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
