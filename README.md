# GAM Admin Tool

A modern graphical user interface (GUI) for [GAM7](https://github.com/GAM-team/GAM) that simplifies common Google Workspace administrative tasks. **Specifically designed for K-12 educational environments**, this tool provides an intuitive, point-and-click interface for managing email operations, users, groups, and more, though it can be utilized anywhere Google Workspace is in use.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

### Email Operations (Fully Implemented)

- **Delete Messages** - Remove emails by query with optional date ranges
- **Manage Delegates** - Add or remove mailbox delegation access
- **Manage Signatures** - Set or remove HTML email signatures
- **Manage Forwarding** - Enable or disable email forwarding
- **Manage Labels** - Create or delete Gmail labels
- **Manage Filters** - Create or delete email filters with flexible criteria

### Bulk Operations Support

- Process single users, groups, all users, or CSV lists
- Multi-select from workspace user list
- Real-time progress tracking
- Detailed success/failure reporting
- Comprehensive error logging

### Coming Soon

- Group Management
- Google Workspace Reports
- Calendar Operations
- Drive Operations
- ACL Management

## Prerequisites

### Required

**GAM7 must be installed and configured:**

1. **Install GAM7** from: https://github.com/GAM-team/GAM
2. **Authenticate GAM**: `gam oauth create`
3. **Verify installation**: `gam info domain`

**Important Notes:**
- This application is a GUI wrapper for GAM7 commands
- GAM7 is NOT included and must be installed separately
- GAM7 must be in your system PATH
- You must have Google Workspace admin access

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8 or higher (for running from source)
- **GAM7**: Latest version recommended
- **Display**: GUI requires X11/display server (tkinter)

## Installation

### Run from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/GAM_CLI_Tool.git
cd GAM_CLI_Tool

# Install dependencies (optional, only for building)
pip install -r requirements.txt

# Run the application
python3 main.py
```

**Note**: Platform-specific installers (Windows .exe, macOS .app, Linux binary) will be available in future releases.

## Usage

### Quick Start

1. **Launch the application**
   ```bash
   python3 main.py
   # or double-click GAM_Admin_Tool.exe
   ```

2. **Select an operation category** (e.g., "Email Operations")

3. **Choose target users**:
   - Single User: Enter one email address
   - Group: Enter group email
   - All Users: Processes all workspace users
   - CSV File: Upload a CSV with email column
   - Select from List: Multi-select from fetched users

4. **Configure operation parameters** (varies by operation)

5. **Click Execute** and monitor progress

6. **Review results** in the progress window

### CSV File Format

For bulk operations using CSV files:

```csv
email
user1@yourdomain.com
user2@yourdomain.com
user3@yourdomain.com
```

**Requirements:**
- Header row must contain `email` column (case-sensitive)
- One email address per row
- UTF-8 encoding

## Building from Source

### Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# (Optional) Create application icon
python3 create_icon.py

# Build the executable
pyinstaller build.spec

# Output will be in dist/GAM_Admin_Tool.exe
```

### Building on Different Platforms

- **Windows**: Produces `.exe` executable
- **macOS**: Produces `.app` bundle
- **Linux**: Produces standalone binary

**Note**: Build on the target platform (Windows build must be done on Windows, etc.)

## Troubleshooting

### "Please upgrade to GAM7" Error

**Cause**: You have GAMADV-XTD3 instead of GAM7
**Solution**: Upgrade to GAM7 from https://github.com/GAM-team/GAM

### "GAM is not authenticated" Error

**Cause**: GAM has not been authorized to access your Google Workspace
**Solution**:
```bash
gam oauth create
# Follow the authentication prompts in your browser
gam info domain  # Verify authentication
```

### "Command not found: gam" Error

**Cause**: GAM7 is not in your system PATH
**Solution**:
- **Windows**: Add GAM7 directory to PATH environment variable
- **macOS/Linux**: Add GAM7 to PATH in `.bashrc` or `.zshrc`
- Verify with: `which gam` (macOS/Linux) or `where gam` (Windows)

### Operations Failing Silently

**Cause**: Permissions or GAM command errors
**Solution**:
1. Click "View Error Log" button in the application
2. Check `gam_tool_errors.log` in application directory
3. Verify GAM command works in terminal: `gam user test@domain.com info`

### GUI Won't Start

**Cause**: tkinter not installed
**Solution**:
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`
- **macOS**: tkinter included with Python
- **Windows**: tkinter included with Python

### Application Freezes During Operations

**Cause**: Normal for large user lists
**Note**: The application uses threading to stay responsive. Large operations may take time but the GUI should remain interactive. Monitor the progress bar and results window.

## FAQ

**Q: Does this replace GAM7?**
A: No, this is a GUI wrapper that makes GAM7 easier to use. GAM7 must be installed.

**Q: Can I run this on a server without a display?**
A: No, this requires a graphical environment (X11/display server). For headless operation, use GAM7 directly.

**Q: Is my Google Workspace data safe?**
A: Yes. This tool only executes GAM7 commands. It has the same access and security as GAM7. Your credentials stay local.

**Q: Can I use this with GAMADV-XTD3?**
A: No, GAM7 is required. Please upgrade to GAM7.

**Q: What Python version do I need?**
A: Python 3.8 or higher. Python 3.10+ recommended.

**Q: Can I contribute or add features?**
A: Yes! This is an open-source project. Fork the repository and submit pull requests with your enhancements.

## Links

- **GAM7 Documentation**: https://github.com/GAM-team/GAM/wiki
- **GAM7 Installation**: https://github.com/GAM-team/GAM
- **Report Issues**: [GitHub Issues](../../issues)
- **GAM Community**: https://groups.google.com/g/google-apps-manager

## License

MIT License - See LICENSE file for details

## Acknowledgments

- **GAM Team** for creating and maintaining GAM7
- **Google Workspace** for providing comprehensive admin APIs
- **Python tkinter** for the cross-platform GUI framework

## Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **GAM Support**: https://groups.google.com/g/google-apps-manager

---

**Note**: This tool is not officially affiliated with Google or the GAM project. It is an independent GUI wrapper built by the community.
