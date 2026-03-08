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
        
        # For the resume, I am just getting the file name for now.
        # In the future I will need to save the actual file to a folder.
        resume_file = request.files.get('resume')
        resume_path = resume_file.filename if resume_file else None

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
        
    return render_template('admin/dashboard.html')

# The company dashboard route.
@app.route('/company/dashboard')
def company_dashboard():
    # Security check: Only companies allowed here.
    if session.get('role') != 'company':
        return redirect(url_for('login'))
        
    # I want to show the company their own details, so I use their session ID to find them in the database.
    company_id = session.get('user_id')
    current_company = Company.query.get(company_id)
    
    # I pass the 'current_company' object to the HTML so my template can say "Welcome Google" or check their approval status.
    return render_template('company/dashboard.html', company=current_company)

# The student dashboard route.
@app.route('/student/dashboard')
def student_dashboard():
    # Security check: Only students allowed here.
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    # Let's find the specific student in the database so we can greet them by name.
    student_id = session.get('user_id')
    current_student = Student.query.get(student_id)
    
    # We pass 'student' to the template so it can say "Welcome John".
    return render_template('student/dashboard.html', student=current_student)

# This is the starting point of the application.
if __name__ == '__main__':
    # Turning debug=True on means the server will auto-reload when I make changes to my code. Very helpful!
    app.run(debug=True)
