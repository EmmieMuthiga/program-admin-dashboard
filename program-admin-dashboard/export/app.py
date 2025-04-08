import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create a base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///program_admin.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure uploads directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize the database
db.init_app(app)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import models to ensure they're registered with SQLAlchemy
with app.app_context():
    from models import User, Program, Participant, Faculty, Partner, Material, Task, Post, Campaign
    # Create all tables
    db.create_all()

# Set up Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Import and register routes
from routes.auth import auth_bp
from routes.programs import programs_bp
from routes.participants import participants_bp
from routes.faculty import faculty_bp
from routes.admin import admin_bp
from routes.marketing import marketing_bp
from routes.ai_assistant import ai_bp

app.register_blueprint(auth_bp)
app.register_blueprint(programs_bp)
app.register_blueprint(participants_bp)
app.register_blueprint(faculty_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(marketing_bp)
app.register_blueprint(ai_bp)

# Home route
@app.route('/')
def index():
    # Redirect to splash page
    return render_template('splash.html')

@app.route('/dashboard')
@login_required
def dashboard():
    from models import Program, Participant, Task, Material, Faculty, Attendance
    from sqlalchemy import func
    
    # Fetch recent/upcoming programs
    upcoming_programs = Program.query.filter(Program.start_date >= datetime.now()).limit(5).all()
    
    # Fetch recent participants
    recent_participants = Participant.query.order_by(Participant.id.desc()).limit(5).all()
    
    # Fetch pending tasks
    pending_tasks = Task.query.filter_by(status='pending').order_by(Task.due_date).limit(5).all()
    
    # Get statistics
    total_programs = Program.query.count()
    active_programs = Program.query.filter_by(status='active').count()
    completed_programs = Program.query.filter_by(status='completed').count()
    draft_programs = Program.query.filter_by(status='draft').count()
    cancelled_programs = Program.query.filter_by(status='cancelled').count()
    
    total_participants = Participant.query.count()
    total_faculty = Faculty.query.count()
    total_materials = Material.query.count()
    
    # Calculate attendance stats
    attendance_stats = {
        'present': Attendance.query.filter_by(status='present').count(),
        'absent': Attendance.query.filter_by(status='absent').count(),
        'excused': Attendance.query.filter_by(status='excused').count()
    }
    total_attendance = sum(attendance_stats.values()) or 1  # Avoid division by zero
    attendance_percentage = {
        'present': round((attendance_stats['present'] / total_attendance) * 100),
        'absent': round((attendance_stats['absent'] / total_attendance) * 100),
        'excused': round((attendance_stats['excused'] / total_attendance) * 100)
    }
    
    # Get participant growth by month (last 6 months)
    six_months_ago = datetime.now().replace(day=1) - timedelta(days=180)
    participant_growth = db.session.query(
        func.date_trunc('month', Participant.created_at).label('month'),
        func.count().label('count')
    ).filter(Participant.created_at >= six_months_ago).group_by('month').all()
    
    # Create a dictionary of participant growth data
    growth_data = {month.strftime('%Y-%m'): count for month, count in participant_growth}
    
    # Program status data for chart
    program_status_data = {
        'labels': ['Active', 'Completed', 'Draft', 'Cancelled'],
        'data': [active_programs, completed_programs, draft_programs, cancelled_programs]
    }
    
    # Faculty load data
    from models import program_faculty
    faculty_query = db.session.query(
        Faculty.id,
        Faculty.first_name,
        Faculty.last_name,
        func.count(program_faculty.c.program_id).label('program_count')
    ).outerjoin(
        program_faculty, Faculty.id == program_faculty.c.faculty_id
    ).group_by(Faculty.id).order_by(func.count(program_faculty.c.program_id).desc()).limit(10).all()
    
    faculty_load_data = {
        'labels': [f"{f.first_name} {f.last_name}" for f in faculty_query],
        'data': [f.program_count for f in faculty_query]
    }
    
    # Program timeline data
    six_months_future = datetime.now() + timedelta(days=180)
    future_programs = db.session.query(
        func.date_trunc('month', Program.start_date).label('month'),
        func.count().label('count')
    ).filter(
        Program.start_date >= datetime.now(),
        Program.start_date <= six_months_future
    ).group_by('month').order_by('month').all()
    
    # Format months for display and ensure all months in range have a value
    current = datetime.now().replace(day=1)
    end = six_months_future.replace(day=1)
    months = []
    program_counts = []

    while current <= end:
        month_str = current.strftime('%b %Y')
        months.append(month_str)
        
        # Check if we have data for this month
        month_data = next((item for item in future_programs if item.month.strftime('%b %Y') == month_str), None)
        program_counts.append(month_data.count if month_data else 0)
        
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    program_timeline_data = {
        'labels': months,
        'data': program_counts
    }
    
    # Get all faculties for filter
    all_faculties = Faculty.query.all()
    
    return render_template('dashboard.html', 
                           upcoming_programs=upcoming_programs,
                           recent_participants=recent_participants,
                           pending_tasks=pending_tasks,
                           total_programs=total_programs,
                           active_programs=active_programs,
                           completed_programs=completed_programs,
                           total_participants=total_participants,
                           total_faculty=total_faculty,
                           total_materials=total_materials,
                           attendance_stats=attendance_stats,
                           attendance_percentage=attendance_percentage,
                           growth_data=growth_data,
                           program_status_data=program_status_data,
                           faculty_load_data=faculty_load_data,
                           program_timeline_data=program_timeline_data,
                           all_faculties=all_faculties)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error=e, title='Page Not Found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error=e, title='Server Error'), 500

# Template filters
@app.template_filter('format_date')
def format_date(date, format='%B %d, %Y'):
    if date is None:
        return ""
    return date.strftime(format)

@app.template_filter('tojson')
def to_json(value):
    import json
    return json.dumps(value)

@app.template_filter('nl2br')
def nl2br(value):
    if value:
        return value.replace('\n', '<br>')
    return ""
# This route was added for the splash page
@app.route('/splash')
def splash():
    return render_template('splash.html')
