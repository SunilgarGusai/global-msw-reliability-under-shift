@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found. Run cmd\00_SETUP_ENV.cmd first.
  exit /b 1
)
echo ============================================================
echo PAPER19 - 08_VERIFY_REPRODUCIBILITY
echo ============================================================
.venv\Scripts\python.exe scripts\08_verify_reproducibility.py > logs\08_VERIFY_REPRODUCIBILITY.log 2>&1
set RC=%errorlevel%
type logs\08_VERIFY_REPRODUCIBILITY.log
if not "%RC%"=="0" (
  echo.
  echo PHASE FAILED: 08_VERIFY_REPRODUCIBILITY
  echo Log: logs\08_VERIFY_REPRODUCIBILITY.log
  exit /b %RC%
)
echo.
echo PHASE COMPLETE: 08_VERIFY_REPRODUCIBILITY
exit /b 0
