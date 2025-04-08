import os
import sys
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get SendGrid API key from environment
sendgrid_key = os.environ.get('SENDGRID_API_KEY')
if not sendgrid_key:
    logger.warning("SENDGRID_API_KEY environment variable not set")

def send_email(
    to_email,
    from_email,
    subject,
    text_content=None,
    html_content=None
):
    """
    Send an email using SendGrid API
    
    Args:
        to_email (str): Recipient email address
        from_email (str): Sender email address
        subject (str): Email subject
        text_content (str, optional): Plain text content
        html_content (str, optional): HTML content
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not sendgrid_key:
        logger.error("SendGrid API key not available")
        return False
    
    sg = SendGridAPIClient(sendgrid_key)

    message = Mail(
        from_email=Email(from_email),
        to_emails=To(to_email),
        subject=subject
    )

    if html_content:
        message.content = Content("text/html", html_content)
    elif text_content:
        message.content = Content("text/plain", text_content)
    else:
        logger.error("Email must have either text or HTML content")
        return False

    try:
        response = sg.send(message)
        logger.info(f"Email sent successfully, status code: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"SendGrid error: {e}")
        return False

def send_confirmation_email(participant, program):
    """
    Send a confirmation email to a participant for a specific program
    
    Args:
        participant: Participant model object
        program: Program model object
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = f"Confirmation: Registration for {program.title}"
    
    # Create HTML content
    html_content = f"""
    <html>
    <body>
        <h1>Registration Confirmation</h1>
        <p>Dear {participant.first_name},</p>
        <p>Thank you for registering for <strong>{program.title}</strong>.</p>
        <p>Details:</p>
        <ul>
            <li><strong>Date:</strong> {program.start_date.strftime('%B %d, %Y')} to {program.end_date.strftime('%B %d, %Y')}</li>
            <li><strong>Location:</strong> {program.location}</li>
        </ul>
        <p>We look forward to your participation!</p>
        <p>Best regards,<br>Program Administration Team</p>
    </body>
    </html>
    """
    
    # Plain text alternative
    text_content = f"""
    Registration Confirmation
    
    Dear {participant.first_name},
    
    Thank you for registering for {program.title}.
    
    Details:
    - Date: {program.start_date.strftime('%B %d, %Y')} to {program.end_date.strftime('%B %d, %Y')}
    - Location: {program.location}
    
    We look forward to your participation!
    
    Best regards,
    Program Administration Team
    """
    
    return send_email(
        to_email=participant.email,
        from_email="admin@programadmin.com",
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )

def send_participant_inquiry(contact_data, participant=None):
    """
    Send an inquiry from a contact form
    
    Args:
        contact_data: Form data from contact form
        participant: Optional participant model object for context
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if participant:
        subject = f"Inquiry about participant: {participant.full_name}"
    else:
        subject = f"New inquiry: {contact_data.get('subject', 'No subject')}"
    
    # Create email content
    html_content = f"""
    <html>
    <body>
        <h1>New Inquiry</h1>
        <p><strong>From:</strong> {contact_data.get('name')}</p>
        <p><strong>Email:</strong> {contact_data.get('email')}</p>
        <p><strong>Subject:</strong> {contact_data.get('subject')}</p>
        <p><strong>Message:</strong></p>
        <p>{contact_data.get('message')}</p>
    </body>
    </html>
    """
    
    text_content = f"""
    New Inquiry
    
    From: {contact_data.get('name')}
    Email: {contact_data.get('email')}
    Subject: {contact_data.get('subject')}
    
    Message:
    {contact_data.get('message')}
    """
    
    return send_email(
        to_email="admin@programadmin.com", # Change to your admin email
        from_email="noreply@programadmin.com",
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )
