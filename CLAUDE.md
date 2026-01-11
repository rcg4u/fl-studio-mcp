# FL Studio MCP - AI Assistant Guide

This guide explains how Claude and other AI assistants should use the FL Studio MCP tools.

## Overview

The FL Studio MCP server provides **13 tools** that enable Claude to:
1. **Modify piano roll notes** - Add, delete, or replace notes
2. **Query project state** - Discover channels, patterns, and current notes
3. **Navigate your project** - Switch channels, select patterns, refresh state
4. **Execute advanced commands** - Direct FL Studio API access for power users

The system automatically:
- Triggers FL Studio when you send notes (CMD+OPT+Y keystroke)
- Monitors for manual edits via FL Studio events
- Keeps state synchronized between Claude and FL Studio
- Handles timing/focus management seamlessly

## Getting Started

### 1. Verify Tools Are Available

Check that you have these MCP tools (they'll have the `mcp__fl_studio_mcp__` prefix):

**Piano Roll Operations:**
- `mcp__fl_studio_mcp__send_notes` - Add or replace notes
- `mcp__fl_studio_mcp__delete_notes` - Delete specific notes
- `mcp__fl_studio_mcp__clear_piano_roll` - Clear all notes

**State Queries:**
- `mcp__fl_studio_mcp__get_project_channels` - List all channels
- `mcp__fl_studio_mcp__get_project_patterns` - List all patterns
- `mcp__fl_studio_mcp__get_current_target` - Current channel/pattern
- `mcp__fl_studio_mcp__get_current_piano_roll_notes` - Current notes
- `mcp__fl_studio_mcp__get_pattern_notes` - Notes from specific pattern
- `mcp__fl_studio_mcp__get_all_pattern_notes` - All patterns' notes

**Navigation & Control:**
- `mcp__fl_studio_mcp__show_piano_roll` - Open piano roll for channel
- `mcp__fl_studio_mcp__select_pattern` - Switch to pattern
- `mcp__fl_studio_mcp__reload` - Manual state refresh

**Advanced:**
- `mcp__fl_studio_mcp__call_fl_midi_controller_api` - Direct FL Studio API

If these aren't available, the MCP server isn't connected. The server is registered as `fl-studio-mcp` in Claude Code.

### 2. Always Start by Getting Current State

Before making ANY changes, query the current state:

```python
# Get current piano roll notes
current_notes = mcp__fl_studio_mcp__get_current_piano_roll_notes()

# See what channels exist
channels = mcp__fl_studio_mcp__get_project_channels()

# See what patterns exist
patterns = mcp__fl_studio_mcp__get_project_patterns()

# See which channel/pattern are currently open
target = mcp__fl_studio_mcp__get_current_target()
```

This tells you:
- What notes already exist in the current piano roll
- The PPQ (timing resolution)
- What channels and patterns are available
- Which is currently selected

## Tool Reference

### Piano Roll Operations

#### `send_notes(notes, mode="add")`

Add or replace notes in the piano roll.

**Parameters:**
- `notes`: List of note dictionaries, each with:
  - `midi` (int, 0-127): MIDI note number
  - `duration` (float): Duration in quarter notes (0.5=8th, 1=quarter, 2=half, 4=whole)
  - `time` (float): Start position in quarter notes (0=beat 1, 4=beat 5)
  - `velocity` (float, optional): Velocity 0.0-1.0 (default: 0.8)
- `mode` (string): "add" (append) or "replace" (clear then add)

**Example - Single note:**
```python
mcp__fl_studio_mcp__send_notes([
    {"midi": 60, "duration": 4, "time": 0}
])
# Adds C4 (middle C) as a whole note at beat 1
```

**Example - Chord (multiple notes at same time):**
```python
mcp__fl_studio_mcp__send_notes([
    {"midi": 60, "duration": 4, "time": 0},  # C
    {"midi": 64, "duration": 4, "time": 0},  # E
    {"midi": 67, "duration": 4, "time": 0}   # G
])
# Adds C major chord
```

**Example - Melody:**
```python
mcp__fl_studio_mcp__send_notes([
    {"midi": 60, "duration": 0.5, "time": 0},   # C
    {"midi": 62, "duration": 0.5, "time": 0.5}, # D
    {"midi": 64, "duration": 0.5, "time": 1},   # E
    {"midi": 65, "duration": 0.5, "time": 1.5}  # F
])
# Adds a 4-note ascending melody
```

**Important:** Always specify `time` for every note. Don't rely on defaults.

#### `delete_notes(notes)`

Delete specific notes from the piano roll.

**Parameters:**
- `notes`: List of note dictionaries to delete, each with:
  - `midi` (int): MIDI note number
  - `time` (float): Start position in quarter notes

**Example:**
```python
# Delete G note at beat 1
mcp__fl_studio_mcp__delete_notes([
    {"midi": 67, "time": 0}
])

# Delete multiple notes
mcp__fl_studio_mcp__delete_notes([
    {"midi": 67, "time": 0},
    {"midi": 72, "time": 4}
])
```

#### `clear_piano_roll()`

Clear all notes from the current piano roll.

**Example:**
```python
mcp__fl_studio_mcp__clear_piano_roll()
# Piano roll is now empty
```

### State Queries

#### `get_project_channels()`

Get list of all channels in the project.

**Returns:** JSON string with array: `[{"index": 0, "name": "Kick"}, ...]`

**Example:**
```python
channels = mcp__fl_studio_mcp__get_project_channels()
# Returns: [
#   {"index": 0, "name": "Kick"},
#   {"index": 1, "name": "Snare"},
#   {"index": 2, "name": "Chords"},
#   ...
# ]
```

#### `get_project_patterns()`

Get list of all patterns in the project.

**Returns:** JSON string with array: `[{"index": 1, "name": "Drums"}, ...]`

**Note:** Pattern 0 is skipped (it's internal to FL Studio). Patterns are 1-based.

**Example:**
```python
patterns = mcp__fl_studio_mcp__get_project_patterns()
# Returns: [
#   {"index": 1, "name": "Drums"},
#   {"index": 2, "name": "Chords"},
#   {"index": 3, "name": "Verse"},
#   ...
# ]
```

#### `get_current_target()`

Get the currently open channel and pattern.

**Returns:** JSON string with current target info:
```json
{
  "channel_index": 0,
  "channel_name": "Kick",
  "pattern_index": 1,
  "pattern_name": "Drums"
}
```

**Example:**
```python
target = mcp__fl_studio_mcp__get_current_target()
# Tells you which channel and pattern are currently visible
```

#### `get_current_piano_roll_notes()`

Get all notes from the currently open piano roll.

**Returns:** JSON string with note data:
```json
{
  "ppq": 96,
  "noteCount": 4,
  "notes": [
    {"number": 60, "time": 0, "length": 96, "velocity": 204, ...},
    {"number": 64, "time": 0, "length": 96, "velocity": 204, ...},
    ...
  ]
}
```

**Example:**
```python
notes_data = mcp__fl_studio_mcp__get_current_piano_roll_notes()
# notes_data["notes"] = array of all notes in current piano roll
# notes_data["ppq"] = timing resolution (usually 96 or 480)
# notes_data["noteCount"] = how many notes exist
```

#### `get_pattern_notes(pattern_identifier)`

Get notes from a specific pattern (by name or index).

**Parameters:**
- `pattern_identifier` (string): Pattern name (e.g., "Chorus") or 1-based index (e.g., "2")

**Returns:** JSON string with note data (same format as `get_current_piano_roll_notes`)

**Example:**
```python
# Get by pattern name
verse_notes = mcp__fl_studio_mcp__get_pattern_notes("Verse")

# Get by pattern index (1-based)
pattern2_notes = mcp__fl_studio_mcp__get_pattern_notes("2")
```

#### `get_all_pattern_notes()`

Get notes from all patterns in the project.

**Returns:** JSON string mapping pattern names to note data:
```json
{
  "Drums": {"ppq": 96, "noteCount": 8, "notes": [...]},
  "Chords": {"ppq": 96, "noteCount": 4, "notes": [...]},
  "Melody": {"ppq": 96, "noteCount": 12, "notes": [...]}
}
```

**Example:**
```python
all_patterns = mcp__fl_studio_mcp__get_all_pattern_notes()
# all_patterns["Drums"]["notes"] = array of drum notes
# all_patterns["Chords"]["notes"] = array of chord notes
# etc.
```

### Navigation & Control

#### `show_piano_roll(channel_id)`

Open the piano roll for a specific channel.

**Parameters:**
- `channel_id` (int): 0-based channel index

**Example:**
```python
# Open piano roll for channel 0 (Kick)
mcp__fl_studio_mcp__show_piano_roll(0)

# Open piano roll for channel 2 (Chords)
mcp__fl_studio_mcp__show_piano_roll(2)
```

#### `select_pattern(pattern_identifier)`

Switch to a different pattern.

**Parameters:**
- `pattern_identifier` (string): Pattern name (e.g., "Verse") or 1-based index (e.g., "1")

**Example:**
```python
# Switch to pattern by name
mcp__fl_studio_mcp__select_pattern("Verse")

# Switch to pattern by index (1-based)
mcp__fl_studio_mcp__select_pattern("2")
```

#### `reload()`

Manually refresh the piano roll state from FL Studio.

Use this if:
- You made manual edits in FL Studio
- State seems out of sync
- You want to ensure latest data from FL Studio

**Example:**
```python
# Manual state refresh
mcp__fl_studio_mcp__reload()
# Piano roll is now reloaded from FL Studio
```

### Advanced - Low-Level API

#### `call_fl_midi_controller_api(method, args, kwargs)`

Execute any FL Studio API function directly.

**Parameters:**
- `method` (string): Full method path like "patterns.jumpToPattern" or "mixer.getTrackVolume"
- `args` (list, optional): Positional arguments `[int, float, str, bool]`
- `kwargs` (dict, optional): Keyword arguments
- `expect_response` (bool, optional): Wait for response from FL Studio (default: true)

**Examples:**
```python
# Get pattern count
mcp__fl_studio_mcp__call_fl_midi_controller_api("patterns.patternCount")

# Get pattern name
mcp__fl_studio_mcp__call_fl_midi_controller_api("patterns.getPatternName", [1])

# Get mixer track volume
mcp__fl_studio_mcp__call_fl_midi_controller_api("mixer.getTrackVolume", [0])

# Get channel name
mcp__fl_studio_mcp__call_fl_midi_controller_api("channels.getChannelName", [2])

# Fast bulk operation (no response wait)
mcp__fl_studio_mcp__call_fl_midi_controller_api(
    "channels.setGridBit",
    [0, 0, 1],
    expect_response=False
)

# With keyword arguments
mcp__fl_studio_mcp__call_fl_midi_controller_api(
    "ui.openEventEditor",
    [262464, 0],
    {"newWindow": 1}
)
```

This is for advanced users who want to access FL Studio features not exposed by the other tools.

## Common Interaction Patterns

### Pattern 1: Add a Chord Progression

```python
# Get state first
state = mcp__fl_studio_mcp__get_current_piano_roll_notes()

# Send I chord (C major)
mcp__fl_studio_mcp__send_notes([
    {"midi": 60, "duration": 4, "time": 0},
    {"midi": 64, "duration": 4, "time": 0},
    {"midi": 67, "duration": 4, "time": 0}
])

# Send IV chord (F major)
mcp__fl_studio_mcp__send_notes([
    {"midi": 65, "duration": 4, "time": 4},
    {"midi": 69, "duration": 4, "time": 4},
    {"midi": 72, "duration": 4, "time": 4}
])

# Send V chord (G major)
mcp__fl_studio_mcp__send_notes([
    {"midi": 67, "duration": 4, "time": 8},
    {"midi": 71, "duration": 4, "time": 8},
    {"midi": 74, "duration": 4, "time": 8}
])

# Notes appear automatically in FL Studio!
```

### Pattern 2: Modify Existing Notes

```python
# Get current state
state = mcp__fl_studio_mcp__get_current_piano_roll_notes()

# Find and delete a specific note (find G at beat 0)
mcp__fl_studio_mcp__delete_notes([
    {"midi": 67, "time": 0}
])

# Add replacement note (A instead)
mcp__fl_studio_mcp__send_notes([
    {"midi": 69, "duration": 4, "time": 0}
])

# Changes appear automatically!
```

### Pattern 3: Clear and Start Fresh

```python
# Clear everything and add new progression
mcp__fl_studio_mcp__send_notes([
    {"midi": 60, "duration": 0.5, "time": 0},   # C
    {"midi": 62, "duration": 0.5, "time": 0.5}, # D
    {"midi": 64, "duration": 0.5, "time": 1},   # E
    {"midi": 65, "duration": 0.5, "time": 1.5}  # F
], mode="replace")

# Old notes cleared, new notes appear!
```

### Pattern 4: Work with Multiple Patterns

```python
# Get all patterns in project
patterns = mcp__fl_studio_mcp__get_project_patterns()
# Returns: [{"index": 1, "name": "Drums"}, {"index": 2, "name": "Verse"}, ...]

# Get notes from specific pattern
verse_notes = mcp__fl_studio_mcp__get_pattern_notes("Verse")

# Switch to a pattern
mcp__fl_studio_mcp__select_pattern("Chorus")

# Add notes to current pattern
mcp__fl_studio_mcp__send_notes([...])
```

### Pattern 5: Discover and Navigate Project

```python
# List all channels
channels = mcp__fl_studio_mcp__get_project_channels()
# Returns: [{"index": 0, "name": "Kick"}, {"index": 1, "name": "Snare"}, ...]

# Open a specific channel's piano roll
mcp__fl_studio_mcp__show_piano_roll(1)  # Open Snare

# Get current target (what's visible)
target = mcp__fl_studio_mcp__get_current_target()
# Returns: {"channel_index": 1, "channel_name": "Snare", "pattern_index": 1, "pattern_name": "Drums"}

# Get notes from that channel
notes = mcp__fl_studio_mcp__get_current_piano_roll_notes()
```

## Key Concepts

### Time is Always in Quarter Notes

Never use ticks or PPQ directly in tool calls. Always use quarter notes:
- `time=0` = Beat 1
- `time=1` = Beat 2
- `time=4` = Beat 5 (start of measure 2 in 4/4)
- `time=8` = Beat 9 (start of measure 3)

Duration is also in quarter notes:
- `duration=0.25` = 16th note
- `duration=0.5` = 8th note
- `duration=1` = Quarter note
- `duration=2` = Half note
- `duration=4` = Whole note

The system automatically converts to ticks using the PPQ value.

### Chords Are Multiple Notes

A chord isn't a special object - it's just multiple notes with the same `time` value:

```python
# C major chord = 3 notes all at time=0
mcp__fl_studio_mcp__send_notes([
    {"midi": 60, "duration": 4, "time": 0},  # C
    {"midi": 64, "duration": 4, "time": 0},  # E
    {"midi": 67, "duration": 4, "time": 0}   # G
])
```

### Event-Based State Synchronization

The system monitors FL Studio for changes:
- When you manually add/edit notes, FL Studio sends events
- The state manager detects these automatically
- Claude sees the changes via state query tools

You don't need to tell Claude to "refresh" - it happens automatically when:
- Piano roll focus changes
- Patterns are switched
- Manual edits are made

### MIDI Note Reference

Common notes you'll use:
- **C4 (middle C)** = MIDI 60 = "C4" in FL Studio
- **A4 (tuning pitch)** = MIDI 69 = "A4" in FL Studio
- **C5** = MIDI 72 = "C5" in FL Studio

**Important:** FL Studio displays notes ONE OCTAVE HIGHER than standard MIDI convention:
- MIDI 60 (C4) displays as C5 in FL Studio
- MIDI 69 (A4) displays as A5 in FL Studio
- MIDI 72 (C5) displays as C6 in FL Studio

## Best Practices

### DO:
- ✅ Always get state first before making changes
- ✅ Always specify `time` for every note explicitly
- ✅ Use quarter notes for all time and duration values
- ✅ Send chords as multiple notes with the same time
- ✅ Tell user notes will appear automatically after brief delay
- ✅ Use `mode="add"` for incremental changes (default)
- ✅ Use `mode="replace"` when user requests a complete rewrite

### DON'T:
- ❌ Don't use ticks or PPQ values in tool calls
- ❌ Don't assume you can see manual edits without querying state
- ❌ Don't forget to specify `time` for notes
- ❌ Don't worry about clicking buttons - everything is automatic
- ❌ Don't tell user to press keyboard shortcuts (unless they manually edited)

## Troubleshooting for AI Assistants

**User says "Nothing happened"**
- Ask: "Is FL Studio running and is a piano roll open?"
- Ask: "Is the MCP server connected?" (Check Claude's available tools)
- Suggest: Restart Claude Code to reconnect the MCP server

**Tools return empty data**
- Check if FL Studio is running
- Check if a project is open
- Try calling `reload()` to refresh state

**Notes appear at wrong positions**
- Verify you're using quarter notes, not ticks
- Remember: `time=4` is beat 5 (counting starts at 0)
- Check the PPQ value from `get_current_piano_roll_notes()`

**User manually edited but Claude doesn't see changes**
- The event system should detect changes automatically
- If not, suggest: "Try switching to a different pattern and back"
- Or: Call `reload()` to manually refresh

## File Locations (For Reference)

The system stores data in these locations:

**FL Studio directories:**
- `~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController/` - Hardware device scripts
- `~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts/` - Piano roll scripts

**Key files:**
- `fl_events.json` - Event stream from FL Studio (JSONL format)
- `mcp_request.json` - Request queue (processed by BeginLLMInteraction script)
- `piano_roll_state.json` - Current piano roll state (exported by FL Studio)
- `project_state.json` - Persisted project state

You don't need to interact with these directly - the MCP tools handle them.

## Advanced Topics

### Using Direct API Access

For power users, the low-level API tool allows direct execution of FL Studio Python functions:

```python
# Example: Get detailed channel info
mcp__fl_studio_mcp__call_fl_midi_controller_api("channels.getChannelColor", [0])
# Returns the color of channel 0

# Example: Bulk operations (fire-and-forget)
for i in range(8):
    mcp__fl_studio_mcp__call_fl_midi_controller_api(
        "mixer.setTrackVolume",
        [i, 0.8],
        expect_response=False
    )
# Efficiently set multiple track volumes
```

See the FL Studio Python scripting documentation for available methods.

### Understanding PPQ

PPQ (Pulses Per Quarter Note) is FL Studio's timing resolution:
- Typical values: 96 (lower resolution) or 480 (higher resolution)
- Used internally to convert quarter notes to ticks
- You don't need to use PPQ directly - the tools handle conversion
- But you can check `get_current_piano_roll_notes()["ppq"]` if you're curious

## Summary

The FL Studio MCP provides a complete bridge between Claude and FL Studio:
1. **Query** project state (channels, patterns, notes)
2. **Modify** piano roll content (add, delete, replace notes)
3. **Navigate** your project (switch channels, select patterns)
4. **Execute** advanced commands via direct API access

Everything is automatic - no manual triggering needed. Just talk to Claude and watch your musical ideas appear in FL Studio!
