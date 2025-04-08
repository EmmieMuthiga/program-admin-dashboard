import os
import random
import csv
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from faker import Faker
from app import db
from models import User, Program, Participant, Faculty, Material, Task, Post, Campaign, Attendance
from werkzeug.security import generate_password_hash

fake = Faker()

def save_file(file, directory='uploads'):
    """
    Save an uploaded file and return its path
    """
    if not file:
        return None
        
    # Ensure directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    file_path = os.path.join(directory, unique_filename)
    
    file.save(file_path)
    return file_path
    
def get_file_extension(filename):
    """
    Return the file extension of a filename
    """
    if not filename:
        return None
        
    return os.path.splitext(filename)[1].lower().lstrip('.')
    
def generate_csv(data, headers, filename='export.csv'):
    """
    Generate a CSV file from data
    """
    file_path = os.path.join('exports', filename)
    # Ensure directory exists
    if not os.path.exists('exports'):
        os.makedirs('exports')
        
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)
            
    return file_path

def generate_sample_data():
    """Generate sample data for the application"""
    # Check if we already have data
    if User.query.count() > 0:
        return "Sample data already exists. Please clear the database first."
    
    try:
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=generate_password_hash("adminpassword"),
            is_admin=True
        )
        db.session.add(admin)
        
        # Create regular user
        user = User(
            username="user",
            email="user@example.com",
            password_hash=generate_password_hash("userpassword"),
            is_admin=False
        )
        db.session.add(user)
        
        # Add faculties
        faculties = []
        for _ in range(10):
            faculty = Faculty(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number(),
                bio=fake.paragraph(nb_sentences=5),
                expertise=", ".join(fake.words(nb=3))
            )
            db.session.add(faculty)
            faculties.append(faculty)
        
        # Add programs
        programs = []
        statuses = ["draft", "active", "completed", "cancelled"]
        for i in range(20):
            start_date = fake.date_time_between(start_date="-30d", end_date="+180d")
            end_date = start_date + timedelta(days=random.randint(1, 30))
            status = statuses[random.randint(0, 3)]
            
            program = Program(
                title=fake.catch_phrase(),
                description=fake.paragraph(nb_sentences=3),
                start_date=start_date,
                end_date=end_date,
                location=fake.city(),
                capacity=random.randint(10, 50),
                status=status
            )
            
            # Assign random faculty to this program
            rand_faculties = random.sample(faculties, random.randint(1, 3))
            for fac in rand_faculties:
                program.faculties.append(fac)
                
            db.session.add(program)
            programs.append(program)
            
            # Add materials for each program
            for _ in range(random.randint(1, 5)):
                material = Material(
                    title=fake.bs(),
                    description=fake.paragraph(nb_sentences=2),
                    file_type=random.choice(["pdf", "doc", "link", "ppt"]),
                    external_link=fake.url() if random.random() > 0.5 else None,
                    program_id=program.id
                )
                db.session.add(material)
        
        # Add participants
        participants = []
        for _ in range(50):
            participant = Participant(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number(),
                organization=fake.company(),
                role=fake.job(),
                bio=fake.paragraph(nb_sentences=3)
            )
            db.session.add(participant)
            participants.append(participant)
            
        # Assign participants to programs
        for program in programs:
            # Randomly select participants for each program
            rand_participants = random.sample(participants, random.randint(5, 15))
            for participant in rand_participants:
                program.participants.append(participant)
                
                # Add attendance records with random status
                if program.status in ["active", "completed"]:
                    status = random.choice(["present", "absent", "excused"])
                    attendance = Attendance(
                        program_id=program.id,
                        participant_id=participant.id,
                        date=program.start_date,
                        status=status
                    )
                    db.session.add(attendance)
        
        # Add tasks
        priorities = ["low", "medium", "high"]
        statuses = ["pending", "in-progress", "completed"]
        for _ in range(15):
            task = Task(
                title=fake.sentence(nb_words=6),
                description=fake.paragraph(nb_sentences=2),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                due_date=fake.date_time_between(start_date="now", end_date="+30d"),
                assigned_to=user.id if random.random() > 0.5 else admin.id,
                created_by=admin.id
            )
            db.session.add(task)
            
        # Add posts
        platforms = ["facebook", "twitter", "linkedin", "instagram"]
        post_statuses = ["draft", "scheduled", "published"]
        for _ in range(10):
            post = Post(
                title=fake.sentence(nb_words=6),
                content=fake.paragraph(nb_sentences=3),
                scheduled_date=fake.date_time_between(start_date="now", end_date="+30d") if random.random() > 0.3 else None,
                platform=random.choice(platforms),
                status=random.choice(post_statuses),
                created_by=admin.id
            )
            db.session.add(post)
            
        # Add campaigns
        campaign_types = ["email", "seo", "social"]
        for _ in range(5):
            start_date = fake.date_time_between(start_date="-30d", end_date="+30d")
            end_date = start_date + timedelta(days=random.randint(30, 90))
            
            campaign = Campaign(
                name=fake.catch_phrase(),
                type=random.choice(campaign_types),
                description=fake.paragraph(nb_sentences=2),
                start_date=start_date,
                end_date=end_date,
                created_by=admin.id
            )
            db.session.add(campaign)
            
        db.session.commit()
        return "Sample data generated successfully!"
    
    except Exception as e:
        db.session.rollback()
        return f"Error generating sample data: {str(e)}"