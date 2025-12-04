@echo off
echo Starting FastAPI backend on http://127.0.0.1:8000 ...
call venv\Scripts\activate
uvicorn backend.app.main:app --reload --port 8000