# MIDI Controller Plan

## Architecture Overview

A file-based system for controlling FL Studio from external Python using request/response JSON files and MIDI triggers.

## System Components

### 1. External Python Scripts (midi-controller/)
- Send commands to FL Studio by writing JSON request files
- Trigger FL Studio to process requests via MIDI messages
- Read JSON response files for results

### 2. FL Studio Device Scripts
- **device_simple_request.py** - Hardware device script
  - Triggered by MIDI messages (OnMidiIn)
  - Reads request.json
  - Executes FL Studio API calls
  - Writes response.json

### 3. Piano Roll Scripts (existing)
- **ComposeWithLLM.pyscript** - Piano roll script
  - Triggered by Cmd+Opt+Y or menu selection
  - Reads mcp_request.json
  - Executes flpianoroll API calls
  - Already implemented in fl-studio-mcp

## Request/Response Format

### General FL API Requests (request.json)
```json
{
  "function": "patterns.selectPattern",
  "args": [2, 1]
}
```

### Response Format (response.json)
```json
{
  "status": "success",
  "result": "Selected pattern 2"
}
```

## Supported APIs

### Hardware Device Script
- **patterns** - Pattern operations (select, get names, etc.)
- **channels** - Channel rack operations
- **mixer** - Mixer operations
- **transport** - Playback control (play, stop, record)
- **ui** - User interface navigation
- **playlist** - Playlist operations

### Piano Roll Script (existing)
- **flpianoroll** - Piano roll note operations
- Uses action-based format in mcp_request.json

## Trigger Mechanisms

### MIDI Triggered (Hardware Device)
1. Python writes request.json
2. Python sends MIDI Note On message to IAC Driver Bus 1
3. FL Studio routes MIDI to "Simple Controller" device
4. device_simple_request.py OnMidiIn() fires
5. Script reads request.json, executes function, writes response.json
6. Python reads response.json

### Keystroke Triggered (Piano Roll)
1. Python/MCP writes mcp_request.json
2. Python sends Cmd+Opt+Y keystroke
3. FL Studio runs last piano roll script (ComposeWithLLM.pyscript)
4. Script reads mcp_request.json, executes actions
5. Script exports piano_roll_state.json

## File Locations

### Request/Response Files
- **request.json** - `~/Documents/Image-Line/FL Studio/Settings/Hardware/SimpleController/request.json`
- **response.json** - `~/Documents/Image-Line/FL Studio/Settings/Hardware/SimpleController/response.json`
- **mcp_request.json** - `~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts/mcp_request.json`
- **piano_roll_state.json** - `~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts/piano_roll_state.json`

### Scripts
- **device_simple.py** - `~/Documents/Image-Line/FL Studio/Settings/Hardware/SimpleController/device_simple.py` (symlinked)
- **ComposeWithLLM.pyscript** - `~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts/ComposeWithLLM.pyscript`

## Example Usage

### Select Pattern by Name
```python
import json
import mido
import time

# Write request
request = {
    "function": "select_pattern_by_name",
    "args": ["bass"]
}
with open(request_file, 'w') as f:
    json.dump(request, f)

# Trigger via MIDI
port = mido.open_output('IAC Driver Bus 1')
port.send(mido.Message('note_on', note=1, velocity=100))
port.close()

# Wait and read response
time.sleep(0.5)
with open(response_file, 'r') as f:
    response = json.load(f)
print(response['result'])  # "Selected pattern: bass"
```

### Get Pattern Names
```python
request = {
    "function": "get_pattern_names",
    "args": []
}
# ... same trigger process ...
# response['result'] = ["Pattern 0", "bass", "chords", "pads", "melody"]
```

### Cycle Through Patterns
```python
patterns = ['bass', 'melody']
for pattern in patterns:
    select_pattern(pattern)
    trigger_piano_roll_script()  # Cmd+Opt+Y
    time.sleep(5)
```

## Benefits

1. **Simple** - Just JSON files, no complex MIDI SysEx encoding
2. **Debuggable** - Easy to inspect request/response files
3. **Flexible** - Can call any FL Studio API function
4. **Integrated** - Works with existing MCP piano roll system
5. **Lightweight** - No dependencies beyond mido and pynput

## Future Enhancements

- Add error handling and validation
- Support batch requests (list of function calls)
- Add response timeouts
- Create helper library for common operations
- Unified API for both hardware and piano roll scripts
