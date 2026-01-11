# FL Studio MCP - Developer Guide

This guide explains the internal architecture, communication systems, and how to extend the FL Studio MCP project.

## Architecture Overview

The system consists of three main layers:

### Layer 1: Claude / MCP Client
- User interacts with Claude through conversation
- Claude has access to 13 MCP tools
- Tools are exposed via the MCP server

### Layer 2: Python Backend
- **MCP Server** (`mcp/fl_studio_mcp_server.py`) - Exposes tools to Claude
- **FLStudioStateManager** (`midi_controller/fl_studio_state_manager.py`) - Manages state and coordination
- **MIDI Communication** (`midi_controller/fl_dual_port.py`) - Bidirectional SysEx system

### Layer 3: FL Studio (DAW)
- **Hardware Device Scripts** - Receive commands and send events
- **Piano Roll Script** - Processes note requests
- **Event System** - Broadcasts state changes

## Data Flow

```
User (Claude) ─► MCP Server ─► StateManager ┬─► Request Queue (JSON)
                                             │    ↓
                                             │    FL Studio Script
                                             │    ↓
                                             └─► Piano Roll Updates

                                             └─► Event Monitor
                                                 ↓ fl_events.json
                                                 ↓ SysEx Queries
                                                 ↓ State Updates
```

## Component Details

### 1. MCP Server (`mcp/fl_studio_mcp_server.py`)

Entry point that exposes 13 tools to Claude.

**Structure:**
```python
class FLStudioMCPServer:
    def __init__(self):
        self.state_manager = FLStudioStateManager()

    # Tool implementations delegate to state_manager
    async def send_notes(self, notes, mode):
        return await self.state_manager.send_notes(notes, mode)

    async def get_project_channels(self):
        return await self.state_manager.get_channels()

    # ... 11 more tools
```

**Key Points:**
- Tools are async (to handle I/O operations)
- All tools ultimately delegate to `FLStudioStateManager`
- The MCP server doesn't directly interact with FL Studio
- Everything goes through StateManager

**Tools exposed:**
1. `send_notes` - Queue notes to piano roll
2. `delete_notes` - Remove specific notes
3. `clear_piano_roll` - Clear all notes
4. `get_project_channels` - Query channels
5. `get_project_patterns` - Query patterns
6. `get_current_target` - Get current channel/pattern
7. `get_current_piano_roll_notes` - Get current notes
8. `get_pattern_notes` - Get notes from pattern
9. `get_all_pattern_notes` - Get all patterns' notes
10. `show_piano_roll` - Open piano roll for channel
11. `select_pattern` - Switch to pattern
12. `reload` - Manual refresh
13. `call_fl_midi_controller_api` - Direct API access

### 2. FLStudioStateManager (`midi_controller/fl_studio_state_manager.py`)

Core coordinator that manages state, triggers FL Studio, and monitors events.

**Architecture:**
```
FLStudioStateManager
├── Event Monitor (Background Thread)
│   ├── Reads fl_events.json (JSONL)
│   ├── Detects project_loaded events
│   ├── Detects target_channel_changed events
│   └── Updates internal state
├── MIDI Communication (fl_dual_port.py)
│   ├── Sends SysEx queries to FL Studio
│   ├── Receives SysEx responses
│   └── Queries channels, patterns, notes
├── Request Queue Manager
│   ├── Queues requests to mcp_request.json
│   ├── Triggers FL Studio (CMD+OPT+Y)
│   └── Monitors responses
└── State Storage
    ├── In-memory state cache
    ├── Persistent project_state.json
    └── Piano roll snapshots
```

**Main Methods:**

```python
# Piano roll operations
async send_notes(notes, mode="add")
async delete_notes(notes)
async clear_piano_roll()

# State queries
async get_channels()
async get_patterns()
async get_current_target()
async get_current_piano_roll_notes()
async get_pattern_notes(pattern_id)
async get_all_pattern_notes()

# Navigation
async show_piano_roll(channel_id)
async select_pattern(pattern_id)
async reload()

# Low-level API
async call_fl_midi_controller_api(method, args, kwargs)

# Internal methods
_trigger_fl_studio()  # Sends CMD+OPT+Y keystroke
_queue_request(request)  # Adds to mcp_request.json
_monitor_events()  # Background thread monitoring fl_events.json
```

**State Tracking:**
- Maintains current channel and pattern from events
- Caches channels and patterns from last query
- Tracks piano roll state from piano_roll_state.json
- Monitors fl_events.json for changes (background thread)

**Event-Based Architecture:**
```
FL Studio (device_FLResponse.py)
    ↓ sends events
fl_events.json (JSONL format)
    ↓ monitored by background thread
StateManager._monitor_events()
    ↓ updates internal state
State available to query tools
```

### 3. MIDI Communication (`midi_controller/fl_dual_port.py`)

Bidirectional SysEx communication with FL Studio via two IAC ports.

**Architecture:**
```
Python Process (MCP Server)
    ↓
Port 1: FLRequest (outgoing commands)
    ↓ SysEx with header 7D 11 00
    ↓
FL Studio (device_FLRequest.py)
    ↓ processes command
    ↓ returns result via dispatch
    ↓
Port 2: FLResponse (incoming responses)
    ↓ SysEx with header 7D 11 10 (success) or 7D 11 20 (error)
    ↓
Port 2 Receiver
    ↓
Result returned to StateManager
```

**How It Works:**

1. **Outgoing (Python → FL Studio):**
   - StateManager calls `dual_port.send_command()`
   - Command encoded as SysEx with header `7D 11 00`
   - Sent on IAC Port 1
   - FL Studio's device_FLRequest.py receives it

2. **Processing (FL Studio):**
   - device_FLRequest.py decodes SysEx
   - Extracts command (e.g., "channels.channelCount")
   - Executes via `eval(command_string)`
   - Gets result

3. **Returning (FL Studio → Python):**
   - device_FLRequest.py dispatches result
   - device_FLResponse.py receives dispatch
   - Sends result as SysEx on Port 2 with header `7D 11 10`

4. **Receiving (Python):**
   - dual_port.py listens on Port 2
   - Decodes SysEx response
   - Returns result to StateManager

**Important Notes:**
- Dual ports prevent MIDI loopback issues
- SysEx is used because it's MIDI-safe (0x7D is universal NRPN)
- eval() in device_FLRequest.py is intentional - allows any FL Studio API call
- 2-second timeout for response waiting

### 4. Hardware Device Scripts

**device_FLRequest.py** - Receives commands from Python:
```python
def OnMidiIn(event):
    # Receives SysEx on Port 1
    # Decodes: method, args, kwargs
    # Executes: eval(method)(*args, **kwargs)
    # Dispatches result via device.dispatch()
```

**device_FLResponse.py** - Sends events to Python:
```python
def OnProjectLoad(status):
    # Project loaded
    # Query all channels and patterns
    # Send project_loaded event to fl_events.json

def OnRefresh(flags):
    # Window focus changed
    # Detect if piano roll gained focus
    # Trigger piano roll refresh

def OnIdle():
    # Periodic polling
    # Check if piano roll focus changed
    # Send target_channel_changed event

def OnDirtyChannel(index, flag):
    # Channel was modified
    # Useful for detecting channel changes
```

### 5. Piano Roll Script (`piano_roll/BeginLLMInteraction.pyscript`)

Triggered by CMD+OPT+Y keystroke, processes requests.

**Flow:**
```
1. Read mcp_request.json
2. For each request:
   - If action="add_notes": Create notes and add to piano roll
   - If action="delete_notes": Find and delete notes
   - If action="clear": Clear all notes
3. Export updated piano roll state to piano_roll_state.json
4. Clear request queue (set to [])
5. Write result to mcp_response.json
```

**Note Creation:**
```python
for note_data in request["notes"]:
    midi = note_data["midi"]
    duration = note_data["duration"]  # in quarter notes
    time = note_data["time"]  # in quarter notes
    velocity = note_data.get("velocity", 0.8)

    # Convert to ticks: ticks = quarter_notes * PPQ
    ticks = int(time * flp.score.ppq)
    length = int(duration * flp.score.ppq)

    # Create and add note
    note = flp.Note(time=ticks, length=length, number=midi)
    note.velocity = int(velocity * 255)
    flp.score.addNote(note)
```

## File Organization

### Source Files

```
fl-studio-mcp/
├── mcp/
│   ├── fl_studio_mcp_server.py          # MCP server (13 tools)
│   └── install_mcp_for_claude.sh        # Installation script
├── midi_controller/
│   ├── fl_studio_state_manager.py       # State management & coordination
│   ├── fl_dual_port.py                  # Bidirectional MIDI/SysEx
│   ├── focus_management.py              # Window focus handling
│   ├── device_FLRequest.py              # Hardware device: command handler
│   └── device_FLResponse.py             # Hardware device: event broadcaster
├── piano_roll/
│   └── BeginLLMInteraction.pyscript     # Piano roll script
├── install_prerequisites.sh             # Setup script
├── README.md                            # User guide
├── CLAUDE.md                            # AI assistant guide
└── DEVELOPER.md                         # This file
```

### FL Studio Installation Directories

```
~/Documents/Image-Line/FL Studio/Settings/
├── Hardware/FLController/
│   ├── device_FLRequest.py              # symlink → source
│   ├── device_FLResponse.py             # symlink → source
│   ├── fl_events.json                   # Event stream (JSONL)
│   └── project_state.json               # Persisted state
└── Piano roll scripts/
    ├── BeginLLMInteraction.pyscript     # Copy → source
    ├── mcp_request.json                 # Request queue
    ├── mcp_response.json                # Execution results
    └── piano_roll_state.json            # Piano roll snapshot
```

## Communication Protocols

### JSON Request Queue (mcp_request.json)

Array of action objects processed sequentially:

```json
[
  {
    "action": "add_notes",
    "notes": [
      {"midi": 60, "duration": 4, "time": 0, "velocity": 0.8}
    ]
  },
  {
    "action": "delete_notes",
    "notes": [
      {"midi": 67, "time": 4}
    ]
  },
  {
    "action": "clear"
  }
]
```

**Action Types:**
- `add_notes` - Add notes to piano roll
- `delete_notes` - Delete specific notes
- `clear` - Clear all notes

### JSONL Event Stream (fl_events.json)

Each line is a complete JSON object (JSONL format):

```jsonl
{"event": "project_loaded", "channels": [...], "patterns": [...]}
{"event": "target_channel_changed", "channel_index": 0, "channel_name": "Kick", "pattern_index": 1, "pattern_name": "Drums"}
{"event": "target_channel_changed", "channel_index": 2, "channel_name": "Chords", "pattern_index": 1, "pattern_name": "Drums"}
```

**Event Types:**
- `project_loaded` - Project fully loaded
  - Data: channels array, patterns array
  - Triggers: Full state discovery
- `target_channel_changed` - Piano roll focus changed
  - Data: channel_index, channel_name, pattern_index, pattern_name
  - Triggers: Piano roll state refresh

### SysEx Command Format

**Request (Python → FL Studio):**
```
F0                    # SysEx start
7D 11 00              # Header (universal, FLRequest marker)
[command_bytes]       # Command encoded
F7                    # SysEx end
```

**Response (FL Studio → Python):**
```
F0                    # SysEx start
7D 11 10              # Header + success flag
[result_bytes]        # Result encoded
F7                    # SysEx end

OR

F0                    # SysEx start
7D 11 20              # Header + error flag
[error_bytes]         # Error message
F7                    # SysEx end
```

## Execution Flow Examples

### Example 1: Send Notes

```
User: "Add a C major chord"
    ↓
Claude: calls send_notes([
    {"midi": 60, "duration": 4, "time": 0},
    {"midi": 64, "duration": 4, "time": 0},
    {"midi": 67, "duration": 4, "time": 0}
])
    ↓
MCP Server: send_notes() → StateManager.send_notes()
    ↓
StateManager.send_notes():
  1. Create request object
  2. Queue to mcp_request.json
  3. Call _trigger_fl_studio()
  4. _trigger_fl_studio():
     - Save current window focus
     - Activate FL Studio
     - Send CMD+OPT+Y keystroke via pynput
     - Wait 2 seconds (auto-trigger delay)
     - Restore previous window focus
    ↓
FL Studio: detects CMD+OPT+Y
  1. Runs BeginLLMInteraction.pyscript
  2. Reads mcp_request.json
  3. Creates 3 note objects
  4. Adds to flp.score
  5. Exports state to piano_roll_state.json
  6. Clears request queue
    ↓
Piano Roll: C major chord appears on screen
    ↓
StateManager: Reads piano_roll_state.json
    ↓
Claude: Returns "Notes added successfully"
```

### Example 2: Query Channels

```
User: "What channels do I have?"
    ↓
Claude: calls get_project_channels()
    ↓
MCP Server: get_project_channels() → StateManager.get_channels()
    ↓
StateManager.get_channels():
  1. Check if channels cached recently
  2. If not cached, query via SysEx
  3. Send SysEx: "channels.channelCount"
  4. Receive response: 8
  5. Loop 0-7, send SysEx: "channels.getChannelName(i)"
  6. Receive responses: ["Kick", "Snare", "Chords", ...]
  7. Return: [{"index": 0, "name": "Kick"}, ...]
    ↓
MCP Server: return JSON string
    ↓
Claude: parses JSON, returns to user
    ↓
User sees: "You have 8 channels: Kick, Snare, Chords, ..."
```

### Example 3: Monitor Events

```
Background: StateManager._monitor_events() (background thread)
  1. Poll fl_events.json every 100ms
  2. Read new lines (JSONL format)
  3. Parse events
  4. If "project_loaded":
     - Extract channels and patterns
     - Update internal cache
  5. If "target_channel_changed":
     - Update current_target
     - Trigger piano_roll_state refresh
  6. Continue polling
    ↓
When user switches channels in FL Studio:
  1. device_FLResponse detects focus change
  2. Appends to fl_events.json:
     {"event": "target_channel_changed", ...}
    ↓
StateManager._monitor_events():
  1. Detects new event
  2. Updates current_target
  3. State is ready for queries
    ↓
Claude: calls get_current_target()
    ↓
StateManager: returns updated target
    ↓
Claude: sees the new channel
```

## Key Design Decisions

### 1. Why Dual IAC Ports?
- Port 1 (request): Avoids MIDI loopback
- Port 2 (response): Cleaner separation of concerns
- Prevents command echoes interfering with responses

### 2. Why eval() in device_FLRequest?
- Provides unlimited access to FL Studio API
- Flexible for advanced use cases
- Requires trust (sandboxed to local Python only)
- Alternative: Whitelist specific methods (future improvement)

### 3. Why Event-Based Monitoring?
- More efficient than polling
- FL Studio actively sends notifications
- StateManager can react immediately
- Scales better than periodic queries

### 4. Why JSONL for Events?
- Append-only format (no file locking issues)
- Each event is independent
- Easy to monitor for changes
- Handles streaming naturally

### 5. Why Background Thread for Event Monitoring?
- Non-blocking state updates
- Responsive to FL Studio changes
- Doesn't slow down command processing
- Clean separation of concerns

## Extension Points

### Adding a New MCP Tool

1. **Add method to FLStudioStateManager:**
```python
async def my_new_tool(self, param1, param2):
    # Implementation
    return result
```

2. **Add tool to MCP server:**
```python
@server.call_tool()
async def handle_my_new_tool(param1, param2):
    result = await self.state_manager.my_new_tool(param1, param2)
    return {"result": result}
```

3. **Test with Claude:**
```
Claude: calls mcp__fl_studio_mcp__my_new_tool(...)
```

### Adding a New SysEx Command

1. **Add handler to device_FLRequest.py:**
```python
def OnMidiIn(event):
    # Extract command from SysEx
    # Command format: "method_name:arg1,arg2"
    # Execute via eval()
```

2. **Add query method to StateManager:**
```python
async def _query_fl_studio(self, method_name, args):
    # Use fl_dual_port to send SysEx
    # Wait for response
    # Return result
```

### Adding a New Event Type

1. **Send event from FL Studio:**
```python
# device_FLResponse.py
def OnSomeEvent(data):
    event = {
        "event": "my_event",
        "data": data
    }
    append_to_events_file(event)
```

2. **Handle event in StateManager:**
```python
def _monitor_events(self):
    if event["event"] == "my_event":
        # Update state
        # Trigger actions
```

## Debugging

### Enable Debug Logging

Set environment variable:
```bash
export FL_STUDIO_MCP_DEBUG=1
```

StateManager will output:
- All state queries
- All requests sent
- All events received
- Timing information

### Monitor Files Directly

Watch JSON files in real-time:
```bash
# Terminal 1
tail -f ~/Documents/Image-Line/FL\ Studio/Settings/Hardware/FLController/fl_events.json

# Terminal 2
tail -f ~/Documents/Image-Line/FL\ Studio/Settings/Piano\ roll\ scripts/mcp_request.json

# Terminal 3
tail -f ~/Documents/Image-Line/FL\ Studio/Settings/Piano\ roll\ scripts/piano_roll_state.json
```

### Test StateManager Standalone

StateManager can run independently for testing:
```bash
cd midi_controller
python -i fl_studio_state_manager.py

# Then in Python REPL:
>>> state_manager = FLStudioStateManager()
>>> channels = state_manager.get_channels()
>>> print(channels)
```

Includes CLI interface:
```bash
python fl_studio_state_manager.py channels
python fl_studio_state_manager.py patterns
python fl_studio_state_manager.py target
python fl_studio_state_manager.py notes
python fl_studio_state_manager.py all
```

### Common Issues

**SysEx not being received:**
- Check IAC ports exist: Audio MIDI Setup → IAC Driver
- Verify device_FLRequest.py is in Hardware/FLController/
- Check FL Studio version supports hardware devices
- Watch fl_events.json for any error events

**Events not being detected:**
- Check fl_events.json is being written to
- Verify StateManager is reading the correct file path
- Watch for JSONL parse errors
- Check file permissions

**Triggers not working:**
- Verify pynput is installed: `uv sync`
- Check Accessibility permissions for Terminal/Claude Code
- Try pressing CMD+OPT+Y manually to test FL Studio script
- Watch for keystroke timing issues

## Performance Notes

### Optimization Tips

1. **Cache queries:**
   - Channels/patterns don't change frequently
   - Cache results with timestamp
   - Invalidate on events

2. **Batch operations:**
   - Multiple note requests queue together
   - Processed in single FL Studio trigger
   - More efficient than individual requests

3. **Event monitoring:**
   - 100ms polling interval is reasonable
   - Can reduce if more responsiveness needed
   - Monitor CPU usage if reducing interval

4. **SysEx timeouts:**
   - 2 seconds is conservative
   - Reduce to 1 second for faster response
   - Increase if FL Studio is slow on your machine

### Scalability

- Tested with 100+ notes in piano roll
- Tested with 50+ channels
- Tested with 100+ patterns
- Dual-port architecture scales well
- Event monitoring doesn't scale with project size

## Testing Strategy

### Unit Tests
```python
# Test StateManager independently
def test_send_notes():
    sm = FLStudioStateManager()
    sm.send_notes([...])
    assert mcp_request.json contains request
```

### Integration Tests
```python
# Test full flow with FL Studio running
def test_end_to_end():
    # Send notes via Claude
    # Wait for trigger
    # Verify notes appear in FL Studio
    # Verify event is sent
    # Verify state is updated
```

### Manual Testing
```
1. Open FL Studio
2. Start Claude Code with MCP server
3. Send various commands
4. Verify:
   - Notes appear correctly
   - Timing is accurate
   - Manual edits are detected
   - Pattern switching works
   - Channel navigation works
```

## Future Enhancements

Potential areas for improvement:

1. **Security:**
   - Replace eval() with command whitelist
   - Add request signing/validation
   - Implement rate limiting

2. **Features:**
   - Support for mixer operations
   - Arrangement editing
   - Undo/Redo support
   - Automation clips
   - Audio analysis integration

3. **Performance:**
   - Optimize SysEx encoding
   - Implement request batching
   - Reduce trigger latency
   - Add response caching

4. **Reliability:**
   - Better error handling
   - Automatic reconnection
   - State recovery on crash
   - File corruption detection

5. **UX:**
   - Real-time note preview
   - Undo/Redo in Claude
   - Progress indicators
   - Visual feedback

## References

- **FL Studio Python Scripting:** FL Studio Docs
- **Model Context Protocol:** https://modelcontextprotocol.io/
- **MIDI/SysEx:** MIDI 1.0 Specification
- **pynput:** https://pynput.readthedocs.io/
