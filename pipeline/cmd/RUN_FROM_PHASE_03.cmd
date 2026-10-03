@echo off
setlocal
cd /d "%~dp0"
for %%F in (
  03_PRIMARY_MODELS.cmd
  04_CONFORMAL_SELECTIVE.cmd
  05_ROBUSTNESS.cmd
  06_SECONDARY_ENDPOINT.cmd
  07_FIGURES_TABLES.cmd
  08_VERIFY_REPRODUCIBILITY.cmd
) do (
  call %%F
  if errorlevel 1 exit /b 1
)
echo RESUME PIPELINE COMPLETE
