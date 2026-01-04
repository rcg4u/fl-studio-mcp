# name=FLResponse
# receiveFrom=FLRequest
# url=https://forum-image-line.com

"""
FL Studio controller that receives messages from FLRequest
and sends SysEx responses back to Python.

Also monitors FL Studio state changes (pattern, channel, piano roll) and writes to state files.
"""

import device
import json
import os
import patterns
import channels
import ui
import time
import transport
import midi

# OnRefresh flag constants
HW_Dirty_Patterns = 1024
HW_Dirty_FocusedWindow = 32
HW_ChannelEvent = 65536
HW_Dirty_Browser = 256  # Browser selection/navigation (discovered via testing)

# Write to Hardware directory where this script lives
SCRIPT_DIR = os.path.expanduser("~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController")

# Event file for communicating with MCP server (single event stream)
EVENT_FILE = os.path.join(SCRIPT_DIR, "fl_events.json")

# Piano roll scripts directory
PIANO_ROLL_SCRIPTS_DIR = os.path.expanduser("~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts")
PIANO_ROLL_STATE_FILE = os.path.join(PIANO_ROLL_SCRIPTS_DIR, "piano_roll_state.json")

# Window ID mapping (verified from actual testing)
WINDOW_NAMES = {
    -1: "Startup",      # Before FL Studio fully loads
    0: "Mixer",         # Confirmed
    1: "Channel Rack",  # Confirmed
    2: "Playlist",      # Confirmed
    3: "Piano Roll",    # Confirmed
    4: "Browser",       # Not yet confirmed
    5: "Unknown (5)",   # Not yet seen
    6: "Plugin",        # Not yet confirmed
    7: "Effect Plugin", # Not yet confirmed
    8: "Generator Plugin" # Not yet confirmed
}

# Track last focused window for general focus tracking
_last_focused_window = None

# Track last written pattern to avoid duplicate events
_last_pattern = None

# Track if HW_ChannelEvent just fired (to skip piano roll trigger)
_channel_event_fired = False
_channel_event_time = 0

# Track last browser node to detect navigation changes
_last_browser_caption = None
_last_browser_file_type = None

# Browser node type names mapping
BROWSER_TYPE_NAMES = {
    -1: "Folder/Category",
    1: "FLP", 2: "ZIP", 3: "FLM", 4: "FST",
    7: "WAV", 13: "MP3", 14: "OGG", 15: "FLAC",
    27: "MIDI", 28: "FLEX Pack", 31: "Library", 32: "Library (Owned)"
}


def get_browser_type_name(file_type):
    """Get human-readable name for browser file type"""
    return BROWSER_TYPE_NAMES.get(file_type, f"Type({file_type})")


def send_event(event_type, data):
    """Send event to MCP server via event stream (single JSONL file)"""
    try:
        event = {"type": event_type, "data": data}

        # Append to event file (JSONL format - one JSON per line)
        with open(EVENT_FILE, 'a') as f:
            f.write(json.dumps(event) + "\n")

        print("Event: " + event_type)
    except Exception as e:
        print("Event failed: " + event_type + " - " + str(e))


def trigger_run_last_script():
    """TEST: Navigate menu to find Run Last Script

    Opens menu → Down 2 (Tools) → Right (submenu) → Down 1 → Enter
    """
    try:
        # Ensure piano roll is focused
        print("Setting piano roll focus...")
        ui.setFocused(3)  # widPianoRoll = 3
        time.sleep(0.3)

        print("Step 1: Opening app menu...")
        # Open the menu
        transport.globalTransport(midi.FPT_Menu, 1)
        time.sleep(0.2)
        print("Menu opened")

        # Right to enter submenu
        print("Step 2: Right to enter submenu...")
        transport.globalTransport(midi.FPT_Right, 1)
        time.sleep(0.1)

        # Down twice
        print("Step 3: Down twice...")
        transport.globalTransport(midi.FPT_Down, 1)
        time.sleep(0.1)
        transport.globalTransport(midi.FPT_Down, 1)
        time.sleep(0.1)

        print("TEST: Menu navigation complete - check what is highlighted!")
        return True

    except Exception as e:
        print(f"Error during menu navigation: {e}")
        import traceback
        traceback.print_exc()
        return False


def OnInit():
    print('FL Response initialized')
    print(f'Sending responses on: {device.getName()}')

def OnSysEx(fl_event):
    """Receive messages from FLRequest and forward to Python"""
    # Check if sysex data exists
    if fl_event.sysex is None or len(fl_event.sysex) < 5:
        fl_event.handled = False
        return

    header = bytes(fl_event.sysex[1:4])
    origin = fl_event.sysex[4]

    # Only forward messages with our response headers AND origin=0x01 (INTERNAL from dispatch)
    if (header == b'\x7d\x11\x10' or header == b'\x7d\x11\x20') and origin == 0x01:
        # Change origin to 0x00 (SERVER) and forward to Python
        sysex_msg = bytes([0xF0]) + header + bytes([0x00]) + bytes(fl_event.sysex[5:])
        device.midiOutSysex(sysex_msg)
        fl_event.handled = True
        return

    # All other messages: ignore (wrong header, wrong origin, or from our own output)
    fl_event.handled = False


def OnRefresh(flags):
    """Called when FL Studio state changes"""
    global _last_pattern, _channel_event_fired, _channel_event_time

    # DEBUG: Log ALL flags to discover new ones
    if flags != 0:
        print("DEBUG: OnRefresh flags = " + str(flags))

    # Pattern changed globally
    if flags & HW_Dirty_Patterns:
        pattern_num = patterns.patternNumber()
        if pattern_num != _last_pattern:
            pattern_name = patterns.getPatternName(pattern_num)
            _last_pattern = pattern_num

            # Just send pattern changed event
            send_event("pattern_changed", {
                "pattern": pattern_num,
                "pattern_name": pattern_name
            })

    # Check if focused window changed
    if flags & HW_Dirty_FocusedWindow:
        focused_window = ui.getFocusedFormID()
        window_name = WINDOW_NAMES.get(focused_window, str(focused_window))
        print("DEBUG: HW_Dirty_FocusedWindow - " + window_name)

        # Only set skip flag if Channel Rack got focus (not Piano Roll)
        # Channel selector click → Channel Rack focus → skip trigger
        # Mini piano roll click → Piano Roll focus → DON'T skip
        if focused_window == 1:  # widChannelRack = 1
            print("DEBUG: Channel Rack focused - setting skip flag")
            _channel_event_fired = True
            _channel_event_time = time.time()
        elif focused_window == 3:  # widPianoRoll = 3
            # Piano roll got focus - send event immediately
            try:
                pat_num = patterns.patternNumber()
                pat_name = patterns.getPatternName(pat_num)
                target_ch = channels.channelNumber()
                target_ch_name = channels.getChannelName(target_ch)

                # Check if this should skip trigger (channel selector was clicked recently)
                skip_trigger = False
                if _channel_event_fired and (time.time() - _channel_event_time) < 0.5:
                    skip_trigger = True
                    print("DEBUG: Skipping trigger (channel selector clicked)")
                    _channel_event_fired = False  # Clear the flag

                send_event("piano_roll_focus", {
                    "pattern": pat_num,
                    "pattern_name": pat_name,
                    "channel": target_ch,
                    "channel_name": target_ch_name,
                    "skip_trigger": skip_trigger
                })
            except Exception as e:
                print("Error sending piano_roll_focus: " + str(e))

    # DEBUG: Check if channel event occurred
    if flags & HW_ChannelEvent:
        print("DEBUG: HW_ChannelEvent fired")

    # Check if browser selection changed
    if flags & HW_Dirty_Browser:
        print("DEBUG: HW_Dirty_Browser fired")
        try:
            # Read browser caption immediately (don't wait for OnIdle poll)
            caption = ui.getFocusedNodeCaption()
            file_type = ui.getFocusedNodeFileType()

            # Only process non-empty captions
            if caption and caption.strip():
                # Check if this is a piano roll entry
                is_piano_roll_node = caption.endswith("Piano roll") or "Piano roll" in caption

                # Get human-readable type name
                type_name = get_browser_type_name(file_type)

                print("Browser caption from OnRefresh: " + str(caption))
                print("Piano Roll: " + ("Yes" if is_piano_roll_node else "No"))

                # Send browser event immediately
                send_event("browser_node_changed", {
                    "caption": caption,
                    "file_type": file_type,
                    "type_name": type_name,
                    "is_piano_roll": is_piano_roll_node if is_piano_roll_node else False
                })
        except Exception as e:
            print("Error reading browser in OnRefresh: " + str(e))


def OnDirtyChannel(index, flag):
    """Called when a specific channel changes"""
    # CE_Select (4) = channel selection changed
    if flag == 4:
        try:
            channel_name = channels.getChannelName(index)
            pattern_num = patterns.patternNumber()
            pattern_name = patterns.getPatternName(pattern_num)
            focused_window = ui.getFocusedFormID()

            # Send different events based on where the selection happened
            if focused_window == 3:  # widPianoRoll = 3
                # Piano roll is focused - target channel changed
                print("Piano Roll Channel: " + str(index) + " (" + channel_name + ")")
                send_event("target_channel_changed", {
                    "pattern": pattern_num,
                    "pattern_name": pattern_name,
                    "channel": index,
                    "channel_name": channel_name
                })
            elif focused_window == 1:  # widChannelRack = 1
                # Channel rack is focused (step sequencer, mini piano roll, etc.)
                print("Channel Rack Selection: " + str(index) + " (" + channel_name + ")")
                send_event("channel_selected", {
                    "pattern": pattern_num,
                    "pattern_name": pattern_name,
                    "channel": index,
                    "channel_name": channel_name
                })
        except Exception as e:
            print("Error in OnDirtyChannel: " + str(e))


def OnIdle():
    """Called periodically - track focus changes and send events"""
    global _last_focused_window, _last_browser_caption, _last_browser_file_type
    global _channel_event_fired, _channel_event_time

    try:
        # Track window focus changes (lightweight polling)
        current_window = ui.getFocusedFormID()
        if current_window != _last_focused_window:
            prev_name = WINDOW_NAMES.get(_last_focused_window, str(_last_focused_window)) if _last_focused_window is not None else "None"
            curr_name = WINDOW_NAMES.get(current_window, str(current_window))

            msg = "Focus: " + prev_name + " -> " + curr_name

            # Add pattern/channel context if focusing Piano Roll
            if current_window == 3:
                try:
                    pat_num = patterns.patternNumber()
                    pat_name = patterns.getPatternName(pat_num)

                    # Read the selected channel (this is the target channel when piano roll is focused)
                    target_ch = channels.channelNumber()
                    target_ch_name = channels.getChannelName(target_ch)

                    msg += " (Pattern " + str(pat_num) + ": " + pat_name + ", Target Channel " + str(target_ch) + ": " + target_ch_name + ")"

                    # Check if this focus was caused by channel selector click (within 0.5 seconds)
                    skip_trigger = False
                    if _channel_event_fired and (time.time() - _channel_event_time) < 0.5:
                        skip_trigger = True
                        print("DEBUG: Skipping trigger (channel selector clicked)")
                        _channel_event_fired = False  # Clear the flag

                    # Send event via stream with the selected channel as target channel
                    send_event("piano_roll_focus", {
                        "pattern": pat_num,
                        "pattern_name": pat_name,
                        "channel": target_ch,
                        "channel_name": target_ch_name,
                        "skip_trigger": skip_trigger
                    })
                except:
                    pass

            print(msg)
            _last_focused_window = current_window

        # Track browser navigation changes (when browser is focused - widBrowser = 4)
        if current_window == 4:
            try:
                caption = ui.getFocusedNodeCaption()
                file_type = ui.getFocusedNodeFileType()

                # Check if browser node has changed
                if caption != _last_browser_caption or file_type != _last_browser_file_type:
                    # Only send event if caption is not empty (skip empty transitions)
                    # But still update tracking to prevent duplicate events
                    prev_caption = _last_browser_caption
                    _last_browser_caption = caption
                    _last_browser_file_type = file_type

                    # Only process non-empty captions
                    if caption and caption.strip():
                        # Get human-readable type name
                        type_name = get_browser_type_name(file_type)

                        # Check if this is a piano roll entry
                        is_piano_roll_node = caption.endswith("Piano roll") or "Piano roll" in caption

                        # Print detailed browser node info
                        print("=" * 50)
                        print("BROWSER NODE CHANGED")
                        print("-" * 50)
                        print("Caption:     " + str(caption))
                        print("Type:        " + str(file_type))
                        print("Type Name:   " + type_name)
                        print("Piano Roll:  " + ("Yes" if is_piano_roll_node else "No"))
                        print("=" * 50)

                        # Send browser navigation event (listener will handle trigger)
                        send_event("browser_node_changed", {
                            "caption": caption,
                            "file_type": file_type,
                            "type_name": type_name,
                            "is_piano_roll": is_piano_roll_node if is_piano_roll_node else False
                        })
            except Exception as e:
                print("Error tracking browser: " + str(e))
        # Note: Don't reset caption when browser loses focus - preserve last known node

    except:
        pass  # Silently ignore errors

