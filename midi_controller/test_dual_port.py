#!/usr/bin/env python3
"""
Test the dual-controller FL Studio communication system.
"""

import sys
from pathlib import Path

# Add venv packages to path
venv_site_packages = Path(__file__).parent / ".venv/lib"
for path in venv_site_packages.glob("python*/site-packages"):
    sys.path.insert(0, str(path))

from fl_dual_port import send_command, close_ports

def test_dual_port():
    """Test dual-port communication"""
    print("=== Testing Dual-Controller System ===\n")

    try:
        # Test 1: Get pattern count
        print("1. Getting pattern count...")
        result = send_command("patterns.patternCount()")
        print(f"   Pattern count: {result}\n")

        # Test 2: Get first pattern name
        print("2. Getting first pattern name...")
        result = send_command("patterns.getPatternName(0)")
        print(f"   Pattern name: {result}\n")

        # Test 3: Get current pattern
        print("3. Getting current pattern...")
        result = send_command("patterns.patternNumber()")
        print(f"   Current pattern: {result}\n")

        # Test 4: Get Channel Names
        print("4. Getting channel names...")
        channel_count = int(send_command("channels.channelCount()"))
        print(f"   Total channels: {channel_count}")
        
        for i in range(min(channel_count, 5)): # Limit to first 5 for brevity
            name = send_command(f"channels.getChannelName({i})")
            print(f"   Channel {i}: {name}")
        print("")

        # Test 5: Switch pattern (no response)
        print("5. Switching to pattern 1 (no response)...")
        send_command("patterns.jumpToPattern(0)", expect_response=False)
        print("   Command sent\n")

        print("✅ All tests passed! Dual-controller system is working.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        close_ports()

if __name__ == "__main__":
    test_dual_port()