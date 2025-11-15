# Packaging & Build Instructions

This folder contains all the files needed to build platform-specific executables for the GAM Admin Tool.

## Prerequisites

```bash
# Install PyInstaller
pip install pyinstaller

# Install other dependencies (if not already installed)
pip install -r ../requirements.txt
```

## Building for Your Platform

### Universal Build (All Platforms)

The `build.spec` file works on all platforms. Run from the project root:

```bash
# From the project root directory
cd /path/to/GAM_CLI_Tool

# (Optional) Create application icon
python3 packaging/create_icon.py

# Build the executable
pyinstaller packaging/build.spec

# Output will be in dist/GAM_Admin_Tool.exe (Windows)
# or dist/GAM_Admin_Tool (macOS/Linux)
```

### Platform-Specific Builds

**Note**: You must build on the target platform (Windows build on Windows, macOS build on macOS, etc.)

#### Windows

```bash
# Build on Windows machine
python packaging/create_icon.py
pyinstaller packaging/build.spec

# Output: dist/GAM_Admin_Tool.exe
```

**Requirements:**
- Windows 10 or later
- Python 3.8+
- PyInstaller

#### macOS

```bash
# Build on macOS machine
python3 packaging/create_icon.py
pyinstaller packaging/build.spec

# Output: dist/GAM_Admin_Tool (or .app bundle)
```

**Requirements:**
- macOS 10.13 or later
- Python 3.8+
- PyInstaller
- Xcode Command Line Tools (for code signing, optional)

**Code Signing (Optional):**
```bash
# Sign the app
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/GAM_Admin_Tool.app

# Verify signature
codesign --verify --verbose dist/GAM_Admin_Tool.app
```

#### Linux

```bash
# Build on Linux machine
python3 packaging/create_icon.py
pyinstaller packaging/build.spec

# Output: dist/GAM_Admin_Tool
```

**Requirements:**
- Ubuntu 20.04+ / Debian 10+ / Fedora 30+ or equivalent
- Python 3.8+
- PyInstaller
- tkinter (python3-tk on Ubuntu/Debian)

**Make executable:**
```bash
chmod +x dist/GAM_Admin_Tool
```

## Build Files

- **build.spec** - PyInstaller specification file (works on all platforms)
- **create_icon.py** - Creates application icon from Python code
- **README.md** - This file

## Output Structure

After building, you'll have:

```
dist/
└── GAM_Admin_Tool[.exe]    # Standalone executable
```

## Troubleshooting

### "tkinter not found" Error

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

### Build Takes Too Long

The first build may take 2-5 minutes. Subsequent builds are faster.

### Large Executable Size

The executable includes Python runtime and all dependencies, typically 30-50 MB. This is normal for PyInstaller builds.

### Icon Not Showing

1. Ensure `create_icon.py` runs successfully
2. Check that `assets/icon.ico` exists
3. Rebuild with `pyinstaller packaging/build.spec`

## Distribution

The executable in `dist/` is self-contained and can be distributed to users. However, users must still:

1. Install GAM7 separately
2. Have GAM7 in their system PATH
3. Authenticate GAM7 with their Google Workspace

## Notes

- The build spec excludes unnecessary modules (matplotlib, numpy, pandas, scipy) to reduce size
- Console window is disabled for GUI app (`console=False`)
- UPX compression is enabled to reduce executable size
- All source code is bundled into the executable

## Support

For build issues, see the main project README or open an issue on GitHub.
