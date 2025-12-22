# name=FLResponse
# receiveFrom=FLRequest
# url=https://forum.image-line.com

"""
FL Studio controller that receives messages from FLRequest
and sends SysEx responses back to Python.
"""

import device

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
