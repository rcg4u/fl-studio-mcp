#!/usr/bin/env python3
"""
Print intro/metadata info about the piano roll state (no note details).
"""
import os
import json

state_file = os.path.expanduser("~/Documents/Image-Line/FL Studio/Settings/Piano roll scripts/piano_roll_state.json")

try:
    with open(state_file, 'r') as f:
        data = json.load(f)

except FileNotFoundError:
    pass
except Exception as e:
    pass
