@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found. Run cmd\00_SETUP_ENV.cmd first.
  exit /b 1
)
echo ============================================================
echo PAPER19 - 01_FETCH_FREEZE_DATA
echo ============================================================
.venv\Scripts\python.exe scripts\01_fetch_data.py > logs\01_FETCH_FREEZE_DATA.log 2>&1
set RC=%errorlevel%
type logs\01_FETCH_FREEZE_DATA.log
if not "%RC%"=="0" (
  echo.
  echo PHASE FAILED: 01_FETCH_FREEZE_DATA
  echo Log: logs\01_FETCH_FREEZE_DATA.log
  exit /b %RC%
)
echo.
echo PHASE COMPLETE: 01_FETCH_FREEZE_DATA
exit /b 0
