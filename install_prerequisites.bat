@echo off
REM FL Studio MCP - Prerequisites Installation Script (Windows)

SETLOCAL ENABLEDELAYEDEXPANSION

echo ============================================================
echo   FL Studio MCP - Prerequisites Installation (Windows)
echo ============================================================
echo.
:: Determine script directory
SET SCRIPT_DIR=%~dp0nIF "%SCRIPT_DIR:~-1%"=="\" SET SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
:: FL Studio scripts directory in Documents
SET FL_SCRIPTS_DIR=%USERPROFILE%\Documents\Image-Line\FL Studio\Settings\Piano roll scripts
:CHECK_PYTHON
echo.necho Checking for Python (py or python)...
where py >nul 2>nulnIF %ERRORLEVEL%==0 (
    SET PYTHON=py -3
) ELSE (
    where python >nul 2>nuln    IF %ERRORLEVEL%==0 (
        SET PYTHON=python
    ) ELSE (
        echo ERROR: Python not found in PATH. Install Python 3 and re-run this script.
        exit /b 1
    )
)
necho.necho ------------------------------------------------------------
echo PART 1: Installing Python environmentnecho ------------------------------------------------------------
cd /d "%SCRIPT_DIR%"
REM Ask whether to use system Python or create and use a local virtualenv
set /p USE_VENV_CHOICE=Do you want to create and use a local virtualenv (.venv)? [Y/n]: 
IF /I "%USE_VENV_CHOICE%"=="n" (
    SET USE_VENV=0
) ELSE (
    SET USE_VENV=1
)

IF "%USE_VENV%"=="1" (
    IF EXIST "%SCRIPT_DIR%\.venv\" (
        echo Virtual environment exists, updating dependencies...
        "%SCRIPT_DIR%\.venv\Scripts\pip.exe" install -e .
        echo Installing optional Windows helpers: pywin32, pynput, pyautogui...
        "%SCRIPT_DIR%\.venv\Scripts\pip.exe" install pywin32 pynput pyautogui || echo Warning: optional package installation failed
    ) ELSE (
        echo Creating new virtual environment...
        %PYTHON% -m venv "%SCRIPT_DIR%\.venv"
        "%SCRIPT_DIR%\.venv\Scripts\pip.exe" install --upgrade pip
        "%SCRIPT_DIR%\.venv\Scripts\pip.exe" install -e .
        echo Installing optional Windows helpers: pywin32, pynput, pyautogui...
        "%SCRIPT_DIR%\.venv\Scripts\pip.exe" install pywin32 pynput pyautogui || echo Warning: optional package installation failed
    )
) ELSE (
    echo Using system Python for installation (may require admin privileges)...
    %PYTHON% -m pip install --upgrade pip || echo Warning: pip upgrade failed
    %PYTHON% -m pip install -e . || echo Warning: package installation failed
    echo Installing optional Windows helpers: pywin32, pynput, pyautogui...
    %PYTHON% -m pip install pywin32 pynput pyautogui || echo Warning: optional package installation failed
)
necho.necho ------------------------------------------------------------
echo PART 2: Setting Up FL Studio scriptsnecho ------------------------------------------------------------
necho FL Studio scripts directory: "%FL_SCRIPTS_DIR%"
IF NOT EXIST "%FL_SCRIPTS_DIR%" (
    echo ERROR: FL Studio scripts directory not found!
    echo Expected: "%FL_SCRIPTS_DIR%"    
    echo Please make sure FL Studio is installed and the folder exists.
    exit /b 1
)
necho Copying ComposeWithLLM.pyscript to FL Studio...
copy /Y "%SCRIPT_DIR%\ComposeWithLLM.pyscript" "%FL_SCRIPTS_DIR%\" >nul 2>nulnIF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to copy ComposeWithLLM.pyscript
    exit /b 1
) ELSE (
    echo ComposeWithLLM.pyscript installed
)
necho Creating initial JSON files...
echo [] > "%FL_SCRIPTS_DIR%\mcp_request.json"
echo {} > "%FL_SCRIPTS_DIR%\mcp_response.json"
echo {"ppq": 96, "noteCount": 0, "notes": []} > "%FL_SCRIPTS_DIR%\piano_roll_state.json"
necho.necho ============================================================
echo Prerequisites Installation Complete!
echo.necho Next steps:necho  1) Register with Claude Code: install_mcp_for_claude.batnecho  2) (Optional) Register with Gemini or Codex: install_mcp_for_gemini.bat install_mcp_for_codex.batnecho  3) Open FL Studio and run ComposeWithLLM once (Tools -> Scripting -> ComposeWithLLM)
necho.necho Happy composing!
ENDLOCAL
