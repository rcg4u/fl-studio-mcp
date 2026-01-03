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

# Write to Hardware directory where this script lives
SCRIPT_DIR = os.path.expanduser("~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController")
PATTERN_STATE_FILE = os.path.join(SCRIPT_DIR, "fl_pattern_state.json")
CHANNEL_STATE_FILE = os.path.join(SCRIPT_DIR, "fl_channel_state.json")
SUSPEND_FILE = os.path.join(SCRIPT_DIR, "suspend_focus_detection.json")
TRIGGER_FILE = os.path.join(SCRIPT_DIR, "trigger_piano_roll_script.flag")

# Piano roll scripts directory
PIANO_ROLL_SCRIPTS_DIR = os.path.expanduser("~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts")
LLM_INTERACTION_FLAG = os.path.join(PIANO_ROLL_SCRIPTS_DIR, "llm_interaction_active.flag")


# Track last written states to avoid duplicates
_last_pattern = None
_last_piano_roll_focused = False


def is_suspend_active():
    """Check if focus detection is suspended (for LLM updates)."""
    try:
        if os.path.exists(SUSPEND_FILE):
            with open(SUSPEND_FILE, 'r') as f:
                data = json.load(f)
                return data.get("suspend", False)
        return False
    except:
        return False


def write_pattern_state():
    """Write current pattern state to JSON file (only if changed)"""
    global _last_pattern
    try:
        pattern_num = patterns.patternNumber()
        if pattern_num == _last_pattern:
            return  # Skip duplicate
        pattern_name = patterns.getPatternName(pattern_num)
        state = {"pattern": pattern_num, "patternName": pattern_name}
        with open(PATTERN_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        _last_pattern = pattern_num
        print(f"Pattern: {pattern_num} - {pattern_name}")
    except Exception as e:
        print(f"Error writing pattern state: {e}")


def write_channel_state():
    """Write current channel state to JSON file"""
    try:
        channel_num = channels.channelNumber()
        channel_name = channels.getChannelName(channel_num)
        state = {"channel": channel_num, "channelName": channel_name}
        with open(CHANNEL_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"Channel: {channel_num} - {channel_name}")
    except Exception as e:
        print(f"Error writing channel state: {e}")


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
    if len(fl_event.sysex) >= 5:  # Need 5 bytes: F0 + 3 header + 1 origin
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
    # Debug: Show all flags
    flag_names = []
    if flags & HW_Dirty_Patterns:
        flag_names.append("HW_Dirty_Patterns")
    if flags & HW_Dirty_FocusedWindow:
        flag_names.append("HW_Dirty_FocusedWindow")
    if flags & HW_ChannelEvent:
        flag_names.append("HW_ChannelEvent")
    if flag_names:
        print(f"OnRefresh flags: {', '.join(flag_names)}, ui.getFocused(3)={ui.getFocused(3)}")

    # Piano roll focused
    if flags & HW_Dirty_FocusedWindow:
        if ui.getFocused(3):  # widPianoRoll = 3
            channel_num = channels.channelNumber()
            channel_name = channels.getChannelName(channel_num)
            pattern_num = patterns.patternNumber()
            pattern_name = patterns.getPatternName(pattern_num)
            print(f"Piano roll opened: Channel {channel_num} ({channel_name}), Pattern {pattern_num} ({pattern_name})")

    # Pattern changed
    if flags & HW_Dirty_Patterns:
        if ui.getFocused(3):  # Piano roll is focused
            pattern_num = patterns.patternNumber()
            pattern_name = patterns.getPatternName(pattern_num)
            print(f"Piano roll pattern changed: {pattern_num} ({pattern_name})")
        write_pattern_state()


def OnDirtyChannel(index, flag):
    """Called when a specific channel changes"""
    print(f"OnDirtyChannel: index={index}, flag={flag}")

    # CE_Select = 4 (channel selection)
    if flag == 4:
        if ui.getFocused(3):  # Piano roll is focused
            channel_name = channels.getChannelName(index)
            print(f"  -> Piano roll channel changed: {index} ({channel_name})")
            write_channel_state()
        else:
            # Normal channel rack click
            write_channel_state()


def OnIdle():
    """Called periodically - check if piano roll closed while LLM session active"""
    global _last_piano_roll_focused

    try:
        # Check if piano roll is currently focused
        piano_roll_focused = ui.getFocused(3)  # widPianoRoll = 3

        # Detect piano roll close (was focused, now not focused)
        if _last_piano_roll_focused and not piano_roll_focused:
            # Piano roll was just closed
            # Check if LLM interaction is active
            if os.path.exists(LLM_INTERACTION_FLAG):
                try:
                    with open(LLM_INTERACTION_FLAG, 'r') as f:
                        content = f.read().strip()

                    if content == "active":
                        # Deactivate the session since piano roll closed
                        with open(LLM_INTERACTION_FLAG, 'w') as f:
                            f.write("inactive")
                        print("Piano roll closed - LLM interaction session deactivated")
                except Exception as e:
                    print(f"Error updating LLM interaction flag: {e}")

        # Update last focused state
        _last_piano_roll_focused = piano_roll_focused

    except Exception as e:
        print(f"Error in OnIdle: {e}")
