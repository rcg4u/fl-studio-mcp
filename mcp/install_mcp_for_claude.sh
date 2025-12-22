#!/bin/bash
# FL Studio MCP - Claude Code Registration
# Registers the MCP server with Claude Code

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
SERVER_SCRIPT="$SCRIPT_DIR/fl_studio_mcp_server.py"

claude mcp remove fl-studio-mcp 2>/dev/null || true
claude mcp add --transport stdio fl-studio-mcp -- "$VENV_PYTHON" "$SERVER_SCRIPT"
