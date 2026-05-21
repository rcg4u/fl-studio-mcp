@echo off
REM FL Studio MCP - Codex CLI Registration (Windows)
nSET SCRIPT_DIR=%~dp0nIF "%SCRIPT_DIR:~-1%"=="\" SET SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
SET VENV_PYTHON=%SCRIPT_DIR%\.venv\Scripts\python.exe
SET SERVER_SCRIPT=%SCRIPT_DIR%\fl_studio_mcp_server.py
SET CODEX_CONFIG_DIR=%USERPROFILE%\.codex
SET CODEX_CONFIG_FILE=%CODEX_CONFIG_DIR%\config.toml
necho Ensuring Codex config directory exists...
IF NOT EXIST "%CODEX_CONFIG_DIR%" (
    mkdir "%CODEX_CONFIG_DIR%"
)
necho Appending MCP registration to %CODEX_CONFIG_FILE%...
echo.>>"%CODEX_CONFIG_FILE%"
echo [mcp_servers.fl-studio-mcp]>>"%CODEX_CONFIG_FILE%"
echo command = "%VENV_PYTHON%" >> "%CODEX_CONFIG_FILE%"
echo args = ["%SERVER_SCRIPT%"] >> "%CODEX_CONFIG_FILE%"
necho Done. Note: This appends registration and may create duplicate entries if run multiple times.
