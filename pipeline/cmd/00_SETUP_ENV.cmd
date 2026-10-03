@echo off
setlocal
cd /d "%~dp0.."
if not exist logs mkdir logs
echo ============================================================
echo PAPER19 - SETUP ENVIRONMENT
echo ============================================================
where py >nul 2>nul
if %errorlevel%==0 (
  set PYCMD=py -3
) else (
  set PYCMD=python
)
if not exist .venv (
  %PYCMD% -m venv .venv
  if errorlevel 1 goto :fail
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto :fail
pip install -r requirements.txt
if errorlevel 1 goto :fail
python -c "import sys, numpy, pandas, sklearn, scipy, matplotlib, requests; print(sys.version); print('numpy',numpy.__version__); print('pandas',pandas.__version__); print('sklearn',sklearn.__version__)"
echo SETUP COMPLETE
exit /b 0
:fail
echo SETUP FAILED. Check the messages above.
exit /b 1
