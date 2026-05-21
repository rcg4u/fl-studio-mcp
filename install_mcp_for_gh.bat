@echo off
REM FL Studio MCP - GitHub CLI (gh) Registration (Windows)
REM Creates a gh alias to run the MCP server from the repository venv

SETLOCAL ENABLEDELAYEDEXPANSION
SET SCRIPT_DIR=%~dp0
IF "%SCRIPT_DIR:~-1%"=="\" SET SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
SET VENV_PYTHON=%SCRIPT_DIR%\.venv\Scripts\python.exe
SET SERVER_SCRIPT=%SCRIPT_DIR%\fl_studio_mcp_server.py
nwhere gh >nul 2>nulnIF %ERRORLEVEL% NEQ 0 (
    echo ERROR: gh CLI not found. Install GitHub CLI and authenticate first.
    exit /b 1
)
n:: Try to unset existing alias (ignore errors)
gh alias set mcp-fl-studio --unset 2>nul || rem ignore
n:: Create alias to run server via venv python
gh alias set mcp-fl-studio "%VENV_PYTHON% %SERVER_SCRIPT%"
echo gh alias 'mcp-fl-studio' created. Run with: gh mcp-fl-studio
ENDLOCAL
