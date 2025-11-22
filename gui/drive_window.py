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

        # Instructions
        info_frame = ttk.LabelFrame(tab, text="About Security Scanner", padding="10")
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
            tab, 'security_scan'
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
        config_frame = ttk.LabelFrame(tab, text="Scan Configuration", padding="10")
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
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        scan_btn = ttk.Button(
            button_frame,
            text="🔍 Scan for External Sharing",
            command=self.execute_security_scan,
            width=30
        )
        scan_btn.pack(side=tk.LEFT, padx=5)

        # Progress and results
        self.security_scan_progress_frame = self.create_progress_frame(tab)
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

        # Search criteria
        criteria_frame = ttk.LabelFrame(tab, text="Search Criteria", padding="10")
        criteria_frame.pack(fill=tk.X, padx=10, pady=5)

        # File Type selection
        type_frame = ttk.Frame(criteria_frame)
        type_frame.pack(fill=tk.X, pady=5)

        ttk.Label(type_frame, text="File Type:").pack(side=tk.LEFT, padx=5)
        self.file_search_type_var = tk.StringVar(value="all")
        file_types = [
            ("All Files", "all"),
            ("Google Docs", "document"),
            ("Google Sheets", "spreadsheet"),
            ("Google Slides", "presentation"),
            ("Google Forms", "form"),
            ("PDFs", "pdf"),
            ("Images", "image"),
            ("Folders", "folder")
        ]
        for label, value in file_types:
            ttk.Radiobutton(
                type_frame,
                text=label,
                variable=self.file_search_type_var,
                value=value
            ).pack(side=tk.LEFT, padx=5)

        # Name/keyword search
        name_frame = ttk.Frame(criteria_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(name_frame, text="Name contains:").pack(side=tk.LEFT, padx=5)
        self.file_search_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.file_search_name_var, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Label(
            name_frame,
            text="(optional - leave blank to skip)",
            font=('Arial', 8, 'italic'),
            foreground='gray'
        ).pack(side=tk.LEFT)

        # Date filter
        date_frame = ttk.Frame(criteria_frame)
        date_frame.pack(fill=tk.X, pady=5)

        ttk.Label(date_frame, text="Modified:").pack(side=tk.LEFT, padx=5)
        self.file_search_date_var = tk.StringVar(value="any")
        date_options = [
            ("Any time", "any"),
            ("Last 7 days", "7days"),
            ("Last 30 days", "30days"),
            ("Last 90 days", "90days"),
            ("This year", "year")
        ]
        for label, value in date_options:
            ttk.Radiobutton(
                date_frame,
                text=label,
                variable=self.file_search_date_var,
                value=value
            ).pack(side=tk.LEFT, padx=5)

        # Special filters
        special_frame = ttk.Frame(criteria_frame)
        special_frame.pack(fill=tk.X, pady=5)

        ttk.Label(special_frame, text="Special:").pack(side=tk.LEFT, padx=5)
        self.file_search_special_var = tk.StringVar(value="none")
        special_options = [
            ("None", "none"),
            ("Trashed files", "trashed"),
            ("Shared with me", "sharedwithme"),
            ("Owned by me", "ownedbyme")
        ]
        for label, value in special_options:
            ttk.Radiobutton(
                special_frame,
                text=label,
                variable=self.file_search_special_var,
                value=value
            ).pack(side=tk.LEFT, padx=5)

        # Preview generated query
        preview_frame = ttk.Frame(criteria_frame)
        preview_frame.pack(fill=tk.X, pady=5)

        ttk.Label(preview_frame, text="Generated Query:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=5)
        self.file_search_query_preview = tk.Text(preview_frame, height=2, wrap=tk.WORD, state=tk.DISABLED)
        self.file_search_query_preview.pack(fill=tk.X, padx=5, pady=2)

        # Bind changes to update preview
        self.file_search_type_var.trace_add('write', lambda *args: self.update_search_query_preview())
        self.file_search_name_var.trace_add('write', lambda *args: self.update_search_query_preview())
        self.file_search_date_var.trace_add('write', lambda *args: self.update_search_query_preview())
        self.file_search_special_var.trace_add('write', lambda *args: self.update_search_query_preview())

        # Initialize preview
        self.update_search_query_preview()

        # Max results
        max_frame = ttk.Frame(criteria_frame)
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
            criteria_frame,
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
            "Transfer ownership of Drive files.\n"
            "Use this when staff leave or files need to be reassigned."
        )
        ttk.Label(info_frame, text=info_text).pack()

        # Mode selection frame
        mode_frame = ttk.LabelFrame(tab, text="Transfer Mode", padding="10")
        mode_frame.pack(fill=tk.X, padx=10, pady=10)

        # Mode variable
        self.ownership_mode_var = tk.StringVar(value="single")

        mode_options_frame = ttk.Frame(mode_frame)
        mode_options_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            mode_options_frame,
            text="Single File Transfer",
            variable=self.ownership_mode_var,
            value="single",
            command=self.update_ownership_input_mode
        ).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Radiobutton(
            mode_options_frame,
            text="Full Drive Transfer",
            variable=self.ownership_mode_var,
            value="full",
            command=self.update_ownership_input_mode
        ).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Radiobutton(
            mode_options_frame,
            text="Bulk Transfer (CSV)",
            variable=self.ownership_mode_var,
            value="csv",
            command=self.update_ownership_input_mode
        ).pack(side=tk.LEFT)

        # Input container (will hold either single, full, or CSV interface)
        self.ownership_input_container = ttk.Frame(mode_frame)
        self.ownership_input_container.pack(fill=tk.BOTH, expand=True)

        # Single file transfer frame
        self.ownership_single_frame = ttk.Frame(self.ownership_input_container)

        # File ID
        file_id_frame = ttk.Frame(self.ownership_single_frame)
        file_id_frame.pack(fill=tk.X, pady=5)
        ttk.Label(file_id_frame, text="File ID:", width=15).pack(side=tk.LEFT)
        self.ownership_file_id_entry = ttk.Entry(file_id_frame, width=40)
        self.ownership_file_id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Current owner
        current_owner_frame = ttk.Frame(self.ownership_single_frame)
        current_owner_frame.pack(fill=tk.X, pady=5)
        ttk.Label(current_owner_frame, text="Current Owner:", width=15).pack(side=tk.LEFT)
        self.ownership_current_owner_entry = ttk.Entry(current_owner_frame, width=40)
        self.ownership_current_owner_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # New owner
        new_owner_frame = ttk.Frame(self.ownership_single_frame)
        new_owner_frame.pack(fill=tk.X, pady=5)
        ttk.Label(new_owner_frame, text="New Owner:", width=15).pack(side=tk.LEFT)
        self.ownership_new_owner_entry = ttk.Entry(new_owner_frame, width=40)
        self.ownership_new_owner_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Send email option
        email_frame = ttk.Frame(self.ownership_single_frame)
        email_frame.pack(fill=tk.X, pady=5)
        ttk.Label(email_frame, text="", width=15).pack(side=tk.LEFT)  # Spacer
        self.ownership_send_email_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            email_frame,
            text="Send email notification to new owner",
            variable=self.ownership_send_email_var
        ).pack(side=tk.LEFT, padx=5)

        # Full Drive transfer frame
        self.ownership_full_frame = ttk.Frame(self.ownership_input_container)

        # Source user (current owner)
        source_user_frame = ttk.Frame(self.ownership_full_frame)
        source_user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(source_user_frame, text="Source User:", width=15).pack(side=tk.LEFT)
        self.ownership_source_user_entry = ttk.Entry(source_user_frame, width=40)
        self.ownership_source_user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(source_user_frame, text="(Transfer FROM)", font=('Arial', 9, 'italic'), foreground='gray').pack(side=tk.LEFT, padx=5)

        # Destination user (new owner)
        dest_user_frame = ttk.Frame(self.ownership_full_frame)
        dest_user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dest_user_frame, text="Destination User:", width=15).pack(side=tk.LEFT)
        self.ownership_dest_user_entry = ttk.Entry(dest_user_frame, width=40)
        self.ownership_dest_user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(dest_user_frame, text="(Transfer TO)", font=('Arial', 9, 'italic'), foreground='gray').pack(side=tk.LEFT, padx=5)

        # Warning for full drive transfer
        warning_frame = ttk.Frame(self.ownership_full_frame)
        warning_frame.pack(fill=tk.X, pady=15)
        ttk.Label(warning_frame, text="", width=15).pack(side=tk.LEFT)  # Spacer
        warning_text = "⚠️  This will transfer ALL files owned by the source user.\nUse Preview first to see what will be transferred.\n\nNote: Email notifications will NOT be sent to avoid spam."
        ttk.Label(warning_frame, text=warning_text, font=('Arial', 9), foreground='#856404').pack(side=tk.LEFT)

        # CSV bulk transfer frame
        self.ownership_csv_frame = ttk.Frame(self.ownership_input_container)

        csv_input_frame = ttk.Frame(self.ownership_csv_frame)
        csv_input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(csv_input_frame, text="CSV File:", width=15).pack(side=tk.LEFT)
        self.ownership_csv_entry = ttk.Entry(csv_input_frame, width=40)
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
        format_frame = ttk.Frame(self.ownership_csv_frame)
        format_frame.pack(fill=tk.X, pady=5)

        format_text = "CSV Format: file_id, current_owner, new_owner, send_email (true/false)"
        ttk.Label(format_frame, text=format_text, font=('Arial', 9, 'italic'), foreground='gray').pack()

        # Execute buttons (shared by all modes)
        button_frame = ttk.Frame(mode_frame)
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

        # Show initial mode (single)
        self.update_ownership_input_mode()

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

    # ==================== HELPER METHODS ====================

    def update_ownership_input_mode(self):
        """Update the ownership transfer input UI based on selected mode."""
        mode = self.ownership_mode_var.get()

        # Hide all frames first
        self.ownership_single_frame.pack_forget()
        self.ownership_full_frame.pack_forget()
        self.ownership_csv_frame.pack_forget()

        # Show the appropriate frame
        if mode == "single":
            self.ownership_single_frame.pack(fill=tk.BOTH, expand=True)
        elif mode == "full":
            self.ownership_full_frame.pack(fill=tk.BOTH, expand=True)
        else:  # csv
            self.ownership_csv_frame.pack(fill=tk.BOTH, expand=True)

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

    def update_search_query_preview(self):
        """Update the search query preview based on selected criteria."""
        query_parts = []

        # File type
        file_type = self.file_search_type_var.get()
        if file_type != "all":
            mime_types = {
                "document": "application/vnd.google-apps.document",
                "spreadsheet": "application/vnd.google-apps.spreadsheet",
                "presentation": "application/vnd.google-apps.presentation",
                "form": "application/vnd.google-apps.form",
                "pdf": "application/pdf",
                "image": "image/",
                "folder": "application/vnd.google-apps.folder"
            }
            if file_type == "image":
                query_parts.append("mimeType contains 'image/'")
            else:
                query_parts.append(f"mimeType = '{mime_types[file_type]}'")

        # Name filter
        name = self.file_search_name_var.get().strip()
        if name:
            query_parts.append(f"name contains '{name}'")

        # Date filter
        date_filter = self.file_search_date_var.get()
        if date_filter != "any":
            from datetime import datetime, timedelta
            today = datetime.now()
            if date_filter == "7days":
                date_str = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            elif date_filter == "30days":
                date_str = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            elif date_filter == "90days":
                date_str = (today - timedelta(days=90)).strftime("%Y-%m-%d")
            elif date_filter == "year":
                date_str = f"{today.year}-01-01"
            query_parts.append(f"modifiedTime > '{date_str}'")

        # Special filters
        special = self.file_search_special_var.get()
        if special == "trashed":
            query_parts.append("trashed = true")
        elif special == "sharedwithme":
            query_parts.append("sharedWithMe = true")
        elif special == "ownedbyme":
            # This is handled per-user in the backend, don't add to query
            pass

        # Build final query
        if query_parts:
            final_query = " and ".join(query_parts)
        else:
            final_query = "# No filters selected - will search all files"

        # Update preview
        self.file_search_query_preview.config(state=tk.NORMAL)
        self.file_search_query_preview.delete("1.0", tk.END)
        self.file_search_query_preview.insert("1.0", final_query)
        self.file_search_query_preview.config(state=tk.DISABLED)

    def build_search_query(self):
        """Build the search query from selected criteria."""
        query_parts = []

        # File type
        file_type = self.file_search_type_var.get()
        if file_type != "all":
            mime_types = {
                "document": "application/vnd.google-apps.document",
                "spreadsheet": "application/vnd.google-apps.spreadsheet",
                "presentation": "application/vnd.google-apps.presentation",
                "form": "application/vnd.google-apps.form",
                "pdf": "application/pdf",
                "image": "image/",
                "folder": "application/vnd.google-apps.folder"
            }
            if file_type == "image":
                query_parts.append("mimeType contains 'image/'")
            else:
                query_parts.append(f"mimeType = '{mime_types[file_type]}'")

        # Name filter
        name = self.file_search_name_var.get().strip()
        if name:
            query_parts.append(f"name contains '{name}'")

        # Date filter
        date_filter = self.file_search_date_var.get()
        if date_filter != "any":
            from datetime import datetime, timedelta
            today = datetime.now()
            if date_filter == "7days":
                date_str = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            elif date_filter == "30days":
                date_str = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            elif date_filter == "90days":
                date_str = (today - timedelta(days=90)).strftime("%Y-%m-%d")
            elif date_filter == "year":
                date_str = f"{today.year}-01-01"
            query_parts.append(f"modifiedTime > '{date_str}'")

        # Special filters
        special = self.file_search_special_var.get()
        if special == "trashed":
            query_parts.append("trashed = true")
        elif special == "sharedwithme":
            query_parts.append("sharedWithMe = true")

        # Build final query (return None if no filters)
        return " and ".join(query_parts) if query_parts else None

    def execute_file_search(self):
        """Execute file search."""
        # Get target users
        users = self.get_target_users('file_search')
        if not users:
            return

        # Build query from selected criteria
        query = self.build_search_query()
        if not query:
            messagebox.showwarning(
                "No Filters Selected",
                "Please select at least one search criterion.\n\n"
                "You can filter by file type, name, date, or special attributes."
            )
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
        """Execute ownership transfer (single, full, or bulk)."""
        mode = self.ownership_mode_var.get()

        if mode == "single":
            # Get single file transfer data
            file_id = self.ownership_file_id_entry.get().strip()
            current_owner = self.ownership_current_owner_entry.get().strip()
            new_owner = self.ownership_new_owner_entry.get().strip()
            send_email = self.ownership_send_email_var.get()

            # Validate inputs
            if not file_id:
                messagebox.showerror("Error", "Please enter a File ID")
                return
            if not current_owner:
                messagebox.showerror("Error", "Please enter the current owner email")
                return
            if not new_owner:
                messagebox.showerror("Error", "Please enter the new owner email")
                return

            # Create transfer data
            transfer_data = [{
                'file_id': file_id,
                'current_owner': current_owner,
                'new_owner': new_owner,
                'send_email': send_email
            }]

            # Confirmation
            confirm_msg = (
                f"Transfer ownership of file:\n\n"
                f"File ID: {transfer_data[0]['file_id']}\n"
                f"From: {transfer_data[0]['current_owner']}\n"
                f"To: {transfer_data[0]['new_owner']}\n"
                f"Send notification: {'Yes' if transfer_data[0]['send_email'] else 'No'}\n\n"
                f"{'[DRY RUN - Preview Only]' if dry_run else 'Are you sure?'}"
            )

            if not messagebox.askyesno("Confirm Transfer", confirm_msg):
                return

            # Import backend function
            from modules.drive import transfer_ownership

            # Run operation
            self.run_operation(
                transfer_ownership,
                self.ownership_progress_frame,
                transfer_data,
                dry_run=dry_run
            )

        elif mode == "full":
            # Get full drive transfer data
            source_user = self.ownership_source_user_entry.get().strip()
            dest_user = self.ownership_dest_user_entry.get().strip()
            send_email = False  # Never send emails for full drive transfers to avoid spam

            # Validate inputs
            if not source_user:
                messagebox.showerror("Error", "Please enter the source user email")
                return
            if not dest_user:
                messagebox.showerror("Error", "Please enter the destination user email")
                return
            if '@' not in source_user or '@' not in dest_user:
                messagebox.showerror("Error", "Please enter valid email addresses")
                return
            if source_user == dest_user:
                messagebox.showerror("Error", "Source and destination users cannot be the same")
                return

            # Strong confirmation for full drive transfer
            confirm_msg = (
                f"⚠️  FULL DRIVE OWNERSHIP TRANSFER  ⚠️\n\n"
                f"This will transfer ALL files owned by:\n"
                f"  FROM: {source_user}\n"
                f"  TO: {dest_user}\n\n"
                f"{'[DRY RUN - Preview Only]\n\n' if dry_run else ''}"
                f"This may include hundreds or thousands of files!\n\n"
                f"{'Click Yes to preview what would be transferred.' if dry_run else 'Are you absolutely sure?'}"
            )

            if not messagebox.askyesno("Confirm Full Drive Transfer", confirm_msg):
                return

            # Import backend function
            from modules.drive import transfer_full_drive_ownership

            # Run operation
            self.run_operation(
                transfer_full_drive_ownership,
                self.ownership_progress_frame,
                source_user,
                dest_user,
                send_email,
                dry_run=dry_run
            )

        else:  # csv mode
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

            # Confirmation
            confirm_msg = (
                f"Transfer ownership for {len(transfer_data)} file(s)?\n\n"
                f"{'[DRY RUN - Preview Only]' if dry_run else 'This will update file ownership.'}"
            )

            if not messagebox.askyesno("Confirm Transfer", confirm_msg):
                return

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
