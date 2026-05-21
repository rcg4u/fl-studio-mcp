#!/bin/bash
# FL Studio MCP - GitHub CLI (gh) Registration
# Creates a gh alias to run the MCP server from the repository venv

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
SERVER_SCRIPT="$SCRIPT_DIR/fl_studio_mcp_server.py"

if ! command -v gh >/dev/null; then
  echo "ERROR: gh CLI not found. Install GitHub CLI and authenticate first."
  exit 1
fi

# Remove existing alias if present
if gh alias list | grep -q "^mcp-fl-studio\b"; then
  gh alias set mcp-fl-studio --unset 2>/dev/null || true
fi

# Set alias to run server using venv python
gh alias set mcp-fl-studio "$VENV_PYTHON $SERVER_SCRIPT"

echo "gh alias 'mcp-fl-studio' created. Run with: gh mcp-fl-studio"
