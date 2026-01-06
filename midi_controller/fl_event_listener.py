#!/usr/bin/env python3
"""
FL Studio Event Listener - Simplified

Watches events from FLResponse controller and prints them.
Essential event processing only - no focus, trigger, or caching code yet.
"""

import json
import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any
from pynput.keyboard import Key, Controller

from focus_management import activate_fl_studio

# File paths
EVENT_FILE = Path.home() / "Documents/Image-Line/FL Studio/Settings/Hardware/FLController/fl_events.json"
PIANO_ROLL_STATE_FILE = Path.home() / "Documents/Image-Line/FL Studio/Settings/Piano roll scripts/piano_roll_state.json"


def trigger_fl_studio_script():
    """Send CMD+OPT+Y keystroke to trigger FL Studio piano roll script."""
    try:
        # First activate FL Studio window
        activate_fl_studio()

        # Small delay to ensure focus is established
        time.sleep(0.1)

        keyboard = Controller()

        # Press CMD and OPT together, then Y
        keyboard.press(Key.cmd)
        keyboard.press(Key.alt)
        time.sleep(0.05)

        keyboard.press('y')
        keyboard.release('y')
        time.sleep(0.05)

        keyboard.release(Key.alt)
        keyboard.release(Key.cmd)

        # Wait for script to execute
        time.sleep(0.5)

        return True
    except Exception as e:
        print(f"  Error triggering script: {e}")
        return False


def duration_to_note_name(duration_qn):
    """Convert duration in quarter notes to note name (1/16, 1/8, 1/4, etc.)."""
    # Map duration in quarter notes to note names
    # Using 16th notes as the smallest unit for display
    duration_map = {
        0.0625: "1/16",   # 16th note (1/16 quarter note)
        0.125: "1/8",     # 8th note
        0.1875: "3/16",   # dotted 16th
        0.25: "1/4",      # quarter note of the sixteenth
        0.375: "3/8",     # dotted 8th
        0.5: "1/2",       # half quarter note (8th)
        0.75: "3/4",      # dotted quarter
        1.0: "1",         # whole (quarter note)
        1.5: "1.5",       # dotted whole
        2.0: "2",         # double whole
        3.0: "3",
        4.0: "4"
    }

    # Find closest match (handle floating point precision)
    for duration, name in sorted(duration_map.items()):
        if abs(duration_qn - duration) < 0.01:
            return name

    # Fallback for unknown durations
    if duration_qn < 0.1:
        return "1/16"
    elif duration_qn < 0.5:
        return "1/8"
    elif duration_qn < 1.0:
        return "1/4"
    else:
        return str(duration_qn)


def display_piano_roll_state():
    """Read and display the current piano roll state."""
    try:
        if not PIANO_ROLL_STATE_FILE.exists():
            print(f"  Piano roll state file not found")
            return

        with open(PIANO_ROLL_STATE_FILE, 'r') as f:
            state = json.load(f)

        ppq = state.get('ppq', 96)
        note_count = state.get('noteCount', 0)
        notes = state.get('notes', [])

        print(f"  Piano Roll: {note_count} notes")

        if notes:
            # Group notes by time (bar)
            notes_by_bar = {}
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

            for note in notes:
                midi_num = note.get('number', 0)
                time_val = note.get('time', 0)
                duration_val = note.get('length', 0)  # duration in ticks

                # Convert to quarter notes and determine bar (4qn per bar)
                time_qn = time_val / ppq
                bar = int(time_qn // 4)

                # Convert MIDI number to note name
                octave = (midi_num // 12) - 1
                note_name = note_names[midi_num % 12]

                # Convert duration from ticks to quarter notes
                duration_qn = duration_val / ppq
                duration_str = duration_to_note_name(duration_qn)

                full_note = f"{note_name}{octave} ({duration_str})"

                if bar not in notes_by_bar:
                    notes_by_bar[bar] = []
                notes_by_bar[bar].append(full_note)

            # Display notes grouped by bar
            for bar in sorted(notes_by_bar.keys()):
                notes_str = ", ".join(notes_by_bar[bar])
                print(f"    Bar {bar + 1}: {notes_str}")
        else:
            print(f"    (empty)")

    except Exception as e:
        print(f"  Error reading piano roll state: {e}")


class SimpleEventPrinter:
    """
    Simple event listener that watches and prints events from FL Studio.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self._running = False
        self._thread: threading.Thread = None
        self._last_file_size = 0

        # Track current state
        self._current_channel = "Unknown"
        self._current_pattern = "Unknown"

    def start(self):
        """Start watching events in a background thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

        if self.verbose:
            print(f"Event Listener started (watching {EVENT_FILE})")

    def stop(self):
        """Stop watching events."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None

        if self.verbose:
            print("Event Listener stopped")

    def is_running(self) -> bool:
        """Check if the listener is running."""
        return self._running

    def get_current_state(self) -> Dict[str, str]:
        """Get the current tracked channel and pattern."""
        return {
            "channel": self._current_channel,
            "pattern": self._current_pattern
        }

    # -------------------------------------------------------------------------
    # Internal - Event Processing
    # -------------------------------------------------------------------------

    def _watch_loop(self):
        """Main watch loop - runs in background thread."""
        while self._running:
            try:
                self._check_for_events()
            except Exception as e:
                if self.verbose:
                    print(f"Error in watch loop: {e}")
            time.sleep(0.1)  # Poll every 100ms

    def _check_for_events(self):
        """Check for new events in the event file."""
        if not EVENT_FILE.exists():
            return

        current_size = os.path.getsize(EVENT_FILE)
        if current_size <= self._last_file_size:
            return

        # Read new events
        try:
            with open(EVENT_FILE, 'r') as f:
                f.seek(self._last_file_size)
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

        self._last_file_size = current_size

        # Truncate file after reading
        try:
            with open(EVENT_FILE, 'w') as f:
                f.truncate()
            self._last_file_size = 0
        except:
            pass

    def _process_event(self, event: Dict[str, Any]):
        """Process a single event - unpack and display it."""
        event_type = event.get('type', 'unknown')
        data = event.get('data', {})

        # Print the event
        print()
        print(f"Event: {event_type}")

        # Handle project_loaded events
        if event_type == "project_loaded":
            channels = data.get('channels', [])
            patterns = data.get('patterns', [])

            print(f"  Channels ({len(channels)}):")
            for ch in channels:
                print(f"    {ch['index']}: {ch['name']}")

            print(f"  Patterns ({len(patterns)}):")
            for pat in patterns:
                print(f"    {pat['index']}: {pat['name']}")

        # Handle target_channel_changed events
        elif event_type == "target_channel_changed":
            target_channel_name = data.get('target_channel_name', 'Unknown')
            target_channel_index = data.get('target_channel_index', -1)
            pattern_name = data.get('pattern_name', 'Unknown')
            pattern_index = data.get('pattern_index', -1)

            # Update current state
            self._current_channel = target_channel_name
            self._current_pattern = pattern_name

            print(f"  Channel: {target_channel_index} - {target_channel_name}")
            print(f"  Pattern: {pattern_index} - {pattern_name}")

            # Trigger FL Studio script
            print(f"  Triggering CMD+OPT+Y...")
            success = trigger_fl_studio_script()
            if success:
                print(f"  ✓ Script triggered")
                # Display the piano roll state after triggering
                display_piano_roll_state()


# -----------------------------------------------------------------------------
# Standalone Mode
# -----------------------------------------------------------------------------

def run_standalone():
    """Run the event listener in standalone mode (for testing)."""
    print("FL Studio Event Listener - Tracking Channel & Pattern")
    print(f"Watching: {EVENT_FILE}")
    print("Press Ctrl+C to stop\n")

    listener = SimpleEventPrinter(verbose=True)

    try:
        listener.start()
        # Keep main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping...")
        listener.stop()


if __name__ == "__main__":
    run_standalone()
