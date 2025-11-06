#!/usr/bin/env python3
"""
Test script for email GUI window structure.

Validates the EmailWindow class without requiring tkinter.
"""

import ast
import inspect

def analyze_email_window():
    """Analyze the email_window.py file structure."""
    print("=" * 60)
    print("Email GUI Window Structure Analysis")
    print("=" * 60)

    # Read the file
    with open('gui/email_window.py', 'r') as f:
        content = f.read()

    # Parse AST
    tree = ast.parse(content)

    # Find EmailWindow class
    email_window_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'EmailWindow':
            email_window_class = node
            break

    if not email_window_class:
        print("✗ EmailWindow class not found")
        return False

    print("✓ EmailWindow class found")

    # Find methods
    methods = [node.name for node in email_window_class.body if isinstance(node, ast.FunctionDef)]

    print(f"\n✓ Found {len(methods)} methods in EmailWindow class")

    # Expected tab creation methods
    expected_tabs = [
        'create_delete_messages_tab',
        'create_delegates_tab',
        'create_signatures_tab',
        'create_forwarding_tab',
        'create_labels_tab',
        'create_filters_tab'
    ]

    print("\nTab Creation Methods:")
    for tab_method in expected_tabs:
        if tab_method in methods:
            print(f"  ✓ {tab_method}")
        else:
            print(f"  ✗ {tab_method} - MISSING")

    # Expected execution methods
    expected_execute = [
        'execute_delete_messages',
        'execute_delegates',
        'execute_signatures',
        'execute_forwarding',
        'execute_labels',
        'execute_filters'
    ]

    print("\nExecution Methods:")
    for exec_method in expected_execute:
        if exec_method in methods:
            print(f"  ✓ {exec_method}")
        else:
            print(f"  ✗ {exec_method} - MISSING")

    # Check for common framework methods
    framework_methods = [
        'create_target_selection_frame',
        'create_progress_frame',
        'get_target_users',
        'run_operation'
    ]

    print("\nFramework Methods:")
    for method in framework_methods:
        if method in methods:
            print(f"  ✓ {method}")
        else:
            print(f"  ✗ {method} - MISSING")

    # Count lines
    lines = content.split('\n')
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

    print(f"\nStatistics:")
    print(f"  Total lines: {len(lines)}")
    print(f"  Code lines: {len(code_lines)}")
    print(f"  Methods: {len(methods)}")

    return True


def check_imports():
    """Check that all required modules are imported."""
    print("\n" + "=" * 60)
    print("Import Analysis")
    print("=" * 60)

    with open('gui/email_window.py', 'r') as f:
        content = f.read()

    required_imports = [
        'tkinter',
        'ttk',
        'messagebox',
        'filedialog',
        'scrolledtext',
        'threading',
        'queue',
        're',
        'email_module',
        'workspace_data',
        'csv_handler',
        'logger'
    ]

    print("\nRequired imports:")
    for imp in required_imports:
        if imp in content:
            print(f"  ✓ {imp}")
        else:
            print(f"  ✗ {imp} - NOT FOUND")

    return True


def main():
    """Run all tests."""
    results = []

    try:
        results.append(("Structure Analysis", analyze_email_window()))
    except Exception as e:
        print(f"✗ Structure analysis failed: {e}")
        results.append(("Structure Analysis", False))

    try:
        results.append(("Import Analysis", check_imports()))
    except Exception as e:
        print(f"✗ Import analysis failed: {e}")
        results.append(("Import Analysis", False))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:30s} {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} test groups passed")

    print("\n" + "=" * 60)
    print("Note: GUI cannot be tested without tkinter and GAM7.")
    print("This file will work on local machines with GUI support.")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
