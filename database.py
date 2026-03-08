from flask_sqlalchemy import SQLAlchemy

# I am creating the 'db' object here in a separate file. 
# This way, I can import "db" in app.py and models.py without causing a circular import error.
db = SQLAlchemy()
