#!/bin/bash

# Setup MIDI Controllers for FL Studio
# Creates FLController directory and symlinks device scripts

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# FL Studio Hardware folder path
FL_HARDWARE_DIR="$HOME/Documents/Image-Line/FL Studio/Settings/Hardware"
FL_CONTROLLER_DIR="$FL_HARDWARE_DIR/FLController"

# Source paths for device scripts
DEVICE_REQUEST_SRC="$SCRIPT_DIR/midi_controller/device_FLRequest.py"
DEVICE_RESPONSE_SRC="$SCRIPT_DIR/midi_controller/device_FLResponse.py"

# Destination paths for symlinks
DEVICE_REQUEST_DEST="$FL_CONTROLLER_DIR/device_FLRequest.py"
DEVICE_RESPONSE_DEST="$FL_CONTROLLER_DIR/device_FLResponse.py"

echo "Setting up MIDI Controllers for FL Studio..."
echo ""

# Check if source files exist
if [ ! -f "$DEVICE_REQUEST_SRC" ]; then
  echo "❌ Error: device_FLRequest.py not found at $DEVICE_REQUEST_SRC"
  exit 1
fi

if [ ! -f "$DEVICE_RESPONSE_SRC" ]; then
  echo "❌ Error: device_FLResponse.py not found at $DEVICE_RESPONSE_SRC"
  exit 1
fi

echo "✓ Source files found"
echo "  - $DEVICE_REQUEST_SRC"
echo "  - $DEVICE_RESPONSE_SRC"
echo ""

# Create FLController directory if it doesn't exist
if [ ! -d "$FL_CONTROLLER_DIR" ]; then
  echo "Creating directory: $FL_CONTROLLER_DIR"
  mkdir -p "$FL_CONTROLLER_DIR"
  echo "✓ Directory created"
else
  echo "✓ Directory already exists: $FL_CONTROLLER_DIR"
fi

echo ""

# Remove old symlinks if they exist (broken or otherwise)
if [ -L "$DEVICE_REQUEST_DEST" ] || [ -f "$DEVICE_REQUEST_DEST" ]; then
  echo "Removing old device_FLRequest.py..."
  rm -f "$DEVICE_REQUEST_DEST"
fi

if [ -L "$DEVICE_RESPONSE_DEST" ] || [ -f "$DEVICE_RESPONSE_DEST" ]; then
  echo "Removing old device_FLResponse.py..."
  rm -f "$DEVICE_RESPONSE_DEST"
fi

echo ""

# Create symlinks
echo "Creating symlinks..."
ln -s "$DEVICE_REQUEST_SRC" "$DEVICE_REQUEST_DEST"
echo "✓ Symlink created: device_FLRequest.py"

ln -s "$DEVICE_RESPONSE_SRC" "$DEVICE_RESPONSE_DEST"
echo "✓ Symlink created: device_FLResponse.py"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Open FL Studio"
echo "2. Go to Options → MIDI Settings"
echo "3. Select 'FLRequest (user)' and 'FLResponse (user)' in the Controller type list"
echo "4. Load both scripts in the Script output window"
echo "5. Verify both show 'init ok'"
echo ""
echo "To verify the symlinks:"
echo "  ls -la '$FL_CONTROLLER_DIR'"
