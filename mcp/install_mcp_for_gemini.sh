#!/bin/bash
# FL Studio MCP - Gemini CLI Registration
# Registers the MCP server with Gemini CLI

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
SERVER_SCRIPT="$SCRIPT_DIR/fl_studio_mcp_server.py"

echo "Registering FL Studio MCP server with Gemini CLI..."
echo "Script directory: $SCRIPT_DIR"
echo "Server script: $SERVER_SCRIPT"

gemini mcp remove fl-studio-mcp 2>/dev/null || true
gemini mcp add --transport stdio fl-studio-mcp "$VENV_PYTHON" "$SERVER_SCRIPT"