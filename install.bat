@echo off
REM cryoDL Installation Script for Windows
REM This script installs cryoDL and sets up the CLI command

echo === cryoDL Installation Script ===
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

echo ✓ Python detected

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed or not in PATH
    echo Please install pip and try again
    pause
    exit /b 1
)

echo ✓ pip detected

REM Install the package
echo.
echo Installing cryoDL...
pip install -e .

REM Verify installation
cryodl --help >nul 2>&1
if errorlevel 1 (
    echo Error: cryoDL CLI was not installed properly
    echo Please check the installation output above for errors
    pause
    exit /b 1
)

echo cryoDL CLI installed successfully!
echo.
echo You can now use the 'cryodl' command from anywhere:
echo   cryodl --help                    # Show help
echo   cryodl init                      # Initialize configuration
echo   cryodl show                      # Show current configuration
echo.
echo For more information, visit: https://github.com/shenlab/cryoDL
pause
