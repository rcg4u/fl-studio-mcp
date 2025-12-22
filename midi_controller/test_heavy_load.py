#!/usr/bin/env python3
"""
Stress test for the chunked FL Studio communication system.
Sends a large request and expects a large response to verify chunking.
"""

import sys
import time
from pathlib import Path

# Add venv packages to path
venv_site_packages = Path(__file__).parent / ".venv/lib"
for path in venv_site_packages.glob("python*/site-packages"):
    sys.path.insert(0, str(path))

from fl_dual_port import send_command, close_ports

def test_heavy_load():
    """Test sending/receiving large payloads"""
    print("=== Testing Heavy Load (Chunking) ===\n")

    try:
        # 1. Large Request
        # Send a script that generates a large string on the server
        print("1. Sending large request (generating 5KB string)...")
        
        # This python code runs INSIDE FL Studio
        long_script = """
def generate_large_data():
    data = []
    for i in range(500):
        data.append(f"Line {i}: This is some filler text to make the payload larger.")
    return "\n".join(data)

generate_large_data()
"""
        # We need to be careful with newlines in eval(), but let's try a simpler approach first
        # Since our eval() only handles expressions, we can't define functions easily.
        # Use a simpler expression that doesn't rely on complex string escaping
        # Join a list of strings with a space
        cmd = "' '.join([f'Line_{i}_FillerText_{i}' for i in range(200)])"
        
        start_time = time.time()
        result = send_command(cmd)
        duration = time.time() - start_time
        
        size_bytes = len(result.encode('utf-8'))
        print(f"   Received {size_bytes} bytes in {duration:.2f} seconds")
        print(f"   First line: {result.splitlines()[0]}")
        print(f"   Last line: {result.splitlines()[-1]}")
        
        if size_bytes > 4000:
            print("✅ Large payload received successfully!")
        else:
            print(f"⚠️ Warning: Payload smaller than expected ({size_bytes} bytes)")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        close_ports()

if __name__ == "__main__":
    test_heavy_load()
