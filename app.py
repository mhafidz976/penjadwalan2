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
    course_name = db.Column(db.String(100), nullable=False)
    
    # Relasi dengan schedule
    schedules = db.relationship('Schedule', backref='course', lazy=True)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey('lab.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False)  # Senin, Selasa, etc.
    time_slot = db.Column(db.String(20), nullable=False)  # 08:00-10:00, etc.
    semester = db.Column(db.String(20), nullable=False)  # Ganjil 2024/2025, etc.
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
    
    return render_template('dashboard.html', user=user, schedules=schedules)

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
        course_name = request.form['course_name']
        
        new_course = Course(course_name=course_name)
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
        course.course_name = request.form['course_name']
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
    semester = request.args.get('semester')
    lab_id = request.args.get('lab_id')
    day = request.args.get('day')
    
    if semester:
        query = query.filter_by(semester=semester)
    if lab_id:
        query = query.filter_by(lab_id=lab_id)
    if day:
        query = query.filter_by(day=day)
        
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
        semester = request.form['semester']
        
        # Cek konflik jadwal
        conflict = Schedule.query.filter_by(
            lab_id=lab_id, 
            day=day, 
            time_slot=time_slot,
            semester=semester
        ).first()
        
        if conflict:
            flash('Jadwal bentrok dengan jadwal yang sudah ada!', 'danger')
            return redirect(url_for('add_schedule'))
        
        # Cek konflik dosen
        lecturer_conflict = Schedule.query.filter_by(
            lecturer_id=lecturer_id,
            day=day,
            time_slot=time_slot,
            semester=semester
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
            semester=semester
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
        schedule.semester = request.form['semester']
        
        # Cek konflik (kecuali dengan jadwal yang sedang diedit)
        conflict = Schedule.query.filter(
            Schedule.lab_id == schedule.lab_id,
            Schedule.day == schedule.day,
            Schedule.time_slot == schedule.time_slot,
            Schedule.semester == schedule.semester,
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
            Schedule.semester == schedule.semester,
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
        
        # Create sample lecturers
        lecturers = [
            User(username='dosen1', password=generate_password_hash('dosen123'), role='lecturer', full_name='Dr. Ahmad Budi'),
            User(username='dosen2', password=generate_password_hash('dosen123'), role='lecturer', full_name='Dr. Siti Nurhaliza'),
            User(username='dosen3', password=generate_password_hash('dosen123'), role='lecturer', full_name='Dr. Budi Santoso'),
        ]
        
        for lecturer in lecturers:
            db.session.add(lecturer)
        
        # Create predefined courses
        courses_data = [
            'Introduction to Information Technology',
            'Programming Fundamentals', 
            'Data Structures',
            'Database Systems',
            'Web Programming',
            'Computer Networks',
            'Operating Systems',
            'Software Engineering',
            'Artificial Intelligence',
            'Human-Computer Interaction'
        ]
        
        for course_name in courses_data:
            course = Course(course_name=course_name)
            db.session.add(course)
        
        # Create sample laboratories
        labs = [
            Lab(lab_name='Lab Komputer 1', capacity=30),
            Lab(lab_name='Lab Komputer 2', capacity=25),
            Lab(lab_name='Lab Komputer 3', capacity=20),
            Lab(lab_name='Lab Jaringan', capacity=15),
        ]
        
        for lab in labs:
            db.session.add(lab)
        
        db.session.commit()
        print('Database berhasil diinisialisasi dengan data sampel!')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
