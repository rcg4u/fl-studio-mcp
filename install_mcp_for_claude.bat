@echo off
REM FL Studio MCP - Claude Code Registration (Windows)
nSET SCRIPT_DIR=%~dp0nIF "%SCRIPT_DIR:~-1%"=="\" SET SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
SET VENV_PYTHON=%SCRIPT_DIR%\.venv\Scripts\python.exe
SET SERVER_SCRIPT=%SCRIPT_DIR%\fl_studio_mcp_server.py
necho Registering fl-studio-mcp with Claude (if 'claude' CLI is available)...
claude mcp remove fl-studio-mcp 2>nul
claude mcp add --transport stdio fl-studio-mcp -- "%VENV_PYTHON%" "%SERVER_SCRIPT%"
necho Done.
