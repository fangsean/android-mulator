@echo off 
set CODE_DIR=E:\android-mulator
echo %CODE_DIR%

rem 开启初始化

start /B  /min cmd /K "C:\ProgramData\anaconda3\Scripts\activate.bat C:\ProgramData\anaconda3 & cd /d %CODE_DIR% & conda activate py3.9 & python main.py --action init --first 16416 --num 6"
rem start /B  /min cmd  /c "cd /d %CODE_DIR% & dir & python main.py --action init --first 16416 --num 6"
rem 等待10s
timeout /t 10

rem 开启执行

start /B  /min cmd /K "C:\ProgramData\anaconda3\Scripts\activate.bat C:\ProgramData\anaconda3 & cd /d %CODE_DIR% & conda activate py3.9 & python main.py --action run --first 16416 --num 6"
rem start /B  /min cmd  /c "cd /d %CODE_DIR% & dir & python main.py --action run --first 16416 --num 6"

echo  开启初始化完成 and 开启执行!

pause