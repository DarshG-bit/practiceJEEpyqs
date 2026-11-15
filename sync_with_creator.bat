@echo off
echo ========================================================
echo JEE Main PYQ Practice - Sync with Original Creator Repo
echo ========================================================
echo.
echo Fetching latest updates from upstream (rupinderiitb/practicemakesperfect)...
git fetch upstream main
if errorlevel 1 (
    echo [ERROR] Failed to fetch from upstream. Check your internet connection.
    pause
    exit /b %errorlevel%
)
echo.
echo Merging upstream changes into your local branch...
git merge upstream/main -m "Merge upstream updates from original repo"
if errorlevel 1 (
    echo [NOTICE] Merge conflict or automatic merge paused.
    echo Please resolve any conflicts or press any key to continue.
    pause
)
echo.
echo Re-running automated patcher to keep all enhancements, dark mode & portal synced...
python patch_all.py
echo.
echo ========================================================
echo Sync completed successfully!
echo ========================================================
pause
