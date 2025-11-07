#!/usr/bin/env python3
"""
Test script to diagnose import issues with GUI modules.
"""

import sys
import traceback

def test_import(module_path, class_name):
    """Test importing a specific module."""
    print(f"\n{'='*60}")
    print(f"Testing: {module_path}.{class_name}")
    print('='*60)
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"✓ SUCCESS: {class_name} imported successfully")
        return True
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}")
        print(f"Error: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("GAM Admin Tool - Import Diagnostic Test")
    print("="*60)

    tests = [
        ("gui.base_operation_window", "BaseOperationWindow"),
        ("gui.email_window", "EmailWindow"),
        ("gui.users_window", "UsersWindow"),
        ("gui.groups_window", "GroupsWindow"),
        ("modules.email", "delete_messages"),
        ("modules.users", "create_user"),
        ("modules.groups", "create_group"),
        ("utils.workspace_data", "fetch_users"),
    ]

    results = {}
    for module_path, item_name in tests:
        results[f"{module_path}.{item_name}"] = test_import(module_path, item_name)

    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed} passed, {failed} failed")

    sys.exit(0 if failed == 0 else 1)
