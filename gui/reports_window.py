"""
Reports window for GAM Admin Tool.

Provides GUI for generating various Google Workspace reports including login
activity, storage usage, email statistics, and admin audit logs.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime, timedelta
from gui.base_operation_window import BaseOperationWindow


class ReportsWindow(BaseOperationWindow):
    """
    Reports window for generating Google Workspace reports.

    Inherits from BaseOperationWindow for standard progress tracking,
    threading, and result display infrastructure.
    """

    def __init__(self, parent):
        """
        Initialize the Reports window.

        Args:
            parent: The parent tkinter widget (usually root window)
        """
        super().__init__(
            parent,
            title="Google Workspace Reports",
            window_size="1100x800",
            min_size=(900, 700)
        )

    def create_operation_tabs(self):
        """
        Create report type tabs.

        Overrides abstract method from BaseOperationWindow.
        """
        # Tab 1: User Activity Reports
        self.create_user_activity_tab()

        # Tab 2: Storage Reports
        self.create_storage_tab()

        # Tab 3: Email Usage Reports
        self.create_email_usage_tab()

        # Tab 4: Admin Audit Reports
        self.create_admin_audit_tab()

    def create_user_activity_tab(self):
        """Create User Activity Reports tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="User Activity")

        # Main container
        main_container = ttk.Frame(tab, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Configuration Frame
        config_frame = ttk.LabelFrame(main_container, text="Report Configuration", padding="10")
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        # Report Type Selection
        type_frame = ttk.Frame(config_frame)
        type_frame.pack(fill=tk.X, pady=5)

        ttk.Label(type_frame, text="Report Type:").pack(side=tk.LEFT, padx=5)

        report_type_var = tk.StringVar(value="login_activity")
        ttk.Radiobutton(
            type_frame,
            text="Login Activity",
            variable=report_type_var,
            value="login_activity"
        ).pack(side=tk.LEFT, padx=10)

        ttk.Radiobutton(
            type_frame,
            text="Inactive Users",
            variable=report_type_var,
            value="inactive_users"
        ).pack(side=tk.LEFT, padx=10)

        # Inactive threshold selection
        threshold_frame = ttk.Frame(config_frame)
        threshold_frame.pack(fill=tk.X, pady=5)

        ttk.Label(threshold_frame, text="Inactive Threshold:").pack(side=tk.LEFT, padx=5)

        inactive_days_var = tk.IntVar(value=90)
        threshold_combo = ttk.Combobox(
            threshold_frame,
            textvariable=inactive_days_var,
            values=[30, 60, 90, 180, 365],
            width=10,
            state='readonly'
        )
        threshold_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(threshold_frame, text="days (for Inactive Users report)").pack(side=tk.LEFT)

        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill=tk.X, pady=5)

        include_suspended_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Include suspended users",
            variable=include_suspended_var
        ).pack(side=tk.LEFT, padx=5)

        auto_export_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Auto-export to CSV",
            variable=auto_export_var
        ).pack(side=tk.LEFT, padx=15)

        # Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=10)

        generate_btn = ttk.Button(
            button_frame,
            text="📊 Generate Report",
            command=lambda: self.execute_user_activity_report(
                report_type_var.get(),
                inactive_days_var.get(),
                include_suspended_var.get(),
                auto_export_var.get()
            ),
            width=20
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        export_btn = ttk.Button(
            button_frame,
            text="📥 Export to CSV",
            command=lambda: self.export_current_results('user_activity'),
            width=20
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        # Progress Frame
        progress_frame = self.create_progress_frame(main_container)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Store variables for later use
        self.user_activity_vars = {
            'report_type': report_type_var,
            'inactive_days': inactive_days_var,
            'include_suspended': include_suspended_var,
            'auto_export': auto_export_var,
            'progress_frame': progress_frame
        }

    def create_storage_tab(self):
        """Create Storage Reports tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Storage Usage")

        # Main container
        main_container = ttk.Frame(tab, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Configuration Frame
        config_frame = ttk.LabelFrame(main_container, text="Report Configuration", padding="10")
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        # Scope selection
        scope_frame = ttk.LabelFrame(config_frame, text="Report Scope", padding="10")
        scope_frame.pack(fill=tk.X, pady=5)

        self.storage_scope_var = tk.StringVar(value="all")

        scope_options_frame = ttk.Frame(scope_frame)
        scope_options_frame.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(
            scope_options_frame,
            text="All Users (Domain-wide)",
            variable=self.storage_scope_var,
            value="all",
            command=self.toggle_storage_scope_fields
        ).pack(side=tk.LEFT, padx=10)

        ttk.Radiobutton(
            scope_options_frame,
            text="Specific User",
            variable=self.storage_scope_var,
            value="user",
            command=self.toggle_storage_scope_fields
        ).pack(side=tk.LEFT, padx=10)

        ttk.Radiobutton(
            scope_options_frame,
            text="Organizational Unit",
            variable=self.storage_scope_var,
            value="ou",
            command=self.toggle_storage_scope_fields
        ).pack(side=tk.LEFT, padx=10)

        # User/OU input frame
        self.storage_target_frame = ttk.Frame(scope_frame)
        self.storage_target_frame.pack(fill=tk.X, pady=5)

        # User email input (for specific user)
        self.storage_user_label = ttk.Label(self.storage_target_frame, text="User Email:")
        self.storage_user_var = tk.StringVar()
        self.storage_user_entry = ttk.Entry(self.storage_target_frame, textvariable=self.storage_user_var, width=40)

        # OU combobox (for OU filter)
        self.storage_ou_label = ttk.Label(self.storage_target_frame, text="Organizational Unit:")
        self.storage_ou_var = tk.StringVar()
        self.storage_ou_combo = ttk.Combobox(
            self.storage_target_frame,
            textvariable=self.storage_ou_var,
            width=38
        )
        self.storage_ou_help = ttk.Label(
            self.storage_target_frame,
            text="(e.g., /Students or /Staff)",
            font=('Arial', 8, 'italic'),
            foreground='gray'
        )

        # Initialize visibility
        self.toggle_storage_scope_fields()

        # Load OUs asynchronously for combobox
        from utils.workspace_data import fetch_org_units
        self.load_combobox_async(
            self.storage_ou_combo,
            fetch_org_units,
            enable_fuzzy=True
        )

        # Quota threshold
        threshold_frame = ttk.Frame(config_frame)
        threshold_frame.pack(fill=tk.X, pady=5)

        ttk.Label(threshold_frame, text="Highlight users over:").pack(side=tk.LEFT, padx=5)

        quota_threshold_var = tk.IntVar(value=80)
        threshold_spin = ttk.Spinbox(
            threshold_frame,
            from_=50,
            to=100,
            increment=5,
            textvariable=quota_threshold_var,
            width=10
        )
        threshold_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(threshold_frame, text="% of quota").pack(side=tk.LEFT)

        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill=tk.X, pady=5)

        auto_export_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Auto-export to CSV",
            variable=auto_export_var
        ).pack(side=tk.LEFT, padx=5)

        # Info label
        info_label = ttk.Label(
            config_frame,
            text="Note: This report may take several minutes for large organizations",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        )
        info_label.pack(pady=5)

        # Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=10)

        generate_btn = ttk.Button(
            button_frame,
            text="📊 Generate Report",
            command=lambda: self.execute_storage_report(
                quota_threshold_var.get(),
                self.storage_scope_var.get(),
                self.storage_user_var.get().strip() if self.storage_scope_var.get() == 'user' else self.storage_ou_var.get().strip(),
                auto_export_var.get()
            ),
            width=20
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        export_btn = ttk.Button(
            button_frame,
            text="📥 Export to CSV",
            command=lambda: self.export_current_results('storage'),
            width=20
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        # Progress Frame
        progress_frame = self.create_progress_frame(main_container)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Store variables
        self.storage_vars = {
            'quota_threshold': quota_threshold_var,
            'auto_export': auto_export_var,
            'progress_frame': progress_frame
        }

    def create_email_usage_tab(self):
        """Create Email Usage Reports tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Email Usage")

        # Main container
        main_container = ttk.Frame(tab, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Configuration Frame
        config_frame = ttk.LabelFrame(main_container, text="Report Configuration", padding="10")
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        # Scope selection
        scope_frame = ttk.LabelFrame(config_frame, text="Report Scope", padding="10")
        scope_frame.pack(fill=tk.X, pady=5)

        self.email_scope_var = tk.StringVar(value="all")

        scope_options_frame = ttk.Frame(scope_frame)
        scope_options_frame.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(
            scope_options_frame,
            text="All Users (Domain-wide)",
            variable=self.email_scope_var,
            value="all",
            command=self.toggle_email_scope_fields
        ).pack(side=tk.LEFT, padx=10)

        ttk.Radiobutton(
            scope_options_frame,
            text="Specific User",
            variable=self.email_scope_var,
            value="user",
            command=self.toggle_email_scope_fields
        ).pack(side=tk.LEFT, padx=10)

        ttk.Radiobutton(
            scope_options_frame,
            text="Group",
            variable=self.email_scope_var,
            value="group",
            command=self.toggle_email_scope_fields
        ).pack(side=tk.LEFT, padx=10)

        # User/Group input frame
        self.email_target_frame = ttk.Frame(scope_frame)
        self.email_target_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.email_target_frame, text="Email/Group:").pack(side=tk.LEFT, padx=5)
        self.email_target_var = tk.StringVar()
        self.email_target_entry = ttk.Entry(self.email_target_frame, textvariable=self.email_target_var, width=40)
        self.email_target_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(
            self.email_target_frame,
            text="(e.g., user@domain.com or group@domain.com)",
            font=('Arial', 8, 'italic'),
            foreground='gray'
        ).pack(side=tk.LEFT)

        # Initialize visibility
        self.toggle_email_scope_fields()

        # Date range selection
        date_frame = ttk.Frame(config_frame)
        date_frame.pack(fill=tk.X, pady=5)

        ttk.Label(date_frame, text="Date Range:").pack(side=tk.LEFT, padx=5)

        date_range_var = tk.StringVar(value="-30d")
        date_range_combo = ttk.Combobox(
            date_frame,
            textvariable=date_range_var,
            values=["-7d", "-30d", "-60d", "-90d"],
            width=12,
            state='readonly'
        )
        date_range_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(date_frame, text="(Last 7, 30, 60, or 90 days)").pack(side=tk.LEFT)

        # Custom date option (for future enhancement)
        custom_date_frame = ttk.Frame(config_frame)
        custom_date_frame.pack(fill=tk.X, pady=5)

        use_custom_dates_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            custom_date_frame,
            text="Use custom dates (YYYY-MM-DD):",
            variable=use_custom_dates_var
        ).pack(side=tk.LEFT, padx=5)

        start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        ttk.Entry(custom_date_frame, textvariable=start_date_var, width=12).pack(side=tk.LEFT, padx=5)

        ttk.Label(custom_date_frame, text="to").pack(side=tk.LEFT, padx=5)

        end_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(custom_date_frame, textvariable=end_date_var, width=12).pack(side=tk.LEFT, padx=5)

        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill=tk.X, pady=5)

        auto_export_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Auto-export to CSV",
            variable=auto_export_var
        ).pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=10)

        generate_btn = ttk.Button(
            button_frame,
            text="📊 Generate Report",
            command=lambda: self.execute_email_usage_report(
                date_range_var.get() if not use_custom_dates_var.get() else start_date_var.get(),
                end_date_var.get() if use_custom_dates_var.get() else None,
                self.email_scope_var.get(),
                self.email_target_var.get().strip(),
                auto_export_var.get()
            ),
            width=20
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        export_btn = ttk.Button(
            button_frame,
            text="📥 Export to CSV",
            command=lambda: self.export_current_results('email_usage'),
            width=20
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        # Progress Frame
        progress_frame = self.create_progress_frame(main_container)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Store variables
        self.email_usage_vars = {
            'date_range': date_range_var,
            'use_custom': use_custom_dates_var,
            'start_date': start_date_var,
            'end_date': end_date_var,
            'auto_export': auto_export_var,
            'progress_frame': progress_frame
        }

    def create_admin_audit_tab(self):
        """Create Admin Audit Reports tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Admin Audit")

        # Main container
        main_container = ttk.Frame(tab, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Configuration Frame
        config_frame = ttk.LabelFrame(main_container, text="Report Configuration", padding="10")
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        # Date range selection
        date_frame = ttk.Frame(config_frame)
        date_frame.pack(fill=tk.X, pady=5)

        ttk.Label(date_frame, text="Date Range:").pack(side=tk.LEFT, padx=5)

        date_range_var = tk.StringVar(value="-30d")
        date_range_combo = ttk.Combobox(
            date_frame,
            textvariable=date_range_var,
            values=["-7d", "-30d", "-60d", "-90d", "-180d"],
            width=12,
            state='readonly'
        )
        date_range_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(date_frame, text="(Google retains 180 days max)").pack(side=tk.LEFT)

        # Event type filter
        event_frame = ttk.Frame(config_frame)
        event_frame.pack(fill=tk.X, pady=5)

        ttk.Label(event_frame, text="Event Type:").pack(side=tk.LEFT, padx=5)

        event_type_var = tk.StringVar(value="all")
        event_combo = ttk.Combobox(
            event_frame,
            textvariable=event_type_var,
            values=["all", "user_settings", "group_settings", "domain_settings", "mobile_settings"],
            width=20,
            state='readonly'
        )
        event_combo.pack(side=tk.LEFT, padx=5)

        # Info label
        info_label = ttk.Label(
            config_frame,
            text="⚠️  Admin audit logs are essential for compliance and security investigations",
            font=('Arial', 9),
            foreground='#856404'
        )
        info_label.pack(pady=5)

        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill=tk.X, pady=5)

        auto_export_var = tk.BooleanVar(value=True)  # Default to true for audit logs
        ttk.Checkbutton(
            options_frame,
            text="Auto-export to CSV (recommended for audit trail)",
            variable=auto_export_var
        ).pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=10)

        generate_btn = ttk.Button(
            button_frame,
            text="📊 Generate Report",
            command=lambda: self.execute_admin_audit_report(
                date_range_var.get(),
                event_type_var.get(),
                auto_export_var.get()
            ),
            width=20
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        export_btn = ttk.Button(
            button_frame,
            text="📥 Export to CSV",
            command=lambda: self.export_current_results('admin_audit'),
            width=20
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        # Progress Frame
        progress_frame = self.create_progress_frame(main_container)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Store variables
        self.admin_audit_vars = {
            'date_range': date_range_var,
            'event_type': event_type_var,
            'auto_export': auto_export_var,
            'progress_frame': progress_frame
        }

    # Helper Methods

    def run_report_operation(self, operation_func, progress_frame, report_type, auto_export, display_type, *args):
        """
        Run a report operation and capture the result from progress messages.

        Args:
            operation_func: The report function to call
            progress_frame: Progress frame for display
            report_type: Type of report for storage
            auto_export: Whether to auto-export
            display_type: Type for display/export purposes
            *args: Arguments for operation_func
        """
        # Clear previous results
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.delete("1.0", tk.END)
        progress_frame.results_text.config(state=tk.DISABLED)

        # Store captured data
        self._last_report_data = None
        self._last_report_type = report_type

        # Override the progress message handler to capture report data
        import queue
        import threading

        if self.operation_running:
            messagebox.showwarning("Operation Running", "An operation is already in progress.")
            return

        self.operation_running = True
        self.cancel_flag.clear()

        progress_frame.progress_bar.start(10)
        result_queue = queue.Queue()

        def worker():
            try:
                for progress in operation_func(*args):
                    if self.cancel_flag.is_set():
                        result_queue.put(('cancelled', None))
                        return

                    # Capture report data from success message
                    if progress.get('status') == 'success' and 'report_data' in progress:
                        # Build complete report structure
                        report_result = {
                            'data': progress.get('report_data', []),
                            'summary': progress.get('summary', {})
                        }
                        result_queue.put(('report_data', report_result))

                    result_queue.put(('progress', progress))

                result_queue.put(('done', None))
            except Exception as e:
                import traceback
                result_queue.put(('error', f"{str(e)}\n{traceback.format_exc()}"))

        # Start thread
        self.current_thread = threading.Thread(target=worker, daemon=True)
        self.current_thread.start()

        # Start checking queue with custom handler
        def check_report_queue():
            try:
                msg_type, msg_data = result_queue.get_nowait()

                if msg_type == 'progress':
                    message = msg_data.get('message', '')
                    if message:
                        progress_frame.results_text.config(state=tk.NORMAL)
                        progress_frame.results_text.insert(tk.END, message + "\n")
                        progress_frame.results_text.see(tk.END)
                        progress_frame.results_text.config(state=tk.DISABLED)
                    self.after(100, check_report_queue)

                elif msg_type == 'report_data':
                    # Capture the report data
                    self._last_report_data = msg_data
                    self.after(100, check_report_queue)

                elif msg_type == 'done':
                    progress_frame.progress_bar.stop()
                    progress_frame.results_text.config(state=tk.NORMAL)
                    progress_frame.results_text.insert(tk.END, "\n" + "="*50 + "\n")
                    progress_frame.results_text.insert(tk.END, "Operation completed!\n")
                    progress_frame.results_text.config(state=tk.DISABLED)
                    self.operation_running = False

                    # Process captured report data
                    if self._last_report_data:
                        self.store_report_data(report_type, self._last_report_data)
                        self.display_report_data(self._last_report_data, progress_frame)
                        if auto_export:
                            self.auto_export_report(self._last_report_data, display_type)

                elif msg_type == 'cancelled':
                    progress_frame.progress_bar.stop()
                    progress_frame.results_text.config(state=tk.NORMAL)
                    progress_frame.results_text.insert(tk.END, "\n" + "="*50 + "\n")
                    progress_frame.results_text.insert(tk.END, "Operation cancelled.\n")
                    progress_frame.results_text.config(state=tk.DISABLED)
                    self.operation_running = False

                elif msg_type == 'error':
                    progress_frame.progress_bar.stop()
                    progress_frame.results_text.config(state=tk.NORMAL)
                    progress_frame.results_text.insert(tk.END, f"\nERROR: {msg_data}\n")
                    progress_frame.results_text.config(state=tk.DISABLED)
                    self.operation_running = False
                    messagebox.showerror("Operation Error", f"An error occurred:\n\n{msg_data}")

            except queue.Empty:
                if self.operation_running:
                    self.after(100, check_report_queue)

        check_report_queue()

    def display_report_data(self, report_data, progress_frame):
        """
        Format and display report data in the results window.

        Args:
            report_data (dict): Report data structure with 'data' list
            progress_frame: Progress frame containing results_text widget
        """
        if not report_data or 'data' not in report_data:
            return

        data = report_data['data']
        if not data:
            return

        # Get field names from first record
        fieldnames = list(data[0].keys())

        # Format as table
        output_lines = []

        # Header row
        header = " | ".join(str(field).ljust(20) for field in fieldnames)
        output_lines.append(header)
        output_lines.append("-" * len(header))

        # Data rows (limit to first 100 for display)
        for i, row in enumerate(data[:100]):
            row_text = " | ".join(str(row.get(field, '')).ljust(20)[:20] for field in fieldnames)
            output_lines.append(row_text)

        if len(data) > 100:
            output_lines.append(f"\n... and {len(data) - 100} more rows")
            output_lines.append("\nUse 'Export to CSV' to save all data")

        # Display summary if available
        if 'summary' in report_data:
            output_lines.append("\n" + "=" * 60)
            output_lines.append("SUMMARY")
            output_lines.append("=" * 60)
            for key, value in report_data['summary'].items():
                output_lines.append(f"{key}: {value}")

        # Update results text
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.insert(tk.END, "\n".join(output_lines) + "\n")
        progress_frame.results_text.config(state=tk.DISABLED)
        progress_frame.results_text.see(tk.END)

    def store_report_data(self, report_type, report_data):
        """
        Store report data for later export.

        Args:
            report_type (str): Type of report
            report_data (dict): Report data structure
        """
        if not hasattr(self, '_stored_reports'):
            self._stored_reports = {}

        self._stored_reports[report_type] = report_data

    def toggle_email_scope_fields(self):
        """Toggle visibility of email target input based on scope selection."""
        scope = self.email_scope_var.get()
        if scope == 'all':
            # Hide the email/group input
            for widget in self.email_target_frame.winfo_children():
                widget.pack_forget()
        else:
            # Show the email/group input
            for widget in self.email_target_frame.winfo_children():
                widget.pack_forget()

            ttk.Label(self.email_target_frame, text="Email/Group:").pack(side=tk.LEFT, padx=5)
            self.email_target_entry.pack(side=tk.LEFT, padx=5)
            ttk.Label(
                self.email_target_frame,
                text="(e.g., user@domain.com or group@domain.com)",
                font=('Arial', 8, 'italic'),
                foreground='gray'
            ).pack(side=tk.LEFT)

    def toggle_storage_scope_fields(self):
        """Toggle visibility of storage target input based on scope selection."""
        scope = self.storage_scope_var.get()

        # Hide all widgets first
        for widget in self.storage_target_frame.winfo_children():
            widget.pack_forget()

        if scope == 'user':
            # Show user email input
            self.storage_user_label.pack(side=tk.LEFT, padx=5)
            self.storage_user_entry.pack(side=tk.LEFT, padx=5)
        elif scope == 'ou':
            # Show OU combobox
            self.storage_ou_label.pack(side=tk.LEFT, padx=5)
            self.storage_ou_combo.pack(side=tk.LEFT, padx=5)
            self.storage_ou_help.pack(side=tk.LEFT, padx=5)
        # else: scope == 'all', keep widgets hidden

    # Execution Methods

    def execute_user_activity_report(self, report_type, inactive_days, include_suspended, auto_export):
        """Execute user activity report generation."""
        progress_frame = self.user_activity_vars['progress_frame']

        # Clear previous results
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.delete("1.0", tk.END)
        progress_frame.results_text.config(state=tk.DISABLED)

        # Import report function
        if report_type == "login_activity":
            from modules.reports import get_login_activity_report
            operation_func = get_login_activity_report
            args = (30, include_suspended)
            report_name = "Login Activity Report"
        else:  # inactive_users
            from modules.reports import get_inactive_users_report
            operation_func = get_inactive_users_report
            args = (inactive_days, 30)
            report_name = "Inactive Users Report"

        # Confirmation
        confirm = messagebox.askyesno(
            "Generate Report",
            f"Generate {report_name}?\n\nThis may take a few minutes."
        )

        if not confirm:
            return

        # Custom run operation with result capture
        self.run_report_operation(
            operation_func,
            progress_frame,
            'user_activity',
            auto_export,
            report_type,
            *args
        )

    def execute_storage_report(self, quota_threshold, scope, target, auto_export):
        """Execute storage usage report generation."""
        progress_frame = self.storage_vars['progress_frame']

        # Clear previous results
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.delete("1.0", tk.END)
        progress_frame.results_text.config(state=tk.DISABLED)

        # Validate scope-specific inputs
        if scope == 'user' and not target:
            messagebox.showerror(
                "Input Required",
                "Please enter a user email address."
            )
            return
        elif scope == 'ou' and not target:
            messagebox.showerror(
                "Input Required",
                "Please select an Organizational Unit."
            )
            return

        from modules.reports import get_storage_usage_report

        # Build confirmation message
        scope_msg = {
            'all': 'All Users (Domain-wide)',
            'user': f'User: {target}',
            'ou': f'OU: {target}'
        }

        confirm = messagebox.askyesno(
            "Generate Report",
            f"Generate Storage Usage Report?\n\n"
            f"Scope: {scope_msg[scope]}\n\n"
            f"This may take several minutes for large organizations."
        )

        if not confirm:
            return

        # Run report operation with result capture
        # Pass org_unit for OU scope, None otherwise
        self.run_report_operation(
            get_storage_usage_report,
            progress_frame,
            'storage',
            auto_export,
            'storage',
            quota_threshold,
            target if scope == 'ou' else None,  # org_unit parameter
            target if scope == 'user' else None  # user_email parameter (new)
        )

    def execute_email_usage_report(self, start_date, end_date, scope, target, auto_export):
        """Execute email usage report generation."""
        progress_frame = self.email_usage_vars['progress_frame']

        # Clear previous results
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.delete("1.0", tk.END)
        progress_frame.results_text.config(state=tk.DISABLED)

        # Validate scope-specific inputs
        if scope in ['user', 'group'] and not target:
            messagebox.showerror(
                "Input Required",
                f"Please enter a {'user email' if scope == 'user' else 'group email'} address."
            )
            return

        from modules.reports import get_email_usage_report

        # Build confirmation message
        scope_msg = {
            'all': 'All Users (Domain-wide)',
            'user': f'User: {target}',
            'group': f'Group: {target}'
        }

        # Confirmation
        confirm = messagebox.askyesno(
            "Generate Report",
            f"Generate Email Usage Report?\n\n"
            f"Scope: {scope_msg[scope]}\n"
            f"Period: {start_date} to {end_date or 'today'}"
        )

        if not confirm:
            return

        # Run report operation with result capture
        self.run_report_operation(
            get_email_usage_report,
            progress_frame,
            'email_usage',
            auto_export,
            'email_usage',
            start_date,
            end_date,
            scope,
            target if scope in ['user', 'group'] else None
        )

    def execute_admin_audit_report(self, start_date, event_type, auto_export):
        """Execute admin audit report generation."""
        progress_frame = self.admin_audit_vars['progress_frame']

        # Clear previous results
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.delete("1.0", tk.END)
        progress_frame.results_text.config(state=tk.DISABLED)

        from modules.reports import get_admin_activity_report

        # Confirmation
        confirm = messagebox.askyesno(
            "Generate Report",
            f"Generate Admin Audit Report?\n\nPeriod: {start_date} to today\nEvent Type: {event_type}"
        )

        if not confirm:
            return

        # Run report operation with result capture
        self.run_report_operation(
            get_admin_activity_report,
            progress_frame,
            'admin_audit',
            auto_export,
            'admin_audit',
            start_date,
            event_type
        )

    def auto_export_report(self, report_data, report_type):
        """
        Automatically export report to CSV.

        Args:
            report_data (dict): Report data structure
            report_type (str): Type of report for filename
        """
        if not report_data or not report_data.get('data'):
            return

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{report_type}_report_{timestamp}.csv'

        try:
            from modules.reports import export_report_to_csv
            success = export_report_to_csv(report_data, filename)

            if success:
                messagebox.showinfo(
                    "Export Successful",
                    f"Report exported to:\n{filename}"
                )
            else:
                messagebox.showerror("Export Failed", "Failed to export report to CSV")

        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report: {str(e)}")

    def export_current_results(self, report_type):
        """
        Export currently displayed results to CSV.

        Args:
            report_type (str): Type of report (determines which results to export)
        """
        # Check if we have stored report data
        if not hasattr(self, '_stored_reports') or report_type not in self._stored_reports:
            messagebox.showinfo("No Data", "No report data available to export.\nPlease generate a report first.")
            return

        report_data = self._stored_reports[report_type]

        if not report_data or 'data' not in report_data or not report_data['data']:
            messagebox.showinfo("No Data", "No report data available to export.")
            return

        # Ask for save location
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_filename = f'{report_type}_report_{timestamp}.csv'

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                from modules.reports import export_report_to_csv
                success = export_report_to_csv(report_data, file_path)

                if success:
                    messagebox.showinfo(
                        "Export Successful",
                        f"Report exported to:\n{file_path}\n\n"
                        f"Total rows: {len(report_data['data'])}"
                    )
                else:
                    messagebox.showerror("Export Failed", "Failed to export report to CSV")

            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
