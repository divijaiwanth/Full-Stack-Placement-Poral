# Placement Portal Application

A campus placement portal managing recruitment drives for an institute. It handles three types of users: Admin, Company, and Student. Companies can create placement drives, and students can apply to them.

## Tech Stack
- **Backend:** Python (Flask framework)
- **Database:** SQLite with Flask-SQLAlchemy (ORM)

## Installation Instructions

1. **Clone the repository or navigate to the project directory**
2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Project

1. **Start the Flask application:**
   ```bash
   python app.py
   ```
   *Note: This will automatically create the database `instance/placement.db` and initialize the default admin user.*
2. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:5000/`. You should immediately be redirected to the secure login application page.

### Roles and Authentication System
This application uses simple session-based authentication to manage access securely. There are three types of user tiers available:

1. **Admin**
   - Can monitor whole portal activities. 
   - **Default Credentials:** Username: `admin` | Password: `admin123`
2. **Companies**
   - Must register through `/register/company` first.
   - Requires Administrator Approval before they gain full abilities. Login attempts while unapproved route to a 'Pending' restriction page.
3. **Students** 
   - May register at `/register/student` independently to browse functionality and drive statuses once approved.
