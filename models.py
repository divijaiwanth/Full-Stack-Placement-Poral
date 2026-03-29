from database import db

# This class creates the Admin table.
# The admin is the one who controls the placement cell.
class Admin(db.Model):
    # Every table needs an ID as a primary key.
    id = db.Column(db.Integer, primary_key=True)
    # The username must be unique so two people can't have the same one.
    username = db.Column(db.String(80), unique=True, nullable=False)
    # The password is required (nullable=False).
    password = db.Column(db.String(120), nullable=False)

# This table will store all the profile details of the students who register.
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # The student's full name.
    name = db.Column(db.String(100), nullable=False)
    # Using email as a unique identifier for login.
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Store their password.
    password = db.Column(db.String(120), nullable=False)
    
    # These fields are optional so nullable=True.
    phone = db.Column(db.String(20), nullable=True)
    education = db.Column(db.String(200), nullable=True)
    # Using db.Text because skills could be a long paragraph.
    skills = db.Column(db.Text, nullable=True)
    # I am just storing the path to the resume file here, not the actual file.
    resume_path = db.Column(db.String(200), nullable=True)
    # This checks if the student account is active. I might use it later to ban students.
    branch = db.Column(db.String(10), default="Btech",nullable=False)
    father_name = db.Column(db.String(100),nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # A relationship link! One student can have many applications. 
    applications = db.relationship('Application', backref='student', lazy=True)

# This table stores the companies who want to recruit students.
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Company email is unique and used for their login.
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    # Extra details about the company.
    website = db.Column(db.String(200), nullable=True)
    hr_contact = db.Column(db.String(100), nullable=True)
    
    # Very important: Companies are "Pending" until the admin approves them.
    approval_status = db.Column(db.String(50), default='Pending')
    # Admin can blacklist a company if they do something wrong.
    is_blacklisted = db.Column(db.Boolean, default=False)
    
    # Relationship: One company can post many placement drives.
    drives = db.relationship('PlacementDrive', backref='company', lazy=True)

# This table represents a single job posting or "drive" created by a company.
class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Foreign key linking this drive to the company who created it.
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    
    # Details about the job.
    job_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    eligibility = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.String(50), nullable=False)
    
    # Drives start as pending until approved by admin. Then they can be closed later.
    status = db.Column(db.String(50), default='Pending')
    
    # Relationship: Many students can apply to this one drive.
    applications = db.relationship('Application', backref='drive', lazy=True)

# This table keeps track of when a student applies for a specific drive.
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Link to the student who is applying.
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    # Link to the drive they are applying for. 
    # Flask-SQLAlchemy automatically named the table 'placement_drive'.
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    
    # Storing the date they applied.
    date_applied = db.Column(db.String(50), nullable=False)
    # The status tells us if they are shortlisted, selected, or rejected.
    status = db.Column(db.String(50), default='Applied')
