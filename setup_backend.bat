@echo off
echo ==========================================
echo  Backend Setup - Python / FastAPI
echo ==========================================
echo.

:: Create virtual environment if it does not exist
if not exist venv (
    echo Creating virtual environment "venv"...
    python -m venv venv
) else (
    echo Virtual environment "venv" already exists.
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing backend requirements from requirements.txt...
pip install -r requirements.txt

echo.
echo Backend setup complete.
echo You can now run "run_backend.bat" to start the API server.
echo.
pause