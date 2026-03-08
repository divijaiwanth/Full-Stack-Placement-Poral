import os

# First, I need to find the base directory of my project so I can save files correctly.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # This class keeps all the configuration settings for the app in one place.
    
    # I need a secret key so that Flask can securely sign my session cookies. 
    # Without this, login won't work properly!
    SECRET_KEY = 'secret_key_123'
    
    # This tells SQLAlchemy exactly where to create my SQLite database file.
    # It will automatically be created inside the 'instance' folder as 'placement.db'.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'placement.db')
    
    # I am turning off modification tracking. I read it uses extra memory and I don't need it.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
