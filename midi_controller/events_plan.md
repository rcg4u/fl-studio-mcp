# FL Studio Events System - Simplified Plan

## Goal

Track piano roll state changes and trigger script reruns when the piano roll editor is focused or when the channel changes while the piano roll is open.

## Events

### 1. `piano_roll_state`

Sent when:
- Pattern changes AND piano roll is visible
- Piano roll gets focus (window focus change)

**Event Data:**
```json
{
  "target_channel_index": int,      // 0-based channel index
  "target_channel_name": string,    // Channel name (e.g., "FLEX Bass")
  "pattern_index": int,             // Pattern index (from FL API)
  "pattern_name": string            // Pattern name (e.g., "Melody")
}
```

**Deduplication:** Only sent if state (pattern + channel) actually changed since last send.

### 2. `rerun_piano_script`

Sent when:
- Piano roll becomes focused (OnIdle detects transition)
- Channel is selected via green LED AND piano roll is focused

**Event Data:**
```json
{}  // Empty - state already sent via piano_roll_state
```

**Timing:** Sent AFTER `piano_roll_state` to ensure state is available first.

## Controller Logic (device_FLResponse.py)

### State Variables

```python
# Track the currently selected channel in channel rack (green LED)
_selected_channel_index = None
_selected_channel_name = None

# Track current pattern
_current_pattern_index = None
_current_pattern_name = None

# Track last sent state to avoid duplicates
_last_sent_pattern = None
_last_sent_channel = None

# Track last focused state for OnIdle
_last_was_focused = False

# Track pending rerun request from OnDirtyChannel
_pending_rerun = False
```

### OnProjectLoad(index)

Called when project loads. Only processes on successful load (index == 100).

- Gets selected channel from channel rack via `channels.channelNumber()`
- Gets current pattern via `patterns.patternNumber()`
- Initializes all state variables
- Prints diagnostic output

### OnDirtyChannel(index, flag)

When `CE_Select` (flag == 4):
- Update `_selected_channel_index` and `_selected_channel_name`
- Print channel change
- If piano roll is focused, set `_pending_rerun = True` (rerun sent later in OnRefresh)

### OnRefresh(flags)

**Pattern tracking:**
- If `HW_Dirty_Patterns` (1024): Update `_current_pattern_index` and `_current_pattern_name`

**State change detection:**
- Compare current pattern and channel against last sent values
- Skip if no change

**Send events:**
- If `HW_Dirty_Patterns` and piano roll visible → send `piano_roll_state`
- If `HW_Dirty_FocusedWindow` and piano roll focused → send `piano_roll_state`
- After sending state, if `_pending_rerun` is True AND piano roll focused → send `rerun_piano_script`

### OnIdle()

Called periodically by FL Studio.

- Check if piano roll (widPianoRoll = 3) is focused
- Detect transition from not-focused → focused
- On transition: send `rerun_piano_script` event

## Event Flow Examples

### Case 1: Click piano roll to focus

```
OnRefresh(HW_Dirty_FocusedWindow) → send piano_roll_state
OnIdle detects focus transition → send rerun_piano_script
```

### Case 2: Double-click pattern in playlist

```
OnRefresh(HW_Dirty_Patterns | HW_Dirty_FocusedWindow)
  → update pattern
  → send piano_roll_state (first time only due to deduplication)
OnIdle detects focus transition → send rerun_piano_script
```

### Case 3: Select different channel in channel rack (piano roll already focused)

```
OnDirtyChannel(CE_Select)
  → update _selected_channel
  → set _pending_rerun = True
OnRefresh(HW_Dirty_FocusedWindow)
  → send piano_roll_state (new channel)
  → send rerun_piano_script (due to pending flag)
```

### Case 4: Right-click channel → Piano Roll

```
OnDirtyChannel(CE_Select) → update _selected_channel
OnRefresh(HW_Dirty_FocusedWindow) → send piano_roll_state
OnIdle detects focus transition → send rerun_piano_script
```

## Cases from notes.qmd

| Action | Events | Result |
|--------|--------|--------|
| Green LED click | `OnDirtyChannel` → `OnRefresh` | Update `_selected_channel`, send `piano_roll_state`, send `rerun_piano_script` (if focused) |
| F7 / Right-click Piano Roll (same channel) | `OnRefresh` | Send `piano_roll_state` with current channel |
| F7 / Right-click Piano Roll (diff channel) | `OnDirtyChannel` → `OnRefresh` | Send `piano_roll_state` with new channel |
| Mini piano roll (same channel) | `OnRefresh` | Send `piano_roll_state` with current channel |
| Mini piano roll (diff channel) | `OnDirtyChannel` → `OnRefresh` | Send `piano_roll_state` with new channel |
| Pattern double-click (visible already) | `OnRefresh` | Send `piano_roll_state` once (deduplication) |

## Listener Logic (fl_event_listener.py)

### Current Implementation

Simple event printer - just prints received events:

```python
def _process_event(self, event):
    event_type = event.get('type', 'unknown')
    data = event.get('data', {})

    print("\n" + "=" * 50)
    print(f"Event received: {event_type}")
    print(json.dumps(data, indent=2))
    print("=" * 50)
```

### Planned Functionality

The listener will eventually:

1. **Track state:** Maintain current pattern/channel from `piano_roll_state` events
2. **Trigger script:** When `rerun_piano_script` received, send CMD+OPT+Y to FL Studio
3. **Cache piano rolls:** Store note data for different pattern/channel combinations
4. **Provide API:** Allow querying state and cached piano roll data

## File Structure

```
midi_controller/
├── device_FLResponse.py           # IMPLEMENTED: Simplified controller
├── device_FLResponse.py.bak       # Backup of old version
├── fl_event_listener.py           # PARTIAL: Simple printer (planned: full handler)
├── fl_event_listener.py.bak       # Backup of old version
└── events_plan.md                 # This file
```

## Key Design Decisions

1. **Two-event system:** `piano_roll_state` carries data, `rerun_piano_script` triggers action
2. **Deduplication:** Track last sent state to avoid duplicate events on double-clicks
3. **Pending rerun flag:** Ensures state is sent before rerun (OnDirtyChannel fires before OnRefresh)
4. **OnIdle for focus transitions:** Reliable detection of piano roll focus changes
5. **PL_LoadOk check:** Only initialize state on successful project load (index 100)

## Next Steps

1. Implement full listener functionality (triggering, caching, API)
2. Handle edge cases (first startup, window close, etc.)
3. Add error handling and recovery
4. Consider additional events (mixer, playlist, etc.)
