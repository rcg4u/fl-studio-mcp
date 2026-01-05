# name=FLResponse
# receiveFrom=FLRequest
# url=https://forum-image-line.com

"""
FL Studio controller - Simplified Events System

Sends events when piano roll gets focus, including target channel and pattern info.
"""

import device
import json
import os
import patterns
import channels
import ui

# Event file for communicating with listener
SCRIPT_DIR = os.path.expanduser("~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController")
EVENT_FILE = os.path.join(SCRIPT_DIR, "fl_events.json")

# =============================================================================
# STATE TRACKING
# =============================================================================

# Track currently selected channel in channel rack (green LED)
# This becomes the target channel when piano roll opens
_selected_channel_index = None
_selected_channel_name = None

# Track current pattern
_current_pattern_index = None
_current_pattern_name = None

# Track last sent state to avoid duplicates
_last_sent_pattern = None
_last_sent_channel = None

# Track last focused state for OnIdle
_last_was_focused = False

# Track pending rerun request from OnDirtyChannel
_pending_rerun = False


def send_event(event_type, data):
    """Send event to listener via event file (JSONL format)."""
    try:
        event = {"type": event_type, "data": data}
        with open(EVENT_FILE, 'a') as f:
            f.write(json.dumps(event) + "\n")
        # Print the complete event
        print("=" * 50)
        print("Event sent: " + event_type)
        print(json.dumps(event, indent=2))
        print("=" * 50)
    except Exception as e:
        print("Event failed: " + event_type + " - " + str(e))


def OnInit():
    print('FL Response initialized')
    print('Sending responses on: ' + device.getName())


def OnProjectLoad(index):
    """Called when a project is loaded."""
    # Only initialize on successful load (PL_LoadOk = 100)
    if index != 100:
        return

    global _selected_channel_index, _selected_channel_name
    global _current_pattern_index, _current_pattern_name

    try:
        print("=" * 50)
        print("OnProjectLoad: Initializing state...")

        # Get the currently selected channel from channel rack
        channel_index = channels.channelNumber()
        channel_name = channels.getChannelName(channel_index)
        _selected_channel_index = channel_index
        _selected_channel_name = channel_name
        print(f"  Selected channel set: {channel_index} - {channel_name}")

        # Get the current pattern
        pattern_index = patterns.patternNumber()
        pattern_name = patterns.getPatternName(pattern_index)
        _current_pattern_index = pattern_index
        _current_pattern_name = pattern_name
        print(f"  Current pattern set: {pattern_index} - {pattern_name}")

        print(f"Project loaded successfully")
        print("=" * 50)
    except Exception as e:
        print(f"Error in OnProjectLoad: {e}")


def OnSysEx(fl_event):
    """Receive messages from FLRequest and forward to Python (not used in this version)."""
    fl_event.handled = False


def OnRefresh(flags):
    """Called when FL Studio state changes."""
    global _current_pattern_index, _current_pattern_name
    global _last_sent_pattern, _last_sent_channel, _pending_rerun

    has_patterns = flags & 1024  # HW_Dirty_Patterns
    has_focus = flags & 32       # HW_Dirty_FocusedWindow

    # Update pattern if it changed
    if has_patterns:
        pattern_index = patterns.patternNumber()
        pattern_name = patterns.getPatternName(pattern_index)
        _current_pattern_index = pattern_index
        _current_pattern_name = pattern_name

    # Get current channel
    target_channel_index = _selected_channel_index if _selected_channel_index is not None else -1
    target_channel_name = _selected_channel_name if _selected_channel_name is not None else "Unknown"

    # Check if state changed before sending
    state_changed = (
        _current_pattern_index != _last_sent_pattern or
        target_channel_index != _last_sent_channel
    )

    if not state_changed:
        return  # Skip if nothing changed

    # Send event based on which flag is present
    if has_patterns:
        # Pattern changed - send if piano roll is visible
        if ui.getVisible(3):  # Piano roll visible
            try:
                send_event("piano_roll_state", {
                    "target_channel_index": target_channel_index,
                    "target_channel_name": target_channel_name,
                    "pattern_index": _current_pattern_index,
                    "pattern_name": _current_pattern_name
                })
                # Update last sent
                _last_sent_pattern = _current_pattern_index
                _last_sent_channel = target_channel_index
            except Exception as e:
                print("Error sending pattern change event: " + str(e))

    elif has_focus:
        # Piano roll focus changed - send if piano roll is focused
        focused_window = ui.getFocusedFormID()
        if focused_window == 3:  # widPianoRoll
            try:
                send_event("piano_roll_state", {
                    "target_channel_index": target_channel_index,
                    "target_channel_name": target_channel_name,
                    "pattern_index": _current_pattern_index if _current_pattern_index is not None else 0,
                    "pattern_name": _current_pattern_name if _current_pattern_name is not None else "Unknown"
                })
                # Update last sent
                _last_sent_pattern = _current_pattern_index
                _last_sent_channel = target_channel_index
            except Exception as e:
                print("Error in OnRefresh: " + str(e))

    # Send pending rerun after state, but only if piano roll is focused
    if _pending_rerun and ui.getFocusedFormID() == 3:  # widPianoRoll
        send_event("rerun_piano_script", {})
        _pending_rerun = False


def OnDirtyChannel(index, flag):
    """Called when a channel changes in the channel rack."""
    global _selected_channel_index, _selected_channel_name, _pending_rerun

    # CE_Select (4) = channel selection changed (green LED click, mini piano roll, etc.)
    if flag == 4:
        try:
            channel_name = channels.getChannelName(index)
            # Update selected channel - this will be used when piano roll opens
            _selected_channel_index = index
            _selected_channel_name = channel_name
            # Print the channel change
            print("=" * 50)
            print(f"Channel selected: {index} - {channel_name}")
            print("=" * 50)

            # If piano roll is focused, set pending rerun flag (will be sent after state)
            if ui.getFocusedFormID() == 3:  # widPianoRoll
                _pending_rerun = True

        except Exception as e:
            print("Error in OnDirtyChannel: " + str(e))


def OnIdle():
    """Called periodically - checks for piano roll focus transitions."""
    global _last_was_focused

    try:
        focused_window = ui.getFocusedFormID()
        is_focused = (focused_window == 3)  # widPianoRoll

        # Detect transition from not-focused to focused
        if is_focused and not _last_was_focused:
            send_event("rerun_piano_script", {})

        # Update tracking state
        _last_was_focused = is_focused

    except Exception as e:
        print(f"Error in OnIdle: {e}")
