#!/usr/bin/env python3
"""
Test script to send F3+9 keyboard shortcut to focused piano roll window.
Waits 5 seconds for user to focus the window first.
"""

import time
from pynput.keyboard import Key, Controller

def send_f3_plus_9():
    """Send F3+9 keystroke"""
    print("Waiting 5 seconds... Focus the window now!")

    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    print("\nSending F3+9...")

    keyboard = Controller()

    # Press F3 and 9 together
    keyboard.press(Key.f3)
    keyboard.press('9')
    #time.sleep(0.1)
    keyboard.release('9')
    keyboard.release(Key.f3)

    print("✓ F3+9 sent")
    time.sleep(0.3)

if __name__ == '__main__':
    send_f3_plus_9()
