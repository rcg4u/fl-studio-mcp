# name=FLResponse
# receiveFrom=FLRequest
# url=https://forum-image-line.com

"""
FL Studio controller - Target Channel Tracking

Tracks the piano roll's target channel and sends events when it changes.
"""

import device
import json
import os
import channels
import ui

# Event file for communicating with listener
SCRIPT_DIR = os.path.expanduser("~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController")
EVENT_FILE = os.path.join(SCRIPT_DIR, "fl_events.json")

# =============================================================================
# STATE TRACKING
# =============================================================================

# The piano roll's target channel (what channel the PR is showing notes for)
# Starts at index 0, will be updated as we detect changes
_target_channel_index = 0
_target_channel_name = "Unknown"

# The channel rack selection (green LED)
# This is what's selected in the channel rack, may or may not match PR target
_channel_rack_selection_index = None
_channel_rack_selection_name = None

# Track last focused state for OnIdle
_last_was_focused = False


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
    print(f"Initial target channel: {_target_channel_index} - {_target_channel_name}")


def OnSysEx(fl_event):
    """Receive messages from FLRequest and forward to Python (not used in this version)."""
    fl_event.handled = False


def OnDirtyChannel(index, flag):
    """Called when a channel changes in the channel rack."""
    global _channel_rack_selection_index, _channel_rack_selection_name
    global _target_channel_index, _target_channel_name

    # CE_Select (4) = channel selection changed (green LED click, mini piano roll, etc.)
    if flag == 4:
        try:
            channel_name = channels.getChannelName(index)

            # Update channel rack selection (what's selected in the rack)
            _channel_rack_selection_index = index
            _channel_rack_selection_name = channel_name

            print(f"[OnDirtyChannel] Channel rack selection: {index} - {channel_name}")

            # Check if piano roll is focused
            pr_is_focused = (ui.getFocusedFormID() == 3)  # widPianoRoll

            if pr_is_focused:
                # Piano roll IS focused - this is likely the PR dropdown menu changing
                # Update the PR's target channel
                _target_channel_index = index
                _target_channel_name = channel_name
                print(f"[OnDirtyChannel] PR focused - target channel updated: {index} - {channel_name}")

                # Send event with new target channel
                send_event("target_channel_changed", {
                    "target_channel_index": _target_channel_index,
                    "target_channel_name": _target_channel_name
                })
            else:
                # Piano roll is NOT focused - this is just channel rack selection
                # Do NOT update target channel (PR will use its own target when it opens)
                print(f"[OnDirtyChannel] PR not focused - channel rack change only (target unchanged: {_target_channel_index} - {_target_channel_name})")

        except Exception as e:
            print(f"Error in OnDirtyChannel: {e}")


def OnRefresh(flags):
    """Called when FL Studio state changes."""
    global _target_channel_index, _target_channel_name

    # Check if piano roll got focus
    has_focus = flags & 32  # HW_Dirty_FocusedWindow

    if has_focus:
        focused_window = ui.getFocusedFormID()
        if focused_window == 3:  # widPianoRoll
            # PR just got focus - update target channel from channel rack selection
            # This is what channel the PR will show
            channel_index = channels.channelNumber()
            channel_name = channels.getChannelName(channel_index)
            _target_channel_index = channel_index
            _target_channel_name = channel_name
            print(f"[OnRefresh] PR focused - target channel set from channel rack: {channel_index} - {channel_name}")

            # Don't send event here - OnIdle will handle it


def OnIdle():
    """Called periodically - detects piano roll focus transitions."""
    global _last_was_focused

    try:
        focused_window = ui.getFocusedFormID()
        is_focused = (focused_window == 3)  # widPianoRoll

        # Detect transition from not-focused to focused
        if is_focused and not _last_was_focused:
            print(f"[OnIdle] PR focus transition detected")
            print(f"[OnIdle] Current target channel: {_target_channel_index} - {_target_channel_name}")

            # Send event with current target channel
            send_event("target_channel_changed", {
                "target_channel_index": _target_channel_index,
                "target_channel_name": _target_channel_name
            })

        # Update tracking state
        _last_was_focused = is_focused

    except Exception as e:
        print(f"Error in OnIdle: {e}")
