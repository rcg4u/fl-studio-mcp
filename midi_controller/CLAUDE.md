# MIDI Controller for FL Studio

A bidirectional MIDI-based system for controlling FL Studio from external Python using SysEx communication, with MCP (Model Context Protocol) integration for Claude AI automation.

## Current Status

### ✅ Working Components

#### 1. Dual-Controller SysEx System
- **Bidirectional MIDI communication** via IAC Driver (Port 1 & Port 2)
- **FLRequest controller**: Receives commands and executes FL API functions
- **FLResponse controller**: Sends responses back to Python
- **Full FL Studio API access** with `eval()` for direct function calls
- **Python utilities**: `fl_dual_port.py` for request/response handling

#### 2. Pattern Switcher UI
- **GUI application**: `pattern_switcher_ui.py` with tkinter
- **Three pattern buttons**: Melody, Chords, Bass
- **Always-on-top window** that floats above FL Studio
- **One-click switching** with piano roll script execution
- **Keyboard shortcut**: CMD+OPT+Y triggers piano roll script

## Architecture

### Dual-Controller System

#### 1. Hardware Device Scripts (SysEx Communication)
**Purpose:** Bidirectional control of FL Studio via SysEx messages

**Location:** `~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController/`

**Files:**
- `device_FLRequest.py` - Receives commands, executes FL API, dispatches to FLResponse
- `device_FLResponse.py` - Receives dispatch, encodes response, sends SysEx back

**MIDI Ports:**
- **Port 1**: Commands from Python → FLRequest
- **Port 2**: Responses from FLResponse → Python

**Request Format:**
```python
send_command("patterns.jumpToPattern(2)")
send_command("patterns.patternCount()")  # Gets response
```

#### 2. Piano Roll Script (Piano Roll API)
**Purpose:** Note operations in piano roll via ComposeWithLLM script

**Location:** `~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts/`

**Files:**
- `ComposeWithLLM.pyscript` - MCP server integration
- `mcp_request.json` - Request file for piano roll operations
- `piano_roll_state.json` - Current piano roll state

**Trigger:** CMD+OPT+Y keystroke (Run Last Script)

## File Structure

```
midi-controller/
├── CLAUDE.md                  # This file - documentation
├── ARCHITECTURE.md            # System architecture details
├── INSTALL_DUAL_CONTROLLER.md # Setup instructions
├── pyproject.toml            # Dependencies
├── fl_dual_port.py           # Bidirectional MIDI communication
├── pattern_switcher_ui.py    # GUI for pattern switching
├── focus_management.py       # Window focus control
├── piano_roll_utils.py       # Piano roll operations
├── run_ui.sh                 # Convenience script for GUI
│
├── Device Scripts (to be symlinked from fl-studio-mcp):
│   ├── device_FLRequest.py
│   └── device_FLResponse.py
│
FL Studio Locations:
├── ~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController/
│   ├── device_FLRequest.py (symlink → fl-studio-mcp)
│   └── device_FLResponse.py (symlink → fl-studio-mcp)
└── ~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts/
    ├── ComposeWithLLM.pyscript
    ├── mcp_request.json
    └── piano_roll_state.json
```

## Key Components

### 1. fl_dual_port.py
Bidirectional SysEx communication via MIDI:
- `send_command(command_string, expect_response=True)` - Main API call function
- Sends SysEx commands on Port 1
- Listens for SysEx responses on Port 2
- Supports both commands and queries with return values

### 2. pattern_switcher_ui.py
GUI application with:
- Dark-themed tkinter interface
- Three pattern buttons
- Status updates during operations
- Always-on-top window
- Sequence: Activate FL → Switch pattern → Show piano roll → Trigger script

### 3. focus_management.py
macOS window management:
- `activate_fl_studio()` - Brings FL Studio to front
- `save_current_window()` - Saves current app for restoration
- `restore_focus()` - Returns focus to saved app

### 4. piano_roll_utils.py
Piano roll operations:
- `trigger_piano_roll_script()` - Sends CMD+OPT+Y keystroke
- `print_piano_roll_info()` - Reads piano roll state from JSON

## How It Works

1. **Pattern Switching:**
   - UI button clicked → `send_command("patterns.jumpToPattern(N)")`
   - Sends SysEx command on Port 1
   - FLRequest receives and executes command
   - Updates pattern in FL Studio
   - FLResponse sends confirmation (optional)

2. **Query with Response:**
   - Python calls `count = send_command("patterns.patternCount()")`
   - FLRequest executes and returns result
   - FLResponse encodes response as SysEx
   - Python receives and returns parsed value

3. **Piano Roll Script:**
   - After pattern switch, piano roll is shown/focused
   - CMD+OPT+Y sends "Run Last Script" command
   - ComposeWithLLM.pyscript executes
   - Reads mcp_request.json, writes piano_roll_state.json

## Opening Channel Piano Rolls

### Get Event ID and Open Piano Roll

To open the piano roll editor for a specific channel:

**Step 1: Get the channel's event ID**
```python
event_id = send_command("channels.getRecEventId(channel_index)")
```

**Step 2: Open the piano roll editor**
```python
send_command("ui.openEventEditor({event_id}, 1, 1)")
```

### Parameters
- `event_id`: The recEventId for the channel (from `channels.getRecEventId(channel_index)`)
- `mode`: Use `1` for piano roll mode
- `newWindow`: Use `1` for full window with piano keys visible

### Example - Open FLEX Bass Piano Roll

```python
# Get the event ID for channel 4 (FLEX Bass)
event_id = send_command("channels.getRecEventId(4)")  # Returns: 262144

# Open the piano roll editor with full window
send_command("ui.openEventEditor(262144, 1, 1)")
```

### Via MCP Tool (Claude)

```python
call_fl_midi_controller_api("channels.getRecEventId", [4])
# Returns: 262144

call_fl_midi_controller_api("ui.openEventEditor", [262144, 1, 1])
```

### Notes
- Each channel has a unique recEventId
- Mode `1` opens the piano roll (not other event types like volume automation)
- NewWindow `1` gives you the full editor window with piano keys

## Setup

See [INSTALL_DUAL_CONTROLLER.md](INSTALL_DUAL_CONTROLLER.md) for complete setup instructions.

### Quick Setup
1. Create two IAC ports (Port 1 and Port 2) in Audio MIDI Setup
2. Create FLController directory in FL Studio Hardware folder
3. Symlink device scripts from fl-studio-mcp:
   - `device_FLRequest.py` → Port 1
   - `device_FLResponse.py` → Port 2
4. Configure FL Studio MIDI settings for both ports
5. Load both device scripts in FL Studio
6. Test with Python: `send_command("patterns.patternCount()")`

### Running the Pattern Switcher
```bash
# Method 1: Direct
python3 pattern_switcher_ui.py

# Method 2: Convenience script
./run_ui.sh
```

## Dependencies

```toml
dependencies = [
    "mido>=1.3.0",          # MIDI library
    "python-rtmidi>=1.5.0",  # MIDI backend
    "pynput>=1.7.6",         # Keyboard control
]
```

## Future Enhancements

- Response file reading/parsing in device script
- Error handling and validation
- More FL API functions in UI (transport, mixer, etc.)
- Batch requests (multiple operations)
- Custom keyboard shortcuts for piano roll scripts

## State Manager (FLStudioStateManager)

For tracking FL Studio project state (channels, patterns, piano roll notes), use the `FLStudioStateManager` class.

### Usage

```python
from midi_controller.fl_studio_state_manager import FLStudioStateManager

manager = FLStudioStateManager()
manager.start()

# Query methods
channels = manager.get_channels()                           # [{'index': 0, 'name': '808 Kick'}, ...]
patterns = manager.get_patterns()                           # [{'index': 1, 'name': 'Drums'}, ...]
target = manager.get_current_target_channel_and_pattern()   # Current channel/pattern
notes = manager.get_current_piano_roll_notes()              # Current piano roll notes

manager.stop()
```

### Standalone Mode

For testing/debugging without MCP server:

```bash
python3 midi_controller/fl_studio_state_manager.py
> channels    # List all channels
> patterns    # List all patterns
> target      # Show current target
> notes       # Show current piano roll notes
> summary     # Show all state
```

### How It Works

1. **device_FLResponse.py** (FL Studio hardware device) sends events to `fl_events.json`
2. **FLStudioStateManager** monitors the event file in background thread
3. On `target_channel_changed` event:
   - Updates current target
   - Sends CMD+OPT+Y to trigger piano roll script
   - Loads notes from `piano_roll_state.json`
4. Provides query API for getting state

### Files

```
~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController/
├── fl_events.json                 # Event stream (JSONL)
└── project_state.json             # Persisted state

midi_controller/
└── fl_studio_state_manager.py    # State manager class
```

## Integration with fl-studio-mcp

This midi-controller project works with the fl-studio-mcp system:
- **device_FLRequest.py** and **device_FLResponse.py** are sourced from fl-studio-mcp
- Dual-controller system provides bidirectional SysEx communication
- Piano roll operations via ComposeWithLLM.pyscript (also from fl-studio-mcp)
- All can be triggered programmatically from Python or MCP clients
- Full FL Studio API access for AI automation via Claude

## Troubleshooting

### Commands Not Executing
- Check both device scripts are loaded (Script output window)
- Verify IAC ports (Port 1 & Port 2) exist and are enabled
- Reload scripts: Script output → Reload

### No Response Received
- Ensure `expect_response=True` in send_command()
- Check FLResponse script is loaded
- Verify Port 2 is enabled in MIDI settings

### Python Connection Issues
- Verify IAC Driver is online (Audio MIDI Setup)
- Check port numbers match: Port 1 (commands), Port 2 (responses)
- Install python-rtmidi: `pip install python-rtmidi`

### Piano Roll Script Not Triggering
- Make sure piano roll window has focus
- ComposeWithLLM must be the last run script
- Check mcp_request.json exists and is valid

### GUI Not Showing (Black Window)
- Use system Python: `/usr/bin/python3 pattern_switcher_ui.py`
- Or use: `./run_ui.sh`

### Symlinks Need Reinstalling
```bash
# After device scripts are available in fl-studio-mcp
ln -s /path/to/fl-studio-mcp/device_FLRequest.py ~/Documents/Image-Line/FL\ Studio/Settings/Hardware/FLController/device_FLRequest.py
ln -s /path/to/fl-studio-mcp/device_FLResponse.py ~/Documents/Image-Line/FL\ Studio/Settings/Hardware/FLController/device_FLResponse.py
```

## Key Design Decisions

1. **Dual-Controller SysEx** - Native MIDI communication, truly bidirectional, works reliably on macOS
2. **Python eval() for commands** - Direct API access without wrapper layer or encoding complexity
3. **Two parallel systems** - Device scripts for general API, piano roll scripts for note operations
4. **Modular utilities** - Separate files for different concerns (dual port, focus, piano roll)
5. **GUI with always-on-top** - Convenient access while working in FL Studio
6. **CMD+OPT+Y for piano roll** - Reliable built-in shortcut mechanism
7. **No file I/O** - Faster, cleaner, prevents race conditions