@echo off
setlocal
cd /d "%~dp0mod"
echo Building SHADOW CLIENT Fabric mod...
call ..\gradlew.bat --no-daemon build
if errorlevel 1 (
  echo.
  echo BUILD FAILED. Copy the full error output and share it for troubleshooting.
  pause
  exit /b 1
)
echo.
echo Build complete. JAR is in mod\build\libs\
pause
