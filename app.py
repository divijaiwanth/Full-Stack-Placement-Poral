from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db
from models import Admin, Student, Company, PlacementDrive, Application

# I am creating my main Flask application right here. This is the core of my project.
app = Flask(__name__)

# Now I'm telling the app to load all my settings from the Config class in config.py.
app.config.from_object(Config)

# Let's connect my SQLAlchemy database to this Flask app.
db.init_app(app)

# Before the app fully starts, I need to make sure my database tables are created.
with app.app_context():
    # This nice command automatically builds the placement.db file and tables if they are missing.
    db.create_all()
    
    # I want to check if the admin user exists. If not, I will create one.
    # This way I don't have to manually insert the admin every time I reset the database.
    admin_user = Admin.query.filter_by(username='admin').first()
    if not admin_user:
        # Putting in the default admin details from my project requirements.
        default_admin = Admin(username='admin', password='admin123')
        db.session.add(default_admin)
        db.session.commit()
        print("I successfully created the default admin user!")

# ==========================================
# AUTHENTICATION & REGISTRATION ROUTES
# ==========================================

# This is the main route. If someone goes to my website, I just want to send them to the login page.
@app.route('/')
def home():
    return redirect(url_for('login'))

# This route handles both showing the login form (GET) and processing the login (POST).
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user clicked the 'Login' button, the request method will be POST.
    if request.method == 'POST':
        # Let's grab what they typed in the HTML form.
        role = request.form.get('role')
        email_or_username = request.form.get('email')
        password = request.form.get('password')

        # I need to check which role they selected so I know which table to search in the database.
        if role == 'admin':
            # For admin, they use a username to log in.
            user = Admin.query.filter_by(username=email_or_username, password=password).first()
            if user:
                # If they are found, I save their ID and role in the Flask session so they stay logged in.
                session['user_id'] = user.id
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))
                
        elif role == 'company':
            # Companies use email to log in.
            user = Company.query.filter_by(email=email_or_username, password=password).first()
            if user:
                session['user_id'] = user.id
                session['role'] = 'company'
                return redirect(url_for('company_dashboard'))
                
        elif role == 'student':
            # Students also use email to log in.
            user = Student.query.filter_by(email=email_or_username, password=password).first()
            if user:
                session['user_id'] = user.id
                session['role'] = 'student'
                return redirect(url_for('student_dashboard'))

        # If I get past all those 'if' statements without returning, it means they typed the wrong password.
        # I use 'flash' to send an error message back to the HTML page.
        flash('Oops! Invalid credentials or you picked the wrong role. Please try again.')
        return redirect(url_for('login'))

    # If it's a GET request (they just visited the page), I show them the login HTML file.
    return render_template('login.html')

# When they want to log out, I just clear the session. It's like throwing away their entry ticket.
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# This route handles student registration.
@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        # I pull all the details from the student form...
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        education = request.form.get('education')
        skills = request.form.get('skills')
        
        import os
        from werkzeug.utils import secure_filename
        
        # For the resume, let's actually save it!
        resume_file = request.files.get('resume')
        resume_path = None
        
        if resume_file and resume_file.filename:
            # Secure the filename so no one can upload weird files like ../../../etc/passwd
            resume_path = secure_filename(resume_file.filename)
            # Create the 'static/resumes' folder if it doesn't exist yet
            save_dir = os.path.join(app.root_path, 'static', 'resumes')
            os.makedirs(save_dir, exist_ok=True)
            # Save the file physically to the directories
            resume_file.save(os.path.join(save_dir, resume_path))

        # Now I create a new Student object using my database model.
        new_student = Student(
            name=name, email=email, password=password,
            phone=phone, education=education, skills=skills,
            resume_path=resume_path
        )
        # Adding it to the session and committing saves it to the SQLite database.
        db.session.add(new_student)
        db.session.commit()
        
        # Tell them it worked and send them to the login page.
        flash('You have registered successfully! You can now login.')
        return redirect(url_for('login'))
        
    # If GET, just show the form.
    return render_template('register_student.html')

# This route handles company registration.
@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        # Get data from the company registration form.
        name = request.form.get('company_name')
        email = request.form.get('email')
        password = request.form.get('password')
        website = request.form.get('website')
        hr_contact = request.form.get('hr_contact')

        # Create the Company object.
        # Note: I don't need to pass approval_status because my model sets it to 'Pending' automatically!
        new_company = Company(
            name=name, email=email, password=password,
            website=website, hr_contact=hr_contact
        )
        
        db.session.add(new_company)
        db.session.commit()
        
        # Explain to the company that they can't do anything until the admin says okay.
        flash('Company registered! But you have to wait for the Admin to approve you before you can use the dashboard.')
        return redirect(url_for('login'))
        
    return render_template('register_company.html')

# ==========================================
# DASHBOARD ROUTES WITH ACCESS CONTROL
# ==========================================

# The admin dashboard route.
@app.route('/admin/dashboard')
def admin_dashboard():
    # Security check: If the session says their role is not 'admin', kick them out to the login page!
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    # We need to count how many records are in each table to show statistics.
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
        
    # Pass all these totals to the template so it can display them.
    return render_template('admin/dashboard.html', 
                           total_students=total_students,
                           total_companies=total_companies,
                           total_drives=total_drives,
                           total_applications=total_applications)

# ==========================================
# ADMIN MANAGEMENT ROUTES - COMPANIES
# ==========================================

@app.route('/admin/companies')
def admin_companies():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    # We grab the 'search' parameter from the URL if it exists (e.g. ?search=Google)
    search_query = request.args.get('search')
    
    # If the admin typed something in the search bar, filter the users list.
    if search_query:
        # We look for any company whose name contains the search query.
        companies = Company.query.filter(Company.name.contains(search_query)).all()
    else:
        # Otherwise, just grab every single company in the database.
        companies = Company.query.all()
        
    return render_template('admin/companies.html', companies=companies)

@app.route('/admin/approve-company/<int:company_id>')
def approve_company(company_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    # Grab the specific company by its ID
    company = db.session.get(Company, company_id)
    if company:
        company.approval_status = 'Approved' # Change status to approved
        db.session.commit() # Save changes to database
        flash(f'Company {company.name} has been Approved!')
        
    return redirect(url_for('admin_companies'))

@app.route('/admin/reject-company/<int:company_id>')
def reject_company(company_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    company = db.session.get(Company, company_id)
    if company:
        company.approval_status = 'Rejected' # Change status to rejected
        db.session.commit()
        flash(f'Company {company.name} has been Rejected.')
        
    return redirect(url_for('admin_companies'))

@app.route('/admin/blacklist-company/<int:company_id>')
def blacklist_company(company_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    company = db.session.get(Company, company_id)
    if company:
        company.is_blacklisted = True # Mark it as completely blacklisted
        db.session.commit()
        flash(f'Company {company.name} has been Blacklisted.')
        
    return redirect(url_for('admin_companies'))

# ==========================================
# ADMIN MANAGEMENT ROUTES - STUDENTS
# ==========================================

@app.route('/admin/students')
def admin_students():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    search_query = request.args.get('search')
    
    if search_query:
        # Search across their name, email, or phone. Use the | (OR) operator for SQLAlchemy.
        # This checks if the query string is inside ANY of those three columns.
        students = Student.query.filter(
            (Student.name.contains(search_query)) | 
            (Student.email.contains(search_query)) | 
            (Student.phone.contains(search_query))
        ).all()
    else:
        # If no search query, list them all.
        students = Student.query.all()
        
    return render_template('admin/students.html', students=students)

@app.route('/admin/deactivate-student/<int:student_id>')
def deactivate_student(student_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    student = db.session.get(Student, student_id)
    if student:
        student.is_active = False # Deactivate their account
        db.session.commit()
        flash(f'Student {student.name} deactivated successfully.')
        
    return redirect(url_for('admin_students'))

# ==========================================
# ADMIN MANAGEMENT ROUTES - DRIVES
# ==========================================

@app.route('/admin/drives')
def admin_drives():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    # Grab all drives. The template will use 'drive.company.name' to show who made the drive.
    drives = PlacementDrive.query.all()
    return render_template('admin/drives.html', drives=drives)

@app.route('/admin/approve-drive/<int:drive_id>')
def approve_drive(drive_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    drive = db.session.get(PlacementDrive, drive_id)
    if drive:
        drive.status = 'Approved'
        db.session.commit()
        flash(f'Placement drive "{drive.job_title}" approved!')
        
    return redirect(url_for('admin_drives'))

@app.route('/admin/reject-drive/<int:drive_id>')
def reject_drive(drive_id):
    if session.get('role') != 'admin': return redirect(url_for('login'))
    
    drive = db.session.get(PlacementDrive, drive_id)
    if drive:
        drive.status = 'Rejected'
        db.session.commit()
        flash(f'Placement drive "{drive.job_title}" rejected.')
        
    return redirect(url_for('admin_drives'))

# The company dashboard route.
@app.route('/company/dashboard')
def company_dashboard():
    # Security check: Only companies allowed here.
    if session.get('role') != 'company':
        return redirect(url_for('login'))
        
    # I want to show the company their own details, so I use their session ID to find them in the database.
    company_id = session.get('user_id')
    current_company = db.session.get(Company, company_id)
    
    # Grab all drives related to this specific company.
    drives = PlacementDrive.query.filter_by(company_id=company_id).all()
    
    # I pass the 'current_company' object to the HTML so my template can say "Welcome Google" or check their approval status.
    return render_template('company/dashboard.html', company=current_company, drives=drives)

@app.route('/company/post-drive', methods=['GET', 'POST'])
def post_drive():
    if session.get('role') != 'company':
        return redirect(url_for('login'))
        
    company_id = session.get('user_id')
    current_company = db.session.get(Company, company_id)
    
    # Must be approved to post drives
    if current_company.approval_status != 'Approved':
        flash('You must be approved by the admin to post drives.')
        return redirect(url_for('company_dashboard'))
        
    if request.method == 'POST':
        # Retrieve form data submitted by company
        job_title = request.form.get('job_title')
        description = request.form.get('description')
        eligibility = request.form.get('eligibility')
        deadline = request.form.get('deadline')
        
        # Create a new PlacementDrive tied to this company
        new_drive = PlacementDrive(
            company_id=company_id,
            job_title=job_title,
            description=description,
            eligibility=eligibility,
            deadline=deadline,
            status='Pending' # default to Pending for Admin approval
        )
        
        db.session.add(new_drive)
        db.session.commit()
        
        flash('Placement drive posted successfully! Waiting for admin approval.')
        return redirect(url_for('company_dashboard'))
        
    # GET method simply renders the page
    return render_template('company/post_drive.html', company=current_company)

@app.route('/company/applications/<int:drive_id>')
def view_drive_applications(drive_id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))
        
    company_id = session.get('user_id')
    drive = db.session.get(PlacementDrive, drive_id)
    
    # Security check: Ensure this drive actually belongs to the logged-in company!
    if not drive or drive.company_id != company_id:
        flash("You do not have permission to view this drive's applications.")
        return redirect(url_for('company_dashboard'))
        
    # Grab all the applications submitted specifically for this drive.
    applications = Application.query.filter_by(drive_id=drive_id).all()
    
    return render_template('company/applications.html', drive=drive, applications=applications)

@app.route('/company/update-application/<int:application_id>', methods=['POST'])
def update_application(application_id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))
        
    company_id = session.get('user_id')
    application = db.session.get(Application, application_id)
    
    # 1. Ensure the application exists
    # 2. Ensure its parent Drive was actually posted by *this* company
    if not application or application.drive.company_id != company_id:
        flash("Unauthorized action.")
        return redirect(url_for('company_dashboard'))
        
    # Grab the new status selected from the dropdown menu in the HTML
    new_status = request.form.get('status')
    valid_statuses = ['Applied', 'Shortlisted', 'Interview', 'Selected', 'Rejected', 'Placed']
    
    if new_status in valid_statuses:
        application.status = new_status
        db.session.commit()
        flash(f"Application status updated to '{new_status}' successfully.")
        
    # Redirect right back to the applications list they were just looking at.
    return redirect(url_for('view_drive_applications', drive_id=application.drive_id))

from datetime import date

# ==========================================
# STUDENT ROUTES AND DASHBOARD
# ==========================================

@app.route('/student/dashboard')
def student_dashboard():
    # Security check: Only students allowed here.
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    student_id = session.get('user_id')
    current_student = db.session.get(Student, student_id)
    
    # We only show drives that the Admin has set to "Approved"
    approved_drives = PlacementDrive.query.filter_by(status='Approved').all()
    
    return render_template('student/dashboard.html', student=current_student, drives=approved_drives)

@app.route('/student/apply/<int:drive_id>')
def apply_to_drive(drive_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    student_id = session.get('user_id')
    
    # 1. Check if the student already applied to this specific drive. We don't want duplicate data!
    existing_application = Application.query.filter_by(student_id=student_id, drive_id=drive_id).first()
    
    if existing_application:
        flash('You have already applied for this drive.')
    else:
        # 2. If no duplicate is found, create a new record.
        new_application = Application(
            student_id=student_id,
            drive_id=drive_id,
            date_applied=date.today().strftime("%Y-%m-%d"),
            status='Applied' # Starting status is always 'Applied'
        )
        db.session.add(new_application)
        db.session.commit()
        flash('Successfully applied to the drive!')
        
    return redirect(url_for('student_dashboard'))

@app.route('/student/applications')
def student_applications():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    student_id = session.get('user_id')
    current_student = db.session.get(Student, student_id)
    
    # Check all applications tied to this specific student ID.
    applications = Application.query.filter_by(student_id=student_id).all()
    
    return render_template('student/applications.html', student=current_student, applications=applications)

# This is the starting point of the application.
if __name__ == '__main__':
    # Turning debug=True on means the server will auto-reload when I make changes to my code. Very helpful!
    app.run(debug=True)
