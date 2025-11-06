"""
Reports window for GAM Admin Tool.

This module is under development.
"""

import tkinter as tk
from tkinter import ttk


class ReportsWindow(tk.Toplevel):
    """
    Reports window (placeholder).

    This window will be implemented in a future release.
    """

    def __init__(self, parent):
        """
        Initialize the Reports window.

        Args:
            parent: The parent tkinter widget
        """
        super().__init__(parent)

        self.title("Reports")
        self.geometry("500x300")

        # Center the window
        self.transient(parent)
        self.grab_set()

        # Create widgets
        self.create_widgets()

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        """Create and layout widgets."""
        # Main container
        container = ttk.Frame(self, padding="40")
        container.pack(fill=tk.BOTH, expand=True)

        # Icon or placeholder
        icon_label = ttk.Label(
            container,
            text="🚧",
            font=('Arial', 48)
        )
        icon_label.pack(pady=(0, 20))

        # Message
        message_label = ttk.Label(
            container,
            text="This module is under development.\nCheck back in a future release!",
            font=('Arial', 12),
            justify=tk.CENTER
        )
        message_label.pack(pady=20)

        # Close button
        close_button = ttk.Button(
            container,
            text="Close",
            command=self.destroy,
            width=15
        )
        close_button.pack(pady=20)
