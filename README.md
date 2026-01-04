# Web-Based Multi-Role Computer Laboratory Scheduling Application

Aplikasi berbasis web untuk manajemen penjadwalan laboratorium komputer di Fakultas Teknologi Informasi, Universitas Bale Bandung.

## Deskripsi Sistem

Sistem ini dirancang untuk mengelola jadwal laboratorium komputer secara efisien dan mencegah konflik antara mata kuliah, dosen, ruangan, dan slot waktu.

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
- 10 mata kuliah standar pre-defined
- Tambah mata kuliah baru
- Integrasi dengan sistem jadwal

### 📅 Manajemen Jadwal
- Pembuatan jadwal otomatis
- Validasi konflik (lab & dosen)
- Edit dan hapus jadwal
- View berdasarkan role

### 📊 Dashboard & Laporan
- Statistik penggunaan
- Overview jadwal
- Informasi sistem

## Struktur Database

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
- `course_name` - Nama mata kuliah

### Tabel Schedules
- `id` - Primary Key
- `course_id` - Foreign key ke courses
- `lecturer_id` - Foreign key ke users
- `lab_id` - Foreign key ke labs
- `day` - Hari (Senin-Jumat)
- `time_slot` - Slot waktu
- `semester` - Semester akademik

## Mata Kuliah Pre-defined

1. Introduction to Information Technology
2. Programming Fundamentals
3. Data Structures
4. Database Systems
5. Web Programming
6. Computer Networks
7. Operating Systems
8. Software Engineering
9. Artificial Intelligence
10. Human-Computer Interaction

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

4. **Akses aplikasi**
   - Buka browser: http://localhost:5000
   - Atau: http://127.0.0.1:5000

### Default Login

Setelah first run, sistem akan otomatis membuat user default:

- **Administrator**
  - Username: `admin`
  - Password: `admin123`

- **Laboratory Staff**
  - Username: `labstaff`
  - Password: `staff123`

- **Sample Lecturers**
  - Username: `dosen1`, `dosen2`, `dosen3`
  - Password: `dosen123`

## Teknologi yang Digunakan

### Backend
- **Flask 2.3.3** - Web framework Python
- **Flask-SQLAlchemy 3.0.5** - ORM database
- **Werkzeug 2.3.7** - Security & utilities

### Frontend
- **Bootstrap 5.3.0** - CSS framework
- **Font Awesome 6.0.0** - Icons
- **Jinja2** - Template engine

### Database
- **SQLite** - Database development (file: database.db)

## Struktur Project

```
penjadwalan2/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database.db          # SQLite database file
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── login.html      # Login page
│   ├── dashboard.html  # Dashboard
│   ├── schedules.html  # Schedule management
│   ├── users.html      # User management
│   ├── labs.html       # Lab management
│   ├── courses.html    # Course management
│   ├── add_*.html      # Add forms
│   └── edit_*.html     # Edit forms
├── static/
│   └── css/            # Custom CSS (if needed)
│   └── js/             # Custom JavaScript (if needed)
└── README.md           # This file
```

## User Roles & Permissions

### Administrator
- ✅ Manajemen user (CRUD)
- ✅ Manajemen laboratorium (CRUD)
- ✅ Manajemen mata kuliah (CRUD)
- ✅ Manajemen jadwal (CRUD)
- ✅ View semua laporan

### Laboratory Staff
- ❌ Manajemen user
- ✅ Manajemen laboratorium (CRUD)
- ✅ Manajemen mata kuliah (CRUD)
- ✅ Manajemen jadwal (CRUD)
- ✅ View jadwal & laporan

### Lecturer
- ❌ Manajemen user
- ❌ Manajemen laboratorium
- ❌ Manajemen mata kuliah
- ❌ Manajemen jadwal
- ✅ View jadwal pribadi
- ✅ View semua jadwal (read-only)

## Validasi Konflik

Sistem secara otomatis memvalidasi:

1. **Konflik Laboratorium**
   - Satu lab tidak bisa dijadwalkan di waktu yang sama
   - Cross-check dengan semester yang sama

2. **Konflik Dosen**
   - Satu dosen tidak bisa mengajar di waktu yang sama
   - Mencegah double booking dosen

3. **Input Validation**
   - Required field validation
   - Format validation
   - Data integrity checks

## Features Highlights

### 🎨 Modern UI/UX
- Bootstrap 5 responsive design
- Clean academic interface
- Font Awesome icons
- Interactive components

### 🔒 Security
- Password hashing (Werkzeug)
- Session-based authentication
- Role-based access control
- CSRF protection ready

### 📱 Responsive
- Mobile-friendly design
- Tablet compatible
- Desktop optimized

### ⚡ Performance
- Efficient database queries
- Optimized templates
- Minimal dependencies

## Development & Deployment

### Development Mode
```bash
python app.py
```

### Production Deployment
Untuk production deployment, disarankan menggunakan:
- Gunicorn atau uWSGI
- Nginx sebagai reverse proxy
- PostgreSQL/MySQL untuk production database
- Environment variables untuk configuration

## Troubleshooting

### Common Issues

1. **Database not found**
   - Pastikan `app.py` dijalankan sekali untuk inisialisasi database
   - File `database.db` akan otomatis terbuat

2. **Module not found**
   - Install requirements: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Port already in use**
   - Change port di `app.py`: `app.run(port=5001)`
   - Atau kill process yang menggunakan port 5000

## Future Enhancements

- 📧 Email notifications
- 📱 Mobile app
- 🔄 Calendar integration
- 📊 Advanced reporting
- 🌐 Multi-language support
- 📈 Analytics dashboard
- 🖨️ Print schedules
- 📤 Export to PDF/Excel

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

This project is for educational purposes at Universitas Bale Bandung.

## Support

For technical support or questions:
- Contact: FTI Support Team
- Email: support@fti.ubl.ac.id
- Location: Fakultas Teknologi Informasi, Universitas Bale Bandung

---

**Developed by:** FTI Development Team  
**Version:** 1.0.0  
**Last Updated:** January 2024
