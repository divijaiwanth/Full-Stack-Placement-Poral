import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for the application securely signing cookies
    SECRET_KEY = 'secret_key_123'
    
    # Database URI pointing to the SQLite database
    # It stores the database in instance/placement.db
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'placement.db')
    
    # Disable tracking modifications of objects to save memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
