"""
Email Operations Window for GAM Admin Tool.

Provides a tabbed interface for all email-related operations including
message deletion, delegate management, signatures, forwarding, labels, and filters.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
import re

from modules import email as email_module
from utils.workspace_data import fetch_users, fetch_groups
from utils.csv_handler import validate_csv, read_csv_emails
from utils.logger import read_log_file, get_log_file_path


class EmailWindow(tk.Toplevel):
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
        super().__init__(parent)

        self.title("Email Operations")
        self.geometry("950x750")
        self.minsize(800, 600)

        # Center the window
        self.transient(parent)

        # Variables for tracking state
        self.operation_running = False
        self.current_thread = None

        # Create UI
        self.create_widgets()

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        """Create and layout all widgets."""
        # Main container
        main_container = ttk.Frame(self, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_container,
            text="Email Operations",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create all tabs
        self.create_delete_messages_tab()
        self.create_delegates_tab()
        self.create_signatures_tab()
        self.create_forwarding_tab()
        self.create_labels_tab()
        self.create_filters_tab()

        # Bottom buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        close_button = ttk.Button(
            button_frame,
            text="Close",
            command=self.destroy,
            width=15
        )
        close_button.pack(side=tk.RIGHT, padx=5)

    # ==================== TAB 1: DELETE MESSAGES ====================

    def create_delete_messages_tab(self):
        """Create the Delete Messages tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Delete Messages")

        # Target selection
        target_frame = self.create_target_selection_frame(tab, "delete_msg")
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

        # Execute button
        execute_btn = ttk.Button(
            params_frame,
            text="Execute Delete",
            command=lambda: self.execute_delete_messages(),
            width=20
        )
        execute_btn.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        # Progress and results
        self.delete_progress_frame = self.create_progress_frame(tab)
        self.delete_progress_frame.pack(fill=tk.BOTH, expand=True)

    def execute_delete_messages(self):
        """Execute delete messages operation."""
        if self.operation_running:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return

        # Get target users
        users = self.get_target_users("delete_msg")
        if not users:
            return

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

        # Confirmation
        if len(users) > 1:
            if not messagebox.askyesno(
                "Confirm Operation",
                f"You are about to delete messages for {len(users)} users.\n\nProceed?"
            ):
                return

        # Execute
        self.run_operation(
            email_module.delete_messages,
            self.delete_progress_frame,
            users, query, date_from, date_to
        )

    # ==================== TAB 2: MANAGE DELEGATES ====================

    def create_delegates_tab(self):
        """Create the Manage Delegates tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Delegates")

        # Target selection
        target_frame = self.create_target_selection_frame(tab, "delegates")
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

        # Delegate email
        ttk.Label(params_frame, text="Delegate Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.delegate_email_entry = ttk.Entry(params_frame, width=40)
        self.delegate_email_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(5, 0))

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

        # Confirmation
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
        target_frame = self.create_target_selection_frame(tab, "signatures")
        target_frame.pack(fill=tk.X, pady=(0, 10))

        # Operation parameters
        params_frame = ttk.LabelFrame(tab, text="Signature Parameters", padding="10")
        params_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Action selection
        self.signature_action = tk.StringVar(value="set")
        ttk.Radiobutton(params_frame, text="Set Signature", variable=self.signature_action,
                       value="set", command=self.toggle_signature_input).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(params_frame, text="Remove Signature", variable=self.signature_action,
                       value="remove", command=self.toggle_signature_input).grid(row=0, column=1, sticky=tk.W, pady=5)

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

    def toggle_signature_input(self):
        """Toggle signature input visibility based on action."""
        if self.signature_action.get() == "set":
            self.signature_input_frame.grid()
            self.toggle_signature_method()
        else:
            self.signature_input_frame.grid_remove()
            self.signature_text_frame.grid_remove()
            self.signature_file_frame.grid_remove()

    def toggle_signature_method(self):
        """Toggle between text and file input for signature."""
        if self.signature_action.get() == "remove":
            return

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

        action = self.signature_action.get()

        if action == "set":
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

        # Confirmation
        if len(users) > 1:
            action_text = "set signature for" if action == "set" else "remove signature from"
            if not messagebox.askyesno(
                "Confirm Operation",
                f"You are about to {action_text} {len(users)} users.\n\nProceed?"
            ):
                return

        # Execute
        if action == "set":
            self.run_operation(
                email_module.set_signature,
                self.signatures_progress_frame,
                users, signature_html
            )
        else:
            self.run_operation(
                email_module.remove_signature,
                self.signatures_progress_frame,
                users
            )

    # ==================== TAB 4: MANAGE FORWARDING ====================

    def create_forwarding_tab(self):
        """Create the Manage Forwarding tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Forwarding")

        # Target selection
        target_frame = self.create_target_selection_frame(tab, "forwarding")
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

        # Confirmation
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
        target_frame = self.create_target_selection_frame(tab, "labels")
        target_frame.pack(fill=tk.X, pady=(0, 10))

        # Operation parameters
        params_frame = ttk.LabelFrame(tab, text="Label Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))

        # Action selection
        self.label_action = tk.StringVar(value="create")
        ttk.Radiobutton(params_frame, text="Create Label", variable=self.label_action,
                       value="create").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(params_frame, text="Delete Label", variable=self.label_action,
                       value="delete").grid(row=0, column=1, sticky=tk.W, pady=5)

        # Label name
        ttk.Label(params_frame, text="Label Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.label_name_entry = ttk.Entry(params_frame, width=40)
        self.label_name_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(5, 0))

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

    def execute_labels(self):
        """Execute label operation."""
        if self.operation_running:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return

        users = self.get_target_users("labels")
        if not users:
            return

        label_name = self.label_name_entry.get().strip()
        if not label_name:
            messagebox.showerror("Validation Error", "Please enter a label name.")
            return

        action = self.label_action.get()

        # Confirmation
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
        target_frame = self.create_target_selection_frame(tab, "filters")
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

        ttk.Label(self.filter_delete_frame, text="Filter ID:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_id_entry = ttk.Entry(self.filter_delete_frame, width=30)
        self.filter_id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

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

    def execute_filters(self):
        """Execute filter operation."""
        if self.operation_running:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete.")
            return

        users = self.get_target_users("filters")
        if not users:
            return

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
            filter_id = self.filter_id_entry.get().strip()
            if not filter_id:
                messagebox.showerror("Validation Error", "Please enter a filter ID.")
                return

        # Confirmation
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

    # ==================== COMMON COMPONENTS ====================

    def create_target_selection_frame(self, parent, tab_id):
        """
        Create target selection frame for a tab.

        Args:
            parent: Parent widget
            tab_id: Unique identifier for this tab's variables

        Returns:
            ttk.LabelFrame: The target selection frame
        """
        frame = ttk.LabelFrame(parent, text="Target Users", padding="10")

        # Create variables for this tab
        target_var = tk.StringVar(value="single")
        setattr(self, f"{tab_id}_target_var", target_var)

        # Radio buttons
        radio_frame = ttk.Frame(frame)
        radio_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(radio_frame, text="Single User", variable=target_var,
                       value="single", command=lambda: self.update_target_input(tab_id)).pack(anchor=tk.W)
        ttk.Radiobutton(radio_frame, text="Group", variable=target_var,
                       value="group", command=lambda: self.update_target_input(tab_id)).pack(anchor=tk.W)
        ttk.Radiobutton(radio_frame, text="All Users", variable=target_var,
                       value="all", command=lambda: self.update_target_input(tab_id)).pack(anchor=tk.W)
        ttk.Radiobutton(radio_frame, text="CSV File", variable=target_var,
                       value="csv", command=lambda: self.update_target_input(tab_id)).pack(anchor=tk.W)
        ttk.Radiobutton(radio_frame, text="Select from List", variable=target_var,
                       value="list", command=lambda: self.update_target_input(tab_id)).pack(anchor=tk.W)

        # Input frame
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X)
        setattr(self, f"{tab_id}_input_frame", input_frame)

        # Create different input widgets
        # Single user / Group entry
        entry = ttk.Entry(input_frame, width=40)
        setattr(self, f"{tab_id}_entry", entry)

        # CSV file browser
        csv_frame = ttk.Frame(input_frame)
        csv_entry = ttk.Entry(csv_frame, width=30)
        csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(csv_frame, text="Browse...",
                  command=lambda: self.browse_csv(tab_id)).pack(side=tk.LEFT)
        setattr(self, f"{tab_id}_csv_frame", csv_frame)
        setattr(self, f"{tab_id}_csv_entry", csv_entry)

        # List selection
        list_frame = ttk.Frame(input_frame)
        list_label = ttk.Label(list_frame, text="Select users:")
        list_label.pack(anchor=tk.W)
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE,
                           yscrollcommand=list_scroll.set, height=6)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=listbox.yview)
        load_btn = ttk.Button(list_frame, text="Load Users",
                            command=lambda: self.load_users_list(tab_id))
        load_btn.pack(pady=(5, 0))
        setattr(self, f"{tab_id}_list_frame", list_frame)
        setattr(self, f"{tab_id}_listbox", listbox)

        # All users label
        all_label = ttk.Label(input_frame, text="All users will be affected")
        setattr(self, f"{tab_id}_all_label", all_label)

        # Initial update
        self.update_target_input(tab_id)

        return frame

    def update_target_input(self, tab_id):
        """Update the input widget based on target selection."""
        target_var = getattr(self, f"{tab_id}_target_var")
        input_frame = getattr(self, f"{tab_id}_input_frame")

        # Clear all widgets
        for widget in input_frame.winfo_children():
            widget.pack_forget()

        # Show appropriate widget
        target = target_var.get()
        if target == "single":
            entry = getattr(self, f"{tab_id}_entry")
            entry.pack(fill=tk.X)
            entry.delete(0, tk.END)
            ttk.Label(input_frame, text="Enter email address",
                     font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        elif target == "group":
            entry = getattr(self, f"{tab_id}_entry")
            entry.pack(fill=tk.X)
            entry.delete(0, tk.END)
            ttk.Label(input_frame, text="Enter group email address",
                     font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        elif target == "all":
            label = getattr(self, f"{tab_id}_all_label")
            label.pack()
        elif target == "csv":
            csv_frame = getattr(self, f"{tab_id}_csv_frame")
            csv_frame.pack(fill=tk.X)
        elif target == "list":
            list_frame = getattr(self, f"{tab_id}_list_frame")
            list_frame.pack(fill=tk.BOTH, expand=True)

    def browse_csv(self, tab_id):
        """Browse for CSV file."""
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            csv_entry = getattr(self, f"{tab_id}_csv_entry")
            csv_entry.delete(0, tk.END)
            csv_entry.insert(0, filename)

    def load_users_list(self, tab_id):
        """Load users into listbox."""
        listbox = getattr(self, f"{tab_id}_listbox")

        # Clear current items
        listbox.delete(0, tk.END)

        # Show loading message
        listbox.insert(tk.END, "Loading users...")
        listbox.config(state=tk.DISABLED)
        self.update_idletasks()

        # Fetch users in thread
        def fetch_and_populate():
            users = fetch_users()
            self.after(0, lambda: self.populate_listbox(tab_id, users))

        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def populate_listbox(self, tab_id, users):
        """Populate listbox with users."""
        listbox = getattr(self, f"{tab_id}_listbox")
        listbox.config(state=tk.NORMAL)
        listbox.delete(0, tk.END)

        if users:
            for user in sorted(users):
                listbox.insert(tk.END, user)
        else:
            listbox.insert(tk.END, "(No users found or error fetching)")

    def get_target_users(self, tab_id):
        """
        Get the list of target users based on selection.

        Args:
            tab_id: Tab identifier

        Returns:
            list: List of user email addresses, or None if validation fails
        """
        target_var = getattr(self, f"{tab_id}_target_var")
        target = target_var.get()

        if target == "single":
            entry = getattr(self, f"{tab_id}_entry")
            email = entry.get().strip()
            if not email or '@' not in email:
                messagebox.showerror("Validation Error", "Please enter a valid email address.")
                return None
            return [email]

        elif target == "group":
            entry = getattr(self, f"{tab_id}_entry")
            group_email = entry.get().strip()
            if not group_email or '@' not in group_email:
                messagebox.showerror("Validation Error", "Please enter a valid group email address.")
                return None
            # For now, return as single item. Could expand to group members.
            return [group_email]

        elif target == "all":
            users = fetch_users()
            if not users:
                messagebox.showerror("Error", "Failed to fetch users or no users found.")
                return None
            return users

        elif target == "csv":
            csv_entry = getattr(self, f"{tab_id}_csv_entry")
            file_path = csv_entry.get().strip()
            if not file_path:
                messagebox.showerror("Validation Error", "Please select a CSV file.")
                return None

            success, result = read_csv_emails(file_path)
            if not success:
                messagebox.showerror("CSV Error", result)
                return None
            return result

        elif target == "list":
            listbox = getattr(self, f"{tab_id}_listbox")
            selection = listbox.curselection()
            if not selection:
                messagebox.showerror("Validation Error", "Please select at least one user from the list.")
                return None
            users = [listbox.get(i) for i in selection]
            return users

        return None

    def create_progress_frame(self, parent):
        """
        Create progress and results frame.

        Args:
            parent: Parent widget

        Returns:
            ttk.LabelFrame: The progress frame
        """
        frame = ttk.LabelFrame(parent, text="Progress and Results", padding="10")

        # Progress bar
        progress_bar = ttk.Progressbar(frame, mode='indeterminate')
        progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Results text area
        results_text = scrolledtext.ScrolledText(frame, height=10, width=60, state=tk.DISABLED)
        results_text.pack(fill=tk.BOTH, expand=True)

        # Store references
        frame.progress_bar = progress_bar
        frame.results_text = results_text

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        clear_btn = ttk.Button(btn_frame, text="Clear Results",
                              command=lambda: self.clear_results(frame))
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))

        log_btn = ttk.Button(btn_frame, text="View Error Log",
                            command=self.view_error_log)
        log_btn.pack(side=tk.LEFT)

        return frame

    def clear_results(self, progress_frame):
        """Clear results text area."""
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.delete("1.0", tk.END)
        progress_frame.results_text.config(state=tk.DISABLED)

    def view_error_log(self):
        """Open error log in a new window."""
        log_window = tk.Toplevel(self)
        log_window.title("Error Log")
        log_window.geometry("700x500")

        text_widget = scrolledtext.ScrolledText(log_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Read log file
        log_content = read_log_file()
        if log_content:
            text_widget.insert("1.0", log_content)
        else:
            text_widget.insert("1.0", "No errors logged yet or log file not found.")

        text_widget.config(state=tk.DISABLED)

        # Close button
        ttk.Button(log_window, text="Close", command=log_window.destroy).pack(pady=(0, 10))

    # ==================== OPERATION EXECUTION ====================

    def run_operation(self, operation_func, progress_frame, *args):
        """
        Run an operation in a background thread.

        Args:
            operation_func: The email module function to call
            progress_frame: The progress frame for this operation
            *args: Arguments to pass to operation_func
        """
        if self.operation_running:
            return

        self.operation_running = True

        # Clear and prepare UI
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.delete("1.0", tk.END)
        progress_frame.progress_bar.start(10)

        # Create queue for communication
        result_queue = queue.Queue()

        # Worker thread
        def worker():
            try:
                for progress in operation_func(*args):
                    result_queue.put(('progress', progress))
                result_queue.put(('done', None))
            except Exception as e:
                result_queue.put(('error', str(e)))

        # Start thread
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        # Start checking queue
        self.check_operation_queue(progress_frame, result_queue)

    def check_operation_queue(self, progress_frame, result_queue):
        """Check queue for operation updates."""
        try:
            msg_type, msg_data = result_queue.get_nowait()

            if msg_type == 'progress':
                # Update progress display
                message = msg_data.get('message', '')
                if message:
                    progress_frame.results_text.config(state=tk.NORMAL)
                    progress_frame.results_text.insert(tk.END, message + "\n")
                    progress_frame.results_text.see(tk.END)
                    progress_frame.results_text.config(state=tk.DISABLED)

                # Continue checking
                self.after(100, lambda: self.check_operation_queue(progress_frame, result_queue))

            elif msg_type == 'done':
                # Operation complete
                progress_frame.progress_bar.stop()
                progress_frame.results_text.config(state=tk.NORMAL)
                progress_frame.results_text.insert(tk.END, "\n" + "="*50 + "\n")
                progress_frame.results_text.insert(tk.END, "Operation completed!\n")
                progress_frame.results_text.config(state=tk.DISABLED)
                self.operation_running = False

            elif msg_type == 'error':
                # Operation error
                progress_frame.progress_bar.stop()
                progress_frame.results_text.config(state=tk.NORMAL)
                progress_frame.results_text.insert(tk.END, f"\nERROR: {msg_data}\n")
                progress_frame.results_text.config(state=tk.DISABLED)
                self.operation_running = False
                messagebox.showerror("Operation Error", f"An error occurred: {msg_data}")

        except queue.Empty:
            # No message yet, check again soon
            self.after(100, lambda: self.check_operation_queue(progress_frame, result_queue))
