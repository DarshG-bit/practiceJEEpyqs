@echo off
title Push Updates to GitHub
cd /d "%~dp0"
echo ============================================================
echo Pushing JEE PYQ Practice to GitHub (DarshG-bit/practiceJEEpyqs)
echo ============================================================
echo.
echo If a browser tab opens, please click "Sign in with browser"
echo to authorize Git for your GitHub account.
echo.
"C:\Program Files\Git\cmd\git.exe" push -u origin main --force
echo.
echo ============================================================
echo All files pushed successfully!
echo Your website will be live in ~30 seconds at:
echo https://darshg-bit.github.io/practiceJEEpyqs/
echo ============================================================
pause
