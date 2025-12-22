#!/usr/bin/env python3
"""Read MIDI notes from an FL Studio project file using PyFLP."""

import json
import pyflp

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

def read_flp_notes_json(flp_path):
    """Parse an FLP file and extract MIDI notes in piano roll JSON format.

    Args:
        flp_path: Path to the FLP file

    Returns:
        JSON data matching piano roll format with extra metadata
    """
    project = pyflp.parse(flp_path)

    # Create channel lookup
    channels = {}
    for i, channel in enumerate(project.channels):
        channels[channel.iid] = {
            "name": channel.name or f"Channel {i}",
            "iid": channel.iid
        }

    # Collect all notes with pattern and channel info
    all_notes = []
    for pattern in project.patterns:
        pattern_name = pattern.name or f"Pattern {pattern.iid}"

        for note in list(pattern.notes):
            # Convert note name to MIDI number
            midi_number = note_name_to_number(note.key)

            # Create note object matching piano roll format
            note_obj = {
                "number": midi_number,
                "time": note.position,
                "length": note.length,
                "velocity": note.velocity / 127.0,  # Convert 0-127 to 0-1
                "pan": 0.5,  # Default
                "color": 0,  # Default
                "fcut": 0.501960814,  # Default
                "fres": 0.501960814,  # Default
                "slide": False,  # Default
                "porta": False,  # Default
                # Extra metadata
                "pattern_name": pattern_name,
                "pattern_iid": pattern.iid,
                "channel_iid": note.rack_channel,
                "note_name": str(note.key)  # Keep original note name
            }

            # Add channel name if available
            if note.rack_channel in channels:
                note_obj["channel_name"] = channels[note.rack_channel]["name"]

            all_notes.append(note_obj)

    # Build result matching piano roll format
    result = {
        "ppq": project.ppq,
        "noteCount": len(all_notes),
        "notes": all_notes,
        # Extra metadata
        "project": {
            "name": project.title or "Untitled",
            "tempo": project.tempo,
            "ppq": project.ppq,
            "total_patterns": len(project.patterns),
            "total_channels": len(project.channels)
        },
        "patterns": {}
    }

    # Also organize by pattern for easier analysis
    for pattern in project.patterns:
        pattern_name = pattern.name or f"Pattern {pattern.iid}"
        result["patterns"][pattern_name] = {
            "iid": pattern.iid,
            "note_count": len(list(pattern.notes))
        }

    return result

def read_flp_notes_compact(flp_path):
    """Parse an FLP file and extract MIDI notes in compact array format.

    Args:
        flp_path: Path to the FLP file

    Returns:
        JSON data with compact array format organized by pattern
    """
    project = pyflp.parse(flp_path)

    # Create channel lookup
    channels = {}
    for i, channel in enumerate(project.channels):
        channels[channel.iid] = {
            "name": channel.name or f"Channel {i}",
            "iid": channel.iid
        }

    # Organize notes by pattern
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

    return result

def read_flp_notes(flp_path):
    """Legacy function that outputs human-readable text format."""
    project = pyflp.parse(flp_path)

    lines = []
    lines.append(f"Parsing: {flp_path}")
    lines.append(f"\nProject: {project.title or 'Untitled'}")
    lines.append(f"PPQ (ticks per quarter note): {project.ppq}")
    lines.append(f"Tempo: {project.tempo} BPM")

    # List channels
    lines.append("\n--- Channels ---")
    for i, channel in enumerate(project.channels):
        lines.append(f"  {i}: {channel.name} (IID: {channel.iid})")

    # Extract notes from patterns
    lines.append("\n--- Patterns and Notes ---")
    for pattern in project.patterns:
        lines.append(f"\nPattern: {pattern.name or f'Pattern {pattern.iid}'} (IID: {pattern.iid})")

        notes_list = list(pattern.notes)
        if notes_list:
            lines.append(f"  Notes ({len(notes_list)}):")
            for note in notes_list:
                # Position is in ticks (PPQ-based)
                pos_beats = note.position / project.ppq
                length_beats = note.length / project.ppq
                lines.append(f"    Key: {note.key:4s} | Pos: {note.position:6d} ticks ({pos_beats:6.2f} beats) | "
                      f"Length: {note.length:5d} ticks ({length_beats:.2f} beats) | "
                      f"Velocity: {note.velocity:3d} | Channel: {note.rack_channel}")
        else:
            lines.append("  (no notes)")

    output_text = "\n".join(lines)
    print(output_text)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        flp_file = sys.argv[1]
    else:
        flp_file = "test.flp"

    # Check output format
    if len(sys.argv) > 2:
        format_type = sys.argv[2]
        if format_type == "--json":
            result = read_flp_notes_json(flp_file)
            print(json.dumps(result, indent=2))
        elif format_type == "--compact":
            result = read_flp_notes_compact(flp_file)
            print(json.dumps(result, indent=2))
        elif format_type == "--save-compact":
            # Save compact format to file
            result = read_flp_notes_compact(flp_file)
            output_file = flp_file.replace('.flp', '_compact.json')
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Saved compact format to {output_file}")
        else:
            print(f"Unknown format: {format_type}")
            print("Available formats: --json, --compact, --save-compact")
    else:
        read_flp_notes(flp_file)
