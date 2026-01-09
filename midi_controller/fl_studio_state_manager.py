#!/usr/bin/env python3
"""
FL Studio State Manager - Tracks FL Studio state from events.

This module monitors events from device_FLResponse.py and provides
a simple query API for channels, patterns, and current piano roll notes.

Can run standalone (for debugging) or imported by MCP server.
"""

import json
import os
import readline
import sys
import time
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from focus_management import save_current_window, restore_focus, activate_fl_studio
from fl_dual_port import send_command
from pynput.keyboard import Key, Controller


# =============================================================================
# File Paths
# =============================================================================

EVENT_FILE = Path.home() / "Documents/Image-Line/FL Studio/Settings/Hardware/FLController/fl_events.json"
STATE_FILE = Path.home() / "Documents/Image-Line/FL Studio/Settings/Hardware/FLController/project_state.json"
PIANO_ROLL_STATE_FILE = Path.home() / "Documents/Image-Line/FL Studio/Settings/Piano roll scripts/piano_roll_state.json"
REQUEST_FILE = Path.home() / "Documents/Image-Line/FL Studio/Settings/Piano roll scripts/mcp_request.json"
FLAG_FILE = Path.home() / "Documents/Image-Line/FL Studio/Settings/Piano roll scripts/llm_interaction_active.flag"


# Print lock to prevent output interleaving
_print_lock = threading.Lock()
_reprint_prompt = threading.Event()


def _safe_print(*args, **kwargs):
    """Thread-safe print function that refreshes the prompt after background output."""
    with _print_lock:
        print(*args, **kwargs)
        sys.stdout.flush()
        # Check if we're in standalone mode and should re-print prompt
        if _reprint_prompt.is_set():
            print("> ", end="", flush=True)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PianoRollNotes:
    """Notes from a piano roll."""
    ppq: int
    note_count: int
    notes: List[dict]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "ppq": self.ppq,
            "noteCount": self.note_count,
            "notes": self.notes
        }


# =============================================================================
# Main Class
# =============================================================================

class FLStudioStateManager:
    """
    Tracks FL Studio state from events.

    Monitors fl_events.json for events from device_FLResponse.py,
    maintains current target channel/pattern and notes, and provides
    a query API for the MCP server.
    """

    def __init__(self, event_file: Optional[Path] = None, state_file: Optional[Path] = None):
        """
        Initialize the state manager.

        Args:
            event_file: Path to fl_events.json (default: FLController/fl_events.json)
            state_file: Path to project_state.json (default: FLController/project_state.json)
        """
        self._event_file = event_file or EVENT_FILE
        self._state_file = state_file or STATE_FILE

        # Internal state
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_event_file_size = 0
        self._last_piano_roll_state_mtime = 0  # Track modification time
        self._in_manual_reload = False  # Prevent double reload during manual trigger

        # Tracked state
        self._channels: Dict[int, dict] = {}  # {index: {"index": int, "name": str}}
        self._patterns: Dict[int, dict] = {}  # {index: {"index": int, "name": str}}
        self._current_target: Optional[dict] = None  # {"channel_index": int, "channel_name": str, "pattern_index": int, "pattern_name": str}
        self._current_piano_roll_notes: Optional[PianoRollNotes] = None

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    def start(self) -> None:
        """Start monitoring events in background thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

        # Load existing state if available
        self._load_state_from_file()

    def stop(self) -> None:
        """Stop monitoring events."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None

    def is_running(self) -> bool:
        """Check if monitoring is active."""
        return self._running

    # =========================================================================
    # EVENT PROCESSING (internal)
    # =========================================================================

    def _watch_loop(self) -> None:
        """Main watch loop - runs in background thread."""
        while self._running:
            try:
                self._check_for_events()
                self._check_for_piano_roll_changes()
            except Exception as e:
                print(f"Error in watch loop: {e}")
            time.sleep(0.1)  # Poll every 100ms

    def _check_for_events(self) -> None:
        """Check for new events in the event file."""
        if not self._event_file.exists():
            return

        current_size = os.path.getsize(self._event_file)
        if current_size <= self._last_event_file_size:
            return

        # Read new events
        try:
            with open(self._event_file, 'r') as f:
                f.seek(self._last_event_file_size)
                new_lines = f.read()
        except Exception:
            return

        # Process each event
        for line in new_lines.strip().split('\n'):
            if line:
                try:
                    event = json.loads(line)
                    self._process_event(event)
                except json.JSONDecodeError:
                    pass

        self._last_event_file_size = current_size

        # Truncate file after reading
        try:
            with open(self._event_file, 'w') as f:
                f.truncate()
            self._last_event_file_size = 0
        except:
            pass

    def _check_for_piano_roll_changes(self) -> None:
        """Check if piano_roll_state.json has been modified and reload notes."""
        if not PIANO_ROLL_STATE_FILE.exists():
            return

        try:
            current_mtime = os.path.getmtime(PIANO_ROLL_STATE_FILE)
            if current_mtime != self._last_piano_roll_state_mtime:
                # File has been modified, reload notes
                _safe_print(f"[Reloading piano_roll_state.json]")
                self._last_piano_roll_state_mtime = current_mtime
                self._load_piano_roll_notes()
                self._save_state_to_file()
        except Exception as e:
            _safe_print(f"Error checking piano roll state file: {e}")

    def _process_event(self, event: Dict[str, Any]) -> None:
        """
        Handle incoming event from FL Studio.

        Event types:
        - project_loaded: Store channels/patterns
        - target_channel_changed: Update current target + trigger piano roll refresh
        """
        event_type = event.get('type', 'unknown')
        data = event.get('data', {})

        # Print the event JSON
        _safe_print(json.dumps(event, indent=2))

        if event_type == "project_loaded":
            self._handle_project_loaded(data)

        elif event_type == "target_channel_changed":
            self._handle_target_channel_changed(data)

    def _handle_project_loaded(self, data: Dict[str, Any]) -> None:
        """Handle project_loaded event - store all channels and patterns."""
        channels = data.get('channels', [])
        patterns = data.get('patterns', [])

        # Store channels
        self._channels = {}
        for ch in channels:
            idx = ch['index']
            self._channels[idx] = {"index": idx, "name": ch['name']}

        # Store patterns
        self._patterns = {}
        for pat in patterns:
            idx = pat['index']
            self._patterns[idx] = {"index": idx, "name": pat['name']}

        self._save_state_to_file()

    def _handle_target_channel_changed(self, data: Dict[str, Any]) -> None:
        """
        Handle target_channel_changed event.
        Update current target and trigger piano roll refresh.
        """
        channel_name = data.get('target_channel_name', 'Unknown')
        channel_idx = data.get('target_channel_index', -1)
        pattern_name = data.get('pattern_name', 'Unknown')
        pattern_idx = data.get('pattern_index', -1)

        # Update current target
        self._current_target = {
            "channel_index": channel_idx,
            "channel_name": channel_name,
            "pattern_index": pattern_idx,
            "pattern_name": pattern_name
        }

        # Skip triggering if we're in the middle of a manual reload
        # (prevents double reload when manual reload triggers the same event)
        if self._in_manual_reload:
            return

        # Trigger CMD+OPT+Y to refresh piano roll state
        self._trigger_script()

        # After trigger, load the updated notes
        time.sleep(0.5)
        self._load_piano_roll_notes()

        self._save_state_to_file()

    def _trigger_script(self) -> None:
        """Send CMD+OPT+Y keystroke to FL Studio to trigger piano roll script."""
        try:
            activate_fl_studio()
            time.sleep(0.1)

            keyboard = Controller()
            keyboard.press(Key.cmd)
            keyboard.press(Key.alt)
            time.sleep(0.05)
            keyboard.press('y')
            keyboard.release('y')
            time.sleep(0.05)
            keyboard.release(Key.alt)
            keyboard.release(Key.cmd)

            time.sleep(0.5)
        except Exception as e:
            _safe_print(f"Error triggering script: {e}")

    def manual_reload(self) -> bool:
        """
        Manually trigger a piano roll reload.

        Saves current focus, activates FL Studio, focuses piano roll,
        sends CMD+OPT+Y to trigger script, then restores focus.

        Returns:
            True if successful, False otherwise.
        """
        self._in_manual_reload = True  # Prevent event handler from triggering

        try:
            # Save current window focus
            saved_window = save_current_window()
            if saved_window:
                _safe_print(f"Saved focus: {saved_window}")

            # Activate FL Studio
            if not activate_fl_studio():
                _safe_print("Failed to activate FL Studio")
                return False

            # time.sleep(0.05)  # was 0.1, now removed

            # Focus the piano roll window (optional - may fail but not critical)
            try:
                send_command("ui.setFocused(3)", expect_response=False)  # widPianoRoll = 3
                # time.sleep(0.05)  # was 0.15, now removed
            except Exception:
                pass  # Ignore if piano roll focus fails - keystroke will still work

            # Send CMD+OPT+Y keystroke
            keyboard = Controller()
            keyboard.press(Key.cmd)
            keyboard.press(Key.alt)
            keyboard.press('y')
            keyboard.release('y')
            keyboard.release(Key.alt)
            keyboard.release(Key.cmd)

            # Wait for script to execute
            time.sleep(0.2)  # was 0.5, then 0.3, now 0.2

            # Restore focus
            if saved_window:
                restore_focus(saved_window)
                _safe_print(f"Restored focus: {saved_window}")

            return True

        except Exception as e:
            _safe_print(f"Error during manual reload: {e}")
            return False

        finally:
            # Clear the flag so events work normally again
            self._in_manual_reload = False

    def _load_piano_roll_notes(self) -> None:
        """Load notes from piano_roll_state.json."""
        try:
            if not PIANO_ROLL_STATE_FILE.exists():
                self._current_piano_roll_notes = None
                return

            with open(PIANO_ROLL_STATE_FILE, 'r') as f:
                state = json.load(f)

            note_count = state.get('noteCount', 0)
            self._current_piano_roll_notes = PianoRollNotes(
                ppq=state.get('ppq', 96),
                note_count=note_count,
                notes=state.get('notes', [])
            )

        except Exception as e:
            _safe_print(f"Error loading piano roll notes: {e}")
            self._current_piano_roll_notes = None

    def _load_state_from_file(self) -> None:
        """Load state from project_state.json (if exists)."""
        try:
            if not self._state_file.exists():
                return

            with open(self._state_file, 'r') as f:
                state = json.load(f)

            # Load channels
            for ch in state.get('channels', []):
                self._channels[ch['index']] = ch

            # Load patterns
            for pat in state.get('patterns', []):
                self._patterns[pat['index']] = pat

            # Load current target
            self._current_target = state.get('current_target')

            # Load current notes (if we saved them)
            notes_data = state.get('current_piano_roll_notes')
            if notes_data:
                self._current_piano_roll_notes = PianoRollNotes(
                    ppq=notes_data.get('ppq', 96),
                    note_count=notes_data.get('noteCount', 0),
                    notes=notes_data.get('notes', [])
                )

        except Exception as e:
            print(f"Error loading state from file: {e}")

    def _save_state_to_file(self) -> None:
        """Save current state to project_state.json."""
        try:
            state = {
                "channels": list(self._channels.values()),
                "patterns": list(self._patterns.values()),
                "current_target": self._current_target,
                "current_piano_roll_notes": self._current_piano_roll_notes.to_dict() if self._current_piano_roll_notes else None
            }

            with open(self._state_file, 'w') as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            print(f"Error saving state to file: {e}")

    # =========================================================================
    # QUERY API (for MCP server)
    # =========================================================================

    def get_channels(self) -> List[dict]:
        """
        Get all channels (queries FL Studio directly for fresh data).

        Returns:
            List of channel dicts: [{'index': 0, 'name': '808 Kick'}, ...]
        """
        try:
            # Get channel count
            count_str = send_command("channels.channelCount()", expect_response=True)
            if count_str is None:
                _safe_print("Error: No response from FL Studio")
                _safe_print("Make sure FL Studio is running and device scripts are loaded")
                return []

            if count_str.startswith("Result: "):
                count_str = count_str[8:]  # Strip "Result: " prefix
            channel_count = int(count_str) if count_str else 0

            # Get each channel name
            channels = []
            for i in range(channel_count):
                name = send_command(f"channels.getChannelName({i})", expect_response=True)
                if name and name.startswith("Result: "):
                    name = name[8:]  # Strip "Result: " prefix
                channels.append({"index": i, "name": name})

            return channels
        except ValueError as e:
            _safe_print(f"Error parsing channel count: {e}")
            return []
        except Exception as e:
            _safe_print(f"Error getting channels: {e}")
            return []

    def get_patterns(self) -> List[dict]:
        """
        Get all patterns (queries FL Studio directly for fresh data, 1-based only).

        Returns:
            List of pattern dicts: [{'index': 1, 'name': 'Drums'}, ...]
        """
        try:
            # Get pattern count
            count_str = send_command("patterns.patternCount()", expect_response=True)
            if count_str is None:
                _safe_print("Error: No response from FL Studio")
                _safe_print("Make sure FL Studio is running and device scripts are loaded")
                return []

            if count_str.startswith("Result: "):
                count_str = count_str[8:]  # Strip "Result: " prefix
            pattern_count = int(count_str) if count_str else 0

            # Get each pattern name (patterns are 1-based in FL Studio)
            patterns = []
            for i in range(1, pattern_count + 1):  # Start from 1, go to pattern_count
                name = send_command(f"patterns.getPatternName({i})", expect_response=True)
                if name and name.startswith("Result: "):
                    name = name[8:]  # Strip "Result: " prefix
                patterns.append({"index": i, "name": name})

            return patterns
        except ValueError as e:
            _safe_print(f"Error parsing pattern count: {e}")
            return []
        except Exception as e:
            _safe_print(f"Error getting patterns: {e}")
            return []

    def get_current_target_channel_and_pattern(self) -> Optional[dict]:
        """
        Get the current target channel and pattern from events.

        Returns:
            Dict with 'channel_index', 'channel_name', 'pattern_index', 'pattern_name'
            or None if no target has been set.
        """
        return self._current_target

    def get_current_piano_roll_notes(self) -> Optional[dict]:
        """
        Get the notes for the current piano roll.

        Returns:
            Dict with 'ppq', 'noteCount', 'notes' or None if no notes loaded.
        """
        if self._current_piano_roll_notes:
            return self._current_piano_roll_notes.to_dict()
        return None

    # =========================================================================
    # PIANO ROLL OPERATIONS
    # =========================================================================

    def _queue_request(self, request: dict) -> bool:
        """
        Queue a request to mcp_request.json.

        Args:
            request: Request dictionary to queue

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read existing requests or create new list
            requests = []
            if REQUEST_FILE.exists():
                try:
                    with open(REQUEST_FILE, 'r') as f:
                        content = json.load(f)
                        if isinstance(content, list):
                            requests = content
                except:
                    pass

            # Append the request
            requests.append(request)

            # Write updated list
            with open(REQUEST_FILE, 'w') as f:
                json.dump(requests, f, indent=2)

            return True
        except Exception as e:
            _safe_print(f"Error queueing request: {e}")
            return False

    def _trigger_script_execution(self) -> bool:
        """
        Trigger FL Studio to execute the queued requests.

        Sends CMD+OPT+Y keystroke to FL Studio and restores focus.

        Returns:
            True if successful, False otherwise
        """
        saved_window = None
        try:
            # Save current window focus
            saved_window = save_current_window()

            # Activate FL Studio and send keystroke
            activate_fl_studio()
            time.sleep(0.1)

            keyboard = Controller()
            keyboard.press(Key.cmd)
            keyboard.press(Key.alt)
            time.sleep(0.05)
            keyboard.press('y')
            keyboard.release('y')
            time.sleep(0.05)
            keyboard.release(Key.alt)
            keyboard.release(Key.cmd)

            time.sleep(0.5)

            # Restore focus to saved window
            if saved_window:
                restore_focus(saved_window)

            return True
        except Exception as e:
            _safe_print(f"Error triggering script: {e}")
            # Try to restore focus even if there was an error
            if saved_window:
                try:
                    restore_focus(saved_window)
                except:
                    pass
            return False

    def send_notes(self, notes: List[dict], mode: str = "add") -> bool:
        """
        Send notes to the FL Studio piano roll.

        Args:
            notes: List of note dictionaries, each containing:
                - midi: MIDI note number (0-127)
                - duration: Note duration in quarter notes
                - time: Start time in quarter notes
                - velocity: Note velocity 0.0-1.0 (default 0.8)
            mode: "add" to add to existing notes, "replace" to clear first (default "add")

        Returns:
            True if successful, False otherwise
        """
        if not notes:
            _safe_print("Error: notes list cannot be empty")
            return False

        # Validate and prepare notes
        prepared_notes = []
        for i, note in enumerate(notes):
            if "midi" not in note:
                _safe_print(f"Error: note {i} missing required 'midi' field")
                return False
            if "duration" not in note:
                _safe_print(f"Error: note {i} missing required 'duration' field")
                return False

            prepared_note = {
                "midi": note["midi"],
                "duration": note["duration"],
                "time": note.get("time", 0),
                "velocity": note.get("velocity", 0.8)
            }
            prepared_notes.append(prepared_note)

        # Create request
        request = {
            "action": "add_notes",
            "notes": prepared_notes,
            "mode": mode
        }

        # If mode is replace, clear the list first and add a clear action
        if mode == "replace":
            clear_request = {"action": "clear"}
            if not self._queue_request(clear_request):
                return False

        # Queue the notes request
        if not self._queue_request(request):
            return False

        # Trigger FL Studio to execute
        return self._trigger_script_execution()

    def delete_notes(self, notes: List[dict]) -> bool:
        """
        Delete specific notes from the FL Studio piano roll.

        Args:
            notes: List of note dictionaries to delete, each containing:
                - midi: MIDI note number (0-127)
                - time: Start time in quarter notes

        Returns:
            True if successful, False otherwise
        """
        if not notes:
            _safe_print("Error: notes list cannot be empty")
            return False

        # Validate notes
        for i, note in enumerate(notes):
            if "midi" not in note:
                _safe_print(f"Error: note {i} missing required 'midi' field")
                return False
            if "time" not in note:
                _safe_print(f"Error: note {i} missing required 'time' field")
                return False

        # Create request
        request = {
            "action": "delete_notes",
            "notes": notes
        }

        # Queue the delete request
        if not self._queue_request(request):
            return False

        # Trigger FL Studio to execute
        return self._trigger_script_execution()

    def clear_piano_roll(self) -> bool:
        """
        Clear all notes from the FL Studio piano roll.

        Returns:
            True if successful, False otherwise
        """
        # Create clear request
        request = {"action": "clear"}

        # Queue the clear request
        if not self._queue_request(request):
            return False

        # Trigger FL Studio to execute
        return self._trigger_script_execution()


# =============================================================================
# Global Singleton (for MCP server use)
# =============================================================================

_global_manager: Optional[FLStudioStateManager] = None


def get_state_manager() -> FLStudioStateManager:
    """Get the global FLStudioStateManager singleton instance."""
    global _global_manager
    if _global_manager is None:
        _global_manager = FLStudioStateManager()
    return _global_manager


# =============================================================================
# Standalone Test Harness
# =============================================================================

def run_standalone():
    """Run the state manager in standalone mode for testing."""
    print("FL Studio State Manager - Standalone Mode")
    print(f"Event file: {EVENT_FILE}")
    print(f"State file: {STATE_FILE}")
    print("\nCommands:")
    print("  channels    - List all channels")
    print("  patterns    - List all patterns")
    print("  target      - Show current target channel and pattern")
    print("  notes       - Show current piano roll notes")
    print("  reload      - Manually trigger piano roll reload (CMD+OPT+Y)")
    print("  summary     - Show summary of all state")
    print("  send        - Send notes to piano roll (C major chord example)")
    print("  delete      - Delete specific note from piano roll")
    print("  clear       - Clear all notes from piano roll")
    print("  quit        - Exit")

    manager = FLStudioStateManager()
    manager.start()

    print("\nWaiting for events from FL Studio...")

    # Enable prompt reprinting for standalone mode
    _reprint_prompt.set()

    try:
        while True:
            cmd = input("\n> ").strip().lower()
            if not cmd:
                continue

            if cmd in ('quit', 'q', 'exit'):
                print("Stopping...")
                _reprint_prompt.clear()  # Disable prompt reprinting before final prints
                manager.stop()
                print("Goodbye!")
                break

            elif cmd == 'channels':
                channels = manager.get_channels()
                print(f"\nChannels ({len(channels)}):")
                for ch in channels:
                    print(f"  {ch['index']}: {ch['name']}")

            elif cmd == 'patterns':
                patterns = manager.get_patterns()
                print(f"\nPatterns ({len(patterns)}):")
                for pat in patterns:
                    print(f"  {pat['index']}: {pat['name']}")

            elif cmd == 'target':
                target = manager.get_current_target_channel_and_pattern()
                if target:
                    print(f"\nCurrent Target:")
                    print(f"  Channel: {target['channel_index']} - {target['channel_name']}")
                    print(f"  Pattern: {target['pattern_index']} - {target['pattern_name']}")
                else:
                    print("\nNo target set yet.")
                    print("Open a piano roll in FL Studio to trigger target_channel_changed event.")

            elif cmd == 'notes':
                notes = manager.get_current_piano_roll_notes()
                if notes:
                    print(f"\nCurrent Piano Roll Notes:")
                    print(f"  PPQ: {notes['ppq']}")
                    print(f"  Note Count: {notes['noteCount']}")
                    if notes['notes']:
                        print(f"  Notes:")
                        for note in notes['notes']:
                            print(f"    MIDI {note.get('number')}, Time: {note.get('time')}, "
                                  f"Length: {note.get('length')}, Velocity: {note.get('velocity')}")
                else:
                    print("\nNo piano roll notes loaded.")
                    print("Make sure target_channel_changed event has been received.")

            elif cmd == 'reload':
                print("\nTriggering manual reload...")
                success = manager.manual_reload()
                if success:
                    print("Reload complete!")
                else:
                    print("Reload failed.")

            elif cmd == 'send':
                print("\nSending C major chord (C4, E4, G4) to piano roll...")
                success = manager.send_notes([
                    {"midi": 60, "duration": 2, "time": 0, "velocity": 0.8},
                    {"midi": 64, "duration": 2, "time": 0, "velocity": 0.8},
                    {"midi": 67, "duration": 2, "time": 0, "velocity": 0.8}
                ], mode="add")
                if success:
                    print("Notes sent successfully!")
                else:
                    print("Failed to send notes.")

            elif cmd == 'delete':
                print("\nDeleting middle note (E4 / MIDI 64) from piano roll...")
                success = manager.delete_notes([
                    {"midi": 64, "time": 0}
                ])
                if success:
                    print("Note deleted successfully!")
                else:
                    print("Failed to delete note.")

            elif cmd == 'clear':
                print("\nClearing all notes from piano roll...")
                success = manager.clear_piano_roll()
                if success:
                    print("Piano roll cleared!")
                else:
                    print("Failed to clear piano roll.")

            elif cmd == 'summary':
                channels = manager.get_channels()
                patterns = manager.get_patterns()
                target = manager.get_current_target_channel_and_pattern()
                notes = manager.get_current_piano_roll_notes()

                print(f"\nState Summary:")
                print(f"  Channels: {len(channels)}")
                print(f"  Patterns: {len(patterns)}")
                if target:
                    print(f"  Current Target: Ch{target['channel_index']} ({target['channel_name']}) / "
                          f"Pat{target['pattern_index']} ({target['pattern_name']})")
                else:
                    print(f"  Current Target: None")
                if notes:
                    print(f"  Notes Loaded: {notes['noteCount']} notes (PPQ: {notes['ppq']})")
                else:
                    print(f"  Notes Loaded: None")

            else:
                print("Unknown command.")
                print("Try: channels, patterns, target, notes, reload, send, delete, clear, summary, quit")

    except KeyboardInterrupt:
        _reprint_prompt.clear()  # Disable prompt reprinting before final prints
        print("\n\nStopping...")
        manager.stop()
        print("Goodbye!")


if __name__ == "__main__":
    run_standalone()
