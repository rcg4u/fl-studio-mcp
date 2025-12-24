"""
Piano roll utilities for FL Studio.

Handles triggering piano roll scripts and reading piano roll state.
"""

import json
import time
import subprocess
from pathlib import Path
from pynput.keyboard import Key, Controller

def list_fl_windows():
    """List all FL Studio window names for debugging"""
    try:
        script = '''
        tell application "System Events"
            set windowList to (windows of process "OsxFL")
            set result to ""
            repeat with w in windowList
                set wName to name of w
                set result to result & wName & ", "
            end repeat
            return result
        end tell
        '''

        result = subprocess.run(['osascript', '-e', script],
                              capture_output=True, text=True, timeout=2)

        if result.returncode == 0:
            windows = result.stdout.strip()
            return windows
    except Exception as e:
        pass
    return None

def get_piano_roll_center():
    """Get the center coordinates of the FL Studio piano roll window using AppleScript

    Handles both detached and docked piano roll windows.
    Falls back to center of main FL Studio window if piano roll is docked.
    """
    try:
        script = '''
        tell application "System Events"
            set windowList to (windows of process "OsxFL")
            repeat with w in windowList
                set wName to name of w
                -- Check for detached piano roll windows (Piano roll in title)
                if wName contains "Piano roll" or wName contains "piano" then
                    set pos to position of w
                    set sz to size of w
                    set x to (item 1 of pos) + ((item 1 of sz) / 2)
                    set y to (item 2 of pos) + ((item 2 of sz) / 2)
                    return x & "," & y
                end if
                -- If no detached piano roll found, use main FL Studio window center
                -- (piano roll is likely docked in the main window)
                if wName contains "FL Studio" then
                    set pos to position of w
                    set sz to size of w
                    set x to (item 1 of pos) + ((item 1 of sz) / 2)
                    set y to (item 2 of pos) + ((item 2 of sz) / 2)
                    return x & "," & y
                end if
            end repeat
        end tell
        return "600,400"
        '''

        result = subprocess.run(['osascript', '-e', script],
                              capture_output=True, text=True, timeout=2)

        if result.returncode == 0 and result.stdout.strip():
            coords = result.stdout.strip().split(',')
            if len(coords) == 2:
                x, y = int(float(coords[0])), int(float(coords[1]))
                return (x, y)
    except Exception as e:
        pass

    # Fallback to default coordinates (works well in most cases)
    return (600, 400)

def trigger_piano_roll_script():
    """Send CMD+OPT+Y to run last piano roll script (with FL Studio focus)"""
    try:
        # Send keystroke
        keyboard = Controller()

        with keyboard.pressed(Key.cmd):
            with keyboard.pressed(Key.alt):
                keyboard.press('y')
                keyboard.release('y')

        # Wait for script to execute and write state file
        time.sleep(0.5)

    except Exception as e:
        import traceback
        raise

def trigger_with_f3_plus_9():
    """Send F3+9 to trigger piano roll script"""
    try:
        keyboard = Controller()

        # Press F3 and 9 together (F3 held while 9 is pressed)
        with keyboard.pressed(Key.f3):
            keyboard.press('9')
            keyboard.release('9')

        keyboard.release(Key.f3)

        # Wait for script to execute and write state file
        time.sleep(0.5)

    except Exception as e:
        import traceback
        raise

def print_piano_roll_info():
    """Get piano roll state metadata"""
    state_file = Path.home() / "Documents/Image-Line/FL Studio/Settings/Piano roll scripts/piano_roll_state.json"

    try:
        with open(state_file, 'r') as f:
            data = json.load(f)

    except FileNotFoundError:
        pass
    except Exception as e:
        pass
