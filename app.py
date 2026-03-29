from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db
from models import Admin, Student, Company, PlacementDrive, Application

# Initialize Flask app, configure it, and connect the database
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Create database tables and the default admin user if it doesn't exist
with app.app_context():
    db.create_all()
    admin_user = Admin.query.filter_by(username='admin').first()
    if not admin_user:
        default_admin = Admin(username='admin', password='admin123')
        db.session.add(default_admin)
        db.session.commit()

# AUTHENTICATION & REGISTRATION ROUTES

# Redirect the root URL to the login page
@app.route('/')
def home():
    return redirect(url_for('login'))

# Handle user login based on role (Admin, Company, or Student)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        email_or_username = request.form.get('email')
        password = request.form.get('password')

        if role == 'admin':
            user = Admin.query.filter_by(username=email_or_username, password=password).first()
            if user:
                session['user_id'] = user.id
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))
                
        elif role == 'company':
            user = Company.query.filter_by(email=email_or_username, password=password).first()
            if user:
                session['user_id'] = user.id
                session['role'] = 'company'
                return redirect(url_for('company_dashboard'))
                
        elif role == 'student':
            user = Student.query.filter_by(email=email_or_username, password=password).first()
            if user:
                session['user_id'] = user.id
                session['role'] = 'student'
                return redirect(url_for('student_dashboard'))

        flash('Oops! Invalid credentials or you picked the wrong role. Please try again.')
        return redirect(url_for('login'))

    return render_template('login.html')

# Log out user by clearing the session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Register a new student and securely save their resume
@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        education = request.form.get('education')
        skills = request.form.get('skills')
        branch = request.form.get('branch')
        father_name = request.form.get('father_name')
        
        import os
        from werkzeug.utils import secure_filename
        
        resume_file = request.files.get('resume')
        resume_path = None
        
        if resume_file and resume_file.filename:
            resume_path = secure_filename(resume_file.filename)
            save_dir = os.path.join(app.root_path, 'static', 'resumes')
            os.makedirs(save_dir, exist_ok=True)
            resume_file.save(os.path.join(save_dir, resume_path))

        new_student = Student(
            name=name, email=email, password=password,
            phone=phone, education=education, skills=skills,
            resume_path=resume_path, branch=branch, father_name=father_name
        )
        db.session.add(new_student)
        db.session.commit()
        
        flash('You have registered successfully! You can now login.')
        return redirect(url_for('login'))
        
    return render_template('register_student.html')

# Register a new company (requires admin approval later)
@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        name = request.form.get('company_name')
        email = request.form.get('email')
        password = request.form.get('password')
        website = request.form.get('website')
        hr_contact = request.form.get('hr_contact')

        new_company = Company(
            name=name, email=email, password=password,
            website=website, hr_contact=hr_contact
        )
        
        db.session.add(new_company)
        db.session.commit()
        
        flash('Company registered! But you have to wait for the Admin to approve you before you can use the dashboard.')
        return redirect(url_for('login'))
        
    return render_template('register_company.html')

# DASHBOARD ROUTES WITH ACCESS CONTROL

# Display statistics on the admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
        
    return render_template('admin/dashboard.html', 
                           total_students=total_students,
                           total_companies=total_companies,
                           total_drives=total_drives,
                           total_applications=total_applications)

# ADMIN MANAGEMENT ROUTES - COMPANIES

# List all companies or filter by search query
@app.route('/admin/companies')
def admin_companies():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    search_query = request.args.get('search')
    
    if search_query:
        companies = Company.query.filter(Company.name.contains(search_query)).all()
    else:
        companies = Company.query.all()
        
    return render_template('admin/companies.html', companies=companies)

# Approve a registered company
@app.route('/admin/approve-company/<int:company_id>')
def approve_company(company_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    company = db.session.get(Company, company_id)
    if company:
        company.approval_status = 'Approved'
        db.session.commit()
        flash(f'Company {company.name} has been Approved!')
        
    return redirect(url_for('admin_companies'))

# Reject a registered company
@app.route('/admin/reject-company/<int:company_id>')
def reject_company(company_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    company = db.session.get(Company, company_id)
    if company:
        company.approval_status = 'Rejected'
        db.session.commit()
        flash(f'Company {company.name} has been Rejected.')
        
    return redirect(url_for('admin_companies'))

# Blacklist a company
@app.route('/admin/blacklist-company/<int:company_id>')
def blacklist_company(company_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    company = db.session.get(Company, company_id)
    if company:
        company.is_blacklisted = True
        db.session.commit()
        flash(f'Company {company.name} has been Blacklisted.')
        
    return redirect(url_for('admin_companies'))

# ADMIN MANAGEMENT ROUTES - STUDENTS

# List all students or filter by search query
@app.route('/admin/students')
def admin_students():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    search_query = request.args.get('search')
    
    if search_query:
        students = Student.query.filter(
            (Student.name.contains(search_query)) | 
            (Student.email.contains(search_query)) | 
            (Student.phone.contains(search_query))
        ).all()
    else:
        students = Student.query.all()
        
    return render_template('admin/students.html', students=students)

# Deactivate a student account
@app.route('/admin/deactivate-student/<int:student_id>')
def deactivate_student(student_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    student = db.session.get(Student, student_id)
    if student:
        student.is_active = False
        db.session.commit()
        flash(f'Student {student.name} deactivated successfully.')
        
    return redirect(url_for('admin_students'))

# ADMIN MANAGEMENT ROUTES - DRIVES

# View all placement drives
@app.route('/admin/drives')
def admin_drives():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    drives = PlacementDrive.query.all()
    return render_template('admin/drives.html', drives=drives)

# Approve a placement drive posted by a company
@app.route('/admin/approve-drive/<int:drive_id>')
def approve_drive(drive_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    drive = db.session.get(PlacementDrive, drive_id)
    if drive:
        drive.status = 'Approved'
        db.session.commit()
        flash(f'Placement drive "{drive.job_title}" approved!')
        
    return redirect(url_for('admin_drives'))

# Reject a placement drive posted by a company
@app.route('/admin/reject-drive/<int:drive_id>')
def reject_drive(drive_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    drive = db.session.get(PlacementDrive, drive_id)
    if drive:
        drive.status = 'Rejected'
        db.session.commit()
        flash(f'Placement drive "{drive.job_title}" rejected.')
        
    return redirect(url_for('admin_drives'))

# Display company dashboard and drives specific to the company
@app.route('/company/dashboard')
def company_dashboard():
    if session.get('role') != 'company':
        return redirect(url_for('login'))
        
    company_id = session.get('user_id')
    current_company = db.session.get(Company, company_id)
    
    drives = PlacementDrive.query.filter_by(company_id=company_id).all()
    
    return render_template('company/dashboard.html', company=current_company, drives=drives)

# Allow approved companies to post new placement drives
@app.route('/company/post-drive', methods=['GET', 'POST'])
def post_drive():
    if session.get('role') != 'company':
        return redirect(url_for('login'))
        
    company_id = session.get('user_id')
    current_company = db.session.get(Company, company_id)
    
    if current_company.approval_status != 'Approved':
        flash('You must be approved by the admin to post drives.')
        return redirect(url_for('company_dashboard'))
        
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        description = request.form.get('description')
        eligibility = request.form.get('eligibility')
        deadline = request.form.get('deadline')
        
        new_drive = PlacementDrive(
            company_id=company_id,
            job_title=job_title,
            description=description,
            eligibility=eligibility,
            deadline=deadline,
            status='Pending'
        )
        
        db.session.add(new_drive)
        db.session.commit()
        
        flash('Placement drive posted successfully! Waiting for admin approval.')
        return redirect(url_for('company_dashboard'))
        
    return render_template('company/post_drive.html', company=current_company)

# View applications for a specific drive belonging to the company
@app.route('/company/applications/<int:drive_id>')
def view_drive_applications(drive_id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))
        
    company_id = session.get('user_id')
    drive = db.session.get(PlacementDrive, drive_id)
    
    if not drive or drive.company_id != company_id:
        flash("You do not have permission to view this drive's applications.")
        return redirect(url_for('company_dashboard'))
        
    applications = Application.query.filter_by(drive_id=drive_id).all()
    
    return render_template('company/applications.html', drive=drive, applications=applications)

# Update application status by the company
@app.route('/company/update-application/<int:application_id>', methods=['POST'])
def update_application(application_id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))
        
    company_id = session.get('user_id')
    application = db.session.get(Application, application_id)
    
    if not application or application.drive.company_id != company_id:
        flash("Unauthorized action.")
        return redirect(url_for('company_dashboard'))
        
    new_status = request.form.get('status')
    valid_statuses = ['Applied', 'Shortlisted', 'Interview', 'Selected', 'Rejected', 'Placed']
    
    if new_status in valid_statuses:
        application.status = new_status
        db.session.commit()
        flash(f"Application status updated to '{new_status}' successfully.")
        
    return redirect(url_for('view_drive_applications', drive_id=application.drive_id))

from datetime import date

# STUDENT ROUTES AND DASHBOARD

# Display student dashboard with approved drives
@app.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    student_id = session.get('user_id')
    current_student = db.session.get(Student, student_id)
    
    approved_drives = PlacementDrive.query.filter_by(status='Approved').all()
    
    return render_template('student/dashboard.html', student=current_student, drives=approved_drives)

# Apply to a specific approved placement drive
@app.route('/student/apply/<int:drive_id>')
def apply_to_drive(drive_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    student_id = session.get('user_id')
    existing_application = Application.query.filter_by(student_id=student_id, drive_id=drive_id).first()
    
    if existing_application:
        flash('You have already applied for this drive.')
    else:
        new_application = Application(
            student_id=student_id,
            drive_id=drive_id,
            date_applied=date.today().strftime("%Y-%m-%d"),
            status='Applied'
        )
        db.session.add(new_application)
        db.session.commit()
        flash('Successfully applied to the drive!')
        
    return redirect(url_for('student_dashboard'))

# View all applications submitted by the student
@app.route('/student/applications')
def student_applications():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    student_id = session.get('user_id')
    current_student = db.session.get(Student, student_id)
    
    applications = Application.query.filter_by(student_id=student_id).all()
    
    return render_template('student/applications.html', student=current_student, applications=applications)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
