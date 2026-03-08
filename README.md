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
   Open your browser and navigate to `http://127.0.0.1:5000/`. You should see the text: "Placement Portal Application Running".

### Default Admin Credentials
- **Username:** `admin`
- **Password:** `admin123`
