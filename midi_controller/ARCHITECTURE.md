# MIDI Controller Architecture

A bidirectional MIDI-based system for controlling FL Studio from external Python, with MCP (Model Context Protocol) integration for Claude AI automation.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Claude (MCP)                          │
│  Calls MCP functions to automate FL Studio workflows        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ MCP calls
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (future)                       │
│  Translates Claude requests to FL Studio function calls     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ send_command()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    fl_dual_port.py                           │
│  Bidirectional SysEx communication over MIDI                │
├─────────────────────┬───────────────────────────────────────┤
│       Port 1        │            Port 2                     │
│  (Python → FL)      │       (FL → Python)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
┌──────────┐    ┌──────────┐    ┌──────────────┐
│   IAC    │    │   IAC    │    │ Audio MIDI   │
│ Request  │    │ Response │    │   Setup      │
│  Port    │    │  Port    │    │              │
└────┬─────┘    └────┬─────┘    └──────────────┘
     │               │
     │               │
     └───────┬───────┘
             │
      ┌──────▼──────────────────────────────────────┐
      │         FL Studio (Hardware Device)         │
      ├──────────────────────────────────────────────┤
      │  FLRequest (device_FLRequest.py)            │
      │  - Receives SysEx commands                  │
      │  - Executes FL API functions               │
      │  - Dispatches to FLResponse                │
      │                                              │
      │  FLResponse (device_FLResponse.py)          │
      │  - Receives dispatch from FLRequest        │
      │  - Sends SysEx responses back to Python   │
      └──────────────────────────────────────────────┘
```

## Current Architecture (Dual-Controller System)

### Components

#### 1. Python Side (fl_dual_port.py)
- **Primary API**: `send_command(command_string, expect_response=True/False)`
- Sends SysEx commands to FL Studio via IAC Driver
- Listens for SysEx responses
- Parses responses and returns data to caller

#### 2. FL Studio Hardware Device Scripts

**FLRequest (device_FLRequest.py)**
- Listens on Port 1
- Receives SysEx messages from Python
- Parses command string
- Executes command using `eval()` on FL API
- Returns result to FLResponse via `device.dispatch()`

**FLResponse (device_FLResponse.py)**
- Special header: `# receiveFrom=FLRequest`
- Receives dispatched results from FLRequest
- Encodes response as SysEx
- Sends back to Python on Port 2

#### 3. MIDI Setup
- **Port 1**: IAC Driver → Commands from Python to FLRequest
- **Port 2**: IAC Driver → Responses from FLResponse to Python

## Available FL API Functions

All FL Studio API functions are available. Common ones:

### Patterns
```python
patterns.jumpToPattern(index)           # Select pattern by index
patterns.getPatternName(index)          # Get pattern name
patterns.patternCount()                 # Get total pattern count
patterns.selectPattern(index, wait=True)# Select with optional wait
```

### Channels
```python
channels.selectedChannel()              # Get current channel
channels.getChannelName(index)          # Get channel name
channels.channelCount()                 # Get total channel count
channels.midiPort()                     # Get MIDI port for channel
```

### Mixer
```python
mixer.getTrackCount()                   # Get mixer track count
mixer.getTrackName(index)               # Get track name
mixer.getSolo(index)                    # Get solo state
mixer.setSolo(index, value)             # Set solo state
```

### UI
```python
ui.showWindow(window_id)                # Show window (1=browser, 3=piano roll)
ui.setFocused(window_id)                # Focus window
```

### Transport
```python
transport.start()                       # Play
transport.stop()                        # Stop
transport.pause()                       # Pause
transport.getSongPos()                  # Get current position
transport.setSongPos(pos)               # Set position
```

### Piano Roll (ComposeWithLLM.pyscript)
```python
# Triggered via CMD+OPT+Y keystroke
# Uses mcp_request.json for input
# Writes piano_roll_state.json for output
```

## Request Format

### Simple Command
```python
send_command("patterns.jumpToPattern(2)")
# Returns: None (no response expected)
```

### Query with Response
```python
count = send_command("patterns.patternCount()")
# Returns: 5
```

### Complex Operations
```python
names = send_command("[patterns.getPatternName(i) for i in range(patterns.patternCount())]")
# Returns: ["Pattern 0", "Pattern 1", "Pattern 2", ...]
```

### Multiple Operations
```python
send_command("patterns.jumpToPattern(2); ui.showWindow(3); ui.setFocused(3)")
# Returns: None
```

## MCP Integration (Planned)

The system will be exposed as an MCP server allowing Claude to:

1. **Call FL API functions directly**
   ```
   Tool: execute_fl_function
   Input: "patterns.jumpToPattern(3)"
   Output: Result from FL Studio
   ```

2. **Describe available functions**
   ```
   Tool: list_fl_functions
   Input: (optional category filter)
   Output: Available functions with descriptions
   ```

3. **Automate workflows**
   ```
   Tool: run_fl_workflow
   Input: List of commands to execute in sequence
   Output: Results array
   ```

## Event System & State Manager

For tracking project state (channels, patterns, piano rolls), we use an event-driven architecture:

### Components

**FLStudioStateManager** (`fl_studio_state_manager.py`)
- Monitors `fl_events.json` for events from FL Studio
- Tracks channels, patterns, current target, and piano roll notes
- Provides 4-method query API
- Can run standalone or imported by MCP server

**Event Source** (`device_FLResponse.py`)
- Sends events when project loads or piano roll focus changes
- Writes to `fl_events.json` (JSONL format)

### Events

| Event | When Sent | Data |
|-------|-----------|------|
| `project_loaded` | Project loads | All channels and patterns |
| `target_channel_changed` | Piano roll focus/channel change | Current channel, pattern, triggers note refresh |

### Query API

```python
from midi_controller.fl_studio_state_manager import FLStudioStateManager

manager = FLStudioStateManager()
manager.start()

channels = manager.get_channels()
patterns = manager.get_patterns()
target = manager.get_current_target_channel_and_pattern()
notes = manager.get_current_piano_roll_notes()
```

### Integration with Dual-Controller System

The event system complements the dual-controller SysEx system:

| System | Purpose | Communication |
|--------|---------|---------------|
| **Dual-Controller** (FLRequest/FLResponse) | Direct API calls, commands | MIDI SysEx (bidirectional) |
| **Event System** (FLStudioStateManager) | State tracking, queries | JSONL file events |

Both systems can be used together:
- Use SysEx for immediate actions (switch patterns, get info)
- Use event system for state queries (what channels exist, current notes)

### Event System File Locations

```
~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController/
├── fl_events.json                 # Event stream (JSONL)
└── project_state.json             # Persisted state

midi_controller/
└── fl_studio_state_manager.py    # State manager class
```

## File Locations

### Root Directory Files
- `fl_dual_port.py` - Main bidirectional MIDI communication
- `pattern_switcher_ui.py` - GUI for manual pattern switching
- `focus_management.py` - macOS window management
- `piano_roll_utils.py` - Piano roll script triggering

### FL Studio Locations (Symlinked)
```
~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController/
├── device_FLRequest.py      (symlink → project)
├── device_FLResponse.py     (symlink → project)
├── request.json             (legacy, not used)
└── response.json            (legacy, not used)

~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts/
├── ComposeWithLLM.pyscript  (MCP integration)
├── mcp_request.json         (input)
└── piano_roll_state.json    (output)
```

## Setup

See [INSTALL_DUAL_CONTROLLER.md](INSTALL_DUAL_CONTROLLER.md) for complete setup instructions.

### Quick Setup
1. Create two IAC ports (Port 1 and Port 2)
2. Symlink device scripts into FL Studio Hardware folder (FLController)
3. Configure FL Studio MIDI settings
4. Load both device scripts in FL Studio
5. Test with `test_dual_port.py`

## Key Features

✅ **Bidirectional Communication** - Get data back from FL Studio
✅ **No File I/O** - Direct MIDI communication, no race conditions
✅ **Full API Access** - Call any FL Studio Python API function
✅ **Error Handling** - Exceptions properly propagated back to Python
✅ **Async-Friendly** - Non-blocking command execution
✅ **MCP-Ready** - Designed for AI automation via Model Context Protocol

## Workflow Examples

### Pattern Switching
```python
from fl_dual_port import send_command

# Get available patterns
names = send_command("[patterns.getPatternName(i) for i in range(patterns.patternCount())]")
print(f"Available patterns: {names}")

# Switch to a pattern
send_command("patterns.jumpToPattern(1)")

# Show and focus piano roll
send_command("ui.showWindow(3); ui.setFocused(3)")
```

### Piano Roll Script Triggering
```python
from piano_roll_utils import trigger_piano_roll_script
from focus_management import activate_fl_studio

activate_fl_studio()
send_command("patterns.jumpToPattern(2)")
send_command("ui.showWindow(3); ui.setFocused(3)")
trigger_piano_roll_script()  # Sends CMD+OPT+Y
```

### Claude AI Automation (Future MCP)
```
Claude: "Switch to the bass pattern and show me the piano roll"
→ MCP calls send_command("patterns.jumpToPattern(0)")
→ MCP calls send_command("ui.showWindow(3); ui.setFocused(3)")
→ MCP calls trigger_piano_roll_script()
→ Claude receives piano_roll_state.json results
```

## Troubleshooting

### Commands Not Executing
1. Check both device scripts are loaded (Script output window)
2. Verify IAC ports exist and are enabled
3. Reload scripts: Script output → Reload

### No Response Received
1. Ensure `expect_response=True` is set
2. Check FLResponse script is loaded
3. Verify Port 2 is enabled in MIDI settings

### Python Connection Issues
1. Verify IAC Driver is online (Audio MIDI Setup)
2. Check port numbers match: Port 1 (commands), Port 2 (responses)
3. Install python-rtmidi: `pip install python-rtmidi`

## Design Decisions

1. **Dual Controllers** - Better separation of concerns than single controller
2. **SysEx Communication** - Native MIDI, works reliably on macOS
3. **Python eval()** - Direct API access, no wrapper layer needed
4. **No Files** - Faster, cleaner, no race conditions
5. **MCP Integration** - Claude can now automate FL Studio workflows
