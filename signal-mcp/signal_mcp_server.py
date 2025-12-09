#!/usr/bin/env python3
"""
Signal MCP Server

Provides MCP tools for interacting with Signal's piano roll via the HTTP API.
This server communicates with Signal's API server running on port 3001.

Usage:
    python signal_mcp_server.py

Or register with Claude Code:
    claude mcp add signal-mcp python3 /path/to/signal_mcp_server.py
"""

from fastmcp import FastMCP
import httpx
import json
from typing import Optional

# Initialize FastMCP server
mcp = FastMCP("Signal MCP Server")

# Signal API server URL
SIGNAL_API_URL = "http://localhost:3001"


def make_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make an HTTP request to the Signal API server."""
    url = f"{SIGNAL_API_URL}{endpoint}"

    try:
        with httpx.Client(timeout=10.0) as client:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=data or {})
            elif method == "DELETE":
                response = client.delete(url, json=data or {})
            else:
                return {"success": False, "error": f"Unknown method: {method}"}

            return response.json()
    except httpx.ConnectError:
        return {
            "success": False,
            "error": "Cannot connect to Signal API server. Make sure Signal is running and the API server is started (node api-server/server.js)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool
def get_piano_roll_state() -> str:
    """
    Read the current piano roll state from Signal.

    Returns all tracks with their notes, including:
    - Track ID, name, and channel
    - All notes with MIDI number, time, duration, and velocity
    - Song metadata (timebase, name)

    Returns:
        JSON string containing the piano roll state
    """
    result = make_request("GET", "/api/state")
    return json.dumps(result, indent=2)


@mcp.tool
def send_notes(notes: list[dict], mode: str = "add", track_id: Optional[int] = None) -> str:
    """
    Send notes to Signal's piano roll.

    Args:
        notes: List of note dictionaries, each containing:
            - midi: MIDI note number (0-127), e.g., 60 = Middle C
            - duration: Note duration in quarter notes (1.0 = quarter note)
            - time: Start time in quarter notes from beginning (0 = beat 1)
            - velocity: Optional, 0.0-1.0 (default 0.8)
        mode: Either "add" to add to existing notes or "replace" to clear first
        track_id: Optional track ID to add notes to (uses first track if not specified)

    Example:
        # Add a C major chord at beat 0
        send_notes([
            {"midi": 60, "duration": 2.0, "time": 0},    # C4
            {"midi": 64, "duration": 2.0, "time": 0},    # E4
            {"midi": 67, "duration": 2.0, "time": 0}     # G4
        ])

        # Add a melody starting at beat 4
        send_notes([
            {"midi": 72, "duration": 0.5, "time": 4},
            {"midi": 74, "duration": 0.5, "time": 4.5},
            {"midi": 76, "duration": 1.0, "time": 5}
        ])

    Returns:
        Status of the note creation
    """
    if not notes:
        return json.dumps({"success": False, "error": "notes list cannot be empty"})

    # Validate notes
    for i, note in enumerate(notes):
        if "midi" not in note:
            return json.dumps({"success": False, "error": f"note {i} missing 'midi' field"})
        if "duration" not in note:
            return json.dumps({"success": False, "error": f"note {i} missing 'duration' field"})
        if "time" not in note:
            return json.dumps({"success": False, "error": f"note {i} missing 'time' field"})

    data = {
        "notes": notes,
        "mode": mode
    }
    if track_id is not None:
        data["trackId"] = track_id

    result = make_request("POST", "/api/notes", data)
    return json.dumps(result, indent=2)


@mcp.tool
def delete_notes(notes: list[dict], track_id: Optional[int] = None) -> str:
    """
    Delete specific notes from Signal's piano roll.

    Args:
        notes: List of note dictionaries to delete, each containing:
            - midi: MIDI note number (0-127)
            - time: Start time in quarter notes
        track_id: Optional track ID (uses first track if not specified)

    Example:
        # Delete the G note at beat 0
        delete_notes([{"midi": 67, "time": 0}])

        # Delete multiple notes
        delete_notes([
            {"midi": 60, "time": 0},
            {"midi": 64, "time": 4}
        ])

    Returns:
        Status of the deletion
    """
    if not notes:
        return json.dumps({"success": False, "error": "notes list cannot be empty"})

    for i, note in enumerate(notes):
        if "midi" not in note:
            return json.dumps({"success": False, "error": f"note {i} missing 'midi' field"})
        if "time" not in note:
            return json.dumps({"success": False, "error": f"note {i} missing 'time' field"})

    data = {"notes": notes}
    if track_id is not None:
        data["trackId"] = track_id

    result = make_request("DELETE", "/api/notes", data)
    return json.dumps(result, indent=2)


@mcp.tool
def clear_notes(track_id: Optional[int] = None) -> str:
    """
    Clear all notes from a track in Signal's piano roll.

    Args:
        track_id: Optional track ID to clear (uses first track if not specified)

    Returns:
        Status of the clearing operation
    """
    data = {}
    if track_id is not None:
        data["trackId"] = track_id

    result = make_request("POST", "/api/notes/clear", data)
    return json.dumps(result, indent=2)


@mcp.tool
def check_connection() -> str:
    """
    Check if the Signal API server is running and Signal app is connected.

    Returns:
        Connection status
    """
    result = make_request("GET", "/api/health")
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
