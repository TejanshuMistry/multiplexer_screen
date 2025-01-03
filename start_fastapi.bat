@echo off
REM Check if the virtual environment exists
cd /d "C:\path\to\your\fastapi\project"
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the FastAPI server
echo Starting FastAPI server...
uvicorn main:app --reload --host 0.0.0.0 --port 8000