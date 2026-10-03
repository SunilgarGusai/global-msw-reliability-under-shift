@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title PAPER19 GitHub Publisher

set "REPO=SunilgarGusai/global-msw-reliability-under-shift"
set "REMOTE=https://github.com/%REPO%.git"
set "TAG=v1.0.0-submission"

echo ============================================================
echo PAPER19 - Global MSW Reliability GitHub Publisher
echo Target: %REPO%
echo Mode: public reproducibility repository
echo ============================================================
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo ERROR: Git was not found on PATH.
  echo Install Git for Windows, reopen this folder, and run this file again.
  goto :fail
)

git --version
if errorlevel 1 goto :fail

if not exist ".git" (
  echo.
  echo Initializing local repository...
  git init
  if errorlevel 1 goto :fail
  git branch -M main
  if errorlevel 1 goto :fail
)

git config user.name >nul 2>&1
if errorlevel 1 git config user.name "Dr. Sunilgar L. Gusai"
git config user.email >nul 2>&1
if errorlevel 1 git config user.email "dr.sunilgargusai@gmail.com"

echo.
echo Staging frozen reproducibility artifact...
git add -A
if errorlevel 1 goto :fail

git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Freeze submission reproducibility artifact v1.0.0-submission"
  if errorlevel 1 goto :fail
) else (
  echo No new staged changes to commit.
)

git remote get-url origin >nul 2>&1
if errorlevel 1 (
  echo.
  echo Adding GitHub remote...
  git remote add origin %REMOTE%
  if errorlevel 1 goto :fail
) else (
  git remote set-url origin %REMOTE%
)

echo.
echo Fetching existing remote state...
git fetch origin main --tags
if errorlevel 1 (
  echo WARNING: Initial fetch did not complete. Continuing because the repository may be new.
)

echo.
echo Publishing the complete frozen repository...
echo The remote currently contains only the initialization created for PAPER19.
echo Using --force-with-lease to replace that initialization with the curated frozen artifact.
git push -u origin main --force-with-lease
if errorlevel 1 goto :fail

echo.
echo Creating/updating frozen submission tag...
git tag -fa %TAG% -m "Frozen submission reproducibility archive"
if errorlevel 1 goto :fail
git push origin refs/tags/%TAG% --force
if errorlevel 1 goto :fail

echo.
echo Verifying remote main and tag...
git ls-remote --exit-code origin refs/heads/main >nul 2>&1
if errorlevel 1 goto :fail
git ls-remote --exit-code origin refs/tags/%TAG% >nul 2>&1
if errorlevel 1 goto :fail

echo.
where gh >nul 2>&1
if errorlevel 1 goto :nogh

gh auth status >nul 2>&1
if errorlevel 1 goto :nogh

echo GitHub CLI detected. Creating the frozen release if it does not already exist...
gh release view %TAG% --repo %REPO% >nul 2>&1
if errorlevel 1 (
  gh release create %TAG% --repo %REPO% --title "%TAG% - Frozen reproducibility archive" --notes-file RELEASE_NOTES_v1.0.0-submission.md
  if errorlevel 1 echo WARNING: Repository push succeeded, but automatic release creation did not complete.
) else (
  echo Release %TAG% already exists.
)
goto :success

:nogh
echo GitHub CLI is not installed or not authenticated. This is not an error.
echo The repository and frozen tag are already published.
echo A GitHub Release can be created from tag %TAG% in the browser.

:success
echo.
echo ============================================================
echo SUCCESS: PAPER19 reproducibility repository is published.
echo Repository: https://github.com/%REPO%
echo Frozen tag: %TAG%
echo NEXT: confirm the Repository verification Action is green.
echo Upload/share the final console screenshot only if an error appears.
echo ============================================================
pause
exit /b 0

:fail
echo.
echo ============================================================
echo ERROR: GitHub publication stopped.
echo Read the message above and send it back for correction.
echo This window will remain open.
echo ============================================================
pause
exit /b 1
