@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found. Run cmd\00_SETUP_ENV.cmd first.
  exit /b 1
)
echo ============================================================
echo PAPER19 - 03_PRIMARY_MODELS
echo ============================================================
.venv\Scripts\python.exe scripts\03_primary_models.py > logs\03_PRIMARY_MODELS.log 2>&1
set RC=%errorlevel%
type logs\03_PRIMARY_MODELS.log
if not "%RC%"=="0" (
  echo.
  echo PHASE FAILED: 03_PRIMARY_MODELS
  echo Log: logs\03_PRIMARY_MODELS.log
  exit /b %RC%
)
echo.
echo PHASE COMPLETE: 03_PRIMARY_MODELS
exit /b 0
