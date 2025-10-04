@echo off
echo === Project Sentinel Setup and Demo ===
echo.

REM Try different Python installation methods
echo Attempting to install Flask dependencies...

REM Method 1: Try with --user flag
echo Method 1: Installing with --user flag...
python -m pip install --user flask flask-socketio flask-cors requests
if %errorlevel% equ 0 (
    echo Success with --user installation!
    goto :run_demo
)

REM Method 2: Try without version constraints
echo Method 2: Installing latest versions...
python -m pip install --user flask flask-socketio flask-cors requests --no-deps
if %errorlevel% equ 0 (
    echo Success with latest versions!
    goto :run_demo
)

REM Method 3: Try with conda if available
echo Method 3: Trying with conda...
where conda >nul 2>nul
if %errorlevel% equ 0 (
    conda install -c conda-forge flask flask-socketio flask-cors requests -y
    if %errorlevel% equ 0 (
        echo Success with conda!
        goto :run_demo
    )
)

REM Method 4: Use standalone version
echo All installation methods failed. Using standalone version...
goto :run_standalone

:run_demo
echo.
echo Starting full Flask demo...
python run_demo.py
goto :end

:run_standalone
echo.
echo Starting standalone demo (no external dependencies)...
python run_standalone.py
goto :end

:end
echo.
pause