"""
Reference implementation for reading FL Studio project files.

This technique uses PyFLP to parse .flp files and extract pattern/note data.
Saved as reference but not currently used in the MCP server.
"""

from pathlib import Path
import platform
import os
from typing import List
import json


def note_name_to_number(note_name):
    """Convert note name (e.g., 'E4') to MIDI number."""
    if not note_name:
        return 60  # Default to C4

    note_map = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }

    # Extract note name and octave
    note_name = str(note_name).strip()
    if len(note_name) < 2:
        return 60

    # Handle sharps/flats (2-character note names)
    if note_name[1] in ['#', 'b']:
        note_letter = note_name[:2]
        octave = int(note_name[2:]) if len(note_name) > 2 else 4
    else:
        note_letter = note_name[0]
        octave = int(note_name[1:]) if len(note_name) > 1 else 4

    midi_number = (octave + 1) * 12 + note_map.get(note_letter, 0)
    return midi_number


def get_fl_studio_projects_dirs() -> List[Path]:
    """Get list of FL Studio project directories to search for FLP files"""
    dirs = []

    # Primary: User's Documents/Image-Line/FL Studio/Projects
    primary_dir = Path(os.path.expanduser("~/Documents/Image-Line/FL Studio/Projects"))
    if primary_dir.exists():
        dirs.append(primary_dir)

    # Secondary: Common locations based on OS
    if platform.system() == "Windows":
        # Windows: C:\Users\[Username]\Documents\Image-Line\FL Studio\Projects
        user_profile = os.environ.get("USERPROFILE", "")
        if user_profile:
            win_docs = Path(user_profile) / "Documents" / "Image-Line" / "FL Studio" / "Projects"
            if win_docs.exists() and win_docs not in dirs:
                dirs.append(win_docs)
    elif platform.system() == "Darwin":
        # macOS: ~/Documents/Image-Line/FL Studio/Projects (already covered by primary)
        pass
    else:
        # Linux: ~/.local/share/FL Studio/Projects or ~/FL-Studio-Projects
        linux_local = Path(os.path.expanduser("~/.local/share/FL Studio/Projects"))
        if linux_local.exists():
            dirs.append(linux_local)
        linux_home = Path(os.path.expanduser("~/FL-Studio-Projects"))
        if linux_home.exists():
            dirs.append(linux_home)

    # Fallback: Current working directory
    cwd = Path.cwd()
    if cwd not in dirs:
        dirs.append(cwd)

    return dirs


def get_project_piano_rolls(flp_filename: str) -> str:
    """
    Read all patterns and notes from an FL Studio project file in compact JSON format.

    This tool searches for the FLP file in standard FL Studio project directories
    and extracts all MIDI notes in a compact array format organized by pattern.
    Times are in quarter notes for easy use with the send_notes function.

    Args:
        flp_filename: Name of the .flp file (e.g., "MyProject.flp")
                      If the extension is omitted, it will be added automatically.

    Returns:
        JSON string containing notes in compact format organized by pattern,
        or an error message if the file cannot be found or read.

    Format:
        {
            "project": {"name": str, "tempo": float, "ppq": int},
            "patterns": {
                "pattern_name": {
                    "midi": [int, ...],
                    "time": [float, ...],  // in quarter notes
                    "duration": [float, ...],  // in quarter notes
                    "velocity": [float, ...],  // 0-1
                    "channel_name": str,
                    "note_count": int
                }, ...
            }
        }
    """
    import pyflp

    # Ensure .flp extension
    if not flp_filename.lower().endswith('.flp'):
        flp_filename += '.flp'

    # Search for the FLP file in standard directories
    search_dirs = get_fl_studio_projects_dirs()
    found_path = None

    for search_dir in search_dirs:
        potential_path = search_dir / flp_filename
        if potential_path.exists() and potential_path.is_file():
            found_path = potential_path
            break

    # Also check absolute paths
    if not found_path:
        abs_path = Path(flp_filename)
        if abs_path.is_absolute() and abs_path.exists():
            found_path = abs_path

    # Check current directory as fallback
    if not found_path:
        current_dir_path = Path.cwd() / flp_filename
        if current_dir_path.exists() and current_dir_path.is_file():
            found_path = current_dir_path

    if not found_path:
        return json.dumps({
            "error": f"FLP file '{flp_filename}' not found.",
            "searched_directories": [str(d) for d in search_dirs],
            "current_directory": str(Path.cwd()),
            "note": "Make sure the file is in your FL Studio Projects folder or provide an absolute path."
        })

    try:
        # Parse the FLP file
        project = pyflp.parse(found_path)

        # Create channel lookup
        channels = {}
        for i, channel in enumerate(project.channels):
            channels[channel.iid] = {
                "name": channel.name or f"Channel {i}",
                "iid": channel.iid
            }

        # Organize notes by pattern in compact format
        patterns_data = {}

        for pattern in project.patterns:
            pattern_name = pattern.name or f"Pattern {pattern.iid}"

            # Initialize arrays for this pattern
            midi_notes = []
            time_notes = []
            duration_notes = []
            velocity_notes = []

            notes_list = list(pattern.notes)
            for note in notes_list:
                # Convert note name to MIDI number
                midi_number = note_name_to_number(note.key)

                # Convert from ticks to quarter notes
                time_qn = note.position / project.ppq
                duration_qn = note.length / project.ppq
                velocity_norm = note.velocity / 127.0

                midi_notes.append(midi_number)
                time_notes.append(time_qn)
                duration_notes.append(duration_qn)
                velocity_notes.append(velocity_norm)

            # Get channel name from first note if available
            channel_name = "Unknown"
            if notes_list:
                first_note = notes_list[0]
                if first_note.rack_channel in channels:
                    channel_name = channels[first_note.rack_channel]["name"]

            patterns_data[pattern_name] = {
                "midi": midi_notes,
                "time": time_notes,
                "duration": duration_notes,
                "velocity": velocity_notes,
                "channel_name": channel_name,
                "note_count": len(midi_notes)
            }

        # Build result with project metadata and pattern arrays
        result = {
            "project": {
                "name": project.title or "Untitled",
                "tempo": project.tempo,
                "ppq": project.ppq
            },
            "patterns": patterns_data
        }

        return json.dumps(result, separators=(',', ':'))  # Compact JSON without extra whitespace

    except TypeError as e:
        if "EventEnum" in str(e):
            return json.dumps({
                "error": "This FLP file appears to be incompatible with the current PyFLP version. "
                        "This might be due to: 1) FLP file created with a newer version of FL Studio, "
                        "2) Corrupted or protected project file, or 3) PyFLP library incompatibility. "
                        "Consider saving the project in an older FL Studio format or creating a new simple project for testing.",
                "file_path": str(found_path),
                "error_type": "EventEnum"
            })
        else:
            raise

    except Exception as e:
        return json.dumps({
            "error": f"Failed to read FLP file: {str(e)}",
            "file_path": str(found_path)
        })
