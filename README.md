# Web-Based Multi-Role Computer Laboratory Scheduling Application

Aplikasi berbasis web untuk manajemen penjadwalan laboratorium komputer di Fakultas Teknologi Informasi, Universitas Bale Bandung.

## Deskripsi Sistem

Sistem ini dirancang untuk mengelola jadwal laboratorium komputer secara efisien dan mencegah konflik antara mata kuliah, dosen, ruangan, dan slot waktu. Versi terbaru telah disesuaikan dengan kurikulum Semester Ganjil 2025-2026.

## Fitur Utama

### 🔐 Autentikasi & Authorization
- Login berbasis session Flask
- Multi-role system (Administrator, Laboratory Staff, Lecturer)
- Hak akses sesuai peran pengguna

### 👥 Manajemen Pengguna (Administrator)
- Tambah, edit, hapus user
- Assign role (admin, staff, lecturer)
- Manajemen akun dosen dan staff

### 🏢 Manajemen Laboratorium
- Tambah, edit, hapus data laboratorium
- Informasi kapasitas ruangan
- Tracking penggunaan lab

### 📚 Manajemen Mata Kuliah
- **[BARU]** Kode Mata Kuliah Unik (misal: MM01)
- **[BARU]** Informasi Semester (1-8) dan SKS (1-4)
- Integrasi dengan sistem jadwal

### 📅 Manajemen Jadwal
- **[BARU]** Format Kelas (misal: 5A, 7B)
- **[BARU]** Slot Waktu 100 Menit (08:00 - 18:40)
- **[BARU]** Filter Jadwal berdasarkan Semester dan Kelas
- Validasi otomatis konflik (lab & dosen)
- Edit dan hapus jadwal

### 📊 Dashboard & Laporan
- Statistik real-time (Total Jadwal, Mata Kuliah, Lab, User)
- Overview jadwal harian
- Informasi sistem

## Struktur Database Terbaru

### Tabel Users
- `id` - Primary Key
- `username` - Username unik
- `password` - Password terenkripsi
- `role` - Role pengguna (admin/staff/lecturer)
- `full_name` - Nama lengkap

### Tabel Labs
- `id` - Primary Key
- `lab_name` - Nama laboratorium
- `capacity` - Kapasitas ruangan

### Tabel Courses
- `id` - Primary Key
- `code` - Kode Mata Kuliah (Unique)
- `course_name` - Nama mata kuliah
- `semester` - Semester (1-8)
- `sks` - Jumlah SKS

### Tabel Schedules
- `id` - Primary Key
- `course_id` - Foreign key ke courses
- `lecturer_id` - Foreign key ke users
- `lab_id` - Foreign key ke labs
- `day` - Hari (Senin-Sabtu)
- `time_slot` - Slot waktu (Pola 100 menit + Istirahat)
- `class_name` - Nama Kelas (A, B, C)

## Slot Waktu Praktikum

1. **Sesi 1**: 08:00 - 09:40
2. **Sesi 2**: 10:00 - 11:40
3. **Istirahat**: 11:40 - 13:00
4. **Sesi 3**: 13:00 - 14:40
5. **Sesi 4**: 15:00 - 16:40
6. **Sesi 5**: 17:00 - 18:40

## Instalasi & Setup

### Prerequisites
- Python 3.7+
- pip package manager

### Langkah Instalasi

1. **Clone atau download project**
   ```bash
   cd penjadwalan2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi**
   ```bash
   python app.py
   ```
   *Catatan: Saat dijalankan pertama kali, aplikasi akan otomatis membuat database dan mengisi data sampel dari jadwal Semester Ganjil 2025-2026.*

4. **Akses aplikasi**
   - Buka browser: http://localhost:5000

### Akun Default

- **Administrator**: `admin` / `admin123`
- **Staff Lab**: `labstaff` / `staff123`
- **Dosen**:
    - `bayu` / `123456`
    - `sutiyono` / `123456`
    - `khilda` / `123456`
    - `ahmad` / `123456`
    - dll.

## Teknologi

- **Backend**: Flask, Flask-SQLAlchemy, Werkzeug
- **Frontend**: Bootstrap 5, Font Awesome, Jinja2
- **Database**: SQLite

## Struktur Project

```
penjadwalan2/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database.db            # SQLite database file
├── templates/             # HTML templates
│   ├── base.html          # Base layout
│   ├── dashboard.html     # Dashboard stats
│   ├── schedules.html     # Schedule list & filters
│   ├── courses.html       # Course management
│   ├── ...                # Other templates
├── static/
└── README.md              # Project documentation
```

## Validasi Konflik

Sistem secara otomatis memvalidasi:
1. **Konflik Laboratorium**: Satu lab tidak bisa digunakan untuk dua jadwal berbeda di waktu yang sama.
2. **Konflik Dosen**: Satu dosen tidak bisa mengajar di dua tempat berbeda di waktu yang sama.

---

**Developed for:** Fakultas Teknologi Informasi, Universitas Bale Bandung  
**Last Updated:** January 2026
