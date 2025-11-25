@echo off
echo ========================================
echo   SmartSort AI - Starting Expo Server
echo ========================================
echo.
cd /d "%~dp0mobile"
echo Current directory: %CD%
echo.
echo Starting Expo development server...
echo QR Code will appear below!
echo.
echo Press Ctrl+C to stop the server
echo.
npx expo start

