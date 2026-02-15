@echo off
call "C:\Users\PC\anaconda3\Scripts\activate.bat" "C:\Users\PC\anaconda3" >nul 2>&1
cd /d "C:\Users\PC\Desktop\Audio to TXT\"
start /b "" pythonw "C:\Users\PC\Desktop\Audio to TXT\mt.py"
exit /b
