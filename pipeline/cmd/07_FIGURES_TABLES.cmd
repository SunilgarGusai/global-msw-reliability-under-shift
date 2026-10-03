@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
if not exist .venv\Scripts\python.exe (
  echo ERROR: .venv not found. Run cmd\00_SETUP_ENV.cmd first.
  exit /b 1
)
echo ============================================================
echo PAPER19 - 07_FIGURES_TABLES
echo ============================================================
.venv\Scripts\python.exe scripts\07_figures_tables.py > logs\07_FIGURES_TABLES.log 2>&1
set RC=%errorlevel%
type logs\07_FIGURES_TABLES.log
if not "%RC%"=="0" (
  echo.
  echo PHASE FAILED: 07_FIGURES_TABLES
  echo Log: logs\07_FIGURES_TABLES.log
  exit /b %RC%
)
echo.
echo PHASE COMPLETE: 07_FIGURES_TABLES
exit /b 0
