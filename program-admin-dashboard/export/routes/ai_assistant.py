from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from forms import AIAssistantForm
from openai_helper import generate_training_outline, suggest_social_media_posts, draft_report_summary, recommend_follow_up_emails

ai_bp = Blueprint('ai_assistant', __name__, url_prefix='/ai-assistant')

@ai_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = AIAssistantForm()
    result = None
    task_type = None
    
    if form.validate_on_submit():
        task_type = form.task_type.data
        input_text = form.input_text.data
        
        if task_type == 'training_outline':
            result = generate_training_outline(input_text)
        elif task_type == 'social_post':
            result = suggest_social_media_posts(input_text)
        elif task_type == 'report_summary':
            result = draft_report_summary(input_text)
        elif task_type == 'follow_up_email':
            result = recommend_follow_up_emails(input_text)
        
        flash('AI-generated content created successfully!', 'success')
    
    return render_template('ai_assistant.html', form=form, result=result, task_type=task_type, title='AI Assistant')

@ai_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    """AJAX endpoint for generating AI content"""
    data = request.json
    task_type = data.get('task_type')
    input_text = data.get('input_text')
    result = None
    
    if not task_type or not input_text:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        if task_type == 'training_outline':
            result = generate_training_outline(input_text)
        elif task_type == 'social_post':
            result = suggest_social_media_posts(input_text)
        elif task_type == 'report_summary':
            result = draft_report_summary(input_text)
        elif task_type == 'follow_up_email':
            result = recommend_follow_up_emails(input_text)
        else:
            return jsonify({'error': 'Invalid task type'}), 400
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
