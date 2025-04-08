from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateTimeField, IntegerField, BooleanField, SelectMultipleField, HiddenField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, URL, ValidationError
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ProgramForm(FlaskForm):
    title = StringField('Program Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_date = DateTimeField('Start Date', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    end_date = DateTimeField('End Date', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    faculty_ids = SelectMultipleField('Faculty', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Program')
    
    def validate_end_date(self, field):
        if field.data < self.start_date.data:
            raise ValidationError('End date must be after start date')

class MaterialForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    file = FileField('Upload File', validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'], 'Only document files are allowed')])
    file_type = SelectField('File Type', choices=[
        ('pdf', 'PDF Document'),
        ('doc', 'Word Document'),
        ('ppt', 'PowerPoint'),
        ('xls', 'Excel Spreadsheet'),
        ('link', 'External Link')
    ])
    external_link = StringField('External Link', validators=[Optional(), URL()])
    program_id = HiddenField('Program ID')
    submit = SubmitField('Save Material')
    
    def validate(self):
        if not super(MaterialForm, self).validate():
            return False
            
        if self.file_type.data == 'link' and not self.external_link.data:
            self.external_link.errors.append('External link is required for link type materials')
            return False
            
        if self.file_type.data != 'link' and not self.file.data and self.file.flags.required:
            self.file.errors.append('File upload is required for this material type')
            return False
            
        return True

class ParticipantForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional()])
    organization = StringField('Organization', validators=[Optional()])
    role = StringField('Role/Position', validators=[Optional()])
    bio = TextAreaField('Biography', validators=[Optional()])
    submit = SubmitField('Save Participant')

class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    participant_id = HiddenField('Participant ID')
    submit = SubmitField('Send Message')

class FacultyForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional()])
    bio = TextAreaField('Biography', validators=[DataRequired()])
    expertise = StringField('Areas of Expertise', validators=[DataRequired()])
    contract_file = FileField('Upload Contract', validators=[Optional(), FileAllowed(['pdf'], 'Only PDF files are allowed')])
    submit = SubmitField('Save Faculty')

class PartnerForm(FlaskForm):
    name = StringField('Partner Name', validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional()])
    agreement_file = FileField('Upload Agreement', validators=[Optional(), FileAllowed(['pdf'], 'Only PDF files are allowed')])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Partner')

class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed')
    ])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])
    due_date = DateTimeField('Due Date', format='%Y-%m-%d %H:%M', validators=[Optional()])
    assigned_to = SelectField('Assigned To', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Task')

class ReportForm(FlaskForm):
    title = StringField('Report Title', validators=[DataRequired()])
    content = TextAreaField('Report Content', validators=[Optional()])
    report_date = DateTimeField('Report Date', format='%Y-%m-%d', default=datetime.now, validators=[DataRequired()])
    report_type = SelectField('Report Type', choices=[
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('annual', 'Annual Report'),
        ('custom', 'Custom Report')
    ])
    file = FileField('Upload Report File', validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'], 'Only document files are allowed')])
    submit = SubmitField('Save Report')

class PostForm(FlaskForm):
    title = StringField('Post Title', validators=[DataRequired()])
    content = TextAreaField('Post Content', validators=[DataRequired()])
    scheduled_date = DateTimeField('Schedule Date', format='%Y-%m-%d %H:%M', validators=[Optional()])
    platform = SelectField('Platform', choices=[
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('instagram', 'Instagram'),
        ('other', 'Other')
    ])
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published')
    ])
    submit = SubmitField('Save Post')

class CampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired()])
    type = SelectField('Campaign Type', choices=[
        ('email', 'Email Campaign'),
        ('seo', 'SEO Campaign'),
        ('social', 'Social Media Campaign'),
        ('other', 'Other')
    ])
    description = TextAreaField('Description', validators=[Optional()])
    start_date = DateTimeField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateTimeField('End Date', format='%Y-%m-%d', validators=[Optional()])
    metrics_file = FileField('Upload Metrics File', validators=[Optional(), FileAllowed(['csv', 'xls', 'xlsx'], 'Only CSV or Excel files are allowed')])
    submit = SubmitField('Save Campaign')
    
    def validate_end_date(self, field):
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('End date must be after start date')

class AIAssistantForm(FlaskForm):
    task_type = SelectField('Task Type', choices=[
        ('training_outline', 'Generate Training Outline'),
        ('social_post', 'Suggest Social Media Posts'),
        ('report_summary', 'Draft Weekly Report Summary'),
        ('follow_up_email', 'Recommend Follow-up Emails')
    ])
    input_text = TextAreaField('Input', validators=[DataRequired()])
    submit = SubmitField('Generate')
