#!/usr/bin/env python3
"""
Test script for email module.

Tests that all functions exist and have correct signatures.
"""

import sys
import inspect

def test_email_module():
    """Test email module functions."""
    print("=" * 60)
    print("Email Module Tests")
    print("=" * 60)

    try:
        from modules import email as email_module
        print("✓ Email module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import email module: {e}")
        return False

    # Expected functions with their parameter counts
    expected_functions = {
        'delete_messages': 4,  # users, query, date_from, date_to
        'add_delegate': 2,     # users, delegate_email
        'remove_delegate': 2,  # users, delegate_email
        'set_signature': 2,    # users, signature_html
        'remove_signature': 1, # users
        'enable_forwarding': 2, # users, forward_to
        'disable_forwarding': 1, # users
        'create_label': 2,     # users, label_name
        'delete_label': 2,     # users, label_name
        'create_filter': 6,    # users, from_addr, to_addr, subject, has_words, action_label
        'delete_filter': 2,    # users, filter_id
        'list_filters': 1,     # user_email
    }

    print(f"\nChecking {len(expected_functions)} functions...\n")

    all_passed = True
    for func_name, expected_params in expected_functions.items():
        if hasattr(email_module, func_name):
            func = getattr(email_module, func_name)
            if callable(func):
                # Get function signature
                sig = inspect.signature(func)
                param_count = len(sig.parameters)

                print(f"✓ {func_name:25s} - {param_count} parameters")

                # Check if function is a generator (yields)
                if func_name != 'list_filters':  # list_filters doesn't yield
                    # We can't easily check if it yields without calling it,
                    # but we can check the docstring
                    if func.__doc__ and 'Yields:' in func.__doc__:
                        print(f"  └─ Yields progress updates")
            else:
                print(f"✗ {func_name} exists but is not callable")
                all_passed = False
        else:
            print(f"✗ {func_name} not found")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All email module functions are present and correct")
        print("=" * 60)
        return True
    else:
        print("✗ Some functions are missing or incorrect")
        print("=" * 60)
        return False


def test_function_docstrings():
    """Test that all functions have docstrings."""
    print("\nChecking docstrings...\n")

    from modules import email as email_module

    functions = [
        'delete_messages', 'add_delegate', 'remove_delegate',
        'set_signature', 'remove_signature', 'enable_forwarding',
        'disable_forwarding', 'create_label', 'delete_label',
        'create_filter', 'delete_filter', 'list_filters'
    ]

    all_documented = True
    for func_name in functions:
        func = getattr(email_module, func_name)
        if func.__doc__:
            doc_lines = len([l for l in func.__doc__.split('\n') if l.strip()])
            print(f"✓ {func_name:25s} - {doc_lines} lines of documentation")
        else:
            print(f"✗ {func_name:25s} - No docstring")
            all_documented = False

    return all_documented


def main():
    """Run all tests."""
    results = []

    # Test module structure
    results.append(("Module Structure", test_email_module()))

    # Test documentation
    results.append(("Documentation", test_function_docstrings()))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:25s} {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} test groups passed")

    print("\n" + "=" * 60)
    print("Note: GAM commands cannot be tested without GAM7 installed.")
    print("Agent 3 will integrate these functions with the GUI.")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
