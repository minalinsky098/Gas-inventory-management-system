@echo off
REM Batch file to install Python Willow image processing library
setlocal

:: Check for Python installation
echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Error: Python not found. Please install Python and add it to PATH.
        echo Download Python: https://www.python.org/downloads/
        timeout /t 5
        exit /b 1
    )
    set py_cmd=python3
) else (
    set py_cmd=python
)

:: Check for pip
echo Checking for pip...
%py_cmd% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip not found. Attempting to install pip...
    %py_cmd% -m ensurepip --default-pip >nul 2>&1
    if %errorlevel% neq 0 (
        echo Failed to install pip. Please install pip manually.
        timeout /t 5
        exit /b 1
    )
)

:: Install Willow library
echo Installing Willow library...
%py_cmd% -m pip install willow --quiet

if %errorlevel% equ 0 (
    echo Successfully installed Willow!
) else (
    echo Failed to install Willow. Check permissions and internet connection.
)

endlocal
timeout /t 3