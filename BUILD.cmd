@echo off
REM DF_Xtra_Large\BUILD.cmd -- Windows/UNC-safe build launcher
setlocal
pushd "%~dp0" >nul || (echo ERROR: cannot enter package directory & exit /b 1)
if "%PYTHON%"=="" set "PYTHON=python"
"%PYTHON%" -B adapter\dfabric\cli.py node-build %*
set "RC=%ERRORLEVEL%"
popd >nul
endlocal & exit /b %RC%
