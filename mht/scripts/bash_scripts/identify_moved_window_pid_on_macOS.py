#!/usr/bin/env python3

"""
This script is designed for macOS to identify the process ID (PID) of a window 
that is moved on the screen within a specified time (3 seconds). It uses 
macOS-specific APIs from the Quartz and Foundation frameworks to:

1. Capture the current state of all visible windows on the screen.
2. Prompt the user to move a window within a given time frame.
3. Capture the updated state of visible windows after the time frame.
4. Compare the two states to detect which window was moved.
5. Extract the process ID (PID) of the application associated with the moved window.
6. Display detailed process information using the `ps` command.

This script is useful for debugging or identifying processes associated with 
specific window activities. It assumes the Quartz module is installed, which is 
part of the PyObjC package. If the required module is not installed, the script 
provides installation instructions.

Dependencies:
- Quartz (macOS-specific, part of PyObjC)
- Foundation (macOS-specific)

Usage:
Run this script in a macOS environment. Follow the on-screen instructions 
to move a window within the specified time frame (3 seconds).
"""

# Import necessary macOS-specific modules
try:
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListExcludeDesktopElements, kCGNullWindowID
except ModuleNotFoundError:
    # Provide guidance if the Quartz module is missing
    print("macOS-specific Python module 'Quartz' not found.")
    print("Please install it via pip:")
    print("\n  pip install pyobjc-framework-Quartz\n")
    raise

# Import additional modules for data handling and system interaction
from Foundation import NSSet, NSMutableSet
import os
import time


def get_visible_windows():
    """
    Retrieves a snapshot of the current visible windows on macOS.
    Excludes desktop elements.
    """
    return CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID)


def identify_moved_window(initial_window_list, updated_window_list):
    """
    Identifies which window (if any) has been moved between two snapshots.
    Compares two sets of window information.

    Args:
        initial_window_list: List of windows at the first snapshot.
        updated_window_list: List of windows at the second snapshot.

    Returns:
        The string representation of the moved window, or None if no window was moved.
    """
    # Create a mutable set from the initial window list
    initial_set = NSMutableSet.setWithArray_(initial_window_list)
    # Subtract updated windows from the initial set to find differences
    initial_set.minusSet_(NSSet.setWithArray_(updated_window_list))
    # Return the result as a string
    return str(initial_set)


def extract_process_id(window_info):
    """
    Extracts the process ID (PID) of the moved window from its information string.

    Args:
        window_info: String representation of the window information.

    Returns:
        The PID as a string, or None if PID is not found.
    """
    if 'PID' in window_info:
        return window_info.split('PID = ')[1].split(';')[0]
    return None


def display_process_info(process_id):
    """
    Prints detailed process information for a given PID.

    Args:
        process_id: The process ID of the target process.
    """
    command = f'ps -p {process_id}'
    print(f"\nProcess information ('{command}'):\n")
    os.system(command)


def main():
    """
    Main function to identify and display the PID of a moved window on macOS.
    """
    print("Move the target window (within 3 seconds)...")
    # Capture the initial snapshot of visible windows
    initial_window_list = get_visible_windows()
    time.sleep(3)  # Wait for the user to move a window
    print()

    # Capture the updated snapshot of visible windows
    updated_window_list = get_visible_windows()

    # Identify the moved window by comparing the two snapshots
    moved_window_info = identify_moved_window(initial_window_list, updated_window_list)

    if moved_window_info:
        # Extract the PID of the moved window
        process_id = extract_process_id(moved_window_info)
        if process_id:
            print(f"Moved window belongs to process with ID (PID): {process_id}")
            display_process_info(process_id)
        else:
            print("No process ID (PID) found for the moved window.")
    else:
        print("No moved window detected.")
    print()


if __name__ == "__main__":
    main()
