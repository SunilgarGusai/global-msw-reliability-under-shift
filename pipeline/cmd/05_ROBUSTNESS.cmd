@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found. Run cmd\00_SETUP_ENV.cmd first.
  exit /b 1
)
echo ============================================================
echo PAPER19 - 05_ROBUSTNESS
echo ============================================================
.venv\Scripts\python.exe scripts\05_robustness.py > logs\05_ROBUSTNESS.log 2>&1
set RC=%errorlevel%
type logs\05_ROBUSTNESS.log
if not "%RC%"=="0" (
  echo.
  echo PHASE FAILED: 05_ROBUSTNESS
  echo Log: logs\05_ROBUSTNESS.log
  exit /b %RC%
)
echo.
echo PHASE COMPLETE: 05_ROBUSTNESS
exit /b 0
