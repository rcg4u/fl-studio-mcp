#!/usr/bin/env python3
"""
Test script to list all FL Studio windows for debugging.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from piano_roll_utils import list_fl_windows

if __name__ == '__main__':
    print("Listing FL Studio windows...\n")
    windows = list_fl_windows()
    if windows:
        print(f"\nResult:\n{windows}")
    else:
        print("No windows found or error occurred")
