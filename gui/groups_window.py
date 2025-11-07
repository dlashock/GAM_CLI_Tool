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

    Provides 7 tabs for different group operations.
    """

    def __init__(self, parent):
        super().__init__(parent, "Group Management", "900x750", (800, 600))

    def create_operation_tabs(self):
        """Create all group management operation tabs."""
        self.create_create_groups_tab()
        self.create_delete_groups_tab()
        self.create_manage_members_tab()

    def create_create_groups_tab(self):
        """Create the Create Groups tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Create Groups")

        instructions = ttk.Label(tab, text="Create new groups from CSV.", wraplength=800)
        instructions.pack(pady=(0, 10), anchor=tk.W)

        csv_frame = ttk.LabelFrame(tab, text="CSV File", padding="10")
        csv_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(csv_frame, text="CSV Format: email,name,description").pack(anchor=tk.W)

        self.create_groups_csv_entry = ttk.Entry(csv_frame, width=60)
        self.create_groups_csv_entry.pack(fill=tk.X, pady=5)

        self.create_groups_progress = self.create_progress_frame(tab)
        self.create_groups_progress.pack(fill=tk.BOTH, expand=True)

        self.create_groups_dry_run = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Dry Run", variable=self.create_groups_dry_run).pack()

    def create_delete_groups_tab(self):
        """Create delete groups tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Delete Groups")

    def create_manage_members_tab(self):
        """Create manage members tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Manage Members")
