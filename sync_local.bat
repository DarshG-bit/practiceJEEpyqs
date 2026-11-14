@echo off
title Sync Local Files with GitHub
cd /d "%~dp0"
echo ============================================================
echo Syncing local files from GitHub (DarshG-bit/practiceJEEpyqs)...
echo ============================================================
echo.

set GIT_CMD=git
where git >nul 2>nul
if %errorlevel% neq 0 (
    set "GIT_CMD=C:\Program Files\Git\cmd\git.exe"
)

"%GIT_CMD%" pull origin main
echo.
echo ============================================================
echo Local files are now up-to-date with your website!
echo ============================================================
pause
