@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found. Run cmd\00_SETUP_ENV.cmd first.
  exit /b 1
)
echo ============================================================
echo PAPER19 - 02_BUILD_COHORTS
echo ============================================================
.venv\Scripts\python.exe scripts\02_build_cohorts.py > logs\02_BUILD_COHORTS.log 2>&1
set RC=%errorlevel%
type logs\02_BUILD_COHORTS.log
if not "%RC%"=="0" (
  echo.
  echo PHASE FAILED: 02_BUILD_COHORTS
  echo Log: logs\02_BUILD_COHORTS.log
  exit /b %RC%
)
echo.
echo PHASE COMPLETE: 02_BUILD_COHORTS
exit /b 0
