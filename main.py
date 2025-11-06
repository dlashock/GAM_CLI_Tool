#!/usr/bin/env python3
"""
GAM Admin Tool - Main Entry Point

A graphical user interface for GAMADV-XTD3/GAM7 that provides an intuitive
interface for common Google Workspace administrative tasks.

This application requires GAM7 to be installed and authenticated.
Visit: https://github.com/GAM-team/GAM
"""

import tkinter as tk
from tkinter import messagebox
import sys

from utils.gam_check import check_gam_version, check_gam_auth
from utils.logger import setup_logger
from gui.main_window import MainWindow


def startup_checks():
    """
    Perform startup checks to ensure GAM7 is installed and authenticated.

    Returns:
        bool: True if all checks pass, False otherwise
    """
    # Check GAM7 version
    version_ok, version_error = check_gam_version()
    if not version_ok:
        messagebox.showerror(
            "GAM Version Error",
            version_error
        )
        return False

    # Check GAM authentication
    auth_ok, auth_error = check_gam_auth()
    if not auth_ok:
        messagebox.showerror(
            "GAM Authentication Error",
            auth_error
        )
        return False

    return True


def main():
    """
    Main application entry point.
    """
    # Setup logger
    setup_logger()

    # Create root window (hidden initially)
    root = tk.Tk()
    root.withdraw()  # Hide root window during startup checks

    # Perform startup checks
    if not startup_checks():
        root.destroy()
        sys.exit(1)

    # All checks passed, show the main window
    root.deiconify()  # Show root window
    root.title("GAM Admin Tool")
    root.geometry("800x600")

    # Set minimum window size
    root.minsize(600, 400)

    # Create main window
    app = MainWindow(root)
    app.pack(fill=tk.BOTH, expand=True)

    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Handle window close
    def on_closing():
        """Handle application close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit GAM Admin Tool?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
