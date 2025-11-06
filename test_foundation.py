#!/usr/bin/env python3
"""
Test script for GAM Admin Tool foundation layer.

Tests individual components without requiring GAM7.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from utils import gam_check, logger, workspace_data, csv_handler
        from gui import main_window, groups_window, reports_window
        from gui import calendar_window, drive_window, acls_window
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_logger():
    """Test logger functionality."""
    print("\nTesting logger...")
    try:
        from utils.logger import setup_logger, log_error, get_log_file_path

        # Setup logger
        setup_logger('test_gam_tool.log')

        # Log a test error
        log_error("Test Operation", "This is a test error message")

        # Check if log file exists
        log_path = get_log_file_path()
        if os.path.exists(log_path):
            print(f"✓ Logger working, log file created at: {log_path}")
            with open(log_path, 'r') as f:
                print(f"  Last log entry: {f.readlines()[-1].strip()}")
            return True
        else:
            print("✗ Log file not created")
            return False
    except Exception as e:
        print(f"✗ Logger test failed: {e}")
        return False

def test_csv_handler():
    """Test CSV handler functionality."""
    print("\nTesting CSV handler...")
    try:
        from utils.csv_handler import create_sample_csv, validate_csv, read_csv_emails

        # Create a sample CSV
        test_file = 'test_emails.csv'
        if create_sample_csv(test_file):
            print(f"✓ Sample CSV created: {test_file}")

            # Validate it
            valid, error = validate_csv(test_file)
            if valid:
                print("✓ CSV validation passed")

                # Read emails
                success, emails = read_csv_emails(test_file)
                if success:
                    print(f"✓ CSV reading successful, found {len(emails)} emails:")
                    for email in emails:
                        print(f"    - {email}")

                    # Cleanup
                    os.remove(test_file)
                    print(f"✓ Test file cleaned up")
                    return True
                else:
                    print(f"✗ CSV reading failed: {emails}")
            else:
                print(f"✗ CSV validation failed: {error}")
        else:
            print("✗ Sample CSV creation failed")
        return False
    except Exception as e:
        print(f"✗ CSV handler test failed: {e}")
        return False

def test_gam_check():
    """Test GAM check functionality."""
    print("\nTesting GAM check...")
    try:
        from utils.gam_check import check_gam_version, check_gam_auth

        # Check version
        version_ok, version_msg = check_gam_version()
        if version_ok:
            print("✓ GAM7 is installed and detected")
        else:
            print(f"⚠ GAM7 not detected: {version_msg}")

        # Check auth (only if version check passed)
        if version_ok:
            auth_ok, auth_msg = check_gam_auth()
            if auth_ok:
                print("✓ GAM is authenticated")
            else:
                print(f"⚠ GAM authentication issue: {auth_msg}")

        return True  # Test succeeds even if GAM not installed
    except Exception as e:
        print(f"✗ GAM check test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("GAM Admin Tool - Foundation Layer Tests")
    print("=" * 60)

    results = []
    results.append(("Imports", test_imports()))
    results.append(("Logger", test_logger()))
    results.append(("CSV Handler", test_csv_handler()))
    results.append(("GAM Check", test_gam_check()))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20s} {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

    # Cleanup
    if os.path.exists('test_gam_tool.log'):
        os.remove('test_gam_tool.log')

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
