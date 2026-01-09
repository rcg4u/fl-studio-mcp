# FL Studio Events System

## Goal

Track FL Studio state changes and provide current channel/pattern and piano roll notes via a simple query API.

## Events

### 1. `project_loaded`

Sent when: Project loads successfully in FL Studio

**Event Data:**
```json
{
  "channels": [
    {"index": 0, "name": "808 Kick"},
    {"index": 1, "name": "808 Clap"}
  ],
  "patterns": [
    {"index": 1, "name": "Drums"},
    {"index": 2, "name": "Melody"}
  ]
}
```

### 2. `target_channel_changed`

Sent when: User opens a piano roll or changes channel/pattern

**Event Data:**
```json
{
  "target_channel_index": 0,
  "target_channel_name": "808 Kick",
  "pattern_index": 1,
  "pattern_name": "Drums"
}
```

**What happens:**
- FLStudioStateManager updates current target
- Sends CMD+OPT+Y to trigger piano roll script
- Loads notes from piano_roll_state.json
- Updates project_state.json

## State Manager (FLStudioStateManager)

Single class that:
1. Monitors fl_events.json for events
2. Tracks channels, patterns, current target, and notes
3. Triggers CMD+OPT+Y on target_channel_changed
4. Provides 4-method query API

### Query API

```python
# Get all channels
channels = manager.get_channels()
# Returns: [{'index': 0, 'name': '808 Kick'}, ...]

# Get all patterns
patterns = manager.get_patterns()
# Returns: [{'index': 1, 'name': 'Drums'}, ...]

# Get current target from events
target = manager.get_current_target_channel_and_pattern()
# Returns: {'channel_index': 0, 'channel_name': '...', 'pattern_index': 1, 'pattern_name': '...'}

# Get current piano roll notes
notes = manager.get_current_piano_roll_notes()
# Returns: {'ppq': 96, 'noteCount': 5, 'notes': [...]}
```

## File Structure

```
midi_controller/
├── fl_studio_state_manager.py    # Main state manager class
├── focus_management.py            # Window focus utilities
├── device_FLResponse.py           # FL Studio hardware device (sends events)
└── device_FLRequest.py            # FL Studio hardware device (receives commands)

~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController/
├── fl_events.json                 # Event stream (JSONL)
└── project_state.json             # Persisted state

~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts/
└── piano_roll_state.json          # Current piano roll notes
```

## Data Flow

```
FL Studio (device_FLResponse.py)
    ↓ writes event
fl_events.json
    ↓ monitored by
FLStudioStateManager
    ↓ reads state
project_state.json
    ↓ query API
MCP Server → Claude
```

## Testing

Standalone mode for debugging:
```bash
python3 midi_controller/fl_studio_state_manager.py
> channels
> patterns
> target
> notes
> summary
```
