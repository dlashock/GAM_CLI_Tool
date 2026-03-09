"""
Reports window for GAM Admin Tool.

Provides a tabbed interface for audit and usage reports:
- Admin Audit: activity log with optional event-type filtering (#42)
- Email Usage: per-user gmail statistics (#43)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import date, timedelta

from gui.base_operation_window import BaseOperationWindow
from modules.reports import ADMIN_EVENT_TYPES, fetch_admin_audit, fetch_email_usage
from utils.workspace_data import fetch_users


class ReportsWindow(BaseOperationWindow):
    """Reports window with Admin Audit and Email Usage tabs."""

    def __init__(self, parent):
        super().__init__(parent, "Reports", "900x700", (700, 500))

    def create_operation_tabs(self):
        """Create all report tabs."""
        self._create_admin_audit_tab()
        self._create_email_usage_tab()

    # ==================== TAB 1: ADMIN AUDIT ====================

    def _create_admin_audit_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Admin Audit")

        ttk.Label(
            tab,
            text="Pull admin activity logs. Filter by event type and/or date range.",
            wraplength=800
        ).pack(pady=(0, 10), anchor=tk.W)

        # --- Filters ---
        filters_frame = ttk.LabelFrame(tab, text="Filters", padding="10")
        filters_frame.pack(fill=tk.X, pady=(0, 10))
        filters_frame.columnconfigure(1, weight=1)

        # Event type
        ttk.Label(filters_frame, text="Event Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self._audit_event_var = tk.StringVar(value="All Events")
        event_combo = ttk.Combobox(
            filters_frame,
            textvariable=self._audit_event_var,
            values=ADMIN_EVENT_TYPES,
            state="readonly",
            width=35
        )
        event_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Start date
        ttk.Label(filters_frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self._audit_start_var = tk.StringVar()
        ttk.Entry(filters_frame, textvariable=self._audit_start_var, width=20).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        ttk.Label(filters_frame, text="(optional)", foreground="gray").grid(row=1, column=2, sticky=tk.W)

        # End date
        ttk.Label(filters_frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self._audit_end_var = tk.StringVar()
        ttk.Entry(filters_frame, textvariable=self._audit_end_var, width=20).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5
        )
        ttk.Label(filters_frame, text="(optional)", foreground="gray").grid(row=2, column=2, sticky=tk.W)

        # --- Run button ---
        ttk.Button(
            tab,
            text="Run Admin Audit",
            command=self._run_admin_audit
        ).pack(pady=(0, 10))

        # --- Output area ---
        output_frame = ttk.LabelFrame(tab, text="Output", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True)

        self._audit_output = tk.Text(output_frame, wrap=tk.NONE, height=18, font=("Courier", 9))
        vsb = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self._audit_output.yview)
        hsb = ttk.Scrollbar(output_frame, orient=tk.HORIZONTAL, command=self._audit_output.xview)
        self._audit_output.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._audit_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _run_admin_audit(self):
        event_type = self._audit_event_var.get().strip()
        start_date = self._audit_start_var.get().strip() or None
        end_date = self._audit_end_var.get().strip() or None

        self._audit_output.delete("1.0", tk.END)
        self._audit_output.insert(tk.END, "Running admin audit...\n")

        def run():
            result = fetch_admin_audit(
                start_date=start_date,
                end_date=end_date,
                event_type=event_type if event_type != "All Events" else None
            )
            self.after(0, lambda: self._display_audit_result(result))

        threading.Thread(target=run, daemon=True).start()

    def _display_audit_result(self, result):
        self._audit_output.delete("1.0", tk.END)
        if result["success"]:
            output = result["output"].strip()
            self._audit_output.insert(tk.END, output if output else "(No results returned)")
        else:
            self._audit_output.insert(tk.END, f"ERROR:\n{result['error']}")

    # ==================== TAB 2: EMAIL USAGE ====================

    def _create_email_usage_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Email Usage")

        ttk.Label(
            tab,
            text="Fetch email usage statistics for a specific user.",
            wraplength=800
        ).pack(pady=(0, 10), anchor=tk.W)

        # --- Parameters ---
        params_frame = ttk.LabelFrame(tab, text="Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)

        # User email
        ttk.Label(params_frame, text="User Email:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self._usage_user_combo = ttk.Combobox(params_frame, width=40)
        self._usage_user_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        # Date
        ttk.Label(params_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        default_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        self._usage_date_var = tk.StringVar(value=default_date)
        ttk.Entry(params_frame, textvariable=self._usage_date_var, width=20).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        ttk.Label(
            params_frame,
            text="(usage data is typically available with a 1-2 day delay)",
            foreground="gray", font=("Arial", 9)
        ).grid(row=1, column=2, sticky=tk.W, padx=5)

        # Parameters field
        ttk.Label(params_frame, text="Parameters:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self._usage_params_var = tk.StringVar(
            value="gmail:num_emails_sent,gmail:num_emails_received"
        )
        ttk.Entry(params_frame, textvariable=self._usage_params_var, width=60).grid(
            row=2, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5
        )
        ttk.Label(
            params_frame,
            text="Comma-separated gmail parameters (leave blank for all)",
            foreground="gray", font=("Arial", 9)
        ).grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5)

        # --- Run button ---
        ttk.Button(
            tab,
            text="Fetch Email Usage",
            command=self._run_email_usage
        ).pack(pady=(0, 10))

        # --- Output area ---
        output_frame = ttk.LabelFrame(tab, text="Output", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True)

        self._usage_output = tk.Text(output_frame, wrap=tk.NONE, height=18, font=("Courier", 9))
        vsb = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self._usage_output.yview)
        hsb = ttk.Scrollbar(output_frame, orient=tk.HORIZONTAL, command=self._usage_output.xview)
        self._usage_output.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._usage_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Load users into combobox
        self.after(100, lambda: self.load_combobox_async(
            self._usage_user_combo, fetch_users, enable_fuzzy=True
        ))

    def _run_email_usage(self):
        user_email = self._usage_user_combo.get().strip()
        if not user_email:
            messagebox.showwarning("Missing Input", "Please enter or select a user email.")
            return

        report_date = self._usage_date_var.get().strip() or None
        parameters = self._usage_params_var.get().strip() or None

        self._usage_output.delete("1.0", tk.END)
        self._usage_output.insert(tk.END, f"Fetching email usage statistics for {user_email}...\n")

        def run():
            result = fetch_email_usage(
                user_email=user_email,
                date=report_date,
                parameters=parameters
            )
            self.after(0, lambda: self._display_usage_result(result))

        threading.Thread(target=run, daemon=True).start()

    def _display_usage_result(self, result):
        self._usage_output.delete("1.0", tk.END)
        if result["success"]:
            output = result["output"].strip()
            self._usage_output.insert(tk.END, output if output else "(No data returned for this date)")
        else:
            self._usage_output.insert(tk.END, f"ERROR:\n{result['error']}")
