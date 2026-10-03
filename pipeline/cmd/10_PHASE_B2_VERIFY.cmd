@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found. Run cmd\00_SETUP_ENV.cmd first.
  exit /b 1
)
echo ============================================================
echo PAPER19 - PHASE 10 B2 VERIFICATION
echo ============================================================
.venv\Scripts\python.exe scripts\10_phaseB2_verify.py > logs\10_PHASE_B2_VERIFY.log 2>&1
set RC=%errorlevel%
type logs\10_PHASE_B2_VERIFY.log
if not "%RC%"=="0" exit /b %RC%
echo PHASE 10 COMPLETE
