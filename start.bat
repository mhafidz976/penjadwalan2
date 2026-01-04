@echo off
echo ========================================
echo  Sistem Penjadwalan Laboratorium
echo  Fakultas Teknologi Informasi
echo  Universitas Bale Bandung
echo ========================================
echo.

echo Memeriksa instalasi Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python tidak ditemukan!
    echo Silakan install Python terlebih dahulu:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python ditemukan!
echo.

echo Memeriksa dependencies...
if not exist "venv" (
    echo Membuat virtual environment...
    python -m venv venv
)

echo Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

echo Menginstall dependencies...
pip install -r requirements.txt

echo.
echo Memulai aplikasi...
echo Aplikasi akan berjalan di: http://localhost:5000
echo Tekan Ctrl+C untuk menghentikan aplikasi.
echo.
python app.py

pause
