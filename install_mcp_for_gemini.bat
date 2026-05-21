@echo off
REM FL Studio MCP - Gemini CLI Registration (Windows)
nSET SCRIPT_DIR=%~dp0nIF "%SCRIPT_DIR:~-1%"=="\" SET SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
SET VENV_PYTHON=%SCRIPT_DIR%\.venv\Scripts\python.exe
SET SERVER_SCRIPT=%SCRIPT_DIR%\fl_studio_mcp_server.py
necho Registering fl-studio-mcp with Gemini (if 'gemini' CLI is available)...
gemini mcp remove fl-studio-mcp 2>nul
gemini mcp add fl-studio-mcp "%VENV_PYTHON%" "%SERVER_SCRIPT%"
necho Done.
