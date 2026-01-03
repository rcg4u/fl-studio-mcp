"""
Window focus management utilities for macOS.

Handles saving, restoring, and switching focus between applications
using AppleScript.
"""

import subprocess

def save_current_window():
    """Save the current active window/app name"""
    try:
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script],
                              capture_output=True, text=True)
        if result.returncode == 0:
            app_name = result.stdout.strip()
            return app_name
    except Exception as e:
        print(f"⚠️  Could not save current window: {e}")
    return None

def restore_focus(window_id):
    """Restore focus to saved window"""
    if not window_id:
        return False
    try:
        subprocess.run(['osascript', '-e', f'tell application "{window_id}" to activate'],
                     timeout=3, capture_output=True)
        return True
    except Exception as e:
        print(f"⚠️  Could not restore focus: {e}")
        return False

def activate_fl_studio():
    """Activate FL Studio application using AppleScript"""
    try:
        script = '''
        tell application "System Events"
            if exists process "OsxFL" then
                tell process "OsxFL"
                    set frontmost to true
                end tell
            end if
        end tell
        '''
        subprocess.run(['osascript', '-e', script], timeout=3, capture_output=True)
        return True
    except Exception as e:
        return False
