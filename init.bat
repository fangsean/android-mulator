@echo off
setlocal enabledelayedexpansion
echo Connection start!

@REM set port=16384
@REM set count=4
set host=%1%
set port=%2%
set count=%3%
echo port parameter is: %port%
echo count parameter is: %count%


echo !host!:!port!
adb connect !host!:!port!

set /a count-=1
for /l %%i in (1,1,%count%) do (
  set /a port+=32
  echo !host!:!port!
  adb connect !host!:!port!
)

echo Connection completed!
pause
