@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ================================
REM Resolve project root (script dir)
REM ================================
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo [INFO] Project directory: %PROJECT_DIR%

REM ================================
REM Config
REM ================================
set "VENV_DIR=%PROJECT_DIR%venv"
set "PYTHON_EXEC=python"
set "APP_FILE=Pasted code.py"
set "REQUIREMENTS_FILE=requirements.txt"

REM ================================
REM Validate Python availability
REM ================================
where %PYTHON_EXEC% >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found in PATH.
    echo Install Python and ensure it is added to PATH.
    pause
    exit /b 1
)

REM ================================
REM Create venv if not exists
REM ================================
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    %PYTHON_EXEC% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Virtual environment already exists. Skipping creation.
)

REM ================================
REM Activate venv
REM ================================
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM ================================
REM Upgrade pip safely
REM ================================
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip >nul

REM ================================
REM Ensure requirements file exists
REM ================================
if not exist "%REQUIREMENTS_FILE%" (
    echo [INFO] requirements.txt not found. Creating default...

    echo streamlit> "%REQUIREMENTS_FILE%"
    echo pandas>> "%REQUIREMENTS_FILE%"
    echo pillow>> "%REQUIREMENTS_FILE%"
)

REM ================================
REM Install dependencies (idempotent)
REM ================================
echo [INFO] Installing dependencies (safe/idempotent)...
pip install -r "%REQUIREMENTS_FILE%"
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)

REM ================================
REM Validate app file
REM ================================
if not exist "%APP_FILE%" (
    echo [ERROR] App file not found: %APP_FILE%
    echo Make sure your file exists in project root.
    pause
    exit /b 1
)

REM ================================
REM Run Streamlit
REM ================================
echo [INFO] Starting Streamlit app...
echo.

streamlit run "%APP_FILE%"

REM ================================
REM Cleanup (optional)
REM ================================
echo.
echo [INFO] App stopped.
pause