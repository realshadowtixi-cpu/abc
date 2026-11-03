@echo off
setlocal EnableExtensions
set "GRADLE_VERSION=8.12.1"
set "CACHE=%USERPROFILE%\.gradle\shadow-bootstrap\gradle-%GRADLE_VERSION%"
set "ZIP=%USERPROFILE%\.gradle\shadow-bootstrap\gradle-%GRADLE_VERSION%-bin.zip"
if not exist "%CACHE%\bin\gradle.bat" (
  echo Downloading Gradle %GRADLE_VERSION%...
  if not exist "%USERPROFILE%\.gradle\shadow-bootstrap" mkdir "%USERPROFILE%\.gradle\shadow-bootstrap"
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing 'https://services.gradle.org/distributions/gradle-%GRADLE_VERSION%-bin.zip' -OutFile '%ZIP%'"
  if errorlevel 1 exit /b 1
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%ZIP%' -DestinationPath '%USERPROFILE%\.gradle\shadow-bootstrap' -Force"
  if errorlevel 1 exit /b 1
)
call "%CACHE%\bin\gradle.bat" %*
exit /b %ERRORLEVEL%
