"""
Email Operations Window for GAM Admin Tool.

Provides a tabbed interface for all email-related operations including
message deletion, delegate management, signatures, forwarding, labels, and filters.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import re

from gui.base_operation_window import BaseOperationWindow
from modules import email as email_module


class EmailWindow(BaseOperationWindow):
    """
    Email Operations window with tabbed interface.

    Provides 6 tabs for different email operations:
    - Delete Messages
    - Manage Delegates
    - Manage Signatures
    - Manage Forwarding
    - Manage Labels
    - Manage Filters
    """

    def __init__(self, parent):
        """
        Initialize the Email Operations window.

        Args:
            parent: The parent tkinter widget
        """
        super().__init__(parent, "Email Operations", "950x750", (800, 600))

    def create_operation_tabs(self):
        """Create all email operation tabs."""
        self.create_delete_messages_tab()
        self.create_delegates_tab()
        self.create_signatures_tab()
        self.create_forwarding_tab()
        self.create_labels_tab()
        self.create_filters_tab()

        # Auto-load comboboxes on window initialization
        self.after(100, self.initialize_comboboxes)

    # ==================== TAB 1: DELETE MESSAGES ====================

    def create_delete_messages_tab(self):
        """Create the Delete Messages tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Delete Messages")

        # Target selection
        target_frame = self.create_combobox_target_selection_frame(tab, "delete_msg")
        target_frame.pack(fill=tk.X, pady=(0, 10))

        # Operation parameters
        params_frame = ttk.LabelFrame(tab, text="Delete Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))

        # Query string
        ttk.Label(params_frame, text="Query String:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.delete_query_entry = ttk.Entry(params_frame, width=50)
        self.delete_query_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(5, 0))
        ttk.Label(params_frame, text='(e.g., "from:sender@example.com" or "subject:test")',
                 font=('Arial', 8), foreground='gray').grid(row=1, column=1, sticky=tk.W)

        # Date range (optional)
        ttk.Label(params_frame, text="Date Range (Optional):").grid(row=2, column=0, sticky=tk.W, pady=5)
        date_frame = ttk.Frame(params_frame)
        date_frame.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(date_frame, text="From:").pack(side=tk.LEFT, padx=(0, 5))
        self.delete_date_from = ttk.Entry(date_frame, width=12)
        self.delete_date_from.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(date_frame, text="To:").pack(side=tk.LEFT, padx=(0, 5))
        self.delete_date_to = ttk.Entry(date_frame, width=12)
        self.delete_date_to.pack(side=tk.LEFT)

        ttk.Label(params_frame, text="Format: YYYY/MM/DD",
                 font=('Arial', 8), foreground='gray').grid(row=3, column=1, sticky=tk.W)

        params_frame.grid_columnconfigure(1, weight=1)

        # Execute button and dry-run checkbox
        btn_frame = ttk.Frame(params_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Execute Delete",
            command=lambda: self.execute_delete_messages(),
            width=20
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Dry run checkbox
        self.delete_messages_dry_run = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run (preview only)",
            variable=self.delete_messages_dry_run
        ).pack(side=tk.LEFT)

        # Progress and results
        self.delete_progress_frame = self.create_progress_frame(tab)
        self.delete_progress_frame.pack(fill=tk.BOTH, expand=True)

    def execute_delete_messages(self):
        """Execute delete messages operation."""
        if self.operation_running:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return

        # Check if group was selected
        target_var = getattr(self, "delete_msg_target_var")
        target_type = target_var.get()

        # Get target users
        users = self.get_target_users("delete_msg")
        if not users:
            return

        # If "group" was selected, fetch group members instead of using group email
        if target_type == "group":
            group_email = users[0]  # get_target_users returns group email in list

            # Fetch group members
            from utils.workspace_data import fetch_group_members
            members = fetch_group_members(group_email)

            if not members:
                messagebox.showerror("Error", f"Failed to fetch members from group {group_email} or group has no members.")
                return

            # Replace group email with member emails
            users = members
            messagebox.showinfo("Group Members", f"Fetched {len(users)} members from group {group_email}")

        # Get query
        query = self.delete_query_entry.get().strip()
        if not query:
            messagebox.showerror("Validation Error", "Please enter a query string.")
            return

        # Get date range
        date_from = self.delete_date_from.get().strip() or None
        date_to = self.delete_date_to.get().strip() or None

        # Validate date format if provided
        if date_from and not re.match(r'\d{4}/\d{2}/\d{2}', date_from):
            messagebox.showerror("Validation Error", "Date From must be in YYYY/MM/DD format.")
            return
        if date_to and not re.match(r'\d{4}/\d{2}/\d{2}', date_to):
            messagebox.showerror("Validation Error", "Date To must be in YYYY/MM/DD format.")
            return

        # Confirmation for multiple users
        dry_run = self.delete_messages_dry_run.get()
        if len(users) > 1 and not dry_run:
            if not messagebox.askyesno(
                "Confirm Operation",
                f"You are about to delete messages for {len(users)} users.\n\nProceed?"
            ):
                return

        # Execute
        self.run_operation(
            email_module.delete_messages,
            self.delete_progress_frame,
            users, query, date_from, date_to,
            dry_run=dry_run
        )

    # ==================== TAB 2: MANAGE DELEGATES ====================

    def create_delegates_tab(self):
        """Create the Manage Delegates tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Delegates")

        # Target selection (simplified - no "All Users" or "Group")
        target_frame = self.create_combobox_user_target_selection_frame(tab, "delegates")
        target_frame.pack(fill=tk.X, pady=(0, 10))

        # Operation parameters
        params_frame = ttk.LabelFrame(tab, text="Delegate Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))

        # Action selection
        self.delegate_action = tk.StringVar(value="add")
        ttk.Radiobutton(params_frame, text="Add Delegate", variable=self.delegate_action,
                       value="add").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(params_frame, text="Remove Delegate", variable=self.delegate_action,
                       value="remove").grid(row=0, column=1, sticky=tk.W, pady=5)

        # Delegate email with dropdown
        ttk.Label(params_frame, text="Delegate Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        delegate_email_frame = ttk.Frame(params_frame)
        delegate_email_frame.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(5, 0))

        self.delegate_email_entry = ttk.Combobox(delegate_email_frame)
        self.delegate_email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            delegate_email_frame,
            text="Load Users",
            command=self.load_users_for_delegates
        ).pack(side=tk.LEFT)

        params_frame.grid_columnconfigure(1, weight=1)

        # Execute button
        execute_btn = ttk.Button(
            params_frame,
            text="Execute",
            command=lambda: self.execute_delegates(),
            width=20
        )
        execute_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Progress and results
        self.delegates_progress_frame = self.create_progress_frame(tab)
        self.delegates_progress_frame.pack(fill=tk.BOTH, expand=True)

    def load_users_for_delegates(self):
        """Load users for the delegate email dropdown."""
        self.delegate_email_entry['values'] = ["Loading..."]
        self.delegate_email_entry.set("Loading...")

        def fetch_and_populate():
            from utils.workspace_data import fetch_users
            users = fetch_users()
            if users:
                sorted_users = sorted(users)
                self.after(0, lambda: self.delegate_email_entry.configure(values=sorted_users))
                self.after(0, lambda: self.delegate_email_entry.set(""))
                self.after(0, lambda: self.enable_standalone_fuzzy_search(self.delegate_email_entry, sorted_users))
            else:
                self.after(0, lambda: self.delegate_email_entry.configure(values=[]))
                self.after(0, lambda: self.delegate_email_entry.set(""))

        import threading
        threading.Thread(target=fetch_and_populate, daemon=True).start()


    def execute_delegates(self):
        """Execute delegate operation."""
        if self.operation_running:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return

        users = self.get_target_users("delegates")
        if not users:
            return

        delegate_email = self.delegate_email_entry.get().strip()
        if not delegate_email or '@' not in delegate_email:
            messagebox.showerror("Validation Error", "Please enter a valid delegate email address.")
            return

        action = self.delegate_action.get()

        # Confirmation for multiple users
        if len(users) > 1:
            action_text = "add delegate to" if action == "add" else "remove delegate from"
            if not messagebox.askyesno(
                "Confirm Operation",
                f"You are about to {action_text} {len(users)} users.\n\nProceed?"
            ):
                return

        # Execute
        if action == "add":
            self.run_operation(
                email_module.add_delegate,
                self.delegates_progress_frame,
                users, delegate_email
            )
        else:
            self.run_operation(
                email_module.remove_delegate,
                self.delegates_progress_frame,
                users, delegate_email
            )

    # ==================== TAB 3: MANAGE SIGNATURES ====================

    def create_signatures_tab(self):
        """Create the Manage Signatures tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Signatures")

        # Target selection
        target_frame = self.create_combobox_target_selection_frame(tab, "signatures")
        target_frame.pack(fill=tk.X, pady=(0, 10))

        # Operation parameters
        params_frame = ttk.LabelFrame(tab, text="Signature Parameters", padding="10")
        params_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Action selection (set only)
        self.signature_action = tk.StringVar(value="set")

        # Signature input method
        self.signature_input_frame = ttk.Frame(params_frame)
        self.signature_input_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=10)

        self.signature_method = tk.StringVar(value="text")
        ttk.Radiobutton(self.signature_input_frame, text="Enter HTML", variable=self.signature_method,
                       value="text", command=self.toggle_signature_method).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(self.signature_input_frame, text="Upload File", variable=self.signature_method,
                       value="file", command=self.toggle_signature_method).pack(side=tk.LEFT)

        # Text entry
        self.signature_text_frame = ttk.Frame(params_frame)
        self.signature_text_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=5)

        ttk.Label(self.signature_text_frame, text="HTML Content:").pack(anchor=tk.W)
        self.signature_text = scrolledtext.ScrolledText(self.signature_text_frame, height=8, width=60)
        self.signature_text.pack(fill=tk.BOTH, expand=True)

        # File entry
        self.signature_file_frame = ttk.Frame(params_frame)
        self.signature_file_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=5)

        ttk.Label(self.signature_file_frame, text="HTML File:").pack(side=tk.LEFT, padx=(0, 5))
        self.signature_file_entry = ttk.Entry(self.signature_file_frame, width=40)
        self.signature_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(self.signature_file_frame, text="Browse...",
                  command=self.browse_signature_file).pack(side=tk.LEFT)

        params_frame.grid_columnconfigure(0, weight=1)
        params_frame.grid_rowconfigure(2, weight=1)

        # Execute button
        execute_btn = ttk.Button(
            params_frame,
            text="Execute",
            command=lambda: self.execute_signatures(),
            width=20
        )
        execute_btn.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # Progress and results
        self.signatures_progress_frame = self.create_progress_frame(tab)
        self.signatures_progress_frame.pack(fill=tk.BOTH, expand=True)

        # Initial toggle
        self.toggle_signature_method()

    def toggle_signature_method(self):
        """Toggle between text and file input for signature."""

        if self.signature_method.get() == "text":
            self.signature_text_frame.grid()
            self.signature_file_frame.grid_remove()
        else:
            self.signature_text_frame.grid_remove()
            self.signature_file_frame.grid()

    def browse_signature_file(self):
        """Open file dialog to select signature HTML file."""
        filename = filedialog.askopenfilename(
            title="Select Signature HTML File",
            filetypes=[("HTML files", "*.html *.htm"), ("All files", "*.*")]
        )
        if filename:
            self.signature_file_entry.delete(0, tk.END)
            self.signature_file_entry.insert(0, filename)

    def execute_signatures(self):
        """Execute signature operation."""
        if self.operation_running:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return

        users = self.get_target_users("signatures")
        if not users:
            return

        # Get signature HTML
        if self.signature_method.get() == "text":
            signature_html = self.signature_text.get("1.0", tk.END).strip()
            if not signature_html:
                messagebox.showerror("Validation Error", "Please enter signature HTML content.")
                return
        else:
            file_path = self.signature_file_entry.get().strip()
            if not file_path:
                messagebox.showerror("Validation Error", "Please select a signature HTML file.")
                return
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    signature_html = f.read()
            except Exception as e:
                messagebox.showerror("File Error", f"Failed to read file: {e}")
                return

        # Confirmation for multiple users
        if len(users) > 1:
            if not messagebox.askyesno(
                "Confirm Operation",
                f"You are about to set signature for {len(users)} users.\n\nProceed?"
            ):
                return

        # Execute
        self.run_operation(
            email_module.set_signature,
            self.signatures_progress_frame,
            users, signature_html
        )

    # ==================== TAB 4: MANAGE FORWARDING ====================

    def create_forwarding_tab(self):
        """Create the Manage Forwarding tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Forwarding")

        # Target selection (simplified - no "All Users" or "Group")
        target_frame = self.create_combobox_user_target_selection_frame(tab, "forwarding")
        target_frame.pack(fill=tk.X, pady=(0, 10))

        # Operation parameters
        params_frame = ttk.LabelFrame(tab, text="Forwarding Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))

        # Action selection
        self.forwarding_action = tk.StringVar(value="enable")
        ttk.Radiobutton(params_frame, text="Enable Forwarding", variable=self.forwarding_action,
                       value="enable", command=self.toggle_forwarding_input).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(params_frame, text="Disable Forwarding", variable=self.forwarding_action,
                       value="disable", command=self.toggle_forwarding_input).grid(row=0, column=1, sticky=tk.W, pady=5)

        # Forward to email
        self.forwarding_input_frame = ttk.Frame(params_frame)
        self.forwarding_input_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)

        ttk.Label(self.forwarding_input_frame, text="Forward To:").pack(side=tk.LEFT, padx=(0, 5))
        self.forward_to_entry = ttk.Entry(self.forwarding_input_frame, width=40)
        self.forward_to_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        params_frame.grid_columnconfigure(1, weight=1)

        # Execute button
        execute_btn = ttk.Button(
            params_frame,
            text="Execute",
            command=lambda: self.execute_forwarding(),
            width=20
        )
        execute_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Progress and results
        self.forwarding_progress_frame = self.create_progress_frame(tab)
        self.forwarding_progress_frame.pack(fill=tk.BOTH, expand=True)

    def toggle_forwarding_input(self):
        """Toggle forwarding email input based on action."""
        if self.forwarding_action.get() == "enable":
            self.forwarding_input_frame.grid()
        else:
            self.forwarding_input_frame.grid_remove()

    def execute_forwarding(self):
        """Execute forwarding operation."""
        if self.operation_running:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return

        users = self.get_target_users("forwarding")
        if not users:
            return

        action = self.forwarding_action.get()

        if action == "enable":
            forward_to = self.forward_to_entry.get().strip()
            if not forward_to or '@' not in forward_to:
                messagebox.showerror("Validation Error", "Please enter a valid email address to forward to.")
                return

        # Confirmation for multiple users
        if len(users) > 1:
            action_text = "enable forwarding for" if action == "enable" else "disable forwarding for"
            if not messagebox.askyesno(
                "Confirm Operation",
                f"You are about to {action_text} {len(users)} users.\n\nProceed?"
            ):
                return

        # Execute
        if action == "enable":
            self.run_operation(
                email_module.enable_forwarding,
                self.forwarding_progress_frame,
                users, forward_to
            )
        else:
            self.run_operation(
                email_module.disable_forwarding,
                self.forwarding_progress_frame,
                users
            )

    # ==================== TAB 5: MANAGE LABELS ====================

    def create_labels_tab(self):
        """Create the Manage Labels tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Labels")

        # Target selection
        target_frame = self.create_combobox_target_selection_frame(tab, "labels")
        target_frame.pack(fill=tk.X, pady=(0, 10))

        # Operation parameters
        params_frame = ttk.LabelFrame(tab, text="Label Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))

        # Action selection
        self.label_action = tk.StringVar(value="create")
        ttk.Radiobutton(params_frame, text="Create Label", variable=self.label_action,
                       value="create", command=self.toggle_label_input).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(params_frame, text="Delete Label", variable=self.label_action,
                       value="delete", command=self.toggle_label_input).grid(row=0, column=1, sticky=tk.W, pady=5)

        # Create label frame (text entry)
        self.label_create_frame = ttk.Frame(params_frame)
        self.label_create_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)

        ttk.Label(self.label_create_frame, text="Label Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.label_name_entry = ttk.Entry(self.label_create_frame, width=40)
        self.label_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Delete label frame (dropdown)
        self.label_delete_frame = ttk.Frame(params_frame)
        self.label_delete_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)

        # Label dropdown with Load button
        label_row = ttk.Frame(self.label_delete_frame)
        label_row.pack(fill=tk.X)
        ttk.Label(label_row, text="Label:").pack(side=tk.LEFT, padx=(0, 5))
        self.label_name_combo = ttk.Combobox(label_row, width=50, state='readonly')
        self.label_name_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(label_row, text="Load Labels", command=self.load_labels_for_user).pack(side=tk.LEFT)

        params_frame.grid_columnconfigure(1, weight=1)

        # Execute button
        execute_btn = ttk.Button(
            params_frame,
            text="Execute",
            command=lambda: self.execute_labels(),
            width=20
        )
        execute_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Progress and results
        self.labels_progress_frame = self.create_progress_frame(tab)
        self.labels_progress_frame.pack(fill=tk.BOTH, expand=True)

        # Initial toggle
        self.toggle_label_input()

    def toggle_label_input(self):
        """Toggle label input based on action."""
        if self.label_action.get() == "create":
            self.label_create_frame.grid()
            self.label_delete_frame.grid_remove()
        else:
            self.label_create_frame.grid_remove()
            self.label_delete_frame.grid()

    def load_labels_for_user(self):
        """Load labels for the user from target selection."""
        users = self.get_target_users("labels")
        if not users:
            return

        # Only use the first user for loading labels
        user_email = users[0]

        # Set loading indicator
        self.label_name_combo['values'] = ["Loading..."]
        self.label_name_combo.set("Loading...")
        self.update_idletasks()

        def fetch_and_populate():
            import modules.email as email_module
            labels = email_module.list_labels(user_email)
            if labels:
                self.after(0, lambda: self.label_name_combo.configure(values=sorted(labels)))
                self.after(0, lambda: self.label_name_combo.set("" if labels else "No labels found"))
            else:
                self.after(0, lambda: self.label_name_combo.configure(values=["No labels found"]))
                self.after(0, lambda: self.label_name_combo.set("No labels found"))

        # Run in background thread
        import threading
        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def execute_labels(self):
        """Execute label operation."""
        if self.operation_running:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return

        # Check if group was selected
        target_var = getattr(self, "labels_target_var")
        target_type = target_var.get()

        users = self.get_target_users("labels")
        if not users:
            return

        # If "group" was selected, fetch group members instead of using group email
        if target_type == "group":
            group_email = users[0]  # get_target_users returns group email in list

            # Fetch group members
            from utils.workspace_data import fetch_group_members
            members = fetch_group_members(group_email)

            if not members:
                messagebox.showerror("Error", f"Failed to fetch members from group {group_email} or group has no members.")
                return

            # Replace group email with member emails
            users = members
            messagebox.showinfo("Group Members", f"Fetched {len(users)} members from group {group_email}")

        action = self.label_action.get()

        # Get label name from appropriate widget
        if action == "create":
            label_name = self.label_name_entry.get().strip()
            if not label_name:
                messagebox.showerror("Validation Error", "Please enter a label name.")
                return
        else:  # delete
            label_name = self.label_name_combo.get().strip()
            if not label_name or label_name in ["Loading...", "No labels found"]:
                messagebox.showerror("Validation Error", "Please select a valid label.")
                return

        # Confirmation for multiple users
        if len(users) > 1:
            action_text = f"{action} label for"
            if not messagebox.askyesno(
                "Confirm Operation",
                f"You are about to {action_text} {len(users)} users.\n\nProceed?"
            ):
                return

        # Execute
        if action == "create":
            self.run_operation(
                email_module.create_label,
                self.labels_progress_frame,
                users, label_name
            )
        else:
            self.run_operation(
                email_module.delete_label,
                self.labels_progress_frame,
                users, label_name
            )

    # ==================== TAB 6: MANAGE FILTERS ====================

    def create_filters_tab(self):
        """Create the Manage Filters tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Filters")

        # Target selection
        target_frame = self.create_combobox_target_selection_frame(tab, "filters")
        target_frame.pack(fill=tk.X, pady=(0, 10))

        # Operation parameters
        params_frame = ttk.LabelFrame(tab, text="Filter Parameters", padding="10")
        params_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Action selection
        self.filter_action = tk.StringVar(value="create")
        ttk.Radiobutton(params_frame, text="Create Filter", variable=self.filter_action,
                       value="create", command=self.toggle_filter_input).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(params_frame, text="Delete Filter", variable=self.filter_action,
                       value="delete", command=self.toggle_filter_input).grid(row=0, column=1, sticky=tk.W, pady=5)

        # Create filter frame
        self.filter_create_frame = ttk.Frame(params_frame)
        self.filter_create_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)

        ttk.Label(self.filter_create_frame, text="From:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.filter_from_entry = ttk.Entry(self.filter_create_frame, width=30)
        self.filter_from_entry.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        ttk.Label(self.filter_create_frame, text="To:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.filter_to_entry = ttk.Entry(self.filter_create_frame, width=30)
        self.filter_to_entry.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        ttk.Label(self.filter_create_frame, text="Subject:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.filter_subject_entry = ttk.Entry(self.filter_create_frame, width=30)
        self.filter_subject_entry.grid(row=2, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        ttk.Label(self.filter_create_frame, text="Has Words:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.filter_words_entry = ttk.Entry(self.filter_create_frame, width=30)
        self.filter_words_entry.grid(row=3, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        ttk.Label(self.filter_create_frame, text="Apply Label:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.filter_label_entry = ttk.Entry(self.filter_create_frame, width=30)
        self.filter_label_entry.grid(row=4, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        self.filter_create_frame.grid_columnconfigure(1, weight=1)

        # Delete filter frame
        self.filter_delete_frame = ttk.Frame(params_frame)
        self.filter_delete_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)

        # Filter dropdown with Load button
        filter_row = ttk.Frame(self.filter_delete_frame)
        filter_row.pack(fill=tk.X)
        ttk.Label(filter_row, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_id_combo = ttk.Combobox(filter_row, width=50, state='readonly')
        self.filter_id_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(filter_row, text="Load Filters", command=self.load_filters_for_user).pack(side=tk.LEFT)

        params_frame.grid_columnconfigure(0, weight=1)

        # Execute button
        execute_btn = ttk.Button(
            params_frame,
            text="Execute",
            command=lambda: self.execute_filters(),
            width=20
        )
        execute_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Progress and results
        self.filters_progress_frame = self.create_progress_frame(tab)
        self.filters_progress_frame.pack(fill=tk.BOTH, expand=True)

        # Initial toggle
        self.toggle_filter_input()

    def toggle_filter_input(self):
        """Toggle filter input based on action."""
        if self.filter_action.get() == "create":
            self.filter_create_frame.grid()
            self.filter_delete_frame.grid_remove()
        else:
            self.filter_create_frame.grid_remove()
            self.filter_delete_frame.grid()

    def load_filters_for_user(self):
        """Load filters for the user from target selection."""
        users = self.get_target_users("filters")
        if not users:
            return

        # Only use the first user for loading filters
        user_email = users[0]

        # Set loading indicator
        self.filter_id_combo['values'] = ["Loading..."]
        self.filter_id_combo.set("Loading...")
        self.update_idletasks()

        def fetch_and_populate():
            import modules.email as email_module
            filters = email_module.list_filters(user_email)
            if filters:
                # Store filter data for later extraction
                self.filter_data = filters
                # Display filter with context: "ID: description"
                filter_display = [f"{f[0]}: {f[1]}" if f[1] != f[0] else f[0] for f in filters]
                self.after(0, lambda: self.filter_id_combo.configure(values=filter_display))
                self.after(0, lambda: self.filter_id_combo.set("" if filter_display else "No filters found"))
            else:
                self.filter_data = []
                self.after(0, lambda: self.filter_id_combo.configure(values=["No filters found"]))
                self.after(0, lambda: self.filter_id_combo.set("No filters found"))

        # Run in background thread
        import threading
        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def execute_filters(self):
        """Execute filter operation."""
        if self.operation_running:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return

        # Check if group was selected
        target_var = getattr(self, "filters_target_var")
        target_type = target_var.get()

        users = self.get_target_users("filters")
        if not users:
            return

        # If "group" was selected, fetch group members instead of using group email
        if target_type == "group":
            group_email = users[0]  # get_target_users returns group email in list

            # Fetch group members
            from utils.workspace_data import fetch_group_members
            members = fetch_group_members(group_email)

            if not members:
                messagebox.showerror("Error", f"Failed to fetch members from group {group_email} or group has no members.")
                return

            # Replace group email with member emails
            users = members
            messagebox.showinfo("Group Members", f"Fetched {len(users)} members from group {group_email}")

        action = self.filter_action.get()

        if action == "create":
            # Get filter criteria (at least one must be provided)
            from_addr = self.filter_from_entry.get().strip() or None
            to_addr = self.filter_to_entry.get().strip() or None
            subject = self.filter_subject_entry.get().strip() or None
            has_words = self.filter_words_entry.get().strip() or None
            action_label = self.filter_label_entry.get().strip() or None

            if not any([from_addr, to_addr, subject, has_words]):
                messagebox.showerror("Validation Error",
                                   "Please provide at least one filter criteria (From, To, Subject, or Has Words).")
                return
        else:
            filter_display = self.filter_id_combo.get().strip()
            if not filter_display or filter_display in ["Loading...", "No filters found"]:
                messagebox.showerror("Validation Error", "Please select a valid filter.")
                return

            # Extract filter ID from display string (format: "ID: description" or just "ID")
            if ':' in filter_display:
                filter_id = filter_display.split(':', 1)[0].strip()
            else:
                filter_id = filter_display

        # Confirmation for multiple users
        if len(users) > 1:
            action_text = f"{action} filter for"
            if not messagebox.askyesno(
                "Confirm Operation",
                f"You are about to {action_text} {len(users)} users.\n\nProceed?"
            ):
                return

        # Execute
        if action == "create":
            self.run_operation(
                email_module.create_filter,
                self.filters_progress_frame,
                users, from_addr, to_addr, subject, has_words, action_label
            )
        else:
            self.run_operation(
                email_module.delete_filter,
                self.filters_progress_frame,
                users, filter_id
            )

    # ==================== COMBOBOX INITIALIZATION ====================

    def initialize_comboboxes(self):
        """Auto-load all comboboxes on window initialization."""
        # Load users for target selection comboboxes
        self.load_users_combobox('delete_msg')
        self.load_users_combobox('delegates')
        self.load_users_combobox('signatures')
        self.load_users_combobox('forwarding')
        self.load_users_combobox('labels')
        self.load_users_combobox('filters')

        # Load users for delegates combobox (the delegate email field)
        self.load_users_for_delegates()
