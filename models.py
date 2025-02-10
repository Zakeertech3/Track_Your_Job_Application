# models.py
from db import db
from datetime import datetime

class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    # Use empty strings as defaults so that even incomplete data is saved.
    name = db.Column(db.String(64), default='', nullable=True)
    email = db.Column(db.String(120), default='', nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Record {self.name}>'

class JobApplication(db.Model):
    __tablename__ = 'job_application'
    id = db.Column(db.Integer, primary_key=True)
    # Automatically use current datetime if no date is provided.
    date = db.Column(db.DateTime, default=datetime.utcnow)
    company = db.Column(db.String(128), default='', nullable=True)
    role = db.Column(db.String(128), default='', nullable=True)
    location = db.Column(db.String(128), default='', nullable=True)
    job_description = db.Column(db.Text, default='', nullable=True)
    resume_filename = db.Column(db.String(128), nullable=True)      # For resume file (pdf, doc, docx)
    jd_screenshot_filename = db.Column(db.String(128), nullable=True) # For screenshot file (jpg, jpeg, png, gif)

    def __repr__(self):
        return f'<JobApplication {self.company} - {self.role}>'

class ColdEmail(db.Model):
    __tablename__ = 'cold_email'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    company = db.Column(db.String(128), default='', nullable=True)
    role = db.Column(db.String(128), default='', nullable=True)
    location = db.Column(db.String(128), default='', nullable=True)
    job_description = db.Column(db.Text, default='', nullable=True)
    resume_filename = db.Column(db.String(128), nullable=True)
    jd_screenshot_filename = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return f'<ColdEmail {self.company} - {self.role}>'
