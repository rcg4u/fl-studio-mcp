# FL Studio Piano Roll MCP

An MCP (Model Context Protocol) server that enables Claude to interact with FL Studio's piano roll and project state through bidirectional MIDI communication. Create melodies, chord progressions, and musical patterns through natural language conversation with **automatic, real-time updates**.

See the playlist here:
[LLMs and FL Studio Piano Roll (MacOs Version)](https://youtube.com/playlist?list=PL3miIiuTRI6fgugjvJhGsXoe_oX65-o0S&si=X68d7kPWanyCq9m4)

## Overview

Talk to Claude and watch your musical ideas appear instantly in FL Studio:
- **Generate and modify** chord progressions, melodies, and bass lines
- **Query project state** - discover all channels and patterns in your project
- **Navigate** between different channels and patterns
- **Real-time synchronization** - Claude always sees your manual edits via events
- **Direct API access** - advanced users can execute any FL Studio function
- **Zero manual intervention** - notes appear automatically with built-in trigger!

## Platform Support

**✅ macOS (Primary)** - Full auto-trigger functionality with osascript integration
**⚠️ Windows (Secondary)** - Partially implemented, may require additional configuration

## Prerequisites

- **macOS or Windows** (macOS working fully, Windows needs more work)
- **FL Studio** (any recent version with Python scripting support)
- **Python 3.11+** (managed automatically by uv)
- **MCP-compatible client** (Claude Desktop, Claude Code CLI, or other MCP client)
- **uv** (Fast Python package manager - [installation guide](https://docs.astral.sh/uv/getting-started/installation/))

### macOS Accessibility Permissions

The auto-trigger uses pynput to send keystrokes to FL Studio. You must enable Accessibility access for **Terminal** (or your terminal app) and **Claude Code** (if using Claude Code CLI):

1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Click the **+** button to add applications
3. Add **Terminal** (or iTerm, Warp, etc.)
4. Add **Claude** (Claude Code CLI) if you're using it
5. Ensure the toggles are **enabled** for each app

Without these permissions, the auto-trigger cannot send the Cmd+Opt+Y keystroke to FL Studio.

## Installation

### Quick Start (3 Commands)

```bash
git clone https://github.com/calvinw/fl-studio-mcp.git
cd fl-studio-mcp

./install_prerequisites.sh    # Install uv and Python environment
./install_mcp_for_claude.sh   # Register with Claude Code
```

**Then restart Claude Code and you're ready to go!**

## Usage

### Quick Start (Every Session)

**Step 1: Open FL Studio**
1. Open FL Studio
2. Open or create a piano roll

**Step 2: Start Claude and begin working**

Just start talking to Claude! The system automatically:
- Monitors your piano roll for changes
- Syncs state whenever you switch channels or patterns
- Sends notes to the piano roll in real-time
- Detects your manual edits automatically

**Example conversation:**

```
You: "Add a C major chord"
[Claude sends it, notes appear automatically ✅]

[You manually add a melody 🎹]

You: "Add a bass line under that"
[Claude sees your melody AND adds bass ✅]
```

No setup scripts needed - it all happens automatically!

### Navigation & Discovery

Claude can help you navigate your project:

```
You: "What channels do I have?"
[Claude lists all channels in your project]

You: "Switch to the drums channel"
[Claude opens the drums piano roll]

You: "Show me the pattern called 'Chorus'"
[Claude switches to that pattern]

You: "What notes are in the Verse pattern?"
[Claude reads and shows the notes]
```

### Example Requests

**Creating music:**
- "Create a I-IV-V-I progression in C major"
- "Add a pentatonic melody over these chords"
- "Add a bass note on the root of each chord"
- "Create a 16-bar drum pattern"

**Modifying music:**
- "Change that G note to an A"
- "Make this melody 2 octaves higher"
- "Add velocity variations to this line"

**Exploring your project:**
- "List all the channels"
- "Show me what patterns exist"
- "What's in the 'Bridge' pattern?"
- "Clear everything and start fresh"

## Available Tools

Claude has access to 13 MCP tools organized by category:

**Piano Roll Operations:**
- `send_notes(notes, mode)` - Add or replace notes in the piano roll
- `delete_notes(notes)` - Remove specific notes
- `clear_piano_roll()` - Clear all notes at once

**Project State Queries:**
- `get_project_channels()` - List all channels in your project
- `get_project_patterns()` - List all patterns
- `get_current_target()` - See which channel and pattern are currently open
- `get_current_piano_roll_notes()` - Get notes from the current piano roll
- `get_pattern_notes(pattern_id)` - Read notes from any pattern
- `get_all_pattern_notes()` - Get notes from all patterns at once

**Navigation & Control:**
- `show_piano_roll(channel_id)` - Open the piano roll for a specific channel
- `select_pattern(pattern_id)` - Switch to a different pattern
- `reload()` - Manually refresh the piano roll state

**Advanced (Low-Level API):**
- `call_fl_midi_controller_api(method, args, kwargs)` - Direct access to FL Studio's Python API

See [CLAUDE.md](CLAUDE.md) for detailed documentation on how Claude uses these tools.

## Architecture

The system uses **bidirectional MIDI communication** and **event-based state synchronization**:

```
┌────────────────────────────────────────────────────────────┐
│ FL Studio (DAW)                                             │
├────────────────────────────────────────────────────────────┤
│  • device_FLResponse.py - Monitors changes, sends events   │
│  • device_FLRequest.py - Receives commands via SysEx       │
│  • BeginLLMInteraction.pyscript - Applies note changes     │
└────────────────────────────────────────────────────────────┘
         ↑              ↓              ↓              ↓
       SysEx       fl_events.json  mcp_request.json  piano_roll_state.json
    (IAC Ports)    (event stream)  (request queue)   (state snapshot)
         ↑              ↓              ↓              ↓
┌────────────────────────────────────────────────────────────┐
│ Python Backend                                              │
├────────────────────────────────────────────────────────────┤
│  • FLStudioStateManager - Manages state & triggers        │
│  • MCP Server - Exposes 13 tools to Claude                │
│  • fl_dual_port.py - Bidirectional MIDI/SysEx            │
└────────────────────────────────────────────────────────────┘
         ↓
      Claude
```

### How It Works

1. **Claude sends a request** → MCP Server queues it to `mcp_request.json`
2. **StateManager triggers FL Studio** → Sends Cmd+Opt+Y keystroke
3. **FL Studio runs script** → BeginLLMInteraction processes requests
4. **Notes appear in piano roll** → Visible on screen immediately
5. **FL Studio sends events** → device_FLResponse notifies of changes
6. **StateManager monitors events** → Updates tracked state
7. **Claude sees updates** → Via state query tools

**Key feature:** When you manually edit in FL Studio, the event system automatically detects it, so Claude always sees your changes without needing manual refresh!

## Troubleshooting

### Notes Not Appearing

**Problem:** You send a request but nothing happens in FL Studio

**Solutions:**
1. Verify FL Studio is running and a piano roll is open
2. Check Claude has **Accessibility permissions** (System Settings → Privacy & Security → Accessibility)
3. Try pressing Cmd+Opt+Y manually (or Ctrl+Alt+Y on Windows) to trigger the script
4. Restart Claude Code to reconnect the MCP server
5. Restart FL Studio and try again

### Claude Can't See Your Manual Edits

**Problem:** You manually add/edit notes in FL Studio, but Claude doesn't know about them

**Solution:** The event system should detect changes automatically. If it doesn't:
- Click on a different channel and back to refresh events
- Run `reload()` tool to manually refresh the piano roll state
- Ensure device scripts are installed in FL Studio hardware folder

### State Query Tools Return Empty/Wrong Data

**Problem:** `get_project_channels()`, `get_project_patterns()`, etc. return nothing or errors

**Solutions:**
- Ensure you have a project open in FL Studio
- Check that hardware device scripts are installed (device_FLRequest.py, device_FLResponse.py)
- Check MIDI communication: Verify IAC Driver ports are available on macOS
- Try pressing Cmd+Opt+Y to trigger a manual state refresh

### MCP Server Not Connecting

**Problem:** Claude says it doesn't have FL Studio tools

**Solutions:**
1. Restart Claude Code
2. Verify MCP is registered: Check `~/.claude_app/claude_desktop_config.json`
3. Ensure dependencies are installed: `uv sync`
4. Check that the virtual environment was created in `.venv/`

### Notes at Wrong Positions

**Problem:** Notes appear at incorrect times

**Solutions:**
- Verify you're using **quarter notes**, not ticks
  - `time=0` = beat 1
  - `time=4` = beat 5 (measure 2 in 4/4)
- Check the PPQ (pulses per quarter note) in current piano roll state
- Remember: duration and time are both in quarter note units

### Hardware Device Scripts Not Working

**Problem:** Tools that query state (channels, patterns) don't work, or trigger fails

**Solutions:**
- Verify symlinks exist in `~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController/`
  - `device_FLRequest.py` (→ source file)
  - `device_FLResponse.py` (→ source file)
- On macOS, verify IAC Driver ports are available (Audio MIDI Setup)
- Restart FL Studio
- Check FL Studio version supports Python hardware devices

### Windows-Specific Issues

**Note:** Windows support is secondary. Known limitations:
- Keystroke triggering may need additional setup
- MIDI port configuration may differ
- For best experience, use macOS

## File Locations

**FL Studio hardware device scripts:**
```
~/Documents/Image-Line/FL Studio/Settings/Hardware/FLController/
├── device_FLRequest.py      (symlink: processes SysEx commands)
├── device_FLResponse.py     (symlink: sends project events)
├── fl_events.json           (event stream from FL Studio)
└── project_state.json       (persisted project state)
```

**FL Studio piano roll scripts:**
```
~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts/
├── BeginLLMInteraction.pyscript  (processes note requests)
├── mcp_request.json              (request queue)
├── mcp_response.json             (execution results)
└── piano_roll_state.json         (exported piano roll state)
```

**Source repository:**
```
/Users/calvinw/develop/fl-studio-mcp/
├── mcp/
│   ├── fl_studio_mcp_server.py           (MCP server: 13 tools)
│   └── install_mcp_for_claude.sh         (MCP registration)
├── midi_controller/
│   ├── fl_studio_state_manager.py        (state management & triggering)
│   ├── fl_dual_port.py                   (bidirectional MIDI/SysEx)
│   ├── focus_management.py               (window focus handling)
│   ├── device_FLRequest.py               (source: FL Studio command handler)
│   └── device_FLResponse.py              (source: FL Studio event broadcaster)
├── piano_roll/
│   └── BeginLLMInteraction.pyscript      (source: processes note requests)
├── install_prerequisites.sh              (setup uv, Python, symlinks)
├── CLAUDE.md                             (AI assistant documentation)
├── DEVELOPER.md                          (architecture & internals)
└── README.md                             (this file: user guide)
```

## Development

For information about the internal architecture, MIDI communication, and state management system, see [DEVELOPER.md](DEVELOPER.md).

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - feel free to use and modify for your projects.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

Built using the [Model Context Protocol](https://modelcontextprotocol.io/) specification.

Special thanks to the FL Studio and Python communities.


