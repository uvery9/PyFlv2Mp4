@echo off
xcopy *config.ini       Release\ /d /y /i /q
xcopy README.*       Release\ /d /y /i /q

cd Release
.\PyFlv2Mp4.exe
pause