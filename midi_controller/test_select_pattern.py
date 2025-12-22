#!/usr/bin/env python3
"""
Test script: Select pattern and trigger piano roll script.

Demonstrates using the dual-controller system:
- fl_dual_port: FL Studio API calls via MIDI (SysEx dual-controller)
- focus_management: Window focus control
- piano_roll_utils: Piano roll operations
"""

import time
from fl_dual_port import send_command, close_ports
from focus_management import save_current_window, activate_fl_studio, restore_focus
from piano_roll_utils import trigger_piano_roll_script, print_piano_roll_info

def main():
    try:
        print("piano roll before")
        print_piano_roll_info()

        saved_window = save_current_window()

        activate_fl_studio()

        # Use dual-controller system via send_command
        send_command("patterns.jumpToPattern(2)", expect_response=False)
        send_command("ui.showWindow(3)", expect_response=False)
        send_command("ui.setFocused(3)", expect_response=False)

        trigger_piano_roll_script()

        if saved_window:
            restore_focus(saved_window)

        time.sleep(0.1)  # Brief pause for focus change
        print("piano roll after")
        print_piano_roll_info()

    finally:
        close_ports()

if __name__ == '__main__':
    main()
