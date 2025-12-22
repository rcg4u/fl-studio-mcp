# name=FLRequest
# url=https://forum.image-line.com

"""
FL Studio controller that receives SysEx commands from Python.
Executes commands and sends results to FL Sender controller.
"""

import ui
import mixer
import transport
import channels
import playlist
import patterns
import plugins
import device
import general

def setChannelSequence(channel_id, sequence):
    """
    Set all grid bits for a channel from a sequence array.
    This avoids sending 32 individual MIDI commands.

    Args:
        channel_id: Channel index (0-based)
        sequence: List of 0s and 1s for each step

    Returns:
        Status message with active step count
    """
    for step, value in enumerate(sequence):
        channels.setGridBit(channel_id, step, value)
    active_steps = sum(sequence)
    return f"Set {active_steps} steps for channel {channel_id}"

def setMultipleChannelSequences(channel_sequences):
    """
    Set sequences for multiple channels at once.
    This batches multiple channel updates into one command.

    Args:
        channel_sequences: List of dicts, each containing:
            - channel_id: Channel index (0-based)
            - sequence: List of 0s and 1s for each step

    Returns:
        Summary message with all channels updated

    Example:
        setMultipleChannelSequences([
            {"channel_id": 0, "sequence": [1,0,1,0,1,0,1,0]},
            {"channel_id": 1, "sequence": [0,0,0,0,1,0,0,0]}
        ])
    """
    results = []
    for item in channel_sequences:
        channel_id = item["channel_id"]
        sequence = item["sequence"]
        for step, value in enumerate(sequence):
            channels.setGridBit(channel_id, step, value)
        active_steps = sum(sequence)
        results.append(f"Channel {channel_id}: {active_steps}/{len(sequence)} active")

    return f"Updated {len(channel_sequences)} channels - " + ", ".join(results)

def OnInit():
    print('FL Request initialized')
    print(f'Listening for commands on: {device.getName()}')

def OnSysEx(fl_event):
    """Receive command from Python"""
    # Check for our command header
    if len(fl_event.sysex) >= 4 and bytes(fl_event.sysex[1:4]) == b'\x7d\x11\x00':
        try:
            # Get command data
            data = fl_event.sysex[4:]
            if data[-1] == 247:  # Remove F7
                data = data[:-1]

            command = bytes(data).decode('utf-8')
            print(f'Request: Got command: {command}')

            # Execute the command
            result = eval(command)
            print(f'Request: Result: {result}')

            # Send success response to FLResponse controller via dispatch
            # Add origin byte 0x01 = INTERNAL (from dispatch)
            result_str = str(result)
            response_sysex = b'\xf0\x7d\x11\x10\x01' + result_str.encode('utf-8') + b'\xf7'

            # Dispatch to FLResponse (receiver index 0)
            if device.dispatchReceiverCount() > 0:
                device.dispatch(0, 0xF0, response_sysex)
                print(f'Request: Dispatched response to FLResponse')
            else:
                print(f'Request ERROR: No FLResponse controller found!')

        except Exception as e:
            print(f'Request error: {e}')
            # Send error response to FLResponse controller
            # Add origin byte 0x01 = INTERNAL (from dispatch)
            error_str = str(e)
            error_sysex = b'\xf0\x7d\x11\x20\x01' + error_str.encode('utf-8') + b'\xf7'

            if device.dispatchReceiverCount() > 0:
                device.dispatch(0, 0xF0, error_sysex)
                print(f'Request: Dispatched error to FLResponse')
            else:
                print(f'Request ERROR: No FLResponse controller found!')

        fl_event.handled = True
    else:
        fl_event.handled = False
