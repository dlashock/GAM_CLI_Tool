"""
Base Operation Window for GAM Admin Tool.

Provides common functionality for all operation windows including:
- Window initialization and layout
- Target selection framework (single, group, all, CSV, list)
- Progress tracking with threading
- Queue-based communication
- Error logging

All operation windows should inherit from BaseOperationWindow.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
from abc import ABC, abstractmethod

from utils.workspace_data import fetch_users, fetch_groups
from utils.csv_handler import validate_csv, read_csv_emails
from utils.logger import read_log_file, get_log_file_path


class BaseOperationWindow(tk.Toplevel, ABC):
    """
    Abstract base class for operation windows.

    Provides common UI elements and functionality for all operation windows.
    Subclasses must implement create_operation_tabs() to define their specific tabs.
    """

    def __init__(self, parent, title, window_size="950x750", min_size=(800, 600)):
        """
        Initialize the base operation window.

        Args:
            parent: The parent tkinter widget
            title: Window title
            window_size: Initial window size (WIDTHxHEIGHT)
            min_size: Minimum window size (width, height)
        """
        super().__init__(parent)

        self.title(title)
        self.geometry(window_size)
        self.minsize(*min_size)

        # Center the window
        self.transient(parent)

        # Variables for tracking state
        self.operation_running = False
        self.current_thread = None
        self.cancel_flag = threading.Event()

        # Create UI
        self.create_widgets()

        # Center on screen
        self.center_window()

    def center_window(self):
        """Center the window on screen."""
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
            text=self.title(),
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Subclass creates specific tabs
        self.create_operation_tabs()

        # Bottom buttons
        self.create_bottom_buttons(main_container)

    @abstractmethod
    def create_operation_tabs(self):
        """
        Create operation-specific tabs.

        Must be implemented by subclasses to define their specific operations.
        Each tab should use create_target_selection_frame() and create_progress_frame()
        for consistency.
        """
        pass

    def create_bottom_buttons(self, parent):
        """
        Create bottom button frame.

        Args:
            parent: Parent widget
        """
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        close_button = ttk.Button(
            button_frame,
            text="Close",
            command=self.destroy,
            width=15
        )
        close_button.pack(side=tk.RIGHT, padx=5)

    # ==================== TARGET SELECTION FRAMEWORK ====================

    def create_combobox_user_target_selection_frame(self, parent, tab_id):
        """
        Create target selection frame using combobox for user selection.
        Combobox combines "Single User" entry and "Select from List" functionality.

        Args:
            parent: Parent widget
            tab_id: Unique identifier for this tab

        Returns:
            ttk.LabelFrame: The target selection frame
        """
        frame = ttk.LabelFrame(parent, text="Target Users", padding="10")

        # Create variable for target type
        target_var = tk.StringVar(value="combobox")
        setattr(self, f"{tab_id}_target_var", target_var)

        # Radio buttons for target type (simplified - combobox or CSV)
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Select User",
            variable=target_var,
            value="combobox",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="CSV File",
            variable=target_var,
            value="csv",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT)

        # Input frame (changes based on selection)
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        setattr(self, f"{tab_id}_input_frame", input_frame)

        # Combobox frame (replaces single user entry + list)
        combobox_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_combobox_frame", combobox_frame)

        ttk.Label(combobox_frame, text="User Email:").pack(side=tk.LEFT, padx=(0, 5))
        combobox = ttk.Combobox(combobox_frame, width=40)
        combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setattr(self, f"{tab_id}_combobox", combobox)

        # CSV frame
        csv_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_csv_frame", csv_frame)

        csv_entry = ttk.Entry(csv_frame, width=50)
        csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        setattr(self, f"{tab_id}_csv_entry", csv_entry)

        ttk.Button(
            csv_frame,
            text="Browse",
            command=lambda: self.browse_csv(tab_id)
        ).pack(side=tk.LEFT)

        # Show initial input (combobox)
        self.update_target_input(tab_id)

        return frame

    def create_combobox_group_target_selection_frame(self, parent, tab_id):
        """
        Create target selection frame using combobox for group selection.

        Args:
            parent: Parent widget
            tab_id: Unique identifier for this tab

        Returns:
            ttk.LabelFrame: The target selection frame
        """
        frame = ttk.LabelFrame(parent, text="Target Groups", padding="10")

        # Create variable for target type
        target_var = tk.StringVar(value="combobox")
        setattr(self, f"{tab_id}_target_var", target_var)

        # Radio buttons for target type
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Select Group",
            variable=target_var,
            value="combobox",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="CSV File",
            variable=target_var,
            value="csv",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT)

        # Input frame (changes based on selection)
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        setattr(self, f"{tab_id}_input_frame", input_frame)

        # Combobox frame
        combobox_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_combobox_frame", combobox_frame)

        ttk.Label(combobox_frame, text="Group Email:").pack(side=tk.LEFT, padx=(0, 5))
        combobox = ttk.Combobox(combobox_frame, width=40)
        combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setattr(self, f"{tab_id}_combobox", combobox)

        # CSV frame
        csv_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_csv_frame", csv_frame)

        csv_entry = ttk.Entry(csv_frame, width=50)
        csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        setattr(self, f"{tab_id}_csv_entry", csv_entry)

        ttk.Button(
            csv_frame,
            text="Browse",
            command=lambda: self.browse_csv(tab_id)
        ).pack(side=tk.LEFT)

        # Show initial input (combobox)
        self.update_target_input(tab_id)

        return frame

    def create_combobox_target_selection_frame(self, parent, tab_id):
        """
        Create target selection frame with combobox replacing Single User + Select from List.
        Includes Group, All Users, and CSV options.

        Args:
            parent: Parent widget
            tab_id: Unique identifier for this tab

        Returns:
            ttk.LabelFrame: The target selection frame
        """
        frame = ttk.LabelFrame(parent, text="Target Selection", padding="10")

        # Create variable for target type
        target_var = tk.StringVar(value="combobox")
        setattr(self, f"{tab_id}_target_var", target_var)

        # Radio buttons for target type
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Select User",
            variable=target_var,
            value="combobox",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Group",
            variable=target_var,
            value="group",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="All Users",
            variable=target_var,
            value="all",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="CSV File",
            variable=target_var,
            value="csv",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT)

        # Input frame (changes based on selection)
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        setattr(self, f"{tab_id}_input_frame", input_frame)

        # Combobox frame (for user selection)
        combobox_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_combobox_frame", combobox_frame)

        ttk.Label(combobox_frame, text="User Email:").pack(side=tk.LEFT, padx=(0, 5))
        combobox = ttk.Combobox(combobox_frame, width=40)
        combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setattr(self, f"{tab_id}_combobox", combobox)

        # Group entry frame
        group_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_entry_frame", group_frame)

        ttk.Label(group_frame, text="Group Email:").pack(side=tk.LEFT, padx=(0, 5))
        entry = ttk.Entry(group_frame, width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setattr(self, f"{tab_id}_entry", entry)

        # CSV frame
        csv_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_csv_frame", csv_frame)

        csv_entry = ttk.Entry(csv_frame, width=50)
        csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        setattr(self, f"{tab_id}_csv_entry", csv_entry)

        ttk.Button(
            csv_frame,
            text="Browse",
            command=lambda: self.browse_csv(tab_id)
        ).pack(side=tk.LEFT)

        # Show initial input (combobox)
        self.update_target_input(tab_id)

        return frame

    def create_single_user_target_selection_frame(self, parent, tab_id):
        """
        Create simplified target selection frame for operations that should not
        target all users or groups (e.g., Delete, Suspend, dangerous operations).

        Args:
            parent: Parent widget
            tab_id: Unique identifier for this tab

        Returns:
            ttk.LabelFrame: The target selection frame
        """
        frame = ttk.LabelFrame(parent, text="Target Users", padding="10")

        # Create variable for target type
        target_var = tk.StringVar(value="single")
        setattr(self, f"{tab_id}_target_var", target_var)

        # Radio buttons for target type (simplified - no "All Users" or "Group")
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Single User",
            variable=target_var,
            value="single",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="CSV File",
            variable=target_var,
            value="csv",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Select from List",
            variable=target_var,
            value="list",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT)

        # Input frame (changes based on selection)
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        setattr(self, f"{tab_id}_input_frame", input_frame)

        # Single user entry
        entry_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_entry_frame", entry_frame)

        ttk.Label(entry_frame, text="User Email:").pack(side=tk.LEFT, padx=(0, 5))
        entry = ttk.Entry(entry_frame, width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setattr(self, f"{tab_id}_entry", entry)

        # CSV frame
        csv_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_csv_frame", csv_frame)

        csv_entry = ttk.Entry(csv_frame, width=50)
        csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        setattr(self, f"{tab_id}_csv_entry", csv_entry)

        ttk.Button(
            csv_frame,
            text="Browse",
            command=lambda: self.browse_csv(tab_id)
        ).pack(side=tk.LEFT)

        # List frame (for selecting users)
        list_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_list_frame", list_frame)

        ttk.Label(list_frame, text="Select users (Ctrl+Click for multiple):").pack(anchor=tk.W)

        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        scrollbar = ttk.Scrollbar(list_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_scroll_frame, selectmode=tk.EXTENDED,
                            yscrollcommand=scrollbar.set, height=8)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        setattr(self, f"{tab_id}_listbox", listbox)

        ttk.Button(
            list_frame,
            text="Load Users",
            command=lambda: self.load_users_list(tab_id)
        ).pack(pady=(5, 0))

        # Show initial input (single user)
        self.update_target_input(tab_id)

        return frame

    def create_single_group_target_selection_frame(self, parent, tab_id):
        """
        Create simplified target selection frame for dangerous group operations.
        Excludes "All Groups" option for safety.

        Args:
            parent: Parent widget
            tab_id: Unique identifier for this tab

        Returns:
            ttk.LabelFrame: The target selection frame
        """
        frame = ttk.LabelFrame(parent, text="Target Groups", padding="10")

        # Create variable for target type
        target_var = tk.StringVar(value="single")
        setattr(self, f"{tab_id}_target_var", target_var)

        # Radio buttons for target type (NO "All Groups" option for safety)
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Single Group",
            variable=target_var,
            value="single",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="CSV File",
            variable=target_var,
            value="csv",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Select from List",
            variable=target_var,
            value="list",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT)

        # Input frame (changes based on selection)
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        setattr(self, f"{tab_id}_input_frame", input_frame)

        # Single group entry
        entry_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_entry_frame", entry_frame)

        ttk.Label(entry_frame, text="Group Email:").pack(side=tk.LEFT, padx=(0, 5))
        entry = ttk.Entry(entry_frame, width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setattr(self, f"{tab_id}_entry", entry)

        # CSV frame
        csv_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_csv_frame", csv_frame)

        csv_entry = ttk.Entry(csv_frame, width=50)
        csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        setattr(self, f"{tab_id}_csv_entry", csv_entry)

        ttk.Button(
            csv_frame,
            text="Browse",
            command=lambda: self.browse_csv(tab_id)
        ).pack(side=tk.LEFT)

        # List frame (for selecting groups)
        list_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_list_frame", list_frame)

        ttk.Label(list_frame, text="Select groups (Ctrl+Click for multiple):").pack(anchor=tk.W)

        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        scrollbar = ttk.Scrollbar(list_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_scroll_frame, selectmode=tk.EXTENDED,
                            yscrollcommand=scrollbar.set, height=8)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        setattr(self, f"{tab_id}_listbox", listbox)

        ttk.Button(
            list_frame,
            text="Load Groups",
            command=lambda: self.load_groups_list(tab_id)
        ).pack(pady=(5, 0))

        # Show initial input (single group)
        self.update_target_input(tab_id)

        return frame

    def create_group_target_selection_frame(self, parent, tab_id):
        """
        Create target selection frame for group operations (simplified).

        Args:
            parent: Parent widget
            tab_id: Unique identifier for this tab

        Returns:
            ttk.LabelFrame: The target selection frame
        """
        frame = ttk.LabelFrame(parent, text="Target Groups", padding="10")

        # Create variable for target type
        target_var = tk.StringVar(value="single")
        setattr(self, f"{tab_id}_target_var", target_var)

        # Radio buttons for target type (simplified for groups)
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Single Group",
            variable=target_var,
            value="single",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="All Groups",
            variable=target_var,
            value="all",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="CSV File",
            variable=target_var,
            value="csv",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Select from List",
            variable=target_var,
            value="list",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT)

        # Input frame (changes based on selection)
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        setattr(self, f"{tab_id}_input_frame", input_frame)

        # Single group entry
        entry_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_entry_frame", entry_frame)

        ttk.Label(entry_frame, text="Group Email:").pack(side=tk.LEFT, padx=(0, 5))
        entry = ttk.Entry(entry_frame, width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setattr(self, f"{tab_id}_entry", entry)

        # CSV frame
        csv_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_csv_frame", csv_frame)

        csv_entry = ttk.Entry(csv_frame, width=50)
        csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        setattr(self, f"{tab_id}_csv_entry", csv_entry)

        ttk.Button(
            csv_frame,
            text="Browse",
            command=lambda: self.browse_csv(tab_id)
        ).pack(side=tk.LEFT)

        # List frame (for selecting groups)
        list_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_list_frame", list_frame)

        ttk.Label(list_frame, text="Select groups (Ctrl+Click for multiple):").pack(anchor=tk.W)

        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        scrollbar = ttk.Scrollbar(list_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_scroll_frame, selectmode=tk.EXTENDED,
                            yscrollcommand=scrollbar.set, height=8)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        setattr(self, f"{tab_id}_listbox", listbox)

        ttk.Button(
            list_frame,
            text="Load Groups",
            command=lambda: self.load_groups_list(tab_id)
        ).pack(pady=(5, 0))

        # Show initial input (single group)
        self.update_target_input(tab_id)

        return frame

    def create_target_selection_frame(self, parent, tab_id):
        """
        Create target selection frame with all options.

        Args:
            parent: Parent widget
            tab_id: Unique identifier for this tab (e.g., 'delete_messages')

        Returns:
            ttk.LabelFrame: The target selection frame
        """
        frame = ttk.LabelFrame(parent, text="Target Selection", padding="10")

        # Create variable for target type
        target_var = tk.StringVar(value="single")
        setattr(self, f"{tab_id}_target_var", target_var)

        # Radio buttons for target type
        options_frame = ttk.Frame(frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Single User",
            variable=target_var,
            value="single",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Group",
            variable=target_var,
            value="group",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="All Users",
            variable=target_var,
            value="all",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="CSV File",
            variable=target_var,
            value="csv",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Radiobutton(
            options_frame,
            text="Select from List",
            variable=target_var,
            value="list",
            command=lambda: self.update_target_input(tab_id)
        ).pack(side=tk.LEFT)

        # Input frame (changes based on selection)
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        setattr(self, f"{tab_id}_input_frame", input_frame)

        # Single user / Group entry
        entry_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_entry_frame", entry_frame)

        ttk.Label(entry_frame, text="Email:").pack(side=tk.LEFT, padx=(0, 5))
        entry = ttk.Entry(entry_frame, width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setattr(self, f"{tab_id}_entry", entry)

        # CSV frame
        csv_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_csv_frame", csv_frame)

        csv_entry = ttk.Entry(csv_frame, width=50)
        csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        setattr(self, f"{tab_id}_csv_entry", csv_entry)

        ttk.Button(
            csv_frame,
            text="Browse",
            command=lambda: self.browse_csv(tab_id)
        ).pack(side=tk.LEFT)

        # List frame
        list_frame = ttk.Frame(input_frame)
        setattr(self, f"{tab_id}_list_frame", list_frame)

        ttk.Label(list_frame, text="Select users (Ctrl+Click for multiple):").pack(anchor=tk.W)

        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        scrollbar = ttk.Scrollbar(list_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(list_scroll_frame, selectmode=tk.EXTENDED,
                            yscrollcommand=scrollbar.set, height=8)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        setattr(self, f"{tab_id}_listbox", listbox)

        ttk.Button(
            list_frame,
            text="Load Users",
            command=lambda: self.load_users_list(tab_id)
        ).pack(pady=(5, 0))

        # Show initial input (single user)
        self.update_target_input(tab_id)

        return frame

    def update_target_input(self, tab_id):
        """
        Update target input fields based on selection.

        Args:
            tab_id: Tab identifier
        """
        target_var = getattr(self, f"{tab_id}_target_var")
        target = target_var.get()

        # Hide all possible frames (some may not exist for certain tab types)
        frames_to_hide = [
            f"{tab_id}_entry_frame",
            f"{tab_id}_csv_frame",
            f"{tab_id}_list_frame",
            f"{tab_id}_combobox_frame"
        ]

        for frame_name in frames_to_hide:
            if hasattr(self, frame_name):
                frame = getattr(self, frame_name)
                frame.pack_forget()

        # Show appropriate frame
        if target == "combobox":
            if hasattr(self, f"{tab_id}_combobox_frame"):
                combobox_frame = getattr(self, f"{tab_id}_combobox_frame")
                combobox_frame.pack(fill=tk.X, pady=(5, 0))
        elif target in ["single", "group"]:
            if hasattr(self, f"{tab_id}_entry_frame"):
                entry_frame = getattr(self, f"{tab_id}_entry_frame")
                entry_frame.pack(fill=tk.X, pady=(5, 0))
        elif target == "csv":
            if hasattr(self, f"{tab_id}_csv_frame"):
                csv_frame = getattr(self, f"{tab_id}_csv_frame")
                csv_frame.pack(fill=tk.X, pady=(5, 0))
        elif target == "list":
            if hasattr(self, f"{tab_id}_list_frame"):
                list_frame = getattr(self, f"{tab_id}_list_frame")
                list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        # "all" shows no input

    def browse_csv(self, tab_id):
        """
        Open file browser for CSV selection.

        Args:
            tab_id: Tab identifier
        """
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            csv_entry = getattr(self, f"{tab_id}_csv_entry")
            csv_entry.delete(0, tk.END)
            csv_entry.insert(0, file_path)

    def load_users_list(self, tab_id):
        """
        Load users into listbox for selection.

        Args:
            tab_id: Tab identifier
        """
        listbox = getattr(self, f"{tab_id}_listbox")
        listbox.config(state=tk.NORMAL)
        listbox.delete(0, tk.END)
        listbox.insert(tk.END, "Loading users...")
        listbox.config(state=tk.DISABLED)
        self.update_idletasks()

        # Fetch users in thread
        def fetch_and_populate():
            users = fetch_users()
            self.after(0, lambda: self.populate_listbox(tab_id, users))

        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def populate_listbox(self, tab_id, users):
        """
        Populate listbox with users.

        Args:
            tab_id: Tab identifier
            users: List of user emails
        """
        listbox = getattr(self, f"{tab_id}_listbox")
        listbox.config(state=tk.NORMAL)
        listbox.delete(0, tk.END)

        if users:
            for user in sorted(users):
                listbox.insert(tk.END, user)
        else:
            listbox.insert(tk.END, "(No users found or error fetching)")

    def load_groups_list(self, tab_id):
        """
        Load groups into listbox for selection.

        Args:
            tab_id: Tab identifier
        """
        listbox = getattr(self, f"{tab_id}_listbox")
        listbox.config(state=tk.NORMAL)
        listbox.delete(0, tk.END)
        listbox.insert(tk.END, "Loading groups...")
        listbox.config(state=tk.DISABLED)
        self.update_idletasks()

        # Fetch groups in thread
        def fetch_and_populate():
            groups = fetch_groups()
            self.after(0, lambda: self.populate_groups_listbox(tab_id, groups))

        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def populate_groups_listbox(self, tab_id, groups):
        """
        Populate listbox with groups.

        Args:
            tab_id: Tab identifier
            groups: List of group emails
        """
        listbox = getattr(self, f"{tab_id}_listbox")
        listbox.config(state=tk.NORMAL)
        listbox.delete(0, tk.END)

        if groups:
            for group in sorted(groups):
                listbox.insert(tk.END, group)
        else:
            listbox.insert(tk.END, "(No groups found or error fetching)")

    def load_users_combobox(self, tab_id):
        """
        Load users into combobox for selection.

        Args:
            tab_id: Tab identifier
        """
        if not hasattr(self, f"{tab_id}_combobox"):
            return

        combobox = getattr(self, f"{tab_id}_combobox")

        # Fetch users in thread
        def fetch_and_populate():
            users = fetch_users()
            self.after(0, lambda: self.populate_combobox(tab_id, users))

        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def load_groups_combobox(self, tab_id):
        """
        Load groups into combobox for selection.

        Args:
            tab_id: Tab identifier
        """
        if not hasattr(self, f"{tab_id}_combobox"):
            return

        combobox = getattr(self, f"{tab_id}_combobox")

        # Fetch groups in thread
        def fetch_and_populate():
            groups = fetch_groups()
            self.after(0, lambda: self.populate_combobox(tab_id, groups))

        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def populate_combobox(self, tab_id, items):
        """
        Populate combobox with items (users or groups).

        Args:
            tab_id: Tab identifier
            items: List of email addresses
        """
        if not hasattr(self, f"{tab_id}_combobox"):
            return

        combobox = getattr(self, f"{tab_id}_combobox")

        if items:
            sorted_items = sorted(items)
            combobox['values'] = sorted_items
            # Store full list for fuzzy search
            setattr(self, f"{tab_id}_combobox_all_values", sorted_items)
            # Enable fuzzy search on this combobox
            self.enable_fuzzy_search(combobox, tab_id)
        else:
            combobox['values'] = []

    def enable_fuzzy_search(self, combobox, tab_id):
        """
        Enable fuzzy search on a combobox.

        Args:
            combobox: The combobox widget
            tab_id: Tab identifier for storing full values list
        """
        def on_keyrelease(event):
            """Filter combobox values based on typed text."""
            typed = combobox.get().lower()

            if not typed:
                # If empty, restore all values
                if hasattr(self, f"{tab_id}_combobox_all_values"):
                    all_values = getattr(self, f"{tab_id}_combobox_all_values")
                    combobox['values'] = all_values
                return

            # Get all values
            if hasattr(self, f"{tab_id}_combobox_all_values"):
                all_values = getattr(self, f"{tab_id}_combobox_all_values")
            else:
                all_values = combobox['values']

            # Filter values that contain the typed text (fuzzy match)
            filtered = [item for item in all_values if typed in item.lower()]

            # Update combobox with filtered values
            combobox['values'] = filtered

            # Open dropdown if there are matches, but keep focus on entry
            if filtered and not event.keysym in ('Up', 'Down', 'Return', 'Escape'):
                combobox.event_generate('<Down>')
                # Immediately restore focus to the entry field
                combobox.focus_set()

        # Bind the keyrelease event
        combobox.bind('<KeyRelease>', on_keyrelease)

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

        if target == "combobox":
            combobox = getattr(self, f"{tab_id}_combobox")
            email = combobox.get().strip()
            if not email or '@' not in email:
                messagebox.showerror("Validation Error", "Please enter or select a valid email address.")
                return None
            return [email]

        elif target == "single":
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
            return [group_email]

        elif target == "all":
            users = fetch_users()
            if not users:
                messagebox.showerror("Error", "Failed to fetch users or no users found.")
                return None

            # Confirm bulk operation
            if not self.confirm_bulk_operation(len(users), "this operation"):
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

            # Confirm bulk operation
            if not self.confirm_bulk_operation(len(result), "this operation"):
                return None

            return result

        elif target == "list":
            listbox = getattr(self, f"{tab_id}_listbox")
            selection = listbox.curselection()
            if not selection:
                messagebox.showerror("Validation Error", "Please select at least one user from the list.")
                return None
            users = [listbox.get(i) for i in selection]

            # Confirm if many users selected
            if len(users) > 50:
                if not self.confirm_bulk_operation(len(users), "this operation"):
                    return None

            return users

        return None

    def get_target_groups(self, tab_id):
        """
        Get the list of target groups based on selection.

        Args:
            tab_id: Tab identifier

        Returns:
            list: List of group email addresses, or None if validation fails
        """
        target_var = getattr(self, f"{tab_id}_target_var")
        target = target_var.get()

        if target == "combobox":
            combobox = getattr(self, f"{tab_id}_combobox")
            email = combobox.get().strip()
            if not email or '@' not in email:
                messagebox.showerror("Validation Error", "Please enter or select a valid group email address.")
                return None
            return [email]

        elif target == "single":
            entry = getattr(self, f"{tab_id}_entry")
            email = entry.get().strip()
            if not email or '@' not in email:
                messagebox.showerror("Validation Error", "Please enter a valid group email address.")
                return None
            return [email]

        elif target == "all":
            groups = fetch_groups()
            if not groups:
                messagebox.showerror("Error", "Failed to fetch groups or no groups found.")
                return None

            # Confirm bulk operation
            if not self.confirm_bulk_operation(len(groups), "this operation"):
                return None

            return groups

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

            # Confirm bulk operation
            if not self.confirm_bulk_operation(len(result), "this operation"):
                return None

            return result

        elif target == "list":
            listbox = getattr(self, f"{tab_id}_listbox")
            selection = listbox.curselection()
            if not selection:
                messagebox.showerror("Validation Error", "Please select at least one group from the list.")
                return None
            groups = [listbox.get(i) for i in selection]

            # Confirm if many groups selected
            if len(groups) > 50:
                if not self.confirm_bulk_operation(len(groups), "this operation"):
                    return None

            return groups

        return None

    def confirm_bulk_operation(self, count, operation_name):
        """
        Confirm bulk operation with user.

        Args:
            count: Number of users affected
            operation_name: Name of the operation

        Returns:
            bool: True if confirmed, False otherwise
        """
        if count > 50:
            response = messagebox.askyesno(
                "Confirm Bulk Operation",
                f"This will affect {count} users.\n\n"
                f"Are you sure you want to proceed with {operation_name}?",
                icon='warning'
            )
            return response
        return True

    # ==================== PROGRESS AND RESULTS ====================

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
        results_text = scrolledtext.ScrolledText(frame, height=5, width=60, state=tk.DISABLED)
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
        """
        Clear results text area.

        Args:
            progress_frame: The progress frame containing results
        """
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

    def run_operation(self, operation_func, progress_frame, *args, dry_run=False, on_success=None):
        """
        Run an operation in a background thread.

        Args:
            operation_func: The module function to call
            progress_frame: The progress frame for this operation
            *args: Arguments to pass to operation_func
            dry_run: If True, preview operation without executing
            on_success: Optional callback function to call on successful completion
        """
        if self.operation_running:
            messagebox.showwarning("Operation Running", "An operation is already in progress.")
            return

        self.operation_running = True
        self.cancel_flag.clear()

        # Clear and prepare UI
        progress_frame.results_text.config(state=tk.NORMAL)
        progress_frame.results_text.delete("1.0", tk.END)

        if dry_run:
            progress_frame.results_text.insert(tk.END, "DRY RUN MODE - No changes will be made\n")
            progress_frame.results_text.insert(tk.END, "="*50 + "\n\n")

        progress_frame.progress_bar.start(10)

        # Create queue for communication
        result_queue = queue.Queue()

        # Worker thread
        def worker():
            try:
                # Pass dry_run flag to operation if it supports it
                import inspect
                sig = inspect.signature(operation_func)
                if 'dry_run' in sig.parameters:
                    for progress in operation_func(*args, dry_run=dry_run):
                        if self.cancel_flag.is_set():
                            result_queue.put(('cancelled', None))
                            return
                        result_queue.put(('progress', progress))
                else:
                    # Fallback for functions without dry_run support
                    for progress in operation_func(*args):
                        if self.cancel_flag.is_set():
                            result_queue.put(('cancelled', None))
                            return
                        result_queue.put(('progress', progress))

                result_queue.put(('done', None))
            except Exception as e:
                result_queue.put(('error', str(e)))

        # Start thread
        self.current_thread = threading.Thread(target=worker, daemon=True)
        self.current_thread.start()

        # Start checking queue
        self.check_operation_queue(progress_frame, result_queue, on_success)

    def check_operation_queue(self, progress_frame, result_queue, on_success=None):
        """
        Check queue for operation updates.

        Args:
            progress_frame: The progress frame
            result_queue: Queue for thread communication
            on_success: Optional callback to call on successful completion
        """
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
                self.after(100, lambda: self.check_operation_queue(progress_frame, result_queue, on_success))

            elif msg_type == 'done':
                # Operation complete
                progress_frame.progress_bar.stop()
                progress_frame.results_text.config(state=tk.NORMAL)
                progress_frame.results_text.insert(tk.END, "\n" + "="*50 + "\n")
                progress_frame.results_text.insert(tk.END, "Operation completed!\n")
                progress_frame.results_text.config(state=tk.DISABLED)
                self.operation_running = False

                # Call success callback if provided
                if on_success:
                    on_success()

            elif msg_type == 'cancelled':
                # Operation cancelled
                progress_frame.progress_bar.stop()
                progress_frame.results_text.config(state=tk.NORMAL)
                progress_frame.results_text.insert(tk.END, "\n" + "="*50 + "\n")
                progress_frame.results_text.insert(tk.END, "Operation cancelled by user.\n")
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
            self.after(100, lambda: self.check_operation_queue(progress_frame, result_queue, on_success))

    def clear_fields(self, *widgets):
        """
        Clear the content of specified widgets (Entry or Combobox).

        Args:
            *widgets: Variable number of widget objects to clear
        """
        for widget in widgets:
            if hasattr(widget, 'delete'):  # Entry widgets
                widget.delete(0, tk.END)
            elif hasattr(widget, 'set'):  # Combobox or other widgets with set method
                widget.set("")

    def create_scrollable_frame(self, parent):
        """
        Create a scrollable frame container.

        Args:
            parent: Parent widget

        Returns:
            tuple: (container_frame, scrollable_frame) where:
                - container_frame should be packed/gridded in parent
                - scrollable_frame is where content should be added
        """
        # Create container
        container = ttk.Frame(parent)

        # Create canvas and scrollbar
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure canvas scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)

        # Pack components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return container, scrollable_frame

    def cancel_operation(self):
        """Cancel the currently running operation."""
        if self.operation_running:
            self.cancel_flag.set()

    # ==================== UTILITY METHODS ====================

    def validate_email(self, email):
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            bool: True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_date(self, date_str, format='YYYY/MM/DD'):
        """
        Validate date string format.

        Args:
            date_str: Date string to validate
            format: Expected format (default: YYYY/MM/DD)

        Returns:
            bool: True if valid, False otherwise
        """
        import re
        if format == 'YYYY/MM/DD':
            pattern = r'^\d{4}/\d{2}/\d{2}$'
            if re.match(pattern, date_str):
                try:
                    year, month, day = map(int, date_str.split('/'))
                    # Basic validation
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        return True
                except:
                    pass
        return False

    def show_error(self, message, title="Error"):
        """
        Show error message dialog.

        Args:
            message: Error message
            title: Dialog title
        """
        messagebox.showerror(title, message)

    def show_info(self, message, title="Information"):
        """
        Show information message dialog.

        Args:
            message: Information message
            title: Dialog title
        """
        messagebox.showinfo(title, message)

    def load_combobox_async(self, combobox, fetch_function, tab_id=None,
                           enable_fuzzy=True, default_value="",
                           loading_text="Loading...", sort=True):
        """
        Load data into combobox asynchronously with optional fuzzy search.

        This method handles the common pattern of:
        1. Showing loading state
        2. Fetching data in background thread
        3. Populating combobox with results
        4. Optionally enabling fuzzy search

        Args:
            combobox: Combobox widget to populate
            fetch_function: Function to call that returns list of items
            tab_id: Optional tab ID for fuzzy search storage
            enable_fuzzy: Enable fuzzy search on combobox (default: True)
            default_value: Value to set after loading (default: "")
            loading_text: Text to show while loading (default: "Loading...")
            sort: Sort results alphabetically (default: True)

        Example:
            self.load_combobox_async(
                self.user_combobox,
                fetch_users,
                tab_id='create_user',
                enable_fuzzy=True
            )
        """
        # Set loading state
        combobox['values'] = [loading_text]
        combobox.set(loading_text)

        def fetch_and_populate():
            """Background thread function to fetch and populate data."""
            try:
                items = fetch_function()

                if items:
                    # Sort if requested
                    if sort:
                        items = sorted(items)

                    # Update combobox on main thread
                    self.after(0, lambda: combobox.configure(values=items))
                    self.after(0, lambda: combobox.set(default_value))

                    # Enable fuzzy search if requested and tab_id provided
                    if enable_fuzzy and tab_id:
                        self.after(0, lambda: self.enable_fuzzy_search(combobox, tab_id))
                    elif enable_fuzzy:
                        # For standalone comboboxes without tab_id
                        self.after(0, lambda: self._enable_standalone_fuzzy_search(combobox, items))
                else:
                    # No data returned
                    self.after(0, lambda: combobox.configure(values=[]))
                    self.after(0, lambda: combobox.set(default_value))

            except Exception as e:
                # Error occurred during fetch
                log_error("ComboboxLoader", f"Failed to load combobox data: {str(e)}")
                self.after(0, lambda: combobox.configure(values=[]))
                self.after(0, lambda: combobox.set("Error loading data"))

        # Start background thread
        import threading
        threading.Thread(target=fetch_and_populate, daemon=True).start()

    def _enable_standalone_fuzzy_search(self, combobox, all_values):
        """
        Enable fuzzy search on a standalone combobox (without tab_id).

        This is used internally by load_combobox_async for comboboxes
        that don't have a tab_id for storing fuzzy search data.

        Args:
            combobox: Combobox widget
            all_values: List of all possible values
        """
        # Store all values on the combobox itself
        combobox._all_values = all_values

        def on_keyrelease(event):
            """Handle key release events for fuzzy filtering."""
            if event.keysym in ('Up', 'Down', 'Return', 'Escape', 'Tab'):
                return

            typed = combobox.get().lower()

            # Filter values
            filtered = [item for item in combobox._all_values if typed in item.lower()]

            # Update combobox values
            combobox['values'] = filtered

            # Show dropdown if there are matches
            if filtered:
                combobox.event_generate('<Down>')
                combobox.focus_set()  # Keep focus on text entry

        # Bind the event
        combobox.bind('<KeyRelease>', on_keyrelease)

    def browse_csv_file(self, entry_widget, title="Select CSV File"):
        """
        Open file dialog to browse for CSV file and populate entry widget.

        Args:
            entry_widget: Entry or Combobox widget to populate with file path
            title: Dialog title (default: "Select CSV File")

        Returns:
            str: Selected file path, or None if canceled

        Example:
            self.browse_csv_file(self.csv_entry, "Select User CSV File")
        """
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
            return file_path

        return None

    def read_and_validate_csv(self, file_path, required_fields, operation_name):
        """
        Read and validate CSV file with standard error handling.

        This method handles the common pattern of:
        1. Reading CSV file with proper encoding
        2. Checking if file is empty
        3. Validating required fields exist
        4. Confirming bulk operations with user

        Args:
            file_path: Path to CSV file
            required_fields: List of required field names (column headers)
            operation_name: Name of operation for error messages (e.g., "create users")

        Returns:
            list: List of dictionaries (CSV rows), or None on error/cancel

        Example:
            data = self.read_and_validate_csv(
                csv_path,
                ['email', 'firstname', 'lastname'],
                'create users'
            )
            if data:
                # Process data
        """
        import csv

        try:
            # Read CSV file
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)

            # Check if empty
            if not data:
                self.show_error("CSV file is empty.")
                return None

            # Validate required fields
            for field in required_fields:
                for i, row in enumerate(data, start=1):
                    if field not in row or not row[field].strip():
                        self.show_error(
                            f"Row {i}: Missing or empty required field '{field}'.\n\n"
                            f"Please ensure all rows have values for: {', '.join(required_fields)}",
                            "Validation Error"
                        )
                        return None

            # Confirm bulk operation
            if not self.confirm_bulk_operation(len(data), operation_name):
                return None

            return data

        except FileNotFoundError:
            self.show_error(f"CSV file not found: {file_path}")
            return None
        except PermissionError:
            self.show_error(f"Permission denied reading CSV file: {file_path}")
            return None
        except Exception as e:
            self.show_error(f"Failed to read CSV file: {str(e)}")
            return None

    def create_mode_toggle(self, parent, tab_id, single_label="Single Entry",
                          csv_label="CSV Bulk Import", default_mode="single"):
        """
        Create standard single/CSV mode toggle with frames.

        This method creates the common pattern of:
        1. Radio buttons for single vs CSV mode
        2. Two frames (single_frame and csv_frame) that toggle visibility
        3. Automatic frame switching based on mode selection

        The frames are returned for customization with operation-specific widgets.

        Args:
            parent: Parent widget
            tab_id: Tab identifier for storing mode variable
            single_label: Label for single mode radio button
            csv_label: Label for CSV mode radio button
            default_mode: Default mode ('single' or 'csv')

        Returns:
            tuple: (mode_frame, single_frame, csv_frame, mode_var)
                - mode_frame: Frame containing radio buttons
                - single_frame: Frame for single entry widgets
                - csv_frame: Frame for CSV entry widgets
                - mode_var: StringVar containing current mode

        Example:
            mode_frame, single_frame, csv_frame, mode_var = self.create_mode_toggle(
                parent_tab,
                'create_user',
                single_label="Create Single User",
                csv_label="Bulk Create from CSV"
            )

            # Then add your custom widgets to single_frame and csv_frame
            ttk.Label(single_frame, text="Email:").pack()
            ttk.Entry(single_frame).pack()
        """
        # Create mode variable and store it
        mode_var = tk.StringVar(value=default_mode)
        setattr(self, f"{tab_id}_mode", mode_var)

        # Create mode selection frame
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        # Create toggle function
        def toggle_mode():
            if mode_var.get() == "single":
                csv_frame.pack_forget()
                single_frame.pack(fill=tk.X, expand=True)
            else:
                single_frame.pack_forget()
                csv_frame.pack(fill=tk.X, expand=True)

        # Radio buttons
        ttk.Radiobutton(
            mode_frame,
            text=single_label,
            variable=mode_var,
            value="single",
            command=toggle_mode
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            mode_frame,
            text=csv_label,
            variable=mode_var,
            value="csv",
            command=toggle_mode
        ).pack(side=tk.LEFT)

        # Create frames for single and CSV modes
        single_frame = ttk.LabelFrame(parent, text=single_label, padding="10")
        csv_frame = ttk.LabelFrame(parent, text=csv_label, padding="10")

        # Show default frame
        if default_mode == "single":
            single_frame.pack(fill=tk.X, expand=True)
        else:
            csv_frame.pack(fill=tk.X, expand=True)

        return mode_frame, single_frame, csv_frame, mode_var
