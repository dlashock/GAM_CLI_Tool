"""
Main window for GAM Admin Tool.

Displays the main menu with buttons for different administrative categories.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class MainWindow(ttk.Frame):
    """
    Main menu window for the GAM Admin Tool.

    Displays category buttons for different types of Google Workspace
    administrative operations.
    """

    def __init__(self, parent):
        """
        Initialize the main window.

        Args:
            parent: The parent tkinter widget (usually root)
        """
        super().__init__(parent)
        self.parent = parent

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Modern theme

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create and layout all widgets for the main window."""
        # Main container
        main_container = ttk.Frame(self, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_container,
            text="GAM Admin Tool - Main Menu",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))

        # Subtitle
        subtitle_label = ttk.Label(
            main_container,
            text="Select an administrative category:",
            font=('Arial', 11)
        )
        subtitle_label.pack(pady=(0, 30))

        # Button container with grid layout
        button_container = ttk.Frame(main_container)
        button_container.pack(expand=True)

        # Configure button style
        self.style.configure(
            'Category.TButton',
            font=('Arial', 12),
            padding=20
        )

        # Define categories with their handlers
        categories = [
            ("Email Operations", self.open_email_window),
            ("User Management", self.open_users_window),
            ("Group Management", self.open_groups_window),
            ("Reports", self.open_reports_window),
            ("Calendar Operations", self.open_calendar_window),
            ("Drive Operations", self.open_drive_window)
        ]

        # Create buttons in 2x3 grid
        for i, (label, command) in enumerate(categories):
            row = i // 2
            col = i % 2

            button = ttk.Button(
                button_container,
                text=label,
                command=command,
                style='Category.TButton',
                width=20
            )
            button.grid(row=row, column=col, padx=10, pady=10, sticky='ew')

        # Configure grid weights for centering
        button_container.grid_columnconfigure(0, weight=1)
        button_container.grid_columnconfigure(1, weight=1)

        # Footer
        footer_label = ttk.Label(
            main_container,
            text="GAM7 must be installed and authenticated",
            font=('Arial', 9),
            foreground='gray'
        )
        footer_label.pack(side=tk.BOTTOM, pady=(20, 0))

    def open_email_window(self):
        """Open the Email Operations window."""
        try:
            from gui.email_window import EmailWindow
            EmailWindow(self.parent)
        except ImportError as e:
            messagebox.showerror(
                "Import Error",
                f"Failed to import Email Operations module.\n\nError: {str(e)}\n\nPlease ensure you've pulled the latest changes."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Email Operations: {str(e)}")

    def open_users_window(self):
        """Open the User Management window."""
        try:
            from gui.users_window import UsersWindow
            UsersWindow(self.parent)
        except ImportError as e:
            messagebox.showerror(
                "Import Error",
                f"Failed to import User Management module.\n\nError: {str(e)}\n\nPlease ensure you've pulled the latest changes."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open User Management: {str(e)}")

    def open_groups_window(self):
        """Open the Groups Management window."""
        try:
            from gui.groups_window import GroupsWindow
            GroupsWindow(self.parent)
        except ImportError as e:
            messagebox.showerror(
                "Import Error",
                f"Failed to import Group Management module.\n\nError: {str(e)}\n\nPlease ensure you've pulled the latest changes."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Group Management: {str(e)}")

    def open_reports_window(self):
        """Open the Reports window."""
        try:
            from gui.reports_window import ReportsWindow
            ReportsWindow(self.parent)
        except ImportError as e:
            messagebox.showinfo(
                "Module Not Available",
                "Reports module is not yet implemented."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Reports: {str(e)}")

    def open_calendar_window(self):
        """Open the Calendar Operations window."""
        try:
            from gui.calendar_window import CalendarWindow
            CalendarWindow(self.parent)
        except ImportError as e:
            messagebox.showinfo(
                "Module Not Available",
                "Calendar Operations module is not yet implemented."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Calendar Operations: {str(e)}")

    def open_drive_window(self):
        """Open the Drive Operations window."""
        try:
            from gui.drive_window import DriveWindow
            DriveWindow(self.parent)
        except ImportError as e:
            messagebox.showerror(
                "Import Error",
                f"Failed to import Drive Operations module.\n\nError: {str(e)}\n\nPlease ensure you've pulled the latest changes."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Drive Operations: {str(e)}")
