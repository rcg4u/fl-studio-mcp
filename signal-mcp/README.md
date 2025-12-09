# Signal MCP Server

MCP (Model Context Protocol) server for controlling Signal music sequencer from Claude and other LLM tools.

## Overview

This integration allows Claude to:
- Read the current state of Signal's piano roll
- Add notes to tracks
- Delete specific notes
- Clear all notes from a track

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Claude/LLM     │────▶│   MCP Server    │────▶│   API Server    │
│  (MCP Client)   │     │  (Python/HTTP)  │     │  (Node.js/WS)   │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │ WebSocket
                                                         ▼
                                                ┌─────────────────┐
                                                │   Signal App    │
                                                │  (React/MobX)   │
                                                └─────────────────┘
```

## Quick Start

### 1. Start Signal with MCP support

```bash
cd signal
./start-with-mcp.sh
```

This starts:
- Signal app at http://localhost:3000/edit
- API server at http://localhost:3001

### 2. Register the MCP server with Claude Code

```bash
claude mcp add signal-mcp -- uv run --directory /path/to/signal-mcp python signal_mcp_server.py
```

### 3. Use Claude to control Signal

Once connected, Claude can use these tools:
- `get_piano_roll_state()` - Read current notes
- `send_notes(notes, mode, track_id)` - Add notes
- `delete_notes(notes, track_id)` - Delete notes
- `clear_notes(track_id)` - Clear all notes
- `check_connection()` - Verify connection

## Installation

### Prerequisites

- Node.js 18+
- Python 3.10+
- uv (Python package manager)

### Setup

1. **Install Signal dependencies:**
   ```bash
   cd signal
   npm install
   ```

2. **Install API server dependencies:**
   ```bash
   cd signal/api-server
   npm install
   ```

3. **Install MCP server dependencies:**
   ```bash
   cd signal-mcp
   uv pip install -e .
   ```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server status |
| GET | `/api/state` | Get piano roll state |
| POST | `/api/notes` | Add notes |
| DELETE | `/api/notes` | Delete notes |
| POST | `/api/notes/clear` | Clear all notes |

### Note Format

Notes use quarter notes for time and duration:

```json
{
  "midi": 60,        // MIDI note number (60 = Middle C)
  "time": 0,         // Start time in quarter notes
  "duration": 1.0,   // Duration in quarter notes
  "velocity": 0.8    // Optional, 0.0-1.0
}
```

### Time Reference

- `time=0` → Beat 1 (start)
- `time=1` → Beat 2
- `time=4` → Beat 5 (start of measure 2 in 4/4)

### Duration Reference

- `0.25` = 16th note
- `0.5` = 8th note
- `1.0` = Quarter note
- `2.0` = Half note
- `4.0` = Whole note

## Usage Examples

### Add a C Major chord

```python
send_notes([
    {"midi": 60, "duration": 2.0, "time": 0},  # C4
    {"midi": 64, "duration": 2.0, "time": 0},  # E4
    {"midi": 67, "duration": 2.0, "time": 0}   # G4
])
```

### Add a melody

```python
send_notes([
    {"midi": 72, "duration": 0.5, "time": 0},
    {"midi": 74, "duration": 0.5, "time": 0.5},
    {"midi": 76, "duration": 0.5, "time": 1},
    {"midi": 77, "duration": 0.5, "time": 1.5},
    {"midi": 79, "duration": 1.0, "time": 2}
])
```

### Clear and replace

```python
send_notes([
    {"midi": 60, "duration": 4.0, "time": 0}
], mode="replace")
```

### Delete specific notes

```python
delete_notes([
    {"midi": 67, "time": 0}
])
```

## Troubleshooting

### "Signal app not connected"

1. Make sure Signal is running at http://localhost:3000/edit
2. Check browser console for WebSocket connection errors
3. Restart the API server

### "Cannot connect to API server"

1. Make sure the API server is running: `node api-server/server.js`
2. Check port 3001 is not in use

### Notes not appearing

1. Verify connection with `check_connection()`
2. Get current state with `get_piano_roll_state()`
3. Check that you're using valid MIDI note numbers (0-127)

## Development

### Running manually

```bash
# Terminal 1: Start Signal app
cd signal
npm run dev

# Terminal 2: Start API server
cd signal/api-server
npm start

# Terminal 3: Run MCP server (for testing)
cd signal-mcp
uv run python signal_mcp_server.py
```

### Testing the API directly

```bash
# Check health
curl http://localhost:3001/api/health

# Get state
curl http://localhost:3001/api/state

# Add notes
curl -X POST http://localhost:3001/api/notes \
  -H "Content-Type: application/json" \
  -d '{"notes": [{"midi": 60, "time": 0, "duration": 1}]}'
```

## License

MIT - Same as Signal
