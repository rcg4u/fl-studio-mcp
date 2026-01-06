# name=FLResponse
# receiveFrom=FLRequest
# url=https://forum-image-line.com

"""
FL Studio controller - Target Channel Tracking

Tracks the piano roll's target channel and current pattern, sending events
when they change. Uses OnSendTempMsg to reliably detect target channel menu
interactions.
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

# The piano roll's target channel (what channel the PR is showing notes for)
# Starts at index 0, will be updated as we detect changes
_target_channel_index = 0
_target_channel_name = "Unknown"

# Current pattern tracking
_current_pattern_index = 0
_current_pattern_name = "Unknown"

# The channel rack selection (green LED)
# This is what's selected in the channel rack, may or may not match PR target
_channel_rack_selection_index = None
_channel_rack_selection_name = None

# Track last focused state for OnIdle
_last_was_focused = False

# Track menu interaction state
_target_channel_menu_in_progress = False
_target_channel_menu_choice = None



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


def find_channel_index_by_name(name):
    """Find channel index by name. Returns -1 if not found."""
    try:
        for i in range(channels.channelCount()):
            if channels.getChannelName(i) == name:
                return i
        return -1
    except Exception as e:
        print(f"Error finding channel index for '{name}': {e}")
        return -1


def update_pattern():
    """Update current pattern tracking."""
    global _current_pattern_index, _current_pattern_name
    try:
        _current_pattern_index = patterns.patternNumber()
        _current_pattern_name = patterns.getPatternName(_current_pattern_index)
    except Exception as e:
        print(f"Error updating pattern: {e}")


def OnInit():
    print('FL Response initialized')
    print('Sending responses on: ' + device.getName())


def OnProjectLoad(status):
    """Called when project is loaded. Status 100 = fully loaded."""
    global _target_channel_index, _target_channel_name
    global _current_pattern_index, _current_pattern_name

    # Only initialize on successful load
    if status != 100:
        return

    try:
        print("=" * 50)
        print("OnProjectLoad: Initializing state...")

        # Get current channel
        channel_index = channels.channelNumber()
        channel_name = channels.getChannelName(channel_index)
        _target_channel_index = channel_index
        _target_channel_name = channel_name
        print(f"  Target channel: {channel_index} - {channel_name}")

        # Get current pattern
        update_pattern()
        print(f"  Current pattern: {_current_pattern_index} - {_current_pattern_name}")

        print("Project loaded successfully")
        print("=" * 50)
    except Exception as e:
        print(f"Error in OnProjectLoad: {e}")


def OnSysEx(fl_event):
    """Receive messages from FLRequest and forward to Python (not used in this version)."""
    fl_event.handled = False


def OnDirtyChannel(index, flag):
    """Called when a channel changes in the channel rack."""
    global _channel_rack_selection_index, _channel_rack_selection_name
    global _target_channel_index, _target_channel_name
    global _current_pattern_index, _current_pattern_name

    # CE_Select (4) = channel selection changed (green LED click, mini piano roll, etc.)
    if flag == 4:
        try:
            channel_name = channels.getChannelName(index)

            # Update channel rack selection (what's selected in the rack)
            _channel_rack_selection_index = index
            _channel_rack_selection_name = channel_name

            # Update current pattern
            update_pattern()

            print(f"[OnDirtyChannel] Channel rack selection: {index} - {channel_name}")

            # Check if piano roll is focused
            pr_is_focused = (ui.getFocusedFormID() == 3)  # widPianoRoll
            pl_is_focused = (ui.getFocusedFormID() == 2)  # widPlayList

            if pl_is_focused:
                _target_channel_index = index
                _target_channel_name = channel_name

            if pr_is_focused:
                # Piano roll IS focused - this is likely the PR dropdown menu changing
                # Update the PR's target channel
                _target_channel_index = index
                _target_channel_name = channel_name
                print(f"[OnDirtyChannel] PR focused - target channel updated: {index} - {channel_name}")

                # Send event with new target channel
                # send_event("target_channel_changed", {
                #    "target_channel_index": _target_channel_index,
                #    "target_channel_name": _target_channel_name,
                #    "pattern_index": _current_pattern_index,
                #    "pattern_name": _current_pattern_name
                #})
            else:
                # Piano roll is NOT focused - this is just channel rack selection
                # Do NOT update target channel (PR will use its own target when it opens)
                print(f"[OnDirtyChannel] PR not focused - channel rack change only (target unchanged: {_target_channel_index} - {_target_channel_name})")

        except Exception as e:
            print(f"Error in OnDirtyChannel: {e}")


def OnSendTempMsg(msg, duration):
    """Called when FL Studio sends a temporary message (e.g., menu selections).

    This is the RELIABLE way to detect target channel menu interactions.
    """
    global _target_channel_menu_in_progress, _target_channel_menu_choice

    try:
        if msg.startswith("Menu - Target channel"):
            # Target channel menu opened - start tracking menu interaction
            _target_channel_menu_in_progress = True
            _target_channel_menu_choice = None

        elif msg.startswith("Target channel - "):
            # User selected a channel from the menu
            channel_name = msg.replace("Target channel - ", "").strip()
            # Store the choice - we'll apply it when menu closes
            _target_channel_menu_choice = channel_name

    except Exception as e:
        print(f"Error in OnSendTempMsg: {e}")


def OnRefresh(flags):
    """Called when FL Studio state changes."""
    global _target_channel_index, _target_channel_name
    global _target_channel_menu_in_progress, _target_channel_menu_choice
    global _last_was_focused
    global _current_pattern_index, _current_pattern_name

    # Update current pattern
    update_pattern()

    # Check if piano roll got focus
    has_focus = flags & 32  # HW_Dirty_FocusedWindow

    if has_focus:
        focused_window = ui.getFocusedFormID()
        if focused_window == 3:  # widPianoRoll
            # Check if target channel menu just closed (focus returns to PR)
            if _target_channel_menu_in_progress:
                # Menu closed, PR got focus - apply the menu choice
                if _target_channel_menu_choice:
                    channel_name = _target_channel_menu_choice
                    channel_index = find_channel_index_by_name(channel_name)

                    if channel_index >= 0:
                        _target_channel_index = channel_index
                        _target_channel_name = channel_name
                        print(f"[OnRefresh] Menu CLOSED - applying target channel: {channel_index} - {channel_name}")

                        # Send event with new target channel and pattern
                        send_event("target_channel_changed", {
                            "target_channel_index": _target_channel_index,
                            "target_channel_name": _target_channel_name,
                            "pattern_index": _current_pattern_index,
                            "pattern_name": _current_pattern_name
                        })
                        # Mark as focused so OnIdle doesn't also send
                        _last_was_focused = True
                    else:
                        print(f"[OnRefresh] Could not find channel index for: {channel_name}")

                # Reset menu tracking
                _target_channel_menu_in_progress = False
                _target_channel_menu_choice = None

            else:
                # Normal PR focus - update target channel from channel rack selection
                channel_index = channels.channelNumber()
                channel_name = channels.getChannelName(channel_index)
                _target_channel_index = channel_index
                _target_channel_name = channel_name

               # _current_pattern_index = patterns.patternNumber()
               # _current_pattern_name = patterns.patternName(_current_pattern_index)
                print(f"[OnRefresh] PR focused - target channel set from channel rack: {channel_index} - {channel_name}")

                # Send event with new target channel and pattern
                send_event("target_channel_changed", {
                    "target_channel_index": _target_channel_index,
                    "target_channel_name": _target_channel_name,
                    "pattern_index": _current_pattern_index,
                    "pattern_name": _current_pattern_name
                })
                # Mark as focused so OnIdle doesn't also send
                _last_was_focused = True


def OnIdle():
    """Called periodically - detects piano roll focus transitions."""
    global _last_was_focused
    global _current_pattern_index, _current_pattern_name

    try:
        focused_window = ui.getFocusedFormID()
        is_focused = (focused_window == 3)  # widPianoRoll

        # Detect transition from not-focused to focused
        if is_focused and not _last_was_focused:
            # Update current pattern
            update_pattern()

            print(f"[OnIdle] PR focus transition detected")
            print(f"[OnIdle] Current target channel: {_target_channel_index} - {_target_channel_name}")
            print(f"[OnIdle] Current pattern: {_current_pattern_index} - {_current_pattern_name}")

            # Send event with current target channel and pattern
            send_event("target_channel_changed", {
                "target_channel_index": _target_channel_index,
                "target_channel_name": _target_channel_name,
                "pattern_index": _current_pattern_index,
                "pattern_name": _current_pattern_name
            })

        # Update tracking state
        _last_was_focused = is_focused

    except Exception as e:
        print(f"Error in OnIdle: {e}")
