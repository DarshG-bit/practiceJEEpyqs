@echo off
title Sync Local Files with GitHub
cd /d "%~dp0"
echo ============================================================
echo Syncing local files from GitHub (DarshG-bit/practiceJEEpyqs)...
echo ============================================================
echo.
"C:\Program Files\Git\cmd\git.exe" pull origin main
echo.
echo ============================================================
echo Local files are now up-to-date with your website!
echo ============================================================
pause
