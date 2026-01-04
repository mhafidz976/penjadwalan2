#!/bin/bash

echo "========================================"
echo " Sistem Penjadwalan Laboratorium"
echo " Fakultas Teknologi Informasi"
echo " Universitas Bale Bandung"
echo "========================================"
echo

echo "Memeriksa instalasi Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 tidak ditemukan!"
    echo "Silakan install Python3 terlebih dahulu:"
    echo "https://www.python.org/downloads/"
    exit 1
fi

echo "Python3 ditemukan!"
echo

echo "Memeriksa dependencies..."
if [ ! -d "venv" ]; then
    echo "Membuat virtual environment..."
    python3 -m venv venv
fi

echo "Mengaktifkan virtual environment..."
source venv/bin/activate

echo "Menginstall dependencies..."
pip install -r requirements.txt

echo
echo "Memulai aplikasi..."
echo "Aplikasi akan berjalan di: http://localhost:5000"
echo "Tekan Ctrl+C untuk menghentikan aplikasi."
echo
python app.py
