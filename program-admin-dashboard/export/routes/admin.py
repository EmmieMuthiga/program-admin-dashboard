from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from models import Report, Task, User
from forms import ReportForm, TaskForm
from app import db
from utils import save_file, generate_csv, generate_sample_data
import io
import csv
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/reports')
@login_required
def reports():
    reports = Report.query.order_by(Report.report_date.desc()).all()
    return render_template('admin/reports.html', reports=reports, title='Reports')

@admin_bp.route('/reports/create', methods=['GET', 'POST'])
@login_required
def create_report():
    form = ReportForm()
    
    if form.validate_on_submit():
        file_path = None
        if form.file.data:
            file_path = save_file(form.file.data, directory='reports')
        
        report = Report(
            title=form.title.data,
            content=form.content.data,
            report_date=form.report_date.data,
            report_type=form.report_type.data,
            file_path=file_path,
            created_by=current_user.id
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Report created successfully!', 'success')
        return redirect(url_for('admin.reports'))
    
    return render_template('admin/create_report.html', form=form, title='Create Report')

@admin_bp.route('/reports/<int:report_id>')
@login_required
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    return render_template('admin/view_report.html', report=report, title=report.title)

@admin_bp.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    db.session.delete(report)
    db.session.commit()
    
    flash('Report deleted successfully!', 'success')
    return redirect(url_for('admin.reports'))

@admin_bp.route('/reports/export', methods=['GET'])
@login_required
def export_reports():
    # Get report data from database
    reports = Report.query.order_by(Report.report_date.desc()).all()
    
    # Prepare data for CSV
    headers = ['Title', 'Type', 'Date', 'Created By']
    data = [[r.title, r.report_type, r.report_date.strftime('%Y-%m-%d'), r.creator.username] for r in reports]
    
    # Create CSV in memory
    csv_data = generate_csv(data, headers)
    
    # Create in-memory file
    mem_file = io.BytesIO()
    mem_file.write(csv_data.encode('utf-8'))
    mem_file.seek(0)
    
    return send_file(
        mem_file,
        mimetype='text/csv',
        download_name=f'reports_export_{datetime.now().strftime("%Y%m%d")}.csv',
        as_attachment=True
    )

@admin_bp.route('/tasks')
@login_required
def tasks():
    # Get all tasks for the task board
    pending_tasks = Task.query.filter_by(status='pending').order_by(Task.due_date).all()
    in_progress_tasks = Task.query.filter_by(status='in-progress').order_by(Task.due_date).all()
    completed_tasks = Task.query.filter_by(status='completed').order_by(Task.due_date).all()
    
    # Get all users for the task form
    users = User.query.all()
    
    # Create a new task form
    form = TaskForm()
    form.assigned_to.choices = [(u.id, u.username) for u in users]
    
    return render_template('admin/tasks.html', 
                          pending_tasks=pending_tasks,
                          in_progress_tasks=in_progress_tasks,
                          completed_tasks=completed_tasks,
                          form=form,
                          title='Task Board')

@admin_bp.route('/tasks/create', methods=['POST'])
@login_required
def create_task():
    form = TaskForm()
    users = User.query.all()
    form.assigned_to.choices = [(u.id, u.username) for u in users]
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            assigned_to=form.assigned_to.data,
            created_by=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully!', 'success')
    else:
        flash('There was an error creating the task. Please check the form.', 'danger')
    
    return redirect(url_for('admin.tasks'))

@admin_bp.route('/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Get data from request
    data = request.json
    
    if 'status' in data:
        task.status = data['status']
    
    if 'priority' in data:
        task.priority = data['priority']
    
    if 'assigned_to' in data:
        task.assigned_to = data['assigned_to']
    
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('admin.tasks'))
    
@admin_bp.route('/generate-sample-data', methods=['GET', 'POST'])
@login_required
def generate_data():
    if not current_user.is_admin:
        flash('Only administrators can generate sample data.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        result = generate_sample_data()
        flash(result, 'info')
        return redirect(url_for('dashboard'))
    
    return render_template('admin/generate_data.html', title='Generate Sample Data')
