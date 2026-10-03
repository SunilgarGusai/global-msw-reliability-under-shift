@echo off
setlocal
cd /d "%~dp0"
call 09_STATISTICAL_AUDIT.cmd
if errorlevel 1 exit /b 1
call 10_PHASE_B2_VERIFY.cmd
if errorlevel 1 exit /b 1
echo ============================================================
echo PAPER19 PHASE B2 COMPLETED
echo ============================================================
echo Please upload:
echo   logs\09_STATISTICAL_AUDIT.log
echo   logs\10_PHASE_B2_VERIFY.log
echo   outputs\tables\phaseB2_*.csv
echo   reproducibility\PHASE_B2_SCIENTIFIC_LOCK.md
echo   reproducibility\PHASE_B2_VERIFICATION_REPORT.md
