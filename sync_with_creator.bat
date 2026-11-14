@echo off
title Sync with Rupinder (Original Creator)
cd /d "%~dp0"
echo ============================================================
echo Fetching latest updates from rupinderiitb/practicemakesperfect...
echo ============================================================
echo.

set GIT_CMD=git
where git >nul 2>nul
if %errorlevel% neq 0 (
    set "GIT_CMD=C:\Program Files\Git\cmd\git.exe"
)

"%GIT_CMD%" fetch upstream main
echo.
echo Pulling new questions and chapters from creator...
"%GIT_CMD%" checkout upstream/main -- Chemistry Maths Physics
echo.
echo Running 1-step patcher (Dark Mode, PDF Notes, Option Fixes, Random Test Pool)...
python patch_all.py
echo.
echo Pushing updated and patched files to your website...
"%GIT_CMD%" add -A
"%GIT_CMD%" commit -m "chore: sync latest questions from creator and auto-patch"
"%GIT_CMD%" push origin main
echo.
echo ============================================================
echo DONE! All new questions synced, patched, and live!
echo Website: https://darshg-bit.github.io/practiceJEEpyqs/
echo ============================================================
pause
