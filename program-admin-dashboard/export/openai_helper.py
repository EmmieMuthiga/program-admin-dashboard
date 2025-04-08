import os
import json
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize OpenAI client if API key is available
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = None

if OPENAI_API_KEY:
    openai = OpenAI(api_key=OPENAI_API_KEY)
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    MODEL = "gpt-4o"
else:
    logger.warning("OPENAI_API_KEY environment variable not set. AI assistant functions will return placeholder messages.")
    MODEL = None

def generate_training_outline(program_title, additional_info=""):
    """
    Generate a training outline based on a program title and additional information
    """
    if not OPENAI_API_KEY:
        return "OpenAI API key is not configured. Please provide the OPENAI_API_KEY environment variable to use this feature."
    
    try:
        prompt = f"""
        Please create a comprehensive training outline for a program titled: "{program_title}"
        
        Additional information about the program:
        {additional_info}
        
        The outline should include:
        1. Program objectives
        2. Key topics to cover
        3. Suggested timeline/schedule
        4. Recommended learning activities
        5. Assessment methods
        
        Format the response as a structured outline that could be presented to participants.
        """
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert curriculum designer with experience in creating effective training programs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating training outline: {e}")
        return f"An error occurred while generating the training outline: {str(e)}"

def suggest_social_media_posts(training_topic, platform="general", number_of_posts=3):
    """
    Generate social media post ideas based on a training topic
    """
    if not OPENAI_API_KEY:
        return "OpenAI API key is not configured. Please provide the OPENAI_API_KEY environment variable to use this feature."
    
    try:
        prompt = f"""
        Generate {number_of_posts} engaging social media post ideas related to the training topic: "{training_topic}"
        
        Target platform: {platform}
        
        For each post idea, include:
        1. A catchy headline or opening line
        2. The main post content (appropriate length for the platform)
        3. Suggested hashtags
        4. A call to action
        
        Format the response as a numbered list of posts.
        """
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a social media marketing expert specializing in educational content and training programs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating social media posts: {e}")
        return f"An error occurred while generating social media posts: {str(e)}"

def draft_report_summary(report_data):
    """
    Generate a summary of weekly report data
    """
    if not OPENAI_API_KEY:
        return "OpenAI API key is not configured. Please provide the OPENAI_API_KEY environment variable to use this feature."
    
    try:
        prompt = f"""
        Please draft a concise and professional weekly report summary based on the following data:
        
        {report_data}
        
        The summary should include:
        1. Key accomplishments for the week
        2. Important metrics or numbers
        3. Challenges faced
        4. Next steps or action items
        
        Format it as a professional executive summary that could be shared with stakeholders.
        """
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert report writer with experience in educational program management and administration."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating report summary: {e}")
        return f"An error occurred while generating the report summary: {str(e)}"

def recommend_follow_up_emails(program_info, participant_type="all"):
    """
    Generate follow-up email templates for program participants
    """
    if not OPENAI_API_KEY:
        return "OpenAI API key is not configured. Please provide the OPENAI_API_KEY environment variable to use this feature."
    
    try:
        prompt = f"""
        Please create email templates for follow-up communications with participants of the following program:
        
        Program details: {program_info}
        Participant type: {participant_type}
        
        Generate three different email templates:
        1. A "thank you" email for immediately after the program
        2. A "feedback request" email for 3 days after the program
        3. A "next steps" email for 1-2 weeks after the program
        
        Each template should include:
        - A subject line
        - Greeting
        - Body text
        - Call to action
        - Professional sign-off
        
        Format as three complete email templates ready to be personalized and sent.
        """
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an experienced communications specialist who creates engaging and effective follow-up emails for educational programs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating follow-up emails: {e}")
        return f"An error occurred while generating follow-up emails: {str(e)}"
