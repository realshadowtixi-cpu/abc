@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.11+ is required to build from source.
  echo You can instead use the included GitHub Actions workflow to build the EXE in the cloud.
  pause
  exit /b 1
)
py -m pip install --upgrade pip pyinstaller
py -m PyInstaller --noconfirm --clean --onefile --windowed --name ShadowClient launcher\shadow_launcher.py
if errorlevel 1 (
  echo EXE build failed.
  pause
  exit /b 1
)
echo EXE created at dist\ShadowClient.exe
pause
