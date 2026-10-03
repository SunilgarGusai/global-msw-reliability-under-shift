@echo off
setlocal
cd /d "%~dp0"
call 00_SETUP_ENV.cmd
if errorlevel 1 exit /b 1

call 01_FETCH_FREEZE_DATA.cmd
if errorlevel 1 exit /b 1

call 02_BUILD_COHORTS.cmd
if errorlevel 1 exit /b 1

call 03_PRIMARY_MODELS.cmd
if errorlevel 1 exit /b 1

call 04_CONFORMAL_SELECTIVE.cmd
if errorlevel 1 exit /b 1

call 05_ROBUSTNESS.cmd
if errorlevel 1 exit /b 1

call 06_SECONDARY_ENDPOINT.cmd
if errorlevel 1 exit /b 1

call 07_FIGURES_TABLES.cmd
if errorlevel 1 exit /b 1

call 08_VERIFY_REPRODUCIBILITY.cmd
if errorlevel 1 exit /b 1

echo ============================================================
echo PAPER19 ALL PHASES COMPLETED SUCCESSFULLY
echo ============================================================
echo Send these back to ChatGPT:
echo   logs\
echo   outputs\tables\
echo   reproducibility\verification_report.md
echo   reproducibility\file_manifest.csv
exit /b 0
