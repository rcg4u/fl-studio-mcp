"""
FL Studio dual-port communication system.

Send commands on FL Request port, receive responses on FL Response port.
Uses two FL Studio controllers to bypass MIDI loopback issues.
"""

import mido
import time

# MIDI ports
REQUEST_PORT = 'FLRequest'
RESPONSE_PORT = 'FLResponse'  # Using separate port to avoid loopback
TIMEOUT = 2.0

# Global MIDI ports
_outport = None
_inport = None

def init_midi():
    """Initialize MIDI ports"""
    global _outport, _inport
    if _outport is None:
        _outport = mido.open_output(REQUEST_PORT)
    if _inport is None:
        _inport = mido.open_input(RESPONSE_PORT)

def send_command(command, expect_response=True):
    """
    Send command to FL Studio

    Args:
        command (str): Python command to execute
        expect_response (bool): Whether to wait for response

    Returns:
        str or None: Response from FL Studio
    """
    init_midi()
    global _outport, _inport

    # Clear any pending messages
    for msg in _inport.iter_pending():
        pass

    # Send command as SysEx
    sysex_data = b'\x7d\x11\x00' + command.encode('utf-8')
    msg = mido.Message('sysex', data=sysex_data)

    _outport.send(msg)

    # Always wait for response to keep queue clean
    # (FL Studio always sends a response, even for void functions)
    start_time = time.time()
    while time.time() - start_time < TIMEOUT:
        msg = _inport.poll()
        if msg and msg.type == 'sysex':
            # Format: header(3) + origin(1) + data
            # In mido, msg.data doesn't include F0/F7
            if len(msg.data) >= 4:
                header = bytes(msg.data[0:3])
                origin = msg.data[3]

                # Only process SERVER messages (origin=0x00)
                if origin == 0x00:
                    if header == b'\x7d\x11\x10':  # Success
                        response = bytes(msg.data[4:]).decode('utf-8')
                        # Return response only if expected, otherwise None
                        return response if expect_response else None
                    elif header == b'\x7d\x11\x20':  # Error
                        error = bytes(msg.data[4:]).decode('utf-8')
                        raise Exception(error)

        time.sleep(0.01)

    raise TimeoutError("No response received")

def close_ports():
    """Close MIDI ports"""
    global _outport, _inport
    if _outport:
        _outport.close()
        _outport = None
    if _inport:
        _inport.close()
        _inport = None
