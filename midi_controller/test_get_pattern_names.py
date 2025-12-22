#!/usr/bin/env python3
"""Get list of all pattern names from FL Studio"""

from fl_dual_port import send_command, close_ports

try:
    # Get total pattern count
    count = int(send_command("patterns.patternCount()"))
    print(f"Total patterns: {count}\n")

    # Get each pattern name (1-based indexing)
    print("Pattern names:")
    for i in range(1, count + 1):
        name = send_command(f"patterns.getPatternName({i})")
        print(f"  {i}: {name}")

except Exception as e:
    print(f"Error: {e}")
finally:
    close_ports()
