@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found. Run cmd\00_SETUP_ENV.cmd first.
  exit /b 1
)
echo ============================================================
echo PAPER19 - 04_CONFORMAL_SELECTIVE
echo ============================================================
.venv\Scripts\python.exe scripts\04_conformal_selective.py > logs\04_CONFORMAL_SELECTIVE.log 2>&1
set RC=%errorlevel%
type logs\04_CONFORMAL_SELECTIVE.log
if not "%RC%"=="0" (
  echo.
  echo PHASE FAILED: 04_CONFORMAL_SELECTIVE
  echo Log: logs\04_CONFORMAL_SELECTIVE.log
  exit /b %RC%
)
echo.
echo PHASE COMPLETE: 04_CONFORMAL_SELECTIVE
exit /b 0
