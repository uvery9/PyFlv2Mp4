@echo off
rd /s /q Release
md Release

xcopy *config.ini       Release\ /d /y /i /q
xcopy README.*       Release\ /d /y /i /q

pip install -r Requirements
pyinstaller  -F -i VideoConverter.ico --hidden-import queue PyFlv2Mp4.py
echo f | xcopy dist\PyFlv2Mp4.exe Release\PyFlv2Mp4.exe /c /h /y /i /q /d

::clean
rem echo ********************cleaning temp files********************
rem rd /s /q build
rem rd /s /q __pycache__
rem del /q PyAuto.spec
rem rd /s /q dist

echo ******************** build succed ********************

@REM set "PYTHONPATH="
@REM for /f %%i in ('where python') do if not defined foo set "PYTHONPATH=%%i"
@REM ECHO %PYTHONPATH%

for /f %%p in ('where python') do set "foo=%%p" & goto :done
:done
REM ECHO %foo% D:\jared\coding\PyAuto\env\Scripts\python.exe
if x%foo:Scripts=%==x%foo% pause

