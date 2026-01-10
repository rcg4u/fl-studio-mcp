#!/usr/bin/env python3
"""
FastMCP server for FL Studio
Handles piano roll operations, project file reading, and music theory tools
"""

from fastmcp import FastMCP
import json
import os
import platform
import subprocess
import sys
import time
import threading
from pathlib import Path

# Import StateManager for FL Studio operations
from midi_controller.fl_studio_state_manager import get_state_manager


# Initialize FastMCP server
mcp = FastMCP("FL Studio MCP Server")

# =============================================================================
# State Manager Integration (lazy initialization)
# =============================================================================

_state_manager = None
_state_manager_started = False


def _get_state_manager():
    """Get or create the StateManager singleton (lazy initialization)."""
    global _state_manager, _state_manager_started
    if _state_manager is None:
        _state_manager = get_state_manager()
    if not _state_manager_started:
        _state_manager.start()
        _state_manager_started = True
    return _state_manager

class FLStudioTrigger:
    """Cross-platform FL Studio trigger - integrated into MCP server"""

    def __init__(self):
        self.system = platform.system()

    def save_current_window(self):
        """Save the current active window/app name"""
        try:
            if self.system == "Darwin":
                script = '''
                tell application "System Events"
                    set frontApp to name of first application process whose frontmost is true
                    return frontApp
                end tell
                '''
                result = subprocess.run(['osascript', '-e', script],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            elif self.system == "Windows":
                try:
                    import win32gui
                    hwnd = win32gui.GetForegroundWindow()
                    return win32gui.GetWindowText(hwnd)
                except ImportError:
                    pass
        except Exception:
            pass
        return None

    def restore_focus(self, window_id):
        """Restore focus to saved window"""
        if not window_id:
            return False
        try:
            if self.system == "Darwin":
                # Handle different app name formats
                app_name = window_id.split(':')[-1] if ':' in window_id else window_id

                # Common app name mappings
                app_mappings = {
                    'Claude': 'Claude',
                    'Terminal': 'Terminal',
                    'iTerm': 'iTerm',
                    'VSCode': 'Code',
                    'Visual Studio Code': 'Code',
                    'Chrome': 'Google Chrome',
                    'Safari': 'Safari',
                    'Firefox': 'Firefox'
                }

                # Map common names to actual application names
                actual_app_name = app_mappings.get(app_name, app_name)

                # Try to activate the app
                subprocess.run(['osascript', '-e', f'tell application "{actual_app_name}" to activate'],
                             timeout=3, capture_output=True)

                # Additional wait to ensure focus is restored
                time.sleep(0.2)

            elif self.system == "Windows":
                try:
                    import win32gui
                    hwnd = win32gui.FindWindow(None, window_id)
                    if hwnd and win32gui.IsWindow(hwnd):
                        win32gui.SetForegroundWindow(hwnd)
                except ImportError:
                    pass
            return True
        except Exception as e:
            return False

    def focus_fl_studio(self):
        """Focus FL Studio window"""
        try:
            if self.system == "Darwin":
                script = '''
                tell application "System Events"
                    if exists process "OsxFL" then
                        tell process "OsxFL"
                            set frontmost to true
                        end tell
                    end if
                end tell
                '''
                subprocess.run(['osascript', '-e', script], timeout=3)
                return True
            elif self.system == "Windows":
                try:
                    import win32gui
                    hwnd = win32gui.FindWindow("TFruityLooshMainForm", None)
                    if hwnd:
                        if win32gui.IsIconic(hwnd):
                            win32gui.ShowWindow(hwnd, 9)
                        win32gui.SetForegroundWindow(hwnd)
                        return True
                except ImportError:
                    pass
        except Exception:
            pass
        return False

    def trigger_flstudio(self):
        """Focus FL Studio, focus piano roll window, send Cmd+Opt+Y keystroke, and restore focus"""
        if not self._is_fl_studio_running():
            return False

        saved_window = self.save_current_window()

        if not self.focus_fl_studio():
            return False

        # Wait for FL Studio to receive focus before sending keystroke
        time.sleep(0.2)

        # Focus the piano roll window using FL Studio's API
        try:
            from midi_controller.fl_dual_port import send_command
            send_command("ui.setFocused(3)", expect_response=False)  # widPianoRoll = 3
            time.sleep(0.1)  # Brief wait for window focus
        except:
            pass  # If focus fails, continue anyway

        # Send the keystroke to trigger "Run Last Script"
        if not self._send_keystroke():
            return False

        # Brief wait after keystroke
        time.sleep(0.1)

        # Try to restore previous window focus (best effort)
        if saved_window:
            try:
                self.restore_focus(saved_window)
            except:
                # If restore fails, no big deal - user can refocus manually
                pass

        return True

    def _send_keystroke(self):
        """Send F3+B keystroke (global FL Studio shortcut for BeginLLMInteraction script)"""
        try:
            from pynput.keyboard import Key, Controller
            keyboard = Controller()

            # Press F3 and B together (F3 held while B is pressed)
            with keyboard.pressed(Key.f3):
                keyboard.press('b')
                keyboard.release('b')
            keyboard.release(Key.f3)

            # Wait for FL Studio to process the keystroke
            time.sleep(1.0)
            return True

        except ImportError:
            # Fallback to osascript on macOS if pynput not available
            if self.system == "Darwin":
                try:
                    # Send F3+B using AppleScript (F3=160, B=11 with control down)
                    subprocess.run(['osascript', '-e',
                        'tell application "System Events" to keystroke "b" using {control down} & key code 160'],
                        timeout=3, capture_output=True)
                    time.sleep(1.0)
                    return True
                except:
                    pass
        except Exception:
            pass
        return False

    def _is_fl_studio_running(self):
        """Check if FL Studio is running"""
        try:
            if self.system == "Windows":
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq FL.exe'],
                                      capture_output=True, text=True)
                return 'FL.exe' in result.stdout
            elif self.system == "Darwin":
                result = subprocess.run(["pgrep", "OsxFL"], capture_output=True)
                return result.returncode == 0
        except:
            pass
        return False


# Global trigger instance
trigger = FLStudioTrigger()

# Request/Response file paths for communication
BRIDGE_DIR = Path(os.path.expanduser("~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts"))
REQUEST_FILE = BRIDGE_DIR / "mcp_request.json"
RESPONSE_FILE = BRIDGE_DIR / "mcp_response.json"

# Path to MIDI controller Hardware directory
HARDWARE_DIR = Path(os.path.expanduser("~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController"))
PIANO_ROLL_CHANNEL_STATE_FILE = HARDWARE_DIR / "piano_roll_state.json"


# =============================================================================
# DISABLED: PianoRollChannelWatcher - Testing if StateManager handles everything
# =============================================================================
# This class watched for piano roll channel/pattern changes and triggered refresh.
# Commented out to test if StateManager's event-based system is sufficient.
#
# class PianoRollChannelWatcher:
#     """
#     Watches for piano roll channel and pattern changes and triggers state refresh.
#
#     When the user opens a different channel's piano roll or changes patterns
#     while LLM interaction mode is active, this triggers Cmd+Opt+Y to refresh the notes state.
#     """
#
#     [entire class implementation removed for testing]
#
# # Global watcher instance (started later)
# channel_watcher = None
# =============================================================================


@mcp.tool
def send_notes(notes: list[dict], mode: str = "add") -> str:
    """
    Send arbitrary notes to the FL Studio piano roll.

    Args:
        notes: List of note dictionaries, each containing:
            - midi: MIDI note number (0-127)
            - duration: Note duration as multiplier of quarter notes (e.g., 1.0=quarter, 2.0=half)
            - time: Start time offset in quarter notes from beginning (default 0)
            - velocity: Note velocity 0.0-1.0 (default 0.8)
        mode: Either "add" to add to existing notes or "replace" to clear first (default "add")

    Example:
        send_notes([
            {"midi": 60, "duration": 1.0, "time": 0},
            {"midi": 64, "duration": 0.5, "time": 1.0},
            {"midi": 67, "duration": 2.0, "time": 1.5}
        ], mode="replace")

    Returns:
        Status of the note creation request
    """
    try:
        manager = _get_state_manager()
        success = manager.send_notes(notes, mode=mode)
        if success:
            midi_notes = [n.get('midi', '?') for n in notes]
            return f"Sent {len(notes)} notes to FL Studio. MIDI notes: {midi_notes}"
        else:
            return "Failed to send notes. Make sure LLM interaction mode is active (run BeginLLMInteraction in FL Studio)."
    except Exception as e:
        return f"Error sending notes: {str(e)}"


@mcp.tool
def delete_notes(notes: list[dict]) -> str:
    """
    Delete specific notes from the FL Studio piano roll.

    Args:
        notes: List of note dictionaries to delete, each containing:
            - midi: MIDI note number (0-127)
            - time: Start time in quarter notes

    Example:
        delete_notes([
            {"midi": 67, "time": 4},
            {"midi": 72, "time": 8}
        ])

    Returns:
        Status of the delete request
    """
    try:
        manager = _get_state_manager()
        success = manager.delete_notes(notes)
        if success:
            midi_notes = [n.get('midi', '?') for n in notes]
            return f"Delete request for {len(notes)} notes sent to FL Studio. MIDI notes: {midi_notes}"
        else:
            return "Failed to delete notes. Make sure LLM interaction mode is active (run BeginLLMInteraction in FL Studio)."
    except Exception as e:
        return f"Error deleting notes: {str(e)}"


@mcp.tool
def clear_piano_roll() -> str:
    """
    Clear all notes from the FL Studio piano roll.

    This creates a clear request that will remove all notes when processed.
    The clear action is executed immediately when FL Studio runs the last script.

    Returns:
        Status of the clear request
    """
    try:
        manager = _get_state_manager()
        success = manager.clear_piano_roll()
        if success:
            return "Clear request sent to FL Studio. All notes will be removed."
        else:
            return "Failed to clear piano roll. Make sure LLM interaction mode is active (run BeginLLMInteraction in FL Studio)."
    except Exception as e:
        return f"Error clearing piano roll: {str(e)}"


@mcp.tool
def get_project_channels() -> str:
    """
    Get all channels in the current FL Studio project.

    Queries FL Studio directly for fresh data.

    Returns:
        JSON string containing array of channels with 'index' and 'name' fields.

    Example:
        get_project_channels()  # Returns: [{"index": 0, "name": "808 Kick"}, ...]
    """
    try:
        manager = _get_state_manager()
        channels = manager.get_channels()
        return json.dumps(channels, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error getting channels: {str(e)}"})


@mcp.tool
def get_project_patterns() -> str:
    """
    Get all patterns in the current FL Studio project.

    Queries FL Studio directly for fresh data (1-based only, skips Pattern 0).

    Returns:
        JSON string containing array of patterns with 'index' and 'name' fields.

    Example:
        get_project_patterns()  # Returns: [{"index": 1, "name": "Drums"}, ...]
    """
    try:
        manager = _get_state_manager()
        patterns = manager.get_patterns()
        return json.dumps(patterns, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error getting patterns: {str(e)}"})


@mcp.tool
def get_current_target() -> str:
    """
    Get the current target channel and pattern from the state manager.

    Returns information about which channel and pattern are currently targeted
    in the piano roll. This is automatically updated when you open different
    piano rolls or change the target channel.

    Returns:
        JSON string containing:
        - channel_index: Current channel index (0-based)
        - channel_name: Current channel name
        - pattern_index: Current pattern index (1-based)
        - pattern_name: Current pattern name
        Or null if no target has been set yet.

    Example:
        get_current_target()  # Returns: {"channel_index": 0, "channel_name": "808 Kick",
                               #           "pattern_index": 1, "pattern_name": "Drums"}
    """
    try:
        manager = _get_state_manager()
        target = manager.get_current_target_channel_and_pattern()
        if target:
            return json.dumps(target, indent=2)
        else:
            return json.dumps({
                "info": "No target set yet. Open a piano roll in FL Studio to trigger target_channel_changed event."
            })
    except Exception as e:
        return json.dumps({"error": f"Error getting current target: {str(e)}"})


@mcp.tool
def get_current_piano_roll_notes() -> str:
    """
    Get the notes for the current piano roll from the state manager.

    Returns all notes in the currently targeted piano roll, including timing,
    duration, velocity, and other properties. The state is automatically
    refreshed when you change channels or patterns.

    Returns:
        JSON string containing:
        - ppq: Pulses per quarter note (timing resolution)
        - noteCount: Number of notes in the piano roll
        - notes: Array of note objects with properties (number, time, length, velocity, etc.)
        Or null if no notes have been loaded yet.

    Example:
        get_current_piano_roll_notes()  # Returns: {"ppq": 96, "noteCount": 5,
                                         #           "notes": [{"number": 60, "time": 0, ...}, ...]}
    """
    try:
        manager = _get_state_manager()
        notes = manager.get_current_piano_roll_notes()
        if notes:
            return json.dumps(notes, indent=2)
        else:
            return json.dumps({
                "info": "No piano roll notes loaded. Ensure target_channel_changed event has been received.",
                "hint": "Open a piano roll in FL Studio to trigger automatic note loading."
            })
    except Exception as e:
        return json.dumps({"error": f"Error getting piano roll notes: {str(e)}"})


@mcp.tool
def reload() -> str:
    """
    Manually trigger a piano roll state refresh.

    This saves current window focus, activates FL Studio, focuses the piano roll,
    sends CMD+OPT+Y (or Ctrl+Alt+Y on Windows) to trigger the piano roll script,
    and then restores focus.

    Use this to manually refresh the piano roll state if automatic updates
    aren't working or if you've made manual edits in FL Studio.

    Returns:
        Status message indicating success or failure.

    Example:
        reload()  # Returns: "Piano roll reload triggered successfully."
    """
    try:
        manager = _get_state_manager()
        success = manager.manual_reload()
        if success:
            return "Piano roll reload triggered successfully. State will refresh momentarily."
        else:
            return "Failed to trigger piano roll reload. Check that FL Studio is running."
    except Exception as e:
        return f"Error triggering piano roll reload: {str(e)}"


def _strip_response(response_str):
    """Strip 'Result: ' prefix from response if present"""
    if isinstance(response_str, str) and response_str.startswith("Result: "):
        return response_str[8:]  # Remove "Result: " prefix
    return response_str


@mcp.tool
def show_piano_roll(channel_id: int) -> str:
    """
    Show the piano roll for a specific channel.

    Intelligently handles window creation:
    - If piano roll is already visible, reuses the existing window (newWindow=0)
    - If piano roll is hidden, creates a new window (newWindow=1)

    Args:
        channel_id: The channel index (0-based)

    Returns:
        Status message indicating success or failure

    Example:
        show_piano_roll(0)  # Show piano roll for channel 0 (Kick)
        show_piano_roll(4)  # Show piano roll for channel 4 (FLEX Bass)
    """
    try:
        from midi_controller.fl_dual_port import send_command

        # Step 1: Select the channel
        send_command(f"channels.selectOneChannel({channel_id})", expect_response=False)

        # Step 2: Get the event ID for this channel
        event_id_str = send_command(f"channels.getRecEventId({channel_id})", expect_response=True)
        if event_id_str is None or event_id_str == "None":
            return f"Error: Could not get event ID for channel {channel_id}. FL Studio may not be ready."
        event_id = int(event_id_str)

        # Step 3: Check if piano roll is already visible
        visible_str = send_command("ui.getVisible(3)", expect_response=True)
        is_visible = visible_str is not None and visible_str != "None" and int(visible_str) == 1

        # Step 4: Open the piano roll with appropriate newWindow flag
        new_window_flag = 0 if is_visible else 1
        send_command(f"ui.openEventEditor({event_id}, 1, {new_window_flag})", expect_response=False)

        # Step 5: Get channel name for confirmation
        channel_name = send_command(f"channels.getChannelName({channel_id})", expect_response=True)
        window_type = "existing window" if is_visible else "new window"

        return f"Piano roll opened for channel {channel_id} ({channel_name}) in {window_type}"

    except TimeoutError:
        return f"Error: No response from FL Studio. Ensure FL Studio is running and MIDI controllers are set up correctly."
    except ValueError as e:
        return f"Error parsing response from FL Studio: {str(e)}"
    except Exception as e:
        return f"Error showing piano roll: {str(e)}"


def _select_pattern_internal(pattern_identifier):
    """
    Internal helper to select a pattern without returning a message.
    Used by both select_pattern tool and get_all_pattern_notes.

    Returns the pattern index on success, None on failure.
    """
    try:
        from midi_controller.fl_dual_port import send_command

        # Save current window focus before making changes
        saved_window = trigger.save_current_window()

        # Try to parse as index first
        pattern_index = None
        try:
            pattern_index = int(pattern_identifier)
        except ValueError:
            # Not a number, so it's a name - look it up
            manager = _get_state_manager()
            patterns = manager.get_patterns()
            for p in patterns:
                if p['name'].lower() == str(pattern_identifier).lower():
                    pattern_index = p['index']
                    break

        if pattern_index is None:
            return None

        # Step 1: Jump to pattern
        send_command(f"patterns.jumpToPattern({pattern_index})", expect_response=False)
        time.sleep(0.001)  # Wait 0.001 seconds after jumpToPattern

        # Step 2: Focus the piano roll window
        send_command("ui.setFocused(3)", expect_response=False)  # widPianoRoll = 3
        time.sleep(0.001)  # Wait 0.001 seconds after focusing piano roll

        # Step 3: Trigger script execution (in the middle)
        manager = _get_state_manager()
        manager._trigger_script_execution()
        time.sleep(0.001)  # Wait 0.001 seconds after trigger

        # Step 4: Focus the playlist window (at the end)
        send_command("ui.setFocused(2)", expect_response=False)  # widPlaylist = 2
        time.sleep(0.001)  # Wait 0.001 seconds after focusing playlist

        # Step 5: Restore focus to original window (terminal)
        if saved_window:
            trigger.restore_focus(saved_window)

        return pattern_index
    except Exception:
        return None


@mcp.tool
def select_pattern(pattern_identifier: str) -> str:
    """
    Select and switch to a pattern by name or index (1-based).

    This uses the reliable sequence: jumpToPattern → trigger script execution.
    Automatically switches to the pattern and refreshes the piano roll view using
    the same trigger mechanism as send_notes.

    Args:
        pattern_identifier: Either a pattern name (e.g., "Chords", "808 Kick") or a 1-based index (e.g., "1", "2")

    Returns:
        Status message confirming pattern selection

    Examples:
        select_pattern("Chords")      # Select by name
        select_pattern("2")            # Select by index (1-based)
        select_pattern("Melody 1")     # Select by name with spaces
    """
    try:
        from midi_controller.fl_dual_port import send_command

        # Use internal helper to perform the selection
        pattern_index = _select_pattern_internal(pattern_identifier)

        if pattern_index is None:
            return f"Error: Pattern '{pattern_identifier}' not found. Use pattern name or 1-based index."

        # Get pattern name for confirmation
        pattern_name = send_command(f"patterns.getPatternName({pattern_index})", expect_response=True)

        return f"Selected pattern {pattern_index} ({pattern_name}). Pattern switched (jumpTo → wait 0.001s → focus piano roll → wait 0.001s → trigger → wait 0.001s → focus playlist → wait 0.001s → restore terminal focus)."

    except Exception as e:
        return f"Error selecting pattern: {str(e)}"


@mcp.tool
def get_all_pattern_notes() -> str:
    """
    Get all notes from all patterns in the current FL Studio project.

    This tool iterates through each pattern, selects it, and collects all notes.
    Returns a comprehensive data structure with all patterns and their note data.

    Returns:
        JSON string containing all patterns with their notes

    Example:
        get_all_pattern_notes()  # Returns: {
                                 #   "patterns": [
                                 #     {"index": 1, "name": "Chords", "noteCount": 16, "notes": [...]},
                                 #     {"index": 2, "name": "Melody 1", "noteCount": 1, "notes": [...]}
                                 #   ],
                                 #   "totalNotes": 22,
                                 #   "totalPatterns": 4
                                 # }
    """
    try:
        manager = _get_state_manager()

        # Get all patterns
        patterns = manager.get_patterns()
        if not patterns:
            return json.dumps({
                "error": "No patterns found in project",
                "patterns": [],
                "totalNotes": 0,
                "totalPatterns": 0
            })

        result_patterns = []
        total_notes = 0

        # Iterate through each pattern
        for pattern in patterns:
            pattern_index = pattern['index']
            pattern_name = pattern['name']

            # Select the pattern using internal helper (this also triggers state refresh)
            _select_pattern_internal(pattern_index)

            # Wait for pattern to fully load before getting notes
            time.sleep(0.2)

            # Get notes for this pattern
            notes_data = manager.get_current_piano_roll_notes()

            if notes_data and 'notes' in notes_data:
                notes = notes_data['notes']
                note_count = len(notes)
                total_notes += note_count

                result_patterns.append({
                    "index": pattern_index,
                    "name": pattern_name,
                    "noteCount": note_count,
                    "ppq": notes_data.get('ppq', 96),
                    "notes": notes
                })
            else:
                # Pattern has no notes
                result_patterns.append({
                    "index": pattern_index,
                    "name": pattern_name,
                    "noteCount": 0,
                    "ppq": 96,
                    "notes": []
                })

        return json.dumps({
            "patterns": result_patterns,
            "totalNotes": total_notes,
            "totalPatterns": len(result_patterns)
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting all pattern notes: {str(e)}"})


@mcp.tool
def get_pattern_notes(pattern_identifier: str, delay: float = 0.1) -> str:
    """
    Get all notes from a specific pattern in the current FL Studio project.

    This tool selects a pattern and collects all notes from it.

    Args:
        pattern_identifier: Either a pattern name (e.g., "Chords", "Melody 1") or a 1-based index (e.g., "1", "2")
        delay: Delay in seconds to wait for pattern to fully load (default 0.1)

    Returns:
        JSON string containing pattern notes data

    Example:
        get_pattern_notes("Chords")      # Get by name
        get_pattern_notes("1")           # Get by index (1-based)
        get_pattern_notes("Melody 1", 0.15)  # With custom delay
    """
    try:
        manager = _get_state_manager()

        # Get all patterns to find the matching one
        patterns = manager.get_patterns()
        if not patterns:
            return json.dumps({
                "error": "No patterns found in project"
            })

        # Find the pattern by name or index
        target_pattern = None

        # Try to match by index first
        try:
            index = int(pattern_identifier)
            target_pattern = next((p for p in patterns if p['index'] == index), None)
        except ValueError:
            # Not a number, try by name
            target_pattern = next((p for p in patterns if p['name'] == pattern_identifier), None)

        if not target_pattern:
            return json.dumps({
                "error": f"Pattern '{pattern_identifier}' not found"
            })

        pattern_index = target_pattern['index']
        pattern_name = target_pattern['name']

        # Select the pattern using internal helper
        _select_pattern_internal(pattern_index)

        # Wait for pattern to fully load before getting notes
        time.sleep(delay)

        # Get notes for this pattern
        notes_data = manager.get_current_piano_roll_notes()

        if notes_data and 'notes' in notes_data:
            notes = notes_data['notes']
            note_count = len(notes)

            return json.dumps({
                "index": pattern_index,
                "name": pattern_name,
                "noteCount": note_count,
                "ppq": notes_data.get('ppq', 96),
                "notes": notes
            }, indent=2)
        else:
            # Pattern has no notes
            return json.dumps({
                "index": pattern_index,
                "name": pattern_name,
                "noteCount": 0,
                "ppq": 96,
                "notes": []
            }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting pattern notes: {str(e)}"})


@mcp.tool
def call_fl_midi_controller_api(method: str, args: list = None, kwargs: dict = None, expect_response: bool = True) -> str:
    """
    Call any FL Studio MIDI controller method directly via SysEx.

    This is a general-purpose tool for calling any method from the FL Studio MIDI Scripting API.
    Refer to midi_controller/docs/midi_scripting.md for available methods and modules.

    Args:
        method: Full method path like "patterns.jumpToPattern" or "mixer.getTrackVolume"
        args: List of positional arguments for the method (int, float, str, bool)
        kwargs: Dict of keyword arguments for the method (optional)
        expect_response: Whether to wait for a response from FL Studio (default True).
                        Set to False for fire-and-forget commands (like setGridBit) for faster bulk operations.

    Returns:
        Result from FL Studio (as string) or error message

    Examples:
        call_fl_midi_controller_api("patterns.patternCount")
        call_fl_midi_controller_api("patterns.getPatternName", [1])
        call_fl_midi_controller_api("mixer.getTrackVolume", [0])
        call_fl_midi_controller_api("channels.getChannelName", [2])
        call_fl_midi_controller_api("channels.setGridBit", [0, 0, 1], expect_response=False)  # Fast bulk operation
        call_fl_midi_controller_api("ui.openEventEditor", [262464, 0], {"newWindow": 1})  # With keyword args
    """
    try:
        from midi_controller.fl_dual_port import send_command

        # Build the command string
        formatted_parts = []

        if args:
            # Convert positional args to proper format (handle different types)
            for arg in args:
                if isinstance(arg, str):
                    formatted_parts.append(f'"{arg}"')
                else:
                    formatted_parts.append(str(arg))

        if kwargs:
            # Format keyword arguments
            for key, value in kwargs.items():
                if isinstance(value, str):
                    formatted_parts.append(f'{key}="{value}"')
                elif isinstance(value, bool):
                    formatted_parts.append(f'{key}={str(value)}')
                else:
                    formatted_parts.append(f'{key}={str(value)}')

        if formatted_parts:
            command = f"{method}({', '.join(formatted_parts)})"
        else:
            command = f"{method}()"

        result = send_command(command, expect_response=expect_response)

        if expect_response:
            return f"Result: {result}"
        else:
            return f"Command sent: {method}"

    except TimeoutError:
        return "Error: No response from FL Studio. Ensure FL Studio is running and MIDI controllers are set up correctly."
    except Exception as e:
        return f"Error calling FL Studio MIDI API: {str(e)}"


if __name__ == "__main__":
    # Start the piano roll channel watcher
    # channel_watcher = PianoRollChannelWatcher(trigger)
    # channel_watcher.start()

    # Run the MCP server
    mcp.run()
