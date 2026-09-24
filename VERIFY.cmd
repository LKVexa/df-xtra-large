@echo off
REM DF_Xtra_Large\VERIFY.cmd -- Windows/UNC-safe verification launcher
setlocal
pushd "%~dp0" >nul || (echo ERROR: cannot enter package directory & exit /b 1)
if "%PYTHON%"=="" set "PYTHON=python"
"%PYTHON%" -B adapter\dfabric\cli.py node-verify %*
set "RC=%ERRORLEVEL%"
popd >nul
endlocal & exit /b %RC%
