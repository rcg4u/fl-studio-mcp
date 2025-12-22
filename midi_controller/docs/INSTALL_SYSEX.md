# SysEx Setup Instructions

## Overview
This guide walks through setting up the SysEx-based MIDI controller for FL Studio, which replaces the JSON file-based approach for more reliable communication.

## What's Changed
- **Before**: Write JSON file → Send MIDI Note On → FL Studio reads file → Executes command
- **After**: Send command directly via SysEx → FL Studio executes immediately

## Setup Steps

### 1. Install the New Device Script in FL Studio

```bash
# Create symlink in FL Studio Hardware directory
ln -s /Users/calvinw/develop/midi-controller/device_sysex_simple.py \
   ~/Documents/Image-Line/FL\ Studio/Settings/Hardware/SimpleController/device_sysex_simple.py
```

### 2. Update FL Studio MIDI Settings

1. Open FL Studio
2. Go to **Options → MIDI Settings**
3. Find **IAC Driver Bus 1** in the list
4. Ensure it's enabled as **Input** ✅
5. Select **"SysEx Controller"** as the controller type
6. Click **Accept**

### 3. Load the New Device Script

1. In FL Studio, go to **VIEW → Script output**
2. In the Script output window:
   - Click the folder icon
   - Select "Hardware" from the dropdown
   - Choose "SysEx Controller" (it should appear in the list)
   - Click "Load"

3. You should see:
   ```
   SysEx Controller initialized
   Device: SysEx Controller
   Port: [port number]
   ```

### 4. Test the Connection

Run the test script to verify everything works:

```bash
python3 test_sysex.py
```

You should see successful responses from FL Studio.

### 5. Run the Updated Pattern Switcher

The new UI uses SysEx instead of JSON:

```bash
# Option 1: Direct run
python3 pattern_switcher_ui_sysex.py

# Option 2: Create a convenience script
echo '#!/bin/bash
python3 pattern_switcher_ui_sysex.py' > run_ui_sysex.sh
chmod +x run_ui_sysex.sh
./run_ui_sysex.sh
```

## Key Files

| File | Purpose |
|------|---------|
| `device_sysex_simple.py` | FL Studio device script that receives SysEx commands |
| `fl_request_sysex.py` | Sends SysEx commands to FL Studio |
| `pattern_switcher_ui_sysex.py` | Updated UI using SysEx |
| `test_sysex.py` | Test script to verify setup |

## Migration Notes

### The Old System (JSON)
- `device_simple_request.py` - Read JSON files
- `request.json` - Command storage
- `fl_request.py` - Write JSON + MIDI Note On

### The New System (SysEx)
- `device_sysex_simple.py` - Execute SysEx commands directly
- `fl_request_sysex.py` - Send SysEx messages
- No files needed - direct MIDI communication

## Troubleshooting

### SysEx Not Working
1. Verify the device script is loaded correctly (check Script output window)
2. Ensure IAC Driver Bus 1 is enabled in MIDI Settings
3. Check FL Studio's Script output for any error messages
4. Try reloading the device script (Script output → Reload)

### Port Issues
- Make sure no other applications are using IAC Driver Bus 1
- Check Audio MIDI Setup to ensure IAC Driver is online

### Python Errors
- Ensure you're using the right Python with the virtual environment
- Verify mido is installed: `pip install mido python-rtmidi`

## Benefits of SysEx Approach

1. **Faster**: Direct command execution, no file I/O
2. **More Reliable**: No timing issues or race conditions
3. **Cleaner**: No temporary files to manage
4. **More Flexible**: Can execute any valid Python expression
5. **Bidirectional**: Easy to get data back from FL Studio

## Example Commands You Can Send

```python
# Pattern operations
"patterns.jumpToPattern(3)"
"patterns.getPatternName(0)"
"[patterns.getPatternName(i) for i in range(patterns.patternCount())]"

# UI operations
"ui.SetWindow(1)"  # Browser
"ui.SetWindow(3)"  # Piano roll
"ui.showWindow(3)"
"ui.setFocused(3)"

# Channel operations
"channels.selectedChannel()"
"channels.getChannelName(0)"
"[channels.getChannelName(i) for i in range(channels.channelCount())]"

# Mixer operations
"mixer.getTrackCount()"
"mixer.getTrackName(0)"

# Transport operations
"transport.start()"
"transport.stop()"
"transport.getSongPos()"
```