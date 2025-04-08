from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Program, Faculty, Material
from forms import ProgramForm, MaterialForm
from app import db
from utils import save_file, get_file_extension

programs_bp = Blueprint('programs', __name__, url_prefix='/programs')

@programs_bp.route('/')
@login_required
def index():
    programs = Program.query.order_by(Program.start_date.desc()).all()
    return render_template('programs/index.html', programs=programs, title='Training Programs')

@programs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ProgramForm()
    
    # Get all faculty for the select field
    form.faculty_ids.choices = [(f.id, f"{f.first_name} {f.last_name}") for f in Faculty.query.all()]
    
    if form.validate_on_submit():
        program = Program(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            location=form.location.data,
            capacity=form.capacity.data,
            status=form.status.data
        )
        
        # Add faculty to program
        if form.faculty_ids.data:
            faculty_list = Faculty.query.filter(Faculty.id.in_(form.faculty_ids.data)).all()
            program.faculties.extend(faculty_list)
        
        db.session.add(program)
        db.session.commit()
        
        flash('Program created successfully!', 'success')
        return redirect(url_for('programs.view', program_id=program.id))
    
    return render_template('programs/create.html', form=form, title='Create Program')

@programs_bp.route('/<int:program_id>')
@login_required
def view(program_id):
    program = Program.query.get_or_404(program_id)
    materials = Material.query.filter_by(program_id=program_id).all()
    return render_template('programs/view.html', program=program, materials=materials, title=program.title)

@programs_bp.route('/<int:program_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(program_id):
    program = Program.query.get_or_404(program_id)
    form = ProgramForm(obj=program)
    
    # Get all faculty for the select field
    form.faculty_ids.choices = [(f.id, f"{f.first_name} {f.last_name}") for f in Faculty.query.all()]
    
    # Set current faculty selections
    if request.method == 'GET':
        form.faculty_ids.data = [f.id for f in program.faculties]
    
    if form.validate_on_submit():
        program.title = form.title.data
        program.description = form.description.data
        program.start_date = form.start_date.data
        program.end_date = form.end_date.data
        program.location = form.location.data
        program.capacity = form.capacity.data
        program.status = form.status.data
        
        # Update faculty assignments
        program.faculties = []
        if form.faculty_ids.data:
            faculty_list = Faculty.query.filter(Faculty.id.in_(form.faculty_ids.data)).all()
            program.faculties.extend(faculty_list)
        
        db.session.commit()
        
        flash('Program updated successfully!', 'success')
        return redirect(url_for('programs.view', program_id=program.id))
    
    return render_template('programs/edit.html', form=form, program=program, title=f'Edit {program.title}')

@programs_bp.route('/<int:program_id>/delete', methods=['POST'])
@login_required
def delete(program_id):
    program = Program.query.get_or_404(program_id)
    
    # Delete associated materials
    Material.query.filter_by(program_id=program_id).delete()
    
    db.session.delete(program)
    db.session.commit()
    
    flash('Program deleted successfully!', 'success')
    return redirect(url_for('programs.index'))

@programs_bp.route('/<int:program_id>/materials/add', methods=['GET', 'POST'])
@login_required
def add_material(program_id):
    program = Program.query.get_or_404(program_id)
    form = MaterialForm()
    
    if form.validate_on_submit():
        file_path = None
        if form.file.data:
            file_path = save_file(form.file.data, directory='materials')
        
        material = Material(
            title=form.title.data,
            description=form.description.data,
            file_path=file_path,
            file_type=form.file_type.data,
            external_link=form.external_link.data,
            program_id=program_id
        )
        
        db.session.add(material)
        db.session.commit()
        
        flash('Material added successfully!', 'success')
        return redirect(url_for('programs.view', program_id=program_id))
    
    return render_template('programs/add_material.html', form=form, program=program, title='Add Material')

@programs_bp.route('/materials/<int:material_id>/delete', methods=['POST'])
@login_required
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    program_id = material.program_id
    
    db.session.delete(material)
    db.session.commit()
    
    flash('Material deleted successfully!', 'success')
    return redirect(url_for('programs.view', program_id=program_id))
