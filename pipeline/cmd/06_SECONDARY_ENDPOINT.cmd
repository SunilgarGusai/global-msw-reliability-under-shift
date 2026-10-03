@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found. Run cmd\00_SETUP_ENV.cmd first.
  exit /b 1
)
echo ============================================================
echo PAPER19 - 06_SECONDARY_ENDPOINT
echo ============================================================
.venv\Scripts\python.exe scripts\06_secondary_endpoint.py > logs\06_SECONDARY_ENDPOINT.log 2>&1
set RC=%errorlevel%
type logs\06_SECONDARY_ENDPOINT.log
if not "%RC%"=="0" (
  echo.
  echo PHASE FAILED: 06_SECONDARY_ENDPOINT
  echo Log: logs\06_SECONDARY_ENDPOINT.log
  exit /b %RC%
)
echo.
echo PHASE COMPLETE: 06_SECONDARY_ENDPOINT
exit /b 0
