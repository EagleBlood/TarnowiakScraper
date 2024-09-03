cd new-tarnowiak
cd api
start "" npm run dev

cd ..
start "" npm start

REM wait 5 seconds
timeout /t 5 /nobreak >nul

start "" "C:/Users/Dawid.Nosal/AppData/Local/Microsoft/WindowsApps/python3.11.exe" "c:/Users/Dawid.Nosal/Desktop/TarnowiakScraper/tarnowiakCarScraper.py"