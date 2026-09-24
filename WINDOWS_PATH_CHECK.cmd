@echo off
setlocal
pushd "%~dp0" >nul || exit /b 1
if "%PYTHON%"=="" set "PYTHON=python"
"%PYTHON%" -B WINDOWS_PATH_CHECK.py
set "RC=%ERRORLEVEL%"
popd >nul
endlocal & exit /b %RC%
