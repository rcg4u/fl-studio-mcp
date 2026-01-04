#!/usr/bin/env python3
"""
Piano Roll State Watcher - Debug Tool
Watches the piano_roll_state.json file and prints changes in real-time.
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime

# Path to the piano roll state file
STATE_FILE = Path.home() / "Documents/Image-Line/FL Studio/Settings/Piano roll scripts/piano_roll_state.json"

def format_note(note, ppq):
    """Format a note for display with human-readable timing."""
    midi_num = note['number']
    time_ticks = note['time']
    length_ticks = note['length']

    # Convert to quarter notes
    time_qn = time_ticks / ppq if ppq > 0 else 0
    length_qn = length_ticks / ppq if ppq > 0 else 0

    # MIDI note name
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_num // 12) - 1
    note_name = note_names[midi_num % 12]

    return (f"  {note_name}{octave} (MIDI {midi_num:3d}) | "
            f"Time: {time_qn:6.2f}qn ({time_ticks:5d}t) | "
            f"Len: {length_qn:6.2f}qn ({length_ticks:5d}t) | "
            f"Vel: {note['velocity']:.2f}")

def print_state(state):
    """Print the piano roll state in a readable format."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"\n{'='*80}")
    print(f"[{timestamp}] Piano Roll State Update")
    print(f"{'='*80}")

    ppq = state.get('ppq', 96)
    note_count = state.get('noteCount', 0)
    notes = state.get('notes', [])

    print(f"PPQ: {ppq} | Note Count: {note_count}")

    if note_count == 0:
        print("  (empty piano roll)")
    else:
        print("\nNotes (sorted by time):")
        # Sort notes by time for easier reading
        sorted_notes = sorted(notes, key=lambda n: n['time'])
        for i, note in enumerate(sorted_notes, 1):
            print(f"{i:2d}. {format_note(note, ppq)}")

    print(f"{'='*80}\n")

def watch_file():
    """Watch the piano roll state file for changes."""
    print(f"Watching: {STATE_FILE}")
    print("Press Ctrl+C to stop\n")

    if not STATE_FILE.exists():
        print(f"WARNING: File does not exist yet: {STATE_FILE}")
        print("Waiting for file to be created...\n")

    last_mtime = 0
    last_content = None

    while True:
        try:
            if STATE_FILE.exists():
                current_mtime = os.path.getmtime(STATE_FILE)

                # Check if file was modified
                if current_mtime != last_mtime:
                    last_mtime = current_mtime

                    # Read and parse the file
                    try:
                        with open(STATE_FILE, 'r') as f:
                            content = f.read()

                        # Only print if content actually changed
                        if content != last_content:
                            last_content = content
                            state = json.loads(content)
                            print_state(state)
                    except json.JSONDecodeError as e:
                        print(f"ERROR: Invalid JSON in state file: {e}")
                    except Exception as e:
                        print(f"ERROR reading file: {e}")

            # Poll every 0.1 seconds
            time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nStopping watcher...")
            break
        except Exception as e:
            print(f"ERROR: {e}")
            time.sleep(1)

if __name__ == "__main__":
    watch_file()
