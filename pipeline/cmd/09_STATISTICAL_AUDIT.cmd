@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found. Run cmd\00_SETUP_ENV.cmd first.
  exit /b 1
)
echo ============================================================
echo PAPER19 - PHASE 09 STATISTICAL AUDIT
echo ============================================================
.venv\Scripts\python.exe scripts\09_statistical_audit.py > logs\09_STATISTICAL_AUDIT.log 2>&1
set RC=%errorlevel%
type logs\09_STATISTICAL_AUDIT.log
if not "%RC%"=="0" exit /b %RC%
echo PHASE 09 COMPLETE
