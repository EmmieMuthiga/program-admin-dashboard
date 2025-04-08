from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Faculty, Program
from forms import FacultyForm
from app import db
from utils import save_file

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@faculty_bp.route('/')
@login_required
def index():
    faculty = Faculty.query.order_by(Faculty.last_name).all()
    return render_template('faculty/index.html', faculty=faculty, title='Faculty')

@faculty_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = FacultyForm()
    
    if form.validate_on_submit():
        # Check if faculty with this email already exists
        existing = Faculty.query.filter_by(email=form.email.data).first()
        if existing:
            flash('A faculty member with this email already exists.', 'danger')
            return render_template('faculty/create.html', form=form, title='Add Faculty')
        
        contract_file = None
        if form.contract_file.data:
            contract_file = save_file(form.contract_file.data, directory='contracts')
        
        faculty = Faculty(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            bio=form.bio.data,
            expertise=form.expertise.data,
            contract_file=contract_file
        )
        
        db.session.add(faculty)
        db.session.commit()
        
        flash('Faculty added successfully!', 'success')
        return redirect(url_for('faculty.view', faculty_id=faculty.id))
    
    return render_template('faculty/create.html', form=form, title='Add Faculty')

@faculty_bp.route('/<int:faculty_id>')
@login_required
def view(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    return render_template('faculty/view.html', faculty=faculty, title=f'{faculty.first_name} {faculty.last_name}')

@faculty_bp.route('/<int:faculty_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    form = FacultyForm(obj=faculty)
    
    if form.validate_on_submit():
        # Check if email is changed and already exists for another faculty
        if form.email.data != faculty.email:
            existing = Faculty.query.filter_by(email=form.email.data).first()
            if existing:
                flash('A faculty member with this email already exists.', 'danger')
                return render_template('faculty/edit.html', form=form, faculty=faculty, title=f'Edit {faculty.first_name} {faculty.last_name}')
        
        faculty.first_name = form.first_name.data
        faculty.last_name = form.last_name.data
        faculty.email = form.email.data
        faculty.phone = form.phone.data
        faculty.bio = form.bio.data
        faculty.expertise = form.expertise.data
        
        if form.contract_file.data:
            faculty.contract_file = save_file(form.contract_file.data, directory='contracts')
        
        db.session.commit()
        
        flash('Faculty updated successfully!', 'success')
        return redirect(url_for('faculty.view', faculty_id=faculty.id))
    
    return render_template('faculty/edit.html', form=form, faculty=faculty, title=f'Edit {faculty.first_name} {faculty.last_name}')

@faculty_bp.route('/<int:faculty_id>/delete', methods=['POST'])
@login_required
def delete(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    
    db.session.delete(faculty)
    db.session.commit()
    
    flash('Faculty deleted successfully!', 'success')
    return redirect(url_for('faculty.index'))

@faculty_bp.route('/<int:faculty_id>/assign/<int:program_id>', methods=['POST'])
@login_required
def assign_to_program(faculty_id, program_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    program = Program.query.get_or_404(program_id)
    
    # Check if already assigned
    if program in faculty.programs:
        flash(f'{faculty.first_name} is already assigned to this program.', 'info')
    else:
        program.faculties.append(faculty)
        db.session.commit()
        flash(f'{faculty.first_name} has been assigned to {program.title}.', 'success')
    
    return redirect(url_for('faculty.view', faculty_id=faculty_id))

@faculty_bp.route('/<int:faculty_id>/remove/<int:program_id>', methods=['POST'])
@login_required
def remove_from_program(faculty_id, program_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    program = Program.query.get_or_404(program_id)
    
    if program in faculty.programs:
        program.faculties.remove(faculty)
        db.session.commit()
        flash(f'{faculty.first_name} has been removed from {program.title}.', 'success')
    else:
        flash(f'{faculty.first_name} is not assigned to this program.', 'info')
    
    return redirect(url_for('faculty.view', faculty_id=faculty_id))
