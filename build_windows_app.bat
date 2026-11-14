@echo off
title Build JEE Main PYQ Practice Windows App
cd /d "%~dp0\windows-app"
echo ============================================================
echo Compiling Native Windows Desktop App (.NET 8 + WebView2)...
echo ============================================================
echo.

"C:\Program Files\dotnet\dotnet.EXE" publish -c Release -o "%~dp0\JEE-Windows-App"

echo.
echo ============================================================
echo BUILD COMPLETE!
echo Your native Windows app is ready at:
echo "%~dp0JEE-Windows-App\JEEPYQPractice.exe"
echo ============================================================
echo.
echo Press any key to launch the app now...
pause >nul
start "" "%~dp0\JEE-Windows-App\JEEPYQPractice.exe"
