from flask import Flask
from config import Config
from database import db
from models import Admin, Student, Company, PlacementDrive, Application

# 1. Create Flask application
app = Flask(__name__)

# 2. Load configuration from config.py
app.config.from_object(Config)

# 3. Initialize SQLAlchemy with the Flask app
db.init_app(app)

# 4. Automatically create database tables and default admin user
with app.app_context():
    # This creates the instance/placement.db file and all tables
    db.create_all()
    
    # 5. Automatically create the default admin user if it does not exist
    # Check if the 'admin' user already exists in the database
    admin_user = Admin.query.filter_by(username='admin').first()
    if not admin_user:
        # Create default admin user
        default_admin = Admin(username='admin', password='admin123')
        db.session.add(default_admin)
        db.session.commit()
        print("Default admin user created successfully.")

# Add a simple test route
@app.route('/')
def home():
    """Return a simple text confirming the app is running."""
    return "Placement Portal Application Running"

if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(debug=True)
