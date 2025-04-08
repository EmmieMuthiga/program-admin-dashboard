from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Participant, Program
from forms import ParticipantForm, ContactForm
from app import db
from sendgrid_helper import send_confirmation_email, send_participant_inquiry

participants_bp = Blueprint('participants', __name__, url_prefix='/participants')

@participants_bp.route('/')
@login_required
def index():
    participants = Participant.query.order_by(Participant.last_name).all()
    return render_template('participants/index.html', participants=participants, title='Participants')

@participants_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ParticipantForm()
    
    if form.validate_on_submit():
        # Check if participant with this email already exists
        existing = Participant.query.filter_by(email=form.email.data).first()
        if existing:
            flash('A participant with this email already exists.', 'danger')
            return render_template('participants/create.html', form=form, title='Add Participant')
        
        participant = Participant(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            organization=form.organization.data,
            role=form.role.data,
            bio=form.bio.data
        )
        
        db.session.add(participant)
        db.session.commit()
        
        flash('Participant added successfully!', 'success')
        return redirect(url_for('participants.view', participant_id=participant.id))
    
    return render_template('participants/create.html', form=form, title='Add Participant')

@participants_bp.route('/<int:participant_id>')
@login_required
def view(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    return render_template('participants/view.html', participant=participant, title=f'{participant.first_name} {participant.last_name}')

@participants_bp.route('/<int:participant_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    form = ParticipantForm(obj=participant)
    
    if form.validate_on_submit():
        # Check if email is changed and already exists for another participant
        if form.email.data != participant.email:
            existing = Participant.query.filter_by(email=form.email.data).first()
            if existing:
                flash('A participant with this email already exists.', 'danger')
                return render_template('participants/edit.html', form=form, participant=participant, title=f'Edit {participant.first_name} {participant.last_name}')
        
        participant.first_name = form.first_name.data
        participant.last_name = form.last_name.data
        participant.email = form.email.data
        participant.phone = form.phone.data
        participant.organization = form.organization.data
        participant.role = form.role.data
        participant.bio = form.bio.data
        
        db.session.commit()
        
        flash('Participant updated successfully!', 'success')
        return redirect(url_for('participants.view', participant_id=participant.id))
    
    return render_template('participants/edit.html', form=form, participant=participant, title=f'Edit {participant.first_name} {participant.last_name}')

@participants_bp.route('/<int:participant_id>/delete', methods=['POST'])
@login_required
def delete(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    
    db.session.delete(participant)
    db.session.commit()
    
    flash('Participant deleted successfully!', 'success')
    return redirect(url_for('participants.index'))

@participants_bp.route('/<int:participant_id>/assign/<int:program_id>', methods=['POST'])
@login_required
def assign_to_program(participant_id, program_id):
    participant = Participant.query.get_or_404(participant_id)
    program = Program.query.get_or_404(program_id)
    
    # Check if already assigned
    if program in participant.programs:
        flash(f'{participant.first_name} is already assigned to this program.', 'info')
    else:
        participant.programs.append(program)
        db.session.commit()
        flash(f'{participant.first_name} has been assigned to {program.title}.', 'success')
        
        # Send confirmation email
        send_confirmation_email(participant, program)
    
    return redirect(url_for('participants.view', participant_id=participant_id))

@participants_bp.route('/<int:participant_id>/remove/<int:program_id>', methods=['POST'])
@login_required
def remove_from_program(participant_id, program_id):
    participant = Participant.query.get_or_404(participant_id)
    program = Program.query.get_or_404(program_id)
    
    if program in participant.programs:
        participant.programs.remove(program)
        db.session.commit()
        flash(f'{participant.first_name} has been removed from {program.title}.', 'success')
    else:
        flash(f'{participant.first_name} is not assigned to this program.', 'info')
    
    return redirect(url_for('participants.view', participant_id=participant_id))

@participants_bp.route('/<int:participant_id>/contact', methods=['GET', 'POST'])
@login_required
def contact(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    form = ContactForm()
    
    if form.validate_on_submit():
        contact_data = {
            'name': form.name.data,
            'email': form.email.data,
            'subject': form.subject.data,
            'message': form.message.data
        }
        
        if send_participant_inquiry(contact_data, participant):
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('participants.view', participant_id=participant_id))
        else:
            flash('There was an error sending your message. Please try again.', 'danger')
    
    return render_template('participants/contact.html', form=form, participant=participant, title=f'Contact {participant.first_name}')
