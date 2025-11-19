"""
Drive Operations window for GAM Admin Tool.

Provides interface for Google Drive operations including:
- Security scanning (non-domain ACL detection) - CRITICAL for K-12
- File search and management
- Ownership transfer
- Permission management
- Drive cleanup
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import csv
from datetime import datetime

from gui.base_operation_window import BaseOperationWindow
from utils.workspace_data import fetch_users


class DriveWindow(BaseOperationWindow):
    """
    Drive Operations window.

    Inherits from BaseOperationWindow to leverage:
    - Standard target selection framework
    - Progress tracking and threading
    - Error logging
    - Utility methods
    """

    def __init__(self, parent):
        """
        Initialize the Drive Operations window.

        Args:
            parent: The parent tkinter widget
        """
        super().__init__(
            parent,
            title="Drive Operations",
            window_size="1100x800",
            min_size=(900, 700)
        )

    def create_operation_tabs(self):
        """Create Drive-specific operation tabs."""
        # Tab 1: Security Scanner (CRITICAL)
        self.create_security_scanner_tab()

        # Tab 2: File Search
        self.create_file_search_tab()

        # Tab 3: Ownership Transfer
        self.create_ownership_transfer_tab()

        # Tab 4: Drive Cleanup
        self.create_cleanup_tab()

    def create_security_scanner_tab(self):
        """
        Create Security Scanner tab - CRITICAL FEATURE.

        Scans for files shared outside the organization domain.
        """
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔍 Security Scanner")

        # Scrollable container for the tab
        container, scrollable = self.create_scrollable_frame(tab)
        container.pack(fill=tk.BOTH, expand=True)

        # Instructions
        info_frame = ttk.LabelFrame(scrollable, text="About Security Scanner", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_text = (
            "⚠️  CRITICAL SECURITY FEATURE\n\n"
            "This scanner identifies files shared outside your organization:\n"
            "• Files shared with external email addresses\n"
            "• 'Anyone with the link' sharing\n"
            "• External domain sharing\n\n"
            "Use this to:\n"
            "✓ Ensure FERPA compliance (K-12)\n"
            "✓ Prevent data leakage\n"
            "✓ Audit external file sharing"
        )
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

        # Target selection
        target_frame = self.create_combobox_user_target_selection_frame(
            scrollable, 'security_scan'
        )
        target_frame.pack(fill=tk.X, padx=10, pady=10)

        # Load users into combobox
        if hasattr(self, 'security_scan_combobox'):
            self.load_combobox_async(
                self.security_scan_combobox,
                fetch_users,
                enable_fuzzy=True
            )

        # Configuration
        config_frame = ttk.LabelFrame(scrollable, text="Scan Configuration", padding="10")
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        # Domain input
        domain_input_frame = ttk.Frame(config_frame)
        domain_input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(domain_input_frame, text="Your Organization Domain:").pack(side=tk.LEFT, padx=5)
        self.security_scan_domain_entry = ttk.Entry(domain_input_frame, width=30)
        self.security_scan_domain_entry.pack(side=tk.LEFT, padx=5)
        self.security_scan_domain_entry.insert(0, "school.edu")  # Placeholder

        ttk.Label(domain_input_frame, text="(e.g., school.edu)").pack(side=tk.LEFT, padx=5)

        # Scan options
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill=tk.X, pady=5)

        self.scan_include_anyone_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text='Include "Anyone with link" sharing',
            variable=self.scan_include_anyone_var
        ).pack(anchor=tk.W, padx=5)

        self.scan_include_external_domain_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text='Include external domain sharing',
            variable=self.scan_include_external_domain_var
        ).pack(anchor=tk.W, padx=5)

        # Export results checkbox
        self.scan_export_results_var = tk.BooleanVar(value=False)
        export_frame = ttk.Frame(config_frame)
        export_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(
            export_frame,
            text='Automatically export results to CSV',
            variable=self.scan_export_results_var
        ).pack(side=tk.LEFT, padx=5)

        # Warning for auto-remove (disabled by default)
        warning_frame = ttk.Frame(config_frame)
        warning_frame.pack(fill=tk.X, pady=10)

        warning_text = "⚠️  Note: This scan will only detect and report external sharing.\nTo remove permissions, use the results to identify files, then use the Permission Management tab."
        ttk.Label(
            warning_frame,
            text=warning_text,
            foreground='red',
            justify=tk.LEFT
        ).pack(padx=5)

        # Execute buttons
        button_frame = ttk.Frame(scrollable)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        scan_btn = ttk.Button(
            button_frame,
            text="🔍 Scan for External Sharing",
            command=self.execute_security_scan,
            width=30
        )
        scan_btn.pack(side=tk.LEFT, padx=5)

        # Progress and results
        self.security_scan_progress_frame = self.create_progress_frame(scrollable)
        self.security_scan_progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_file_search_tab(self):
        """Create File Search tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔎 Search Files")

        # Instructions
        info_frame = ttk.LabelFrame(tab, text="File Search", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_text = "Search for files across user Drive accounts using Google Drive query syntax."
        ttk.Label(info_frame, text=info_text).pack()

        # Target selection
        target_frame = self.create_combobox_user_target_selection_frame(tab, 'file_search')
        target_frame.pack(fill=tk.X, padx=10, pady=10)

        # Load users
        if hasattr(self, 'file_search_combobox'):
            self.load_combobox_async(
                self.file_search_combobox,
                fetch_users,
                enable_fuzzy=True
            )

        # Search query
        query_frame = ttk.LabelFrame(tab, text="Search Query", padding="10")
        query_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(query_frame, text="Query:").pack(side=tk.LEFT, padx=5)
        self.file_search_query_entry = ttk.Entry(query_frame, width=50)
        self.file_search_query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.file_search_query_entry.insert(0, "name contains 'budget'")

        # Query examples
        examples_frame = ttk.Frame(query_frame)
        examples_frame.pack(fill=tk.X, pady=5)

        ttk.Label(examples_frame, text="Examples:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        examples = [
            "name contains 'budget'",
            "mimeType = 'application/vnd.google-apps.spreadsheet'",
            "modifiedTime > '2025-01-01'",
            "trashed = true"
        ]
        for example in examples:
            ttk.Label(examples_frame, text=f"  • {example}", font=('Arial', 8)).pack(anchor=tk.W)

        # Max results
        max_frame = ttk.Frame(query_frame)
        max_frame.pack(fill=tk.X, pady=5)

        ttk.Label(max_frame, text="Max results per user:").pack(side=tk.LEFT, padx=5)
        self.file_search_max_var = tk.IntVar(value=100)
        ttk.Spinbox(
            max_frame,
            from_=1,
            to=1000,
            textvariable=self.file_search_max_var,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        # Execute button
        search_btn = ttk.Button(
            query_frame,
            text="🔎 Search Files",
            command=self.execute_file_search,
            width=20
        )
        search_btn.pack(pady=10)

        # Progress and results
        self.file_search_progress_frame = self.create_progress_frame(tab)
        self.file_search_progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_ownership_transfer_tab(self):
        """Create Ownership Transfer tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📤 Transfer Ownership")

        # Instructions
        info_frame = ttk.LabelFrame(tab, text="Transfer File Ownership", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_text = (
            "Transfer ownership of Drive files in bulk.\n"
            "Use this when staff leave or files need to be reassigned.\n\n"
            "CSV Format: file_id, current_owner, new_owner, send_email"
        )
        ttk.Label(info_frame, text=info_text).pack()

        # CSV file selection
        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, padx=10, pady=10)

        csv_input_frame = ttk.Frame(csv_frame)
        csv_input_frame.pack(fill=tk.X)

        self.ownership_csv_entry = ttk.Entry(csv_input_frame, width=50)
        self.ownership_csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(
            csv_input_frame,
            text="Browse",
            command=lambda: self.browse_csv_file(
                self.ownership_csv_entry,
                "Select Ownership Transfer CSV"
            )
        ).pack(side=tk.LEFT, padx=5)

        # CSV format help
        format_frame = ttk.Frame(csv_frame)
        format_frame.pack(fill=tk.X, pady=5)

        format_text = "CSV must have columns: file_id, current_owner, new_owner, send_email (true/false)"
        ttk.Label(format_frame, text=format_text, font=('Arial', 8)).pack()

        # Preview and execute buttons
        button_frame = ttk.Frame(csv_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame,
            text="🔍 Preview",
            command=lambda: self.execute_ownership_transfer(dry_run=True),
            width=15
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="▶ Transfer Ownership",
            command=lambda: self.execute_ownership_transfer(dry_run=False),
            width=20
        ).pack(side=tk.LEFT, padx=5)

        # Progress and results
        self.ownership_progress_frame = self.create_progress_frame(tab)
        self.ownership_progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_cleanup_tab(self):
        """Create Drive Cleanup tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🧹 Drive Cleanup")

        # Instructions
        info_frame = ttk.LabelFrame(tab, text="Empty Drive Trash", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_text = (
            "Permanently delete all files in users' Drive trash.\n"
            "⚠️  WARNING: This action cannot be undone!"
        )
        ttk.Label(info_frame, text=info_text).pack()

        # Target selection
        target_frame = self.create_combobox_user_target_selection_frame(tab, 'cleanup')
        target_frame.pack(fill=tk.X, padx=10, pady=10)

        # Load users
        if hasattr(self, 'cleanup_combobox'):
            self.load_combobox_async(
                self.cleanup_combobox,
                fetch_users,
                enable_fuzzy=True
            )

        # Execute buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(
            button_frame,
            text="🔍 Preview",
            command=lambda: self.execute_empty_trash(dry_run=True),
            width=15
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="🧹 Empty Trash",
            command=lambda: self.execute_empty_trash(dry_run=False),
            width=15
        ).pack(side=tk.LEFT, padx=5)

        # Progress and results
        self.cleanup_progress_frame = self.create_progress_frame(tab)
        self.cleanup_progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ==================== EXECUTION METHODS ====================

    def execute_security_scan(self):
        """Execute security scan for external sharing."""
        # Get target users
        users = self.get_target_users('security_scan')
        if not users:
            return

        # Get domain
        domain = self.security_scan_domain_entry.get().strip()
        if not domain:
            messagebox.showerror("Error", "Please enter your organization domain (e.g., school.edu)")
            return

        # Validate domain format
        if '.' not in domain or '@' in domain:
            messagebox.showerror("Error", "Please enter just the domain (e.g., school.edu)\nDo not include @ symbol.")
            return

        # Get options
        include_anyone = self.scan_include_anyone_var.get()

        # Confirmation
        response = messagebox.askyesno(
            "Confirm Scan",
            f"This will scan Drive files for {len(users)} user(s).\n\n"
            f"Domain: {domain}\n"
            f"Include 'anyone' links: {include_anyone}\n\n"
            "This may take several minutes for users with many files.\n\n"
            "Continue?",
            icon='question'
        )

        if not response:
            return

        # Import backend function
        from modules.drive import scan_non_domain_acls

        # Run operation
        def on_scan_complete():
            """Callback after scan completes."""
            if self.scan_export_results_var.get():
                # Auto-export results
                self.export_scan_results()

        self.run_operation(
            scan_non_domain_acls,
            self.security_scan_progress_frame,
            users,
            domain,
            include_anyone,
            on_success=on_scan_complete
        )

    def export_scan_results(self):
        """Export security scan results to CSV."""
        # Get results from text widget
        results_text = self.security_scan_progress_frame.results_text.get("1.0", tk.END)

        if not results_text.strip() or "No external sharing" in results_text:
            messagebox.showinfo("Export", "No external sharing findings to export.")
            return

        # Ask for file location
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f'drive_security_scan_{timestamp}.csv'

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                # Write results to CSV
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(results_text)
                messagebox.showinfo("Exported", f"Results exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")

    def execute_file_search(self):
        """Execute file search."""
        # Get target users
        users = self.get_target_users('file_search')
        if not users:
            return

        # Get query
        query = self.file_search_query_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a search query")
            return

        # Get max results
        max_results = self.file_search_max_var.get()

        # Import backend function
        from modules.drive import search_files

        # Run operation
        self.run_operation(
            search_files,
            self.file_search_progress_frame,
            users,
            query,
            max_results
        )

    def execute_ownership_transfer(self, dry_run=False):
        """Execute ownership transfer from CSV."""
        # Get CSV file
        csv_path = self.ownership_csv_entry.get().strip()
        if not csv_path:
            messagebox.showerror("Error", "Please select a CSV file")
            return

        # Read and validate CSV
        transfer_data = self.read_and_validate_csv(
            csv_path,
            ['file_id', 'current_owner', 'new_owner'],
            'transfer file ownership'
        )

        if not transfer_data:
            return

        # Convert send_email to boolean if present
        for item in transfer_data:
            if 'send_email' in item:
                send_val = item['send_email'].lower()
                item['send_email'] = send_val in ['true', '1', 'yes']
            else:
                item['send_email'] = False

        # Import backend function
        from modules.drive import transfer_ownership

        # Run operation
        self.run_operation(
            transfer_ownership,
            self.ownership_progress_frame,
            transfer_data,
            dry_run=dry_run
        )

    def execute_empty_trash(self, dry_run=False):
        """Execute empty trash operation."""
        # Get target users
        users = self.get_target_users('cleanup')
        if not users:
            return

        # Warning confirmation
        if not dry_run:
            response = messagebox.askyesno(
                "Confirm Empty Trash",
                f"⚠️  WARNING: This will PERMANENTLY DELETE all files in trash for {len(users)} user(s).\n\n"
                "This action CANNOT be undone!\n\n"
                "Are you absolutely sure?",
                icon='warning'
            )

            if not response:
                return

        # Import backend function
        from modules.drive import empty_trash

        # Run operation
        self.run_operation(
            empty_trash,
            self.cleanup_progress_frame,
            users,
            dry_run=dry_run
        )
