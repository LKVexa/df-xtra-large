@echo off
REM DF_Xtra_Large\RUN.cmd -- Windows/UNC-safe run launcher
setlocal
pushd "%~dp0" >nul || (echo ERROR: cannot enter package directory & exit /b 1)
if "%PYTHON%"=="" set "PYTHON=python"
"%PYTHON%" -B adapter\dfabric\cli.py node-run %*
set "RC=%ERRORLEVEL%"
popd >nul
endlocal & exit /b %RC%
