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
            text="Create new groups. Choose single group or CSV for bulk creation.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Mode selection
        mode_frame = ttk.Frame(tab)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.create_groups_mode = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="Single Group",
            variable=self.create_groups_mode,
            value="single",
            command=self.toggle_create_groups_mode
        ).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(
            mode_frame,
            text="CSV Bulk Import",
            variable=self.create_groups_mode,
            value="csv",
            command=self.toggle_create_groups_mode
        ).pack(side=tk.LEFT)

        # Container for mode-specific content (keeps layout stable)
        mode_container = ttk.Frame(tab)
        mode_container.pack(fill=tk.X, pady=(0, 10))

        # Single group input frame
        self.create_groups_single_frame = ttk.LabelFrame(mode_container, text="Group Details", padding="10")

        # Email (required)
        ttk.Label(self.create_groups_single_frame, text="Email*:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.create_group_email = ttk.Entry(self.create_groups_single_frame, width=40)
        self.create_group_email.grid(row=0, column=1, sticky=tk.EW, pady=5)

        # Name (required)
        ttk.Label(self.create_groups_single_frame, text="Name*:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.create_group_name = ttk.Entry(self.create_groups_single_frame, width=40)
        self.create_group_name.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # Description (optional)
        ttk.Label(self.create_groups_single_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.create_group_description = ttk.Entry(self.create_groups_single_frame, width=40)
        self.create_group_description.grid(row=2, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self.create_groups_single_frame, text="* Required fields", font=('Arial', 8), foreground='gray').grid(row=3, column=1, sticky=tk.W, pady=(5, 0))

        self.create_groups_single_frame.grid_columnconfigure(1, weight=1)

        # CSV selection frame
        self.create_groups_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.create_groups_csv_frame, text="CSV Format: email,name,description").pack(anchor=tk.W)
        ttk.Label(self.create_groups_csv_frame, text="Required: email, name. Optional: description").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(self.create_groups_csv_frame)
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
            text="Create Group(s)",
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

        # Initial toggle
        self.toggle_create_groups_mode()

    def toggle_create_groups_mode(self):
        """Toggle between single and CSV mode for create groups."""
        if self.create_groups_mode.get() == "single":
            self.create_groups_csv_frame.pack_forget()
            self.create_groups_single_frame.pack(fill=tk.X, expand=True)
        else:
            self.create_groups_single_frame.pack_forget()
            self.create_groups_csv_frame.pack(fill=tk.X, expand=True)

    def execute_create_groups(self):
        """Execute create groups operation."""
        mode = self.create_groups_mode.get()

        if mode == "single":
            # Single group mode
            email = self.create_group_email.get().strip()
            name = self.create_group_name.get().strip()
            description = self.create_group_description.get().strip()

            # Validate required fields
            if not email:
                messagebox.showerror("Validation Error", "Email is required.")
                return
            if not name:
                messagebox.showerror("Validation Error", "Name is required.")
                return

            # Create group data dict
            groups_data = [{
                'email': email,
                'name': name,
                'description': description
            }]

        else:
            # CSV mode
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

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
                return

        # Execute
        dry_run = self.create_groups_dry_run.get()
        self.run_operation(
            groups_module.create_group,
            self.create_groups_progress,
            groups_data,
            dry_run=dry_run
        )

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

        # Target selection (use group-specific selector)
        self.delete_groups_target = self.create_group_target_selection_frame(tab, 'delete_groups')
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
        groups = self.get_target_groups('delete_groups')
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
            text="Add or remove members from groups. Choose single entry for individual operations or CSV for bulk operations.",
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

        # Mode selection
        mode_frame = ttk.LabelFrame(tab, text="Input Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.manage_members_mode = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="Single Entry",
            variable=self.manage_members_mode,
            value="single",
            command=self.toggle_manage_members_mode
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            mode_frame,
            text="CSV Bulk Import",
            variable=self.manage_members_mode,
            value="csv",
            command=self.toggle_manage_members_mode
        ).pack(side=tk.LEFT)

        # Container for mode-specific frames
        mode_container = ttk.Frame(tab)
        mode_container.pack(fill=tk.X, pady=(0, 10))

        # Single entry frame
        self.manage_members_single_frame = ttk.LabelFrame(mode_container, text="Member Details", padding="10")

        # Group selection with dropdown
        group_frame = ttk.Frame(self.manage_members_single_frame)
        group_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(group_frame, text="Group:").pack(side=tk.LEFT, padx=(0, 5))
        self.manage_members_group_combo = ttk.Combobox(group_frame, width=47, state='readonly')
        self.manage_members_group_combo.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(group_frame, text="Load Groups", command=self.load_groups_for_manage_members).pack(side=tk.LEFT)

        # Member email
        ttk.Label(self.manage_members_single_frame, text="Member Email:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.manage_members_email = ttk.Entry(self.manage_members_single_frame, width=50)
        self.manage_members_email.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

        # Role selection (for add action)
        ttk.Label(self.manage_members_single_frame, text="Role (for Add):").grid(row=2, column=0, sticky=tk.W)
        self.manage_members_role = ttk.Combobox(
            self.manage_members_single_frame,
            values=["MEMBER", "MANAGER", "OWNER"],
            state='readonly',
            width=47
        )
        self.manage_members_role.set("MEMBER")
        self.manage_members_role.grid(row=2, column=1, sticky=tk.W)

        self.manage_members_single_frame.grid_columnconfigure(1, weight=1)

        # CSV frame
        self.manage_members_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.manage_members_csv_frame, text="For Add: group,member,role (role: MEMBER, MANAGER, or OWNER)").pack(anchor=tk.W)
        ttk.Label(self.manage_members_csv_frame, text="For Remove: group,member").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(self.manage_members_csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.manage_members_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.manage_members_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_file(self.manage_members_csv_entry)
        ).pack(side=tk.LEFT)

        # Show single frame by default
        self.manage_members_single_frame.pack(fill=tk.X, expand=True)

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

    def toggle_manage_members_mode(self):
        """Toggle between single entry and CSV mode for manage members."""
        if self.manage_members_mode.get() == "single":
            self.manage_members_csv_frame.pack_forget()
            self.manage_members_single_frame.pack(fill=tk.X, expand=True)
        else:
            self.manage_members_single_frame.pack_forget()
            self.manage_members_csv_frame.pack(fill=tk.X, expand=True)

    def load_groups_for_manage_members(self):
        """Load groups into combobox for manage members."""
        # Set loading indicator
        self.manage_members_group_combo['values'] = ["Loading..."]
        self.manage_members_group_combo.set("Loading...")

        def fetch_and_populate():
            from utils.workspace_data import fetch_groups
            groups = fetch_groups()
            if groups:
                # Update combobox in main thread
                self.after(0, lambda: self.manage_members_group_combo.configure(values=sorted(groups)))
                self.after(0, lambda: self.manage_members_group_combo.set(""))
            else:
                self.after(0, lambda: self.manage_members_group_combo.configure(values=["No groups found"]))
                self.after(0, lambda: self.manage_members_group_combo.set("No groups found"))

        # Run in background thread
        import threading
        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def execute_manage_members(self):
        """Execute manage members operation."""
        mode = self.manage_members_mode.get()
        action = self.manage_members_action.get()
        dry_run = self.manage_members_dry_run.get()

        if mode == "single":
            # Single entry mode
            group = self.manage_members_group_combo.get().strip()
            member = self.manage_members_email.get().strip()
            role = self.manage_members_role.get()

            if not group:
                messagebox.showerror("Validation Error", "Group is required.")
                return
            if not member:
                messagebox.showerror("Validation Error", "Member email is required.")
                return

            # Build data dict
            if action == 'add':
                data = [{'group': group, 'member': member, 'role': role}]
            else:  # remove
                data = [{'group': group, 'member': member}]

        else:
            # CSV mode
            csv_file = self.manage_members_csv_entry.get().strip()
            if not csv_file:
                messagebox.showerror("Validation Error", "Please select a CSV file.")
                return

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

                # Confirm bulk operation
                if not self.confirm_bulk_operation(len(data), f"{action} members"):
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
                return

        # Execute
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
        group_frame = ttk.LabelFrame(tab, text="Select Group", padding="10")
        group_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(group_frame, text="Group:").pack(side=tk.LEFT, padx=(0, 5))

        self.list_members_combo = ttk.Combobox(group_frame, width=47, state='readonly')
        self.list_members_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            group_frame,
            text="Load Groups",
            command=self.load_groups_for_list_members
        ).pack(side=tk.LEFT, padx=(0, 10))

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

    def load_groups_for_list_members(self):
        """Load groups into the combobox for list members."""
        self.list_members_combo['values'] = ["Loading..."]
        self.list_members_combo.current(0)
        self.update_idletasks()

        # Fetch groups in thread
        def fetch_and_populate():
            from utils.workspace_data import fetch_groups
            groups = fetch_groups()
            if groups:
                self.after(0, lambda: self.list_members_combo.configure(values=sorted(groups)))
            else:
                self.after(0, lambda: self.list_members_combo.configure(values=["(No groups found)"]))

        import threading
        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def execute_list_members(self):
        """Execute list members operation."""
        group_email = self.list_members_combo.get().strip()
        if not group_email or group_email == "Loading..." or group_email == "(No groups found)":
            messagebox.showerror("Validation Error", "Please select a group from the dropdown.")
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
            text="Update group settings. Choose single entry for individual groups or CSV for bulk updates.",
            wraplength=800
        )
        instructions.pack(pady=(0, 10), anchor=tk.W)

        # Mode selection
        mode_frame = ttk.LabelFrame(tab, text="Input Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.group_settings_mode = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="Single Entry",
            variable=self.group_settings_mode,
            value="single",
            command=self.toggle_group_settings_mode
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            mode_frame,
            text="CSV Bulk Import",
            variable=self.group_settings_mode,
            value="csv",
            command=self.toggle_group_settings_mode
        ).pack(side=tk.LEFT)

        # Container for mode-specific frames
        mode_container = ttk.Frame(tab)
        mode_container.pack(fill=tk.X, pady=(0, 10))

        # Single entry frame
        self.group_settings_single_frame = ttk.LabelFrame(mode_container, text="Group Settings", padding="10")

        # Group selection with dropdown
        group_frame = ttk.Frame(self.group_settings_single_frame)
        group_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(group_frame, text="Group:").pack(side=tk.LEFT, padx=(0, 5))
        self.group_settings_group_combo = ttk.Combobox(group_frame, width=47, state='readonly')
        self.group_settings_group_combo.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(group_frame, text="Load Groups", command=self.load_groups_for_settings).pack(side=tk.LEFT)

        # Common group settings
        settings_info = ttk.Label(
            self.group_settings_single_frame,
            text="Leave fields empty to keep current settings unchanged.",
            font=('Arial', 9, 'italic')
        )
        settings_info.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # whoCanPostMessage
        ttk.Label(self.group_settings_single_frame, text="Who Can Post:").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.group_settings_post = ttk.Combobox(
            self.group_settings_single_frame,
            values=["", "ALL_IN_DOMAIN_CAN_POST", "ALL_MEMBERS_CAN_POST", "ALL_MANAGERS_CAN_POST", "OWNERS_ONLY"],
            width=47
        )
        self.group_settings_post.set("")
        self.group_settings_post.grid(row=2, column=1, sticky=tk.W, pady=(0, 10))

        # whoCanViewGroup
        ttk.Label(self.group_settings_single_frame, text="Who Can View:").grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        self.group_settings_view = ttk.Combobox(
            self.group_settings_single_frame,
            values=["", "ALL_IN_DOMAIN_CAN_VIEW", "ALL_MEMBERS_CAN_VIEW", "ALL_MANAGERS_CAN_VIEW", "OWNERS_ONLY"],
            width=47
        )
        self.group_settings_view.set("")
        self.group_settings_view.grid(row=3, column=1, sticky=tk.W, pady=(0, 10))

        # whoCanJoin
        ttk.Label(self.group_settings_single_frame, text="Who Can Join:").grid(row=4, column=0, sticky=tk.W)
        self.group_settings_join = ttk.Combobox(
            self.group_settings_single_frame,
            values=["", "CAN_REQUEST_TO_JOIN", "ALL_IN_DOMAIN_CAN_JOIN", "INVITED_CAN_JOIN", "ANYONE_CAN_JOIN"],
            width=47
        )
        self.group_settings_join.set("")
        self.group_settings_join.grid(row=4, column=1, sticky=tk.W)

        self.group_settings_single_frame.grid_columnconfigure(1, weight=1)

        # CSV frame
        self.group_settings_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.group_settings_csv_frame, text="CSV Format: group,whoCanPostMessage,whoCanViewGroup,whoCanJoin").pack(anchor=tk.W)
        ttk.Label(self.group_settings_csv_frame, text="Values: ALL_IN_DOMAIN_CAN_POST, ALL_MEMBERS_CAN_POST, OWNERS_ONLY, etc.").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(self.group_settings_csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.group_settings_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.group_settings_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_file(self.group_settings_csv_entry)
        ).pack(side=tk.LEFT)

        # Show single frame by default
        self.group_settings_single_frame.pack(fill=tk.X, expand=True)

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

    def toggle_group_settings_mode(self):
        """Toggle between single entry and CSV mode for group settings."""
        if self.group_settings_mode.get() == "single":
            self.group_settings_csv_frame.pack_forget()
            self.group_settings_single_frame.pack(fill=tk.X, expand=True)
        else:
            self.group_settings_single_frame.pack_forget()
            self.group_settings_csv_frame.pack(fill=tk.X, expand=True)

    def load_groups_for_settings(self):
        """Load groups into combobox for group settings."""
        # Set loading indicator
        self.group_settings_group_combo['values'] = ["Loading..."]
        self.group_settings_group_combo.set("Loading...")

        def fetch_and_populate():
            from utils.workspace_data import fetch_groups
            groups = fetch_groups()
            if groups:
                # Update combobox in main thread
                self.after(0, lambda: self.group_settings_group_combo.configure(values=sorted(groups)))
                self.after(0, lambda: self.group_settings_group_combo.set(""))
            else:
                self.after(0, lambda: self.group_settings_group_combo.configure(values=["No groups found"]))
                self.after(0, lambda: self.group_settings_group_combo.set("No groups found"))

        # Run in background thread
        import threading
        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def execute_group_settings(self):
        """Execute group settings operation."""
        mode = self.group_settings_mode.get()
        dry_run = self.group_settings_dry_run.get()

        if mode == "single":
            # Single entry mode
            group = self.group_settings_group_combo.get().strip()
            who_can_post = self.group_settings_post.get().strip()
            who_can_view = self.group_settings_view.get().strip()
            who_can_join = self.group_settings_join.get().strip()

            if not group:
                messagebox.showerror("Validation Error", "Group is required.")
                return

            # Build settings dict with only non-empty values
            settings = {'group': group}
            if who_can_post:
                settings['whoCanPostMessage'] = who_can_post
            if who_can_view:
                settings['whoCanViewGroup'] = who_can_view
            if who_can_join:
                settings['whoCanJoin'] = who_can_join

            # At least one setting must be provided
            if len(settings) == 1:  # Only 'group' key
                messagebox.showerror("Validation Error", "At least one setting must be provided.")
                return

            settings_data = [settings]

        else:
            # CSV mode
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

                # Confirm bulk operation
                if not self.confirm_bulk_operation(len(settings_data), "update group settings"):
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
                return

        # Execute
        self.run_operation(
            groups_module.update_group_settings,
            self.group_settings_progress,
            settings_data,
            dry_run=dry_run
        )

    # ==================== TAB 6: GROUP ALIASES ====================

    def create_group_aliases_tab(self):
        """Create the Group Aliases tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Group Aliases")

        # Instructions
        instructions = ttk.Label(
            tab,
            text="Add or remove group aliases. Choose single entry for individual operations or CSV for bulk operations.",
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

        # Mode selection
        mode_frame = ttk.LabelFrame(tab, text="Input Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.group_aliases_mode = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="Single Entry",
            variable=self.group_aliases_mode,
            value="single",
            command=self.toggle_group_aliases_mode
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            mode_frame,
            text="CSV Bulk Import",
            variable=self.group_aliases_mode,
            value="csv",
            command=self.toggle_group_aliases_mode
        ).pack(side=tk.LEFT)

        # Container for mode-specific frames
        mode_container = ttk.Frame(tab)
        mode_container.pack(fill=tk.X, pady=(0, 10))

        # Single entry frame
        self.group_aliases_single_frame = ttk.LabelFrame(mode_container, text="Alias Details", padding="10")

        # Group selection with dropdown (for add action)
        group_frame = ttk.Frame(self.group_aliases_single_frame)
        group_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(group_frame, text="Group (for Add):").pack(side=tk.LEFT, padx=(0, 5))
        self.group_aliases_group_combo = ttk.Combobox(group_frame, width=40, state='readonly')
        self.group_aliases_group_combo.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(group_frame, text="Load Groups", command=self.load_groups_for_aliases).pack(side=tk.LEFT)

        # Alias entry
        ttk.Label(self.group_aliases_single_frame, text="Alias:").grid(row=1, column=0, sticky=tk.W)
        self.group_aliases_alias = ttk.Entry(self.group_aliases_single_frame, width=50)
        self.group_aliases_alias.grid(row=1, column=1, sticky=(tk.W, tk.E))

        self.group_aliases_single_frame.grid_columnconfigure(1, weight=1)

        # CSV frame
        self.group_aliases_csv_frame = ttk.LabelFrame(mode_container, text="CSV File", padding="10")

        ttk.Label(self.group_aliases_csv_frame, text="For Add: group,alias").pack(anchor=tk.W)
        ttk.Label(self.group_aliases_csv_frame, text="For Remove: Just list aliases (header: alias)").pack(anchor=tk.W, pady=(5, 10))

        csv_input_frame = ttk.Frame(self.group_aliases_csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.group_aliases_csv_entry = ttk.Entry(csv_input_frame, width=60)
        self.group_aliases_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_file(self.group_aliases_csv_entry)
        ).pack(side=tk.LEFT)

        # Show single frame by default
        self.group_aliases_single_frame.pack(fill=tk.X, expand=True)

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

    def toggle_group_aliases_mode(self):
        """Toggle between single entry and CSV mode for group aliases."""
        if self.group_aliases_mode.get() == "single":
            self.group_aliases_csv_frame.pack_forget()
            self.group_aliases_single_frame.pack(fill=tk.X, expand=True)
        else:
            self.group_aliases_single_frame.pack_forget()
            self.group_aliases_csv_frame.pack(fill=tk.X, expand=True)

    def load_groups_for_aliases(self):
        """Load groups into combobox for group aliases."""
        # Set loading indicator
        self.group_aliases_group_combo['values'] = ["Loading..."]
        self.group_aliases_group_combo.set("Loading...")

        def fetch_and_populate():
            from utils.workspace_data import fetch_groups
            groups = fetch_groups()
            if groups:
                # Update combobox in main thread
                self.after(0, lambda: self.group_aliases_group_combo.configure(values=sorted(groups)))
                self.after(0, lambda: self.group_aliases_group_combo.set(""))
            else:
                self.after(0, lambda: self.group_aliases_group_combo.configure(values=["No groups found"]))
                self.after(0, lambda: self.group_aliases_group_combo.set("No groups found"))

        # Run in background thread
        import threading
        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def execute_group_aliases(self):
        """Execute group aliases operation."""
        mode = self.group_aliases_mode.get()
        action = self.group_aliases_action.get()
        dry_run = self.group_aliases_dry_run.get()

        if mode == "single":
            # Single entry mode
            alias = self.group_aliases_alias.get().strip()

            if not alias:
                messagebox.showerror("Validation Error", "Alias is required.")
                return

            if action == 'add':
                group = self.group_aliases_group_combo.get().strip()
                if not group:
                    messagebox.showerror("Validation Error", "Group is required for add action.")
                    return
                data = [{'group': group, 'alias': alias}]
            else:  # remove
                data = [{'alias': alias}]

        else:
            # CSV mode
            csv_file = self.group_aliases_csv_entry.get().strip()
            if not csv_file:
                messagebox.showerror("Validation Error", "Please select a CSV file.")
                return

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
                else:
                    # Validate remove format
                    for row in data:
                        if 'alias' not in row or not row['alias']:
                            messagebox.showerror("Validation Error", "Missing 'alias' field in CSV.")
                            return

                # Confirm bulk operation
                if not self.confirm_bulk_operation(len(data), f"{action} group aliases"):
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
                return

        # Execute
        if action == 'add':
            self.run_operation(
                groups_module.add_group_alias,
                self.group_aliases_progress,
                data,
                dry_run=dry_run
            )
        else:  # remove
            self.run_operation(
                groups_module.remove_group_alias,
                self.group_aliases_progress,
                data,
                dry_run=dry_run
            )

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
        user_frame = ttk.LabelFrame(tab, text="Select User", padding="10")
        user_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(user_frame, text="User:").pack(side=tk.LEFT, padx=(0, 5))

        self.user_groups_combo = ttk.Combobox(user_frame, width=47, state='readonly')
        self.user_groups_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            user_frame,
            text="Load Users",
            command=self.load_users_for_user_groups
        ).pack(side=tk.LEFT, padx=(0, 10))

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

    def load_users_for_user_groups(self):
        """Load users into the combobox for user groups."""
        self.user_groups_combo['values'] = ["Loading..."]
        self.user_groups_combo.current(0)
        self.update_idletasks()

        # Fetch users in thread
        def fetch_and_populate():
            from utils.workspace_data import fetch_users
            users = fetch_users()
            if users:
                self.after(0, lambda: self.user_groups_combo.configure(values=sorted(users)))
            else:
                self.after(0, lambda: self.user_groups_combo.configure(values=["(No users found)"]))

        import threading
        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def execute_user_groups(self):
        """Execute user groups operation."""
        user_email = self.user_groups_combo.get().strip()
        if not user_email or user_email == "Loading..." or user_email == "(No users found)":
            messagebox.showerror("Validation Error", "Please select a user from the dropdown.")
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
