#!/bin/bash
# Quick Mac Testing Script for GAM Admin Tool

echo "╔════════════════════════════════════════════════════════╗"
echo "║       GAM Admin Tool - Mac Quick Test Script          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ $PYTHON_VERSION"
else
    echo "   ✗ Python 3 not found. Install from python.org"
    exit 1
fi

# Check tkinter
echo ""
echo "2. Checking tkinter..."
if python3 -c "import tkinter" 2>/dev/null; then
    echo "   ✓ tkinter is available"
else
    echo "   ✗ tkinter not available"
    echo "   On Mac, tkinter should come with Python"
    echo "   Try reinstalling Python from python.org"
    exit 1
fi

# Check GAM7
echo ""
echo "3. Checking GAM7..."
if command -v gam &> /dev/null; then
    GAM_VERSION=$(gam version 2>&1 | head -1)
    echo "   ✓ GAM found: $GAM_VERSION"

    # Check if it's GAM7
    if echo "$GAM_VERSION" | grep -q "7\."; then
        echo "   ✓ GAM7 detected!"
    else
        echo "   ⚠ Warning: Not GAM7. Please upgrade."
        echo "   Visit: https://github.com/GAM-team/GAM"
    fi

    # Check authentication
    echo ""
    echo "4. Checking GAM authentication..."
    if gam info domain &> /dev/null; then
        echo "   ✓ GAM is authenticated"
    else
        echo "   ✗ GAM is not authenticated"
        echo "   Run: gam oauth create"
    fi
else
    echo "   ✗ GAM not found"
    echo "   Install from: https://github.com/GAM-team/GAM"
    echo ""
    echo "   Quick install: pip3 install gam7"
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "Ready to test!"
echo ""
echo "Run the application with:"
echo "    python3 main.py"
echo ""
echo "Or build executable with:"
echo "    pip3 install pyinstaller"
echo "    pyinstaller build.spec"
echo "════════════════════════════════════════════════════════"
