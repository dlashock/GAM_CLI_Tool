"""
CSV file handling module.

Validates and reads CSV files containing user email addresses
for bulk operations.
"""

import csv
import os
from .logger import log_error


def validate_csv(file_path):
    """
    Validate that a CSV file exists and has the required 'email' header.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        tuple: (success: bool, error_message: str or None)
            - (True, None) if file is valid
            - (False, error_message) if validation fails
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return (False, f"File not found: {file_path}")

    # Check if file is readable
    if not os.access(file_path, os.R_OK):
        return (False, f"File is not readable: {file_path}")

    # Check if file is empty
    if os.path.getsize(file_path) == 0:
        return (False, "File is empty")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to read the first line as CSV
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                return (False, "File is empty or has no header row")

            # Check for 'email' column (case-sensitive)
            if 'email' not in header:
                return (False, f"CSV file must have 'email' column in header. Found: {', '.join(header)}")

            # File is valid
            return (True, None)

    except UnicodeDecodeError:
        return (False, "File encoding error. Please ensure file is UTF-8 encoded.")
    except csv.Error as e:
        return (False, f"CSV parsing error: {str(e)}")
    except Exception as e:
        return (False, f"Error validating file: {str(e)}")


def read_csv_emails(file_path):
    """
    Read email addresses from a CSV file.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        tuple: (success: bool, data: list or error_message: str)
            - (True, [emails]) if successful
            - (False, error_message) if reading fails

    The CSV file must have an 'email' column header.
    Empty rows and rows without email values are skipped.
    """
    # First validate the file
    valid, error_msg = validate_csv(file_path)
    if not valid:
        log_error("Read CSV", error_msg)
        return (False, error_msg)

    try:
        emails = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Read all email addresses
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because header is row 1
                email = row.get('email', '').strip()

                # Skip empty emails
                if not email:
                    continue

                # Basic email validation (optional but recommended)
                if '@' not in email:
                    log_error("Read CSV", f"Invalid email format in row {row_num}: {email}")
                    continue

                emails.append(email)

        # Check if we found any emails
        if not emails:
            error_msg = "No valid email addresses found in CSV file"
            log_error("Read CSV", error_msg)
            return (False, error_msg)

        return (True, emails)

    except UnicodeDecodeError:
        error_msg = "File encoding error. Please ensure file is UTF-8 encoded."
        log_error("Read CSV", error_msg)
        return (False, error_msg)
    except csv.Error as e:
        error_msg = f"CSV parsing error: {str(e)}"
        log_error("Read CSV", error_msg)
        return (False, error_msg)
    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        log_error("Read CSV", error_msg)
        return (False, error_msg)


def count_emails_in_csv(file_path):
    """
    Count the number of valid email addresses in a CSV file without reading all data.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        int: Number of valid email addresses, or 0 on error
    """
    success, result = read_csv_emails(file_path)
    if success:
        return len(result)
    else:
        return 0


def create_sample_csv(file_path):
    """
    Create a sample CSV file with the correct format.

    This is a utility function for testing or providing users with a template.

    Args:
        file_path (str): Path where the sample CSV should be created

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['email'])
            writer.writerow(['user1@example.com'])
            writer.writerow(['user2@example.com'])
            writer.writerow(['user3@example.com'])
        return True
    except Exception as e:
        log_error("Create Sample CSV", f"Error creating sample file: {str(e)}")
        return False
