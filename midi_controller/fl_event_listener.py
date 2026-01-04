#!/usr/bin/env python3
"""
Test listener for FL Studio events via file monitoring.

This script watches the event file and displays events
sent by the MIDI controller in real-time (like tail -f).
"""

import json
import os
import sys
import time
from pathlib import Path

# Add midi_controller to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Try to import pynput for keyboard control
try:
    from pynput.keyboard import Controller as KeyboardController, Key
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False
    print("Warning: pynput not installed - keystroke sending disabled")

EVENT_FILE = Path.home() / "Documents/Image-Line/FL Studio/Settings/Hardware/FLController/fl_events.json"
PIANO_ROLL_STATE_FILE = Path.home() / "Documents/Image-Line/FL Studio/Settings/Piano roll scripts/piano_roll_state.json"


def get_current_channel():
    """Query FL Studio for the current piano roll channel using MIDI controller"""
    try:
        from fl_dual_port import send_command

        # Get current channel number
        result = send_command("channels.channelNumber()")
        if result and result.isdigit():
            channel_num = int(result)

            # Get channel name
            channel_name = send_command(f"channels.getChannelName({channel_num})")

            return channel_num, channel_name
    except Exception as e:
        print(f"  Error querying channel: {e}")

    return None, None


def send_cmd_opt_y():
    """Send Cmd+Opt+Y keystroke combination"""
    if not HAS_KEYBOARD:
        return False

    try:
        keyboard = KeyboardController()

        # Press Cmd+Opt
        keyboard.press(Key.cmd)
        keyboard.press(Key.alt)
        time.sleep(0.05)

        # Press and release Y
        keyboard.press('y')
        keyboard.release('y')
        time.sleep(0.05)

        # Release Cmd+Opt
        keyboard.release(Key.alt)
        keyboard.release(Key.cmd)

        return True
    except Exception as e:
        print(f"  Keystroke error: {e}")
        return False


def get_note_name(midi_note):
    """Convert MIDI note number to note name"""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note // 12) - 1
    note = notes[midi_note % 12]
    return f"{note}{octave}"


def display_piano_roll_contents():
    """Read and display current piano roll contents"""
    try:
        if not PIANO_ROLL_STATE_FILE.exists():
            print("  No piano roll state file found")
            return

        with open(PIANO_ROLL_STATE_FILE, 'r') as f:
            state = json.load(f)

        notes = state.get('notes', [])
        ppq = state.get('ppq', 96)

        if not notes:
            print("  Piano roll is empty")
            return

        print(f"  Notes ({len(notes)}):")

        # Sort notes by time, then pitch
        sorted_notes = sorted(notes, key=lambda n: (n.get('time', 0), n.get('number', 0)))

        for note in sorted_notes[:10]:  # Show first 10 notes
            midi_note = note.get('number', 0)
            note_name = get_note_name(midi_note)
            position = note.get('time', 0)
            length = note.get('length', 0)

            # Convert to quarter notes for display
            pos_qn = position / float(ppq) if ppq > 0 else 0
            len_qn = length / float(ppq) if ppq > 0 else 0

            print(f"    {note_name:>5s} pos:{pos_qn:5.2f} len:{len_qn:4.2f}")

        if len(notes) > 10:
            print(f"    ... and {len(notes) - 10} more")

    except Exception as e:
        print(f"  Error reading piano roll: {e}")


def listen_to_events():
    """Listen for events from MIDI controller (tail -f style)"""
    print(f"Watching: {EVENT_FILE}")
    print("Press Ctrl+C to stop\n")

    # Track last position in file
    last_size = 0

    try:
        while True:
            if EVENT_FILE.exists():
                current_size = os.path.getsize(EVENT_FILE)

                # Check if file has grown
                if current_size > last_size:
                    with open(EVENT_FILE, 'r') as f:
                        f.seek(last_size)
                        new_lines = f.read()

                    # Process new lines
                    for line in new_lines.strip().split('\n'):
                        if line:
                            try:
                                event = json.loads(line)
                                display_event(event)
                            except json.JSONDecodeError as e:
                                print(f"Error parsing JSON: {e}")
                            except Exception as e:
                                print(f"Error processing event: {e}")

                    last_size = current_size

                    # Truncate file after reading (clear processed events)
                    try:
                        with open(EVENT_FILE, 'w') as f:
                            f.truncate()
                        last_size = 0
                    except:
                        pass  # Ignore truncate errors

            time.sleep(0.1)  # Check 10 times per second

    except KeyboardInterrupt:
        print("\nStopped")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def display_event(event):
    """Display event in a nice format"""
    event_type = event.get("type", "unknown")
    data = event.get("data", {})

    # Map event types to titles
    titles = {
        "piano_roll_focus": "Piano Roll Focused",
        "piano_roll_channel_changed": "Piano Roll Channel Changed",
        "pattern_changed": "Pattern Changed",
        "channel_selected": "Channel (Channel Rack)",
        "target_channel_changed": "Channel (Piano Roll)",
    }

    title = titles.get(event_type, event_type)

    print(f"\n[{title}]")

    if "pattern" in data:
        pat = data["pattern"]
        pat_name = data.get("pattern_name", "Unknown")
        print(f"  Pattern: {pat} - {pat_name}")

    if "channel" in data:
        ch = data["channel"]
        ch_name = data.get("channel_name", "Unknown")
        print(f"  Channel: {ch} - {ch_name}")

    # Trigger script and show contents for piano roll events
    if event_type == "piano_roll_focus":
        # Check if we should skip trigger (channel selector was clicked, not mini piano roll)
        skip_trigger = data.get("skip_trigger", False)
        if skip_trigger:
            print("  (Skipping trigger - channel selector clicked)")
        elif send_cmd_opt_y():
            print("  Triggered script...")
            time.sleep(0.3)  # Wait for script to export state
            display_piano_roll_contents()
    elif event_type == "target_channel_changed":
        # Target channel changed via piano roll menu - trigger script
        if send_cmd_opt_y():
            print("  Triggered script...")
            time.sleep(0.3)
            display_piano_roll_contents()
    elif event_type == "channel_selected":
        # Channel rack selection - just log it (piano_roll_focus will handle trigger)
        print("  (Channel selected - waiting for piano_roll_focus event)")
    elif event_type == "piano_roll_channel_changed":
        # Legacy event - trigger script
        if send_cmd_opt_y():
            print("  Triggered script...")
            time.sleep(0.3)  # Wait for script to export state
            display_piano_roll_contents()
    elif event_type == "pattern_changed":
        # Query current channel directly (no trigger - piano roll not focused)
        ch_num, ch_name = get_current_channel()
        if ch_num is not None:
            print(f"  Current channel: {ch_num} - {ch_name}")
        else:
            print("  Could not get current channel")
    elif event_type == "browser_node_changed":
        # Browser piano roll entry clicked
        is_piano_roll = data.get("is_piano_roll", False)
        caption = data.get("caption", "")

        if is_piano_roll:
            print(f"  Browser piano roll entry: {caption}")
            print("  Focusing piano roll and triggering script...")
            try:
                from fl_dual_port import send_command

                # Show and focus the piano roll (it opens but doesn't auto-focus)
                send_command("ui.showWindow(3)", expect_response=False)
                send_command("ui.setFocused(3)", expect_response=False)

                # Small delay to let piano roll focus
                time.sleep(0.1)

                # Trigger the script
                if send_cmd_opt_y():
                    print("  Triggered script...")
                    time.sleep(0.3)
                    display_piano_roll_contents()
                else:
                    print("  Failed to send keystroke")
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"  Browser navigation: {caption}")


if __name__ == "__main__":
    listen_to_events()
