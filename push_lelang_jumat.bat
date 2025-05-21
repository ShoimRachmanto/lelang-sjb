@echo off
setlocal

:: === Ganti ke direktori project
cd /d D:\WongsoApps\lelang-sjb

:: === Format tanggal untuk nama file log
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do (
    set logdate=%%c-%%a-%%b
)

:: === Format jam (hilangkan titik dua)
for /f "tokens=1-2 delims=: " %%a in ("%time%") do (
    set logtime=%%a%%b
)

set logfile=logs\pushlog_%logdate%_%logtime%.txt

:: === Jalankan script export
echo [INFO] Menjalankan export_lelang_pekan_ini.py >> %logfile%
python export_lelang_pekan_ini.py >> %logfile% 2>&1

:: === Git push
echo [INFO] Melakukan git add dan commit >> %logfile%
git add data\lelang_segera.json >> %logfile% 2>&1
git commit -m "Auto update lelang pekan ini - %date% %time%" >> %logfile% 2>&1

echo [INFO] Push ke GitHub... >> %logfile%
git push origin main >> %logfile% 2>&1

echo [SELESAI] Lihat log di: %logfile%

endlocal
pause
