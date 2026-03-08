from database import db

class Admin(db.Model):
    """This table represents the placement cell administrator."""
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    # Unique username for the admin
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Admin password
    password = db.Column(db.String(120), nullable=False)

class Student(db.Model):
    """This table stores student profiles."""
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    # Student name
    name = db.Column(db.String(100), nullable=False)
    # Unique email address for the student
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Student password
    password = db.Column(db.String(120), nullable=False)
    # Phone number
    phone = db.Column(db.String(20), nullable=True)
    # Student education details
    education = db.Column(db.String(200), nullable=True)
    # Skills possessed by the student
    skills = db.Column(db.Text, nullable=True)
    # Path to the uploaded resume
    resume_path = db.Column(db.String(200), nullable=True)
    # Boolean to check if the student is active
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship: A student can have multiple applications.
    applications = db.relationship('Application', backref='student', lazy=True)

class Company(db.Model):
    """Companies must be approved by admin before posting placement drives."""
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    # Company Name
    name = db.Column(db.String(100), nullable=False)
    # Unique company email
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Company password
    password = db.Column(db.String(120), nullable=False)
    # Company website
    website = db.Column(db.String(200), nullable=True)
    # HR contact details
    hr_contact = db.Column(db.String(100), nullable=True)
    # Approval status: Pending / Approved / Rejected
    approval_status = db.Column(db.String(50), default='Pending')
    # Boolean to check if the company is blacklisted
    is_blacklisted = db.Column(db.Boolean, default=False)
    
    # Relationship: One company can create multiple placement drives.
    drives = db.relationship('PlacementDrive', backref='company', lazy=True)

class PlacementDrive(db.Model):
    """This represents a recruitment drive created by a company."""
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    # Foreign key referencing company.id
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    # Job title
    job_title = db.Column(db.String(100), nullable=False)
    # Job description
    description = db.Column(db.Text, nullable=False)
    # Eligibility criteria
    eligibility = db.Column(db.Text, nullable=False)
    # Deadline to apply
    deadline = db.Column(db.String(50), nullable=False)
    # Status of the drive: Pending / Approved / Closed
    status = db.Column(db.String(50), default='Pending')
    
    # Relationship: A drive can receive multiple applications.
    applications = db.relationship('Application', backref='drive', lazy=True)

class Application(db.Model):
    """This table stores when students apply for placement drives."""
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    # Foreign key referencing student.id
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    # Foreign key referencing placementdrive.id
    # Note: Flask-SQLAlchemy automatically names the table 'placement_drive' by default.
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    # Date when the student applied
    date_applied = db.Column(db.String(50), nullable=False)
    # Status of the application: Applied / Shortlisted / Selected / Rejected
    status = db.Column(db.String(50), default='Applied')
