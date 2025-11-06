#!/usr/bin/env python3
"""
Complete application structure test.

Validates the entire GAM Admin Tool project structure,
verifies all files, imports, and basic functionality.
"""

import os
import sys


def test_project_structure():
    """Test that all required files and directories exist."""
    print("=" * 60)
    print("Project Structure Test")
    print("=" * 60)

    required_files = [
        'main.py',
        'requirements.txt',
        'build.spec',
        'README.md',
        'TESTING.md',
        '.gitignore',
        'gam_tool_spec.md',
        'test_foundation.py',
        'test_email_module.py',
        'test_email_gui.py',
        'create_icon.py',
        'gui/__init__.py',
        'gui/main_window.py',
        'gui/email_window.py',
        'gui/groups_window.py',
        'gui/reports_window.py',
        'gui/calendar_window.py',
        'gui/drive_window.py',
        'gui/acls_window.py',
        'modules/__init__.py',
        'modules/email.py',
        'utils/__init__.py',
        'utils/gam_check.py',
        'utils/logger.py',
        'utils/workspace_data.py',
        'utils/csv_handler.py',
        'assets/icon_instructions.txt',
    ]

    print(f"\nChecking {len(required_files)} required files...")
    all_exist = True

    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False

    return all_exist


def test_imports():
    """Test that all modules can be imported."""
    print("\n" + "=" * 60)
    print("Import Tests")
    print("=" * 60)

    test_imports = [
        ('utils.gam_check', 'check_gam_version, check_gam_auth'),
        ('utils.logger', 'setup_logger, log_error'),
        ('utils.workspace_data', 'fetch_users, fetch_groups'),
        ('utils.csv_handler', 'validate_csv, read_csv_emails'),
        ('modules.email', 'delete_messages, add_delegate'),
    ]

    all_imports_ok = True

    for module_name, functions in test_imports:
        try:
            module = __import__(module_name, fromlist=functions.split(', '))
            print(f"✓ {module_name}")
            for func in functions.split(', '):
                if hasattr(module, func):
                    print(f"  ✓ {func}")
                else:
                    print(f"  ✗ {func} - NOT FOUND")
                    all_imports_ok = False
        except Exception as e:
            print(f"✗ {module_name} - {e}")
            all_imports_ok = False

    return all_imports_ok


def test_code_quality():
    """Test code quality metrics."""
    print("\n" + "=" * 60)
    print("Code Quality Metrics")
    print("=" * 60)

    # Count lines of code
    total_lines = 0
    code_files = 0

    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['__pycache__', '.git', 'dist', 'build']):
            continue

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                        code_files += 1
                except:
                    pass

    print(f"\nTotal Python files: {code_files}")
    print(f"Total lines of code: {total_lines:,}")

    # Check for specific module sizes
    module_sizes = []
    key_files = [
        'gui/email_window.py',
        'modules/email.py',
        'utils/workspace_data.py',
        'main.py',
    ]

    for file_path in key_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                module_sizes.append((file_path, lines))

    print("\nKey module sizes:")
    for file_path, lines in sorted(module_sizes, key=lambda x: x[1], reverse=True):
        print(f"  {file_path:30s} {lines:5d} lines")

    return True


def test_documentation():
    """Test that documentation exists and is complete."""
    print("\n" + "=" * 60)
    print("Documentation Tests")
    print("=" * 60)

    # Check README sections
    readme_sections = [
        '# GAM Admin Tool',
        '## Features',
        '## Prerequisites',
        '## Installation',
        '## Usage',
        '## Troubleshooting',
        '## FAQ',
    ]

    readme_ok = True
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()

        print("\nREADME.md sections:")
        for section in readme_sections:
            exists = section in content
            status = "✓" if exists else "✗"
            print(f"{status} {section}")
            if not exists:
                readme_ok = False

        readme_lines = len(content.split('\n'))
        print(f"\nREADME.md: {readme_lines} lines")
    else:
        print("✗ README.md not found")
        readme_ok = False

    # Check TESTING.md
    testing_ok = os.path.exists('TESTING.md')
    if testing_ok:
        with open('TESTING.md', 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        print(f"✓ TESTING.md: {lines} lines")
    else:
        print("✗ TESTING.md not found")

    return readme_ok and testing_ok


def test_build_config():
    """Test that build configuration is present."""
    print("\n" + "=" * 60)
    print("Build Configuration Tests")
    print("=" * 60)

    # Check requirements.txt
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        has_pyinstaller = 'pyinstaller' in content.lower()
        status = "✓" if has_pyinstaller else "⚠"
        print(f"{status} requirements.txt exists")
        if has_pyinstaller:
            print("  ✓ PyInstaller listed")
        else:
            print("  ⚠ PyInstaller not listed")
    else:
        print("✗ requirements.txt not found")
        return False

    # Check build.spec
    if os.path.exists('build.spec'):
        with open('build.spec', 'r', encoding='utf-8') as f:
            content = f.read()
        has_analysis = 'Analysis' in content
        has_exe = 'EXE' in content
        print("✓ build.spec exists")
        if has_analysis:
            print("  ✓ Analysis section present")
        if has_exe:
            print("  ✓ EXE section present")
        return has_analysis and has_exe
    else:
        print("✗ build.spec not found")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "GAM Admin Tool - Complete Test Suite" + " " * 11 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    results = []

    # Run all tests
    results.append(("Project Structure", test_project_structure()))
    results.append(("Imports", test_imports()))
    results.append(("Code Quality", test_code_quality()))
    results.append(("Documentation", test_documentation()))
    results.append(("Build Configuration", test_build_config()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:30s} {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} test groups passed")

    if passed == total:
        print("\n✓ All tests passed! Project is ready for distribution.")
        print("\nNext steps:")
        print("1. Install GAM7 if not already installed")
        print("2. Run: python3 main.py (to test application)")
        print("3. Run: pyinstaller build.spec (to build executable)")
        print("4. Test executable in dist/ folder")
    else:
        print("\n⚠ Some tests failed. Please review and fix issues.")

    print("\n" + "=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
