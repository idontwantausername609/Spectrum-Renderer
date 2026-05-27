@echo off
REM Run the local Spectrum webapp using the Anaconda 'base' environment.
REM Double-click this file to start the app in a new terminal window.

:: Attempt to activate conda (assumes default install location in %USERPROFILE%\anaconda3)
if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\anaconda3\Scripts\activate.bat" base
) else (
    echo Could not find activate.bat; make sure Anaconda is installed and in %USERPROFILE%\anaconda3
)

REM Run the webapp using the activated python
python "%~dp0webapp.py"

necho Webapp exited. Press any key to close this window...
pause
