#!/usr/bin/env python3
"""Read MIDI notes from an FL Studio project file using PyFLP."""

import pyflp

def read_flp_notes(flp_path):
    """Parse an FLP file and extract MIDI notes from all patterns.

    Args:
        flp_path: Path to the FLP file
    """
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
        flp_file = "TestTwoTrack.flp"

    read_flp_notes(flp_file)
