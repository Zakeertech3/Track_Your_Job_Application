# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from db import db
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

# --- File Upload Configuration ---
# Define the folder to store uploaded files (for resumes and screenshots)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Allowed file extensions for resumes and screenshots
app.config['ALLOWED_RESUME_EXTENSIONS'] = {'pdf', 'doc', 'docx'}
app.config['ALLOWED_SCREENSHOT_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_resume_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_RESUME_EXTENSIONS']

def allowed_screenshot_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_SCREENSHOT_EXTENSIONS']

# Initialize SQLAlchemy with our Flask app
db.init_app(app)

from models import Record, JobApplication, ColdEmail

with app.app_context():
    db.create_all()

# -------------------------
# Routes for General Records
# -------------------------
@app.route('/')
def index():
    # Check for an optional query parameter "record_type"
    record_type = request.args.get('record_type', 'general')
    if record_type == 'general':
        records = Record.query.order_by(Record.created_at.desc()).all()
    elif record_type == 'job':
        records = JobApplication.query.order_by(JobApplication.date.desc()).all()
    elif record_type == 'cold':
        records = ColdEmail.query.order_by(ColdEmail.date.desc()).all()
    else:
        records = []
    total_records = len(records)
    print(f"DEBUG: Total Records in DB for {record_type} =", total_records)
    return render_template('index.html', records=records, total_records=total_records, record_type=record_type)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Even if name or email is missing, store an empty string.
        name = request.form.get('name') or ''
        email = request.form.get('email') or ''
        new_record = Record(name=name, email=email)
        db.session.add(new_record)
        db.session.commit()
        flash(f'Record created successfully at {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}', 'success')
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    record = Record.query.get_or_404(id)
    if request.method == 'POST':
        record.name = request.form.get('name') or ''
        record.email = request.form.get('email') or ''
        db.session.commit()
        flash(f'Record updated successfully at {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}', 'success')
        return redirect(url_for('index'))
    return render_template('update.html', record=record)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    record = Record.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash(f'Record deleted successfully at {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}', 'success')
    return redirect(url_for('index'))

# -------------------------
# Routes for Job Applications
# -------------------------
@app.route('/job_applications')
def job_applications():
    job_apps = JobApplication.query.order_by(JobApplication.date.desc()).all()
    return render_template('job_applications.html', job_apps=job_apps)

@app.route('/job_applications/create', methods=['GET', 'POST'])
def create_job_application():
    if request.method == 'POST':
        company = request.form.get('company') or ''
        role = request.form.get('role') or ''
        location = request.form.get('location') or ''
        job_description = request.form.get('job_description') or ''
        date_str = request.form.get('date')
        # Use current date if no valid date is provided.
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                date = datetime.utcnow()
        else:
            date = datetime.utcnow()
        
        # Process resume file upload.
        resume_file = request.files.get('resume')
        resume_filename = None
        if resume_file and allowed_resume_file(resume_file.filename):
            filename = secure_filename(resume_file.filename)
            resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resume_filename = filename

        # Process job description screenshot file upload.
        jd_screenshot_file = request.files.get('jd_screenshot')
        jd_screenshot_filename = None
        if jd_screenshot_file and allowed_screenshot_file(jd_screenshot_file.filename):
            filename = secure_filename(jd_screenshot_file.filename)
            jd_screenshot_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            jd_screenshot_filename = filename

        job_app = JobApplication(date=date, company=company, role=role,
                                 location=location, job_description=job_description,
                                 resume_filename=resume_filename,
                                 jd_screenshot_filename=jd_screenshot_filename)
        db.session.add(job_app)
        db.session.commit()
        flash('Job Application created successfully!', 'success')
        return redirect(url_for('job_applications'))
    return render_template('create_job_application.html')

# -------------------------
# Routes for Cold Emails
# -------------------------
@app.route('/cold_emails')
def cold_emails():
    cold_emails = ColdEmail.query.order_by(ColdEmail.date.desc()).all()
    return render_template('cold_emails.html', cold_emails=cold_emails)

@app.route('/cold_emails/create', methods=['GET', 'POST'])
def create_cold_email():
    if request.method == 'POST':
        company = request.form.get('company') or ''
        role = request.form.get('role') or ''
        location = request.form.get('location') or ''
        job_description = request.form.get('job_description') or ''
        date_str = request.form.get('date')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                date = datetime.utcnow()
        else:
            date = datetime.utcnow()

        resume_file = request.files.get('resume')
        resume_filename = None
        if resume_file and allowed_resume_file(resume_file.filename):
            filename = secure_filename(resume_file.filename)
            resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resume_filename = filename

        jd_screenshot_file = request.files.get('jd_screenshot')
        jd_screenshot_filename = None
        if jd_screenshot_file and allowed_screenshot_file(jd_screenshot_file.filename):
            filename = secure_filename(jd_screenshot_file.filename)
            jd_screenshot_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            jd_screenshot_filename = filename

        cold_email = ColdEmail(date=date, company=company, role=role,
                               location=location, job_description=job_description,
                               resume_filename=resume_filename,
                               jd_screenshot_filename=jd_screenshot_filename)
        db.session.add(cold_email)
        db.session.commit()
        flash('Cold Email created successfully!', 'success')
        return redirect(url_for('cold_emails'))
    return render_template('create_cold_email.html')

if __name__ == '__main__':
    app.run(debug=True)
