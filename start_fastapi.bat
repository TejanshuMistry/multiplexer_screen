@echo off
REM Navigate to the FastAPI project directory
cd /d "C:\path\to\your\fastapi\project"

REM Check if the virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment. Exiting...
        pause
        exit /b %errorlevel%
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

REM Activate the virtual environment
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment. Exiting...
    pause
    exit /b %errorlevel%
)

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Failed to upgrade pip. Exiting...
    pause
    exit /b %errorlevel%
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies. Exiting...
    pause
    exit /b %errorlevel%
)

REM Run the FastAPI server
echo Starting FastAPI server...
uvicorn main:app --reload --host 0.0.0.0 --port 8000
if %errorlevel% neq 0 (
    echo Failed to start FastAPI server. Exiting...
    pause
    exit /b %errorlevel%
)

pause