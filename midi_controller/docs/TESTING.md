# Testing the Request/Response System

## Setup

### 1. Install the FL Studio Device Script

Create a symlink so FL Studio can find the new request handler:

```bash
# Remove old symlink if it exists
rm ~/Documents/Image-Line/FL\ Studio/Settings/Hardware/SimpleController/device_simple.py

# Create symlink for the new request handler
ln -s /Users/calvinw/develop/midi-controller/device_simple_request.py ~/Documents/Image-Line/FL\ Studio/Settings/Hardware/SimpleController/device_simple_request.py
```

### 2. Configure FL Studio

1. Open FL Studio
2. Go to **Options → MIDI Settings**
3. Find **IAC Driver Bus 1** in the input list
4. Set **Controller type** to **Simple Request Controller**
5. Click **Accept**

### 3. Verify Script Loaded

1. Go to **VIEW → Script output**
2. You should see: `Simple Request Controller initialized`
3. Check the request file path is correct

## Running the Test

### Prerequisites

- FL Studio must be open
- IAC Driver Bus 1 must be enabled (Audio MIDI Setup)
- You need a pattern named "Bass" (or modify the test script index)
- ComposeWithLLM.pyscript should be the last run piano roll script

### Run the Test

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the test
python test_bass_pattern.py
```

### Expected Output

```
============================================================
Test: Select Bass Pattern + Trigger Piano Roll Script
============================================================

[1] Writing request to select 'Bass' pattern...
✓ Wrote request: {"function": "patterns.jumpToPattern", "args": [0]}
  to ~/Documents/.../request.json

[2] Sending MIDI trigger to FL Studio...
✓ Sent MIDI trigger: note_on channel=0 note=1 velocity=100

[3] Waiting for FL Studio to process request...

[4] Activating piano roll window...
✓ Sent F7 to activate piano roll

[5] Triggering piano roll script...
✓ Sent CMD+OPT+Y keystroke

============================================================
✓ Test complete!
============================================================
```

### In FL Studio

Check the **Script output** window:
- You should see the MIDI trigger received
- The request should be logged
- The function execution should be logged
- The Bass pattern should be selected

## Debugging

### Script not triggering

1. Check MIDI settings - IAC Driver Bus 1 enabled?
2. Check controller type selected correctly
3. Reload script: **Script output → Reload**

### Pattern not found

1. Check your pattern index
2. Pattern 0 is usually the first pattern
3. You can list patterns with `device_debug.py`

### Request file not found

1. Check the path in Script output window
2. Verify directory exists
3. Check symlink is correct

### Keyboard shortcuts not working

1. Make sure FL Studio has focus
2. F7 should open piano roll
3. CMD+OPT+Y should run last script
4. Check System Preferences → Keyboard → Shortcuts for conflicts

## Next Steps

Once this works:
1. Implement pattern selection by name
2. Add response.json writing
3. Add response.json reading in Python
4. Create helper library for common operations
5. Test pattern cycling with piano roll operations
