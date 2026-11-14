@echo off
title Sync with Rupinder (Original Creator)
cd /d "%~dp0"
echo ============================================================
echo Fetching latest updates from rupinderiitb/practicemakesperfect...
echo ============================================================
echo.
"C:\Program Files\Git\cmd\git.exe" fetch upstream main
echo.
echo Pulling new questions and chapters...
"C:\Program Files\Git\cmd\git.exe" checkout upstream/main -- Chemistry Maths Physics index.html
echo.
echo Running 1-step patcher (Dark Mode, PDF Notes, Option Fixes, Physics Unlock)...
python patch_all.py
echo.
echo Pushing updated and patched files to your website...
"C:\Program Files\Git\cmd\git.exe" add -A
"C:\Program Files\Git\cmd\git.exe" commit -m "chore: sync latest questions from creator and auto-patch"
"C:\Program Files\Git\cmd\git.exe" push origin main
echo.
echo ============================================================
echo DONE! All new questions synced, patched, and live!
echo Website: https://darshg-bit.github.io/practiceJEEpyqs/
echo ============================================================
pause
