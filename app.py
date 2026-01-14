from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, staff, lecturer
    full_name = db.Column(db.String(100), nullable=False)
    
    # Relasi dengan schedule
    schedules = db.relationship('Schedule', backref='lecturer', lazy=True)

class Lab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lab_name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
    # Relasi dengan schedule
    schedules = db.relationship('Schedule', backref='laboratory', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)  # 1-8
    sks = db.Column(db.Integer, nullable=False)  # 1-4
    
    # Relasi dengan schedule
    schedules = db.relationship('Schedule', backref='course', lazy=True)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey('lab.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False)  # Senin, Selasa, etc.
    time_slot = db.Column(db.String(20), nullable=False)  # 08:00-10:00, etc.
    class_name = db.Column(db.String(5), nullable=False)  # A, B, C
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Decorator untuk role-based access
def role_required(*roles):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Silakan login terlebih dahulu', 'danger')
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            if user.role not in roles:
                flash('Anda tidak memiliki akses ke halaman ini', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    schedules = Schedule.query.all()
    courses = Course.query.all()
    labs = Lab.query.all()
    users = User.query.all() if user.role == 'admin' else []
    
    return render_template('dashboard.html', user=user, schedules=schedules, courses=courses, labs=labs, users=users)

# User Management Routes (Admin only)
@app.route('/users')
@role_required('admin')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@role_required('admin')
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        full_name = request.form['full_name']
        
        # Cek apakah username sudah ada
        if User.query.filter_by(username=username).first():
            flash('Username sudah ada!', 'danger')
            return redirect(url_for('add_user'))
        
        # Buat user baru
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role, full_name=full_name)
        db.session.add(new_user)
        db.session.commit()
        
        flash('User berhasil ditambahkan!', 'success')
        return redirect(url_for('users'))
    
    return render_template('add_user.html')

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@role_required('admin')
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.role = request.form['role']
        user.full_name = request.form['full_name']
        
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        
        db.session.commit()
        flash('User berhasil diperbarui!', 'success')
        return redirect(url_for('users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/users/delete/<int:id>')
@role_required('admin')
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User berhasil dihapus!', 'success')
    return redirect(url_for('users'))

# Laboratory Management Routes (Admin & Staff)
@app.route('/labs')
@role_required('admin', 'staff')
def labs():
    labs = Lab.query.all()
    return render_template('labs.html', labs=labs)

@app.route('/labs/add', methods=['GET', 'POST'])
@role_required('admin', 'staff')
def add_lab():
    if request.method == 'POST':
        lab_name = request.form['lab_name']
        capacity = request.form['capacity']
        
        new_lab = Lab(lab_name=lab_name, capacity=capacity)
        db.session.add(new_lab)
        db.session.commit()
        
        flash('Laboratorium berhasil ditambahkan!', 'success')
        return redirect(url_for('labs'))
    
    return render_template('add_lab.html')

@app.route('/labs/edit/<int:id>', methods=['GET', 'POST'])
@role_required('admin', 'staff')
def edit_lab(id):
    lab = Lab.query.get_or_404(id)
    
    if request.method == 'POST':
        lab.lab_name = request.form['lab_name']
        lab.capacity = request.form['capacity']
        db.session.commit()
        
        flash('Laboratorium berhasil diperbarui!', 'success')
        return redirect(url_for('labs'))
    
    return render_template('edit_lab.html', lab=lab)

@app.route('/labs/delete/<int:id>')
@role_required('admin', 'staff')
def delete_lab(id):
    lab = Lab.query.get_or_404(id)
    db.session.delete(lab)
    db.session.commit()
    flash('Laboratorium berhasil dihapus!', 'success')
    return redirect(url_for('labs'))

# Course Management Routes (Admin & Staff)
@app.route('/courses')
@role_required('admin', 'staff')
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/courses/add', methods=['GET', 'POST'])
@role_required('admin', 'staff')
def add_course():
    if request.method == 'POST':
        code = request.form['code']
        course_name = request.form['course_name']
        semester = request.form['semester']
        sks = request.form['sks']
        
        # Cek kode unik
        if Course.query.filter_by(code=code).first():
            flash('Kode mata kuliah sudah ada!', 'danger')
            return redirect(url_for('add_course'))
        
        new_course = Course(code=code, course_name=course_name, semester=semester, sks=sks)
        db.session.add(new_course)
        db.session.commit()
        
        flash('Mata kuliah berhasil ditambahkan!', 'success')
        return redirect(url_for('courses'))
    
    return render_template('add_course.html')

@app.route('/courses/edit/<int:id>', methods=['GET', 'POST'])
@role_required('admin', 'staff')
def edit_course(id):
    course = Course.query.get_or_404(id)
    
    if request.method == 'POST':
        new_code = request.form['code']
        # Cek unik jika kode berubah
        if new_code != course.code and Course.query.filter_by(code=new_code).first():
            flash('Kode mata kuliah sudah digunakan!', 'danger')
            return redirect(url_for('edit_course', id=id))

        course.code = new_code
        course.course_name = request.form['course_name']
        course.semester = request.form['semester']
        course.sks = request.form['sks']
        db.session.commit()
        
        flash('Mata kuliah berhasil diperbarui!', 'success')
        return redirect(url_for('courses'))
    
    return render_template('edit_course.html', course=course)

@app.route('/courses/delete/<int:id>')
@role_required('admin', 'staff')
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash('Mata kuliah berhasil dihapus!', 'success')
    return redirect(url_for('courses'))

# Schedule Management Routes
@app.route('/schedules')
def schedules():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    query = Schedule.query
    
    # Filter logic
    if user.role == 'lecturer':
        query = query.filter_by(lecturer_id=user.id)
        
    # Apply filters from request args
    lab_id = request.args.get('lab_id')
    day = request.args.get('day')
    semester = request.args.get('semester')
    class_name = request.args.get('class_name')
    
    if lab_id:
        query = query.filter_by(lab_id=lab_id)
    if day:
        query = query.filter_by(day=day)
    if class_name:
        query = query.filter_by(class_name=class_name)
    if semester:
        query = query.join(Course).filter(Course.semester == semester)
        
    schedules = query.all()
    
    return render_template('schedules.html', schedules=schedules, user=user, labs=Lab.query.all())

@app.route('/schedules/add', methods=['GET', 'POST'])
@role_required('admin', 'staff')
def add_schedule():
    if request.method == 'POST':
        course_id = request.form['course_id']
        lecturer_id = request.form['lecturer_id']
        lab_id = request.form['lab_id']
        day = request.form['day']
        time_slot = request.form['time_slot']
        class_name = request.form['class_name']
        
        # Cek konflik jadwal
        conflict = Schedule.query.filter_by(
            lab_id=lab_id, 
            day=day, 
            time_slot=time_slot
        ).first()
        
        if conflict:
            flash('Jadwal bentrok dengan jadwal yang sudah ada!', 'danger')
            return redirect(url_for('add_schedule'))
        
        # Cek konflik dosen
        lecturer_conflict = Schedule.query.filter_by(
            lecturer_id=lecturer_id,
            day=day,
            time_slot=time_slot
        ).first()
        
        if lecturer_conflict:
            flash('Dosen sudah memiliki jadwal di waktu yang sama!', 'danger')
            return redirect(url_for('add_schedule'))
        
        new_schedule = Schedule(
            course_id=course_id,
            lecturer_id=lecturer_id,
            lab_id=lab_id,
            day=day,
            time_slot=time_slot,
            class_name=class_name
        )
        
        db.session.add(new_schedule)
        db.session.commit()
        
        flash('Jadwal berhasil ditambahkan!', 'success')
        return redirect(url_for('schedules'))
    
    courses = Course.query.all()
    lecturers = User.query.filter_by(role='lecturer').all()
    labs = Lab.query.all()
    
    return render_template('add_schedule.html', 
                         courses=courses, 
                         lecturers=lecturers, 
                         labs=labs)

@app.route('/schedules/edit/<int:id>', methods=['GET', 'POST'])
@role_required('admin', 'staff')
def edit_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    
    if request.method == 'POST':
        schedule.course_id = request.form['course_id']
        schedule.lecturer_id = request.form['lecturer_id']
        schedule.lab_id = request.form['lab_id']
        schedule.day = request.form['day']
        schedule.time_slot = request.form['time_slot']
        schedule.class_name = request.form['class_name']
        
        # Cek konflik (kecuali dengan jadwal yang sedang diedit)
        conflict = Schedule.query.filter(
            Schedule.lab_id == schedule.lab_id,
            Schedule.day == schedule.day,
            Schedule.time_slot == schedule.time_slot,
            Schedule.id != schedule.id
        ).first()
        
        if conflict:
            flash('Jadwal bentrok dengan jadwal yang sudah ada!', 'danger')
            return redirect(url_for('edit_schedule', id=id))
        
        # Cek konflik dosen
        lecturer_conflict = Schedule.query.filter(
            Schedule.lecturer_id == schedule.lecturer_id,
            Schedule.day == schedule.day,
            Schedule.time_slot == schedule.time_slot,
            Schedule.id != schedule.id
        ).first()
        
        if lecturer_conflict:
            flash('Dosen sudah memiliki jadwal di waktu yang sama!', 'danger')
            return redirect(url_for('edit_schedule', id=id))
        
        db.session.commit()
        flash('Jadwal berhasil diperbarui!', 'success')
        return redirect(url_for('schedules'))
    
    courses = Course.query.all()
    lecturers = User.query.filter_by(role='lecturer').all()
    labs = Lab.query.all()
    
    return render_template('edit_schedule.html', 
                         schedule=schedule,
                         courses=courses, 
                         lecturers=lecturers, 
                         labs=labs)

@app.route('/schedules/delete/<int:id>')
@role_required('admin', 'staff')
def delete_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Jadwal berhasil dihapus!', 'success')
    return redirect(url_for('schedules'))

# Initialize database with sample data
def init_sample_data():
    # Cek apakah sudah ada data
    if User.query.first() is None:
        # Create default admin
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin',
            full_name='Administrator'
        )
        db.session.add(admin)
        
        # Create sample staff
        staff = User(
            username='labstaff',
            password=generate_password_hash('staff123'),
            role='staff',
            full_name='Laboratory Staff'
        )
        db.session.add(staff)
        
        # Create Lecturers
        lecturers = [
            {'username': 'bayu', 'name': 'Mohammad Bayu A, S.Kom, M.Kom'},
            {'username': 'sutiyono', 'name': 'Sutiyono, ST, M.Kom'},
            {'username': 'khilda', 'name': 'Khilda Nistrina, S.Pd., M.Sc'},
            {'username': 'ahmad', 'name': 'Ahmad Faojan M, S.Kom'},
            {'username': 'rosmalina', 'name': 'Rosmalina, ST., M.Kom'},
            {'username': 'denny', 'name': 'Denny Rusdianto, ST., M.Kom'},
            {'username': 'cecep', 'name': 'Cecep Suwanda, S.Si., M.Kom'},
        ]
        
        lecturer_objs = {}
        for l in lecturers:
            user = User(
                username=l['username'],
                password=generate_password_hash('123456'),
                role='lecturer',
                full_name=l['name']
            )
            db.session.add(user)
            lecturer_objs[l['username']] = user
        
        db.session.commit() # Commit to get IDs

        # Create Laboratories
        labs = [
            Lab(lab_name='Lab Komputer 1', capacity=30),
            Lab(lab_name='Lab Komputer 2', capacity=30),
        ]
        db.session.add_all(labs)
        db.session.commit()
        
        lab1 = labs[0]
        lab2 = labs[1]

        # Create Courses
        # Format: (Code, Name, Semester, SKS)
        courses_data = [
            ('MM01', 'Praktikum Sistem Multimedia', 3, 3),
            ('GD01', 'Praktikum Pengantar Pemograman Game', 3, 3),
            ('ML01', 'Praktikum Pembelajaran Mesin', 5, 3),
            ('PV01', 'Praktikum Pemograman Visual', 5, 3),
            ('OS01', 'Praktikum Sistem Operasi dan Jaringan Komputer', 5, 3),
            ('IOT1', 'Praktikum IoT', 7, 3),
            ('PS01', 'Praktikum Pemodelan dan Simulasi', 5, 3),
            ('SP01', 'Praktikum Statistik & Probabilitas', 1, 3),
            ('GH01', 'Praktikum GitHub', 3, 2),
            ('BD01', 'Praktikum Sistem Basis Data', 3, 3),
            ('ADK1', 'Praktikum Aplikasi Dasar Komputer', 3, 3),
            ('SIG1', 'Praktikum Sistem Informasi Geografis', 7, 3),
            ('APSI', 'Praktikum Analisis dan Perancangan SI', 3, 3),
            ('ALGO', 'Praktikum Algoritma dan Pemrograman 1', 1, 3),
            ('DA01', 'Praktikum Data Analisis Dasar', 1, 3),
            ('PPSI', 'Praktikum Pengelolaan Proyek SI', 5, 3),
            ('AK01', 'Praktikum Akuntansi', 1, 3),
            ('BPTR', 'Praktikum Bahasa Pemograman Tingkat Rendah', 3, 3),
        ]
        
        course_objs = {}
        for code, name, sem, sks in courses_data:
            course = Course(code=code, course_name=name, semester=sem, sks=sks)
            db.session.add(course)
            course_objs[name] = course # Map by name for easy lookup
        
        db.session.commit()

        # Helper to get course by partial name pattern if needed, but we used exact names above
        def get_course(name):
            return course_objs.get(name)

        # Helper to create schedule
        def create_sched(lab, day, time, course_name, lecturer_user, class_name):
            course = get_course(course_name)
            lecturer = lecturer_objs[lecturer_user]
            if course and lecturer:
                sched = Schedule(
                    course_id=course.id,
                    lecturer_id=lecturer.id,
                    lab_id=lab.id,
                    day=day,
                    time_slot=time,
                    class_name=class_name
                )
                db.session.add(sched)

        # --- LAB 1 SCHEDULES ---
        # Senin
        create_sched(lab1, 'Senin', '08:00-09:40', 'Praktikum Sistem Multimedia', 'bayu', 'B') # 3B inferred
        create_sched(lab1, 'Senin', '10:00-11:40', 'Praktikum Sistem Multimedia', 'bayu', 'A') # 3A inferred
        create_sched(lab1, 'Senin', '13:00-14:40', 'Praktikum Pengantar Pemograman Game', 'sutiyono', 'A') # 3A
        create_sched(lab1, 'Senin', '15:00-16:40', 'Praktikum Pengantar Pemograman Game', 'sutiyono', 'B') # 3B
        create_sched(lab1, 'Senin', '17:00-18:40', 'Praktikum Sistem Multimedia', 'bayu', 'C') # 3C
        
        # Selasa
        create_sched(lab1, 'Selasa', '08:00-09:40', 'Praktikum Pembelajaran Mesin', 'bayu', 'A')
        create_sched(lab1, 'Selasa', '13:00-14:40', 'Praktikum Pembelajaran Mesin', 'bayu', 'B')
        create_sched(lab1, 'Selasa', '15:00-16:40', 'Praktikum Pemograman Visual', 'khilda', 'A') # 5PAGI
        create_sched(lab1, 'Selasa', '17:00-18:40', 'Praktikum Sistem Operasi dan Jaringan Komputer', 'ahmad', 'C') 
        
        # Rabu
        create_sched(lab1, 'Rabu', '10:00-11:40', 'Praktikum IoT', 'sutiyono', 'A')
        create_sched(lab1, 'Rabu', '13:00-14:40', 'Praktikum IoT', 'sutiyono', 'B')
        create_sched(lab1, 'Rabu', '17:00-18:40', 'Praktikum IoT', 'sutiyono', 'C')
        # 19:00 Pemodelan dan Simulasi (Bayu) 5C - skipped or mapped to 17:00 if allowed (but 17:00 taken). Skipped.
        
        # Jumat
        create_sched(lab1, 'Jumat', '08:00-09:40', 'Praktikum GitHub', 'sutiyono', 'A') # ?PAGI
        create_sched(lab1, 'Jumat', '10:00-11:40', 'Praktikum Sistem Basis Data', 'sutiyono', 'A') # 5PAGI
        create_sched(lab1, 'Jumat', '15:00-16:40', 'Praktikum Aplikasi Dasar Komputer', 'denny', 'A') # 3PAGI
        create_sched(lab1, 'Jumat', '17:00-18:40', 'Praktikum Sistem Informasi Geografis', 'ahmad', 'C')
        
        # Sabtu
        create_sched(lab1, 'Sabtu', '08:00-09:40', 'Praktikum Aplikasi Dasar Komputer', 'denny', 'A') # 3SORE (A)
        create_sched(lab1, 'Sabtu', '10:00-11:40', 'Praktikum Pemodelan dan Simulasi', 'bayu', 'A') # 5A
        create_sched(lab1, 'Sabtu', '13:00-14:40', 'Praktikum Analisis dan Perancangan SI', 'denny', 'A') # 3PAGI
        create_sched(lab1, 'Sabtu', '17:00-18:40', 'Praktikum Analisis dan Perancangan SI', 'denny', 'C') # 3SORE
        
        # --- LAB 2 SCHEDULES ---
        # Senin
        create_sched(lab2, 'Senin', '08:00-09:40', 'Praktikum Data Analisis Dasar', 'sutiyono', 'B') # 1B
        create_sched(lab2, 'Senin', '10:00-11:40', 'Praktikum Aplikasi Dasar Komputer', 'sutiyono', 'B') # 1B
        create_sched(lab2, 'Senin', '13:00-14:40', 'Praktikum GitHub', 'sutiyono', 'B') # 7B
        create_sched(lab2, 'Senin', '15:00-16:40', 'Praktikum Data Analisis Dasar', 'sutiyono', 'A') # 1A
        create_sched(lab2, 'Senin', '17:00-18:40', 'Praktikum Aplikasi Dasar Komputer', 'sutiyono', 'C') # 1C
        
        # Selasa
        create_sched(lab2, 'Selasa', '08:00-09:40', 'Praktikum Sistem Basis Data', 'sutiyono', 'A') # 5A
        create_sched(lab2, 'Selasa', '10:00-11:40', 'Praktikum Pengelolaan Proyek SI', 'rosmalina', 'A') # 7PAGI
        create_sched(lab2, 'Selasa', '13:00-14:40', 'Praktikum Sistem Basis Data', 'sutiyono', 'B') # 5B
        create_sched(lab2, 'Selasa', '15:00-16:40', 'Praktikum Aplikasi Dasar Komputer', 'sutiyono', 'A') # 1A
        create_sched(lab2, 'Selasa', '17:00-18:40', 'Praktikum Sistem Basis Data', 'sutiyono', 'C') # 5C
        
        # Rabu
        create_sched(lab2, 'Rabu', '08:00-09:40', 'Praktikum GitHub', 'sutiyono', 'A') # 7A
        create_sched(lab2, 'Rabu', '10:00-11:40', 'Praktikum Statistik & Probabilitas', 'rosmalina', 'A') # 1PAGI
        create_sched(lab2, 'Rabu', '13:00-14:40', 'Praktikum Analisis Data', 'sutiyono', 'A') # ?PAGI
        create_sched(lab2, 'Rabu', '15:00-16:40', 'Praktikum Akuntansi', 'khilda', 'A') # 3PAGI
        
        # Kamis
        create_sched(lab2, 'Kamis', '08:00-09:40', 'Praktikum Algoritma dan Pemrograman 1', 'cecep', 'A') # 1PAGI
        create_sched(lab2, 'Kamis', '10:00-11:40', 'Praktikum Algoritma dan Pemrograman 1', 'ahmad', 'A') # 1A
        create_sched(lab2, 'Kamis', '13:00-14:40', 'Praktikum Algoritma dan Pemrograman 1', 'ahmad', 'B') # 1B
        create_sched(lab2, 'Kamis', '15:00-16:40', 'Praktikum Sistem Operasi dan Jaringan Komputer', 'sutiyono', 'A') # 5PAGI
        create_sched(lab2, 'Kamis', '17:00-18:40', 'Praktikum Algoritma dan Pemrograman 1', 'ahmad', 'C') # 1C
        
        # Jumat
        create_sched(lab2, 'Jumat', '08:00-09:40', 'Praktikum Sistem Informasi Geografis', 'ahmad', 'A') # 7A
        create_sched(lab2, 'Jumat', '10:00-11:40', 'Praktikum Sistem Informasi Geografis', 'ahmad', 'B') # 7B
        create_sched(lab2, 'Jumat', '17:00-18:40', 'Praktikum Sistem Basis Data', 'sutiyono', 'C') # ?SORE ?? Duplicate? Image has Basis Data at 17:00
        
        # Sabtu
        create_sched(lab2, 'Sabtu', '08:00-09:40', 'Praktikum Sistem Operasi dan Jaringan Komputer', 'ahmad', 'A') # ?
        create_sched(lab2, 'Sabtu', '10:00-11:40', 'Praktikum Sistem Operasi dan Jaringan Komputer', 'ahmad', 'B') # 5B
        create_sched(lab2, 'Sabtu', '13:00-14:40', 'Praktikum Bahasa Pemograman Tingkat Rendah', 'ahmad', 'B') # ?
        create_sched(lab2, 'Sabtu', '15:00-16:40', 'Praktikum Bahasa Pemograman Tingkat Rendah', 'ahmad', 'C') # 5B?

        db.session.commit()
        print('Database berhasil diinisialisasi dengan data real dari gambar!')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
