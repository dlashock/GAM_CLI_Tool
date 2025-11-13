"""
Password Generator Dialog for GAM Admin Tool.

Provides a dialog to generate secure random passwords with customizable options.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import string


class PasswordGeneratorDialog(tk.Toplevel):
    """Dialog for generating secure random passwords."""

    def __init__(self, parent, callback):
        """
        Initialize the password generator dialog.

        Args:
            parent: Parent window
            callback: Function to call with generated password
        """
        super().__init__(parent)
        self.callback = callback
        self.generated_password = None

        self.title("Generate Password")
        self.geometry("450x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.center_on_parent(parent)

        self.create_widgets()

    def center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """Create and layout all widgets."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Password Generator",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 15))

        # Length selection
        length_frame = ttk.LabelFrame(main_frame, text="Password Length", padding="10")
        length_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(length_frame, text="Length:").pack(side=tk.LEFT, padx=(0, 10))

        self.length_var = tk.IntVar(value=16)
        length_spinbox = ttk.Spinbox(
            length_frame,
            from_=14,
            to=128,
            textvariable=self.length_var,
            width=10
        )
        length_spinbox.pack(side=tk.LEFT)

        ttk.Label(
            length_frame,
            text="(minimum: 14)",
            font=('Arial', 8),
            foreground='gray'
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Character options
        options_frame = ttk.LabelFrame(main_frame, text="Include Characters", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))

        self.uppercase_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Uppercase Letters (A-Z)",
            variable=self.uppercase_var
        ).pack(anchor=tk.W, pady=2)

        self.lowercase_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Lowercase Letters (a-z)",
            variable=self.lowercase_var
        ).pack(anchor=tk.W, pady=2)

        self.numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Numbers (0-9)",
            variable=self.numbers_var
        ).pack(anchor=tk.W, pady=2)

        self.special_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Special Characters (!@#$%^&*)",
            variable=self.special_var
        ).pack(anchor=tk.W, pady=2)

        # Generated password display
        display_frame = ttk.LabelFrame(main_frame, text="Generated Password", padding="10")
        display_frame.pack(fill=tk.X, pady=(0, 15))

        self.password_entry = ttk.Entry(display_frame, font=('Courier', 10))
        self.password_entry.pack(fill=tk.X, pady=(0, 5))
        self.password_entry.config(state='readonly')

        copy_btn = ttk.Button(
            display_frame,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard
        )
        copy_btn.pack()

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="Generate",
            command=self.generate_password,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame,
            text="Use Password",
            command=self.use_password,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=15
        ).pack(side=tk.RIGHT)

        # Generate initial password
        self.generate_password()

    def generate_password(self):
        """Generate a random password based on selected options."""
        length = self.length_var.get()

        # Validate length
        if length < 14:
            messagebox.showerror(
                "Invalid Length",
                "Password length must be at least 14 characters.",
                parent=self
            )
            self.length_var.set(14)
            return

        # Build character set
        char_set = ""
        required_chars = []

        if self.uppercase_var.get():
            char_set += string.ascii_uppercase
            required_chars.append(random.choice(string.ascii_uppercase))

        if self.lowercase_var.get():
            char_set += string.ascii_lowercase
            required_chars.append(random.choice(string.ascii_lowercase))

        if self.numbers_var.get():
            char_set += string.digits
            required_chars.append(random.choice(string.digits))

        if self.special_var.get():
            special_chars = "!@#$%^&*"
            char_set += special_chars
            required_chars.append(random.choice(special_chars))

        # Validate at least one option selected
        if not char_set:
            messagebox.showerror(
                "No Options Selected",
                "Please select at least one character type.",
                parent=self
            )
            return

        # Generate password ensuring at least one of each selected type
        remaining_length = length - len(required_chars)
        password_chars = required_chars + [random.choice(char_set) for _ in range(remaining_length)]

        # Shuffle to randomize position of required characters
        random.shuffle(password_chars)

        self.generated_password = ''.join(password_chars)

        # Display password
        self.password_entry.config(state='normal')
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, self.generated_password)
        self.password_entry.config(state='readonly')

    def copy_to_clipboard(self):
        """Copy generated password to clipboard."""
        if self.generated_password:
            self.clipboard_clear()
            self.clipboard_append(self.generated_password)
            messagebox.showinfo(
                "Copied",
                "Password copied to clipboard!",
                parent=self
            )

    def use_password(self):
        """Use the generated password and close dialog."""
        if self.generated_password:
            self.callback(self.generated_password)
            self.destroy()
        else:
            messagebox.showwarning(
                "No Password",
                "Please generate a password first.",
                parent=self
            )
