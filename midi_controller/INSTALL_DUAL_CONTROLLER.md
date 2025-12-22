# Dual-Controller Setup Instructions

## Overview
This system uses two FL Studio controllers to enable bidirectional SysEx communication, bypassing the macOS IAC Driver loopback limitation.

## What's Happening
1. Python sends SysEx → **FLRequest** (Port 1)
2. **FLRequest** executes command → internally dispatches to **FLResponse**
3. **FLResponse** sends SysEx response → Python (Port 2)

## Setup Steps

### 1. Create Two MIDI Ports in Audio MIDI Setup

1. Open Audio MIDI Setup
2. Window → Show MIDI Studio (⌘+2)
3. Double-click IAC Driver
4. Create two ports:
   - **Port 1** (for commands from Python to FLRequest)
   - **Port 2** (for responses from FLResponse to Python)

### 2. Install Controller Scripts in FL Studio

```bash
# Install FLRequest
ln -s /Users/calvinw/develop/midi-controller/device_FLRequest.py \
   ~/Documents/Image-Line/FL\ Studio/Settings/Hardware/FLController/device_FLRequest.py

# Install FLResponse
ln -s /Users/calvinw/develop/midi-controller/device_FLResponse.py \
   ~/Documents/Image-Line/FL\ Studio/Settings/Hardware/FLController/device_FLResponse.py
```

### 3. Configure FL Studio MIDI Settings

1. Options → MIDI Settings (F10)
2. Enable **Port 1** as Input ✅
3. Enable **Port 2** as Input ✅
4. For **Port 1**:
   - Controller type: **FLRequest**
   - Enable Input ✅
5. For **Port 2**:
   - Controller type: **FLResponse**
   - Enable Input ✅ (and optionally Output)

### 4. Load the Controllers

1. VIEW → Script output
2. Click folder icon
3. Select **Hardware** → **FLController**
4. Load **FLRequest** first
5. Load **FLResponse** second

You should see:
```
FLRequest initialized
Listening for commands on: FLRequest
FLResponse initialized
Sending responses on: FLResponse
```

### 5. Test It

```bash
python3 test_dual_port.py
```

## How It Works

### FLRequest (device_FLRequest.py)
- Receives SysEx commands from Python
- Executes the command using `eval()`
- Sends result to FLResponse using `device.dispatch()`
- Uses Control Change messages (CC 1-119) to send text

### FLResponse (device_FLResponse.py)
- Has special header: `# receiveFrom=FLRequest`
- Receives CC messages from FLRequest
- Builds response string from CC data
- Sends SysEx response back to Python
- Uses header `0x7d 0x11 0x10` for success, `0x7d 0x11 0x20` for error

### Python Client (fl_dual_port.py)
- Sends commands on **Port 1**
- Listens for responses on **Port 2**
- Simple request/response API

## Benefits
- ✅ True bidirectional SysEx communication
- ✅ No file I/O needed
- ✅ Fast and reliable
- ✅ Works on macOS with IAC Driver
- ✅ Simple to understand

## Troubleshooting

### If Controllers Don't Appear
- Check symlinks are created correctly
- Restart FL Studio
- Reload scripts in Script output window

### If No Responses
- Make sure both controllers are loaded
- Check Script output for error messages
- Verify both MIDI ports are enabled in FL Studio settings

### Internal Dispatch Not Working
- The `receiveFrom=FLRequest` header is crucial
- Load FLRequest BEFORE FLResponse
- Check that both controllers have different names

## Example Usage

```python
from fl_dual_port import send_command, jump_to_pattern

# Get data (needs response)
count = send_command("patterns.patternCount()")
print(f"Pattern count: {count}")

# Switch pattern (no response needed)
jump_to_pattern(3)
```