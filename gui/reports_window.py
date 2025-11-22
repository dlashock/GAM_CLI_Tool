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

        # Store report data for later export
        self.current_report_data = None

        def on_complete(result):
            """Handle report completion."""
            if result:
                # Store the report data
                self.store_report_data('user_activity', result)
                # Display the formatted report
                self.display_report_data(result, progress_frame)
                # Auto-export if requested
                if auto_export:
                    self.auto_export_report(result, report_type)

        # Run operation
        self.run_operation(
            operation_func,
            progress_frame,
            *args,
            on_success=on_complete
        )

    def execute_storage_report(self, quota_threshold, auto_export):
        """Execute storage usage report generation."""
        progress_frame = self.storage_vars['progress_frame']

        # Clear previous results
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.delete("1.0", tk.END)
        progress_frame.results_text.config(state=tk.DISABLED)

        from modules.reports import get_storage_usage_report

        # Confirmation
        confirm = messagebox.askyesno(
            "Generate Report",
            "Generate Storage Usage Report?\n\nThis may take several minutes for large organizations."
        )

        if not confirm:
            return

        def on_complete(result):
            """Handle report completion."""
            if result:
                # Store the report data
                self.store_report_data('storage', result)
                # Display the formatted report
                self.display_report_data(result, progress_frame)
                # Auto-export if requested
                if auto_export:
                    self.auto_export_report(result, 'storage')

        # Run operation
        self.run_operation(
            get_storage_usage_report,
            progress_frame,
            quota_threshold,
            on_success=on_complete
        )

    def execute_email_usage_report(self, start_date, end_date, auto_export):
        """Execute email usage report generation."""
        progress_frame = self.email_usage_vars['progress_frame']

        # Clear previous results
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.delete("1.0", tk.END)
        progress_frame.results_text.config(state=tk.DISABLED)

        from modules.reports import get_email_usage_report

        # Confirmation
        confirm = messagebox.askyesno(
            "Generate Report",
            f"Generate Email Usage Report?\n\nPeriod: {start_date} to {end_date or 'today'}"
        )

        if not confirm:
            return

        def on_complete(result):
            """Handle report completion."""
            if result:
                # Store the report data
                self.store_report_data('email_usage', result)
                # Display the formatted report
                self.display_report_data(result, progress_frame)
                # Auto-export if requested
                if auto_export:
                    self.auto_export_report(result, 'email_usage')

        # Run operation
        self.run_operation(
            get_email_usage_report,
            progress_frame,
            start_date,
            end_date,
            on_success=on_complete
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

        def on_complete(result):
            """Handle report completion."""
            if result:
                # Store the report data
                self.store_report_data('admin_audit', result)
                # Display the formatted report
                self.display_report_data(result, progress_frame)
                # Auto-export if requested
                if auto_export:
                    self.auto_export_report(result, 'admin_audit')

        # Run operation
        self.run_operation(
            get_admin_activity_report,
            progress_frame,
            start_date,
            event_type,
            on_success=on_complete
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
