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
import general

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

# Note: Channel rack selection tracking removed - was set but never used

# Track last focused state for OnIdle
_last_was_focused = False

# Track menu interaction state
_target_channel_menu_in_progress = False
_target_channel_menu_choice = None



def send_event(event_type, data):
    """Send event to listener via event file (JSONL format)."""
    global _target_channel_name, _current_pattern_name
    try:
        event = {"type": event_type, "data": data}
        with open(EVENT_FILE, 'a') as f:
            f.write(json.dumps(event) + "\n")
        print()
        print(f"     Event {{ t: {_target_channel_name}, p: {_current_pattern_name} }}")
        print()
    except Exception as e:
        print(f"     Event failed: {event_type} - {str(e)}")


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
    global _target_channel_name, _current_pattern_name
    print(f"OnInit()")
    print()
    print(f"     enter: target: {_target_channel_name}, pattern: {_current_pattern_name}")
    print(f"     exit: target: {_target_channel_name}, pattern: {_current_pattern_name}")
    print()


def OnProjectLoad(status):
    """Called when project is loaded. Status 100 = fully loaded."""
    global _target_channel_index, _target_channel_name
    global _current_pattern_index, _current_pattern_name
    print(f"OnProjectLoad(status={status})")
    print()
    print(f"     enter: target: {_target_channel_name}, pattern: {_current_pattern_name}")

    # Only initialize on successful load
    if status != 100:
        print(f"     exit: target: {_target_channel_name}, pattern: {_current_pattern_name}")
        print()
        return

    try:
        # Get project name
        project_name = "Unknown"
        try:
            project_name = general.getProjectTitle()
        except Exception as e:
            print(f"Error getting project name: {e}")

        # Get current channel
        channel_index = channels.channelNumber()
        channel_name = channels.getChannelName(channel_index)
        _target_channel_index = channel_index
        _target_channel_name = channel_name

        # Get current pattern
        update_pattern()

        # Collect all channels
        channels_list = []
        try:
            channel_count = channels.channelCount()
            for i in range(channel_count):
                ch_name = channels.getChannelName(i)
                channels_list.append({
                    "index": i,
                    "name": ch_name
                })
        except Exception as e:
            print(f"Error collecting channels: {e}")

        # Collect all patterns (1-based in FL Studio)
        patterns_list = []
        try:
            pattern_count = patterns.patternCount()
            # Patterns in FL Studio are 1-based, start from index 1
            for i in range(1, pattern_count + 1):
                pat_name = patterns.getPatternName(i)
                patterns_list.append({
                    "index": i,
                    "name": pat_name
                })
        except Exception as e:
            print(f"Error collecting patterns: {e}")

        # Send project loaded event with all channels, patterns, and project name
        send_event("project_loaded", {
            "project_name": project_name,
            "channels": channels_list,
            "patterns": patterns_list
        })

    except Exception as e:
        print(f"Error in OnProjectLoad: {e}")

    print(f"     exit: target: {_target_channel_name}, pattern: {_current_pattern_name}")
    print()


def OnSysEx(fl_event):
    """Receive messages from FLRequest and forward to Python (not used in this version)."""
    fl_event.handled = False


def OnDirtyChannel(index, flag):
    """Called when a channel changes in the channel rack."""
    global _target_channel_index, _target_channel_name
    global _current_pattern_index, _current_pattern_name

    # Flag breakdown
    flag_names = {
        0: "CE_New",
        1: "CE_Delete",
        2: "CE_Replace",
        3: "CE_Rename",
        4: "CE_Select"
    }
    flag_name = flag_names.get(flag, f"unknown({flag})")

    # Get channel name for display
    try:
        if index >= 0:
            channel_name = channels.getChannelName(index)
            index_str = f"{index} ({channel_name})"
        else:
            index_str = f"{index} (all channels)"
    except:
        index_str = str(index)

    print(f"OnDirtyChannel(index={index_str}, flag={flag_name})")
    print()
    print(f"     enter: target: {_target_channel_name}, pattern: {_current_pattern_name}")

    # CE_Select (4) = channel selection changed (green LED click, mini piano roll, etc.)
    if flag == 4:
        try:
            channel_name = channels.getChannelName(index)
            update_pattern()

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

        except Exception as e:
            print(f"Error in OnDirtyChannel: {e}")

    print(f"     exit: target: {_target_channel_name}, pattern: {_current_pattern_name}")
    print()


def OnSendTempMsg(msg, duration):
    """Called when FL Studio sends a temporary message (e.g., menu selections).

    This is the RELIABLE way to detect target channel menu interactions.
    """
    global _target_channel_name, _current_pattern_name
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

    # Flag breakdown
    flag_names = []
    flag_map = {
        1: "HW_Dirty_Mixer_Sel",
        2: "HW_Dirty_Mixer_Display",
        4: "HW_Dirty_Mixer_Controls",
        16: "HW_Dirty_RemoteLinks",
        32: "HW_Dirty_FocusedWindow",
        64: "HW_Dirty_Performance",
        256: "HW_Dirty_LEDs",
        512: "HW_Dirty_RemoteLinkValues",
        1024: "HW_Dirty_Patterns",
        2048: "HW_Dirty_Tracks",
        4096: "HW_Dirty_ControlValues",
        8192: "HW_ChannelEvent",
        16384: "HW_Dirty_Colors"
    }
    for bit, name in flag_map.items():
        if flags & bit:
            flag_names.append(name)
    flags_str = " | ".join(flag_names) if flag_names else "0"

    print(f"OnRefresh(flags={flags_str})")
    print()
    print(f"     enter: target: {_target_channel_name}, pattern: {_current_pattern_name}")

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
                        print(f"     Menu choice applied: {channel_name}")
                        _target_channel_index = channel_index
                        _target_channel_name = channel_name

                        # Send event with new target channel and pattern
                        send_event("target_channel_changed", {
                            "target_channel_index": _target_channel_index,
                            "target_channel_name": _target_channel_name,
                            "pattern_index": _current_pattern_index,
                            "pattern_name": _current_pattern_name
                        })
                        # Mark as focused so OnIdle doesn't also send
                        _last_was_focused = True

                # Reset menu tracking
                _target_channel_menu_in_progress = False
                _target_channel_menu_choice = None

            else:
                # Normal PR focus - update target channel from channel rack selection
                channel_index = channels.channelNumber()
                channel_name = channels.getChannelName(channel_index)
                _target_channel_index = channel_index
                _target_channel_name = channel_name

                # Send event with new target channel and pattern
                send_event("target_channel_changed", {
                    "target_channel_index": _target_channel_index,
                    "target_channel_name": _target_channel_name,
                    "pattern_index": _current_pattern_index,
                    "pattern_name": _current_pattern_name
                })
                # Mark as focused so OnIdle doesn't also send
                _last_was_focused = True

    print(f"     exit: target: {_target_channel_name}, pattern: {_current_pattern_name}")
    print()


def OnIdle():
    """Called periodically - detects piano roll focus transitions."""
    global _last_was_focused
    global _target_channel_index, _target_channel_name
    global _current_pattern_index, _current_pattern_name
    # Note: OnIdle called too frequently to print every call

    try:
        focused_window = ui.getFocusedFormID()
        is_focused = (focused_window == 3)  # widPianoRoll

        # Detect transition from not-focused to focused
        if is_focused and not _last_was_focused:
            # Update current pattern
            update_pattern()

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
