from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Simple user storage (in production, use a database)
users = {
    'patient1': {'password': generate_password_hash('password123'), 'role': 'patient'},
    'doctor1': {'password': generate_password_hash('password123'), 'role': 'doctor'}
}

# Patient data storage
patients_data = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            session['role'] = users[username]['role']
            
            if users[username]['role'] == 'patient':
                return redirect(url_for('patient_dashboard'))
            else:
                return redirect(url_for('doctor_dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        if username in users:
            flash('Username already exists. Please choose another.')
        else:
            users[username] = {
                'password': generate_password_hash(password),
                'role': user_type
            }
            flash('Account created successfully. Please login.')
            return redirect(url_for('login'))
    
    return render_template('login.html', signup=True)

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'username' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))
    
    username = session['username']
    if username not in patients_data:
        patients_data[username] = {
            'personal_info': {},
            'reports': []
        }
    
    return render_template('patient_dashboard.html', 
                          patient_data=patients_data[username],
                          username=username)

@app.route('/save_patient_data', methods=['POST'])
def save_patient_data():
    if 'username' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))
    
    username = session['username']
    
    # Initialize patient data if not exists
    if username not in patients_data:
        patients_data[username] = {
            'personal_info': {},
            'reports': []
        }
    
    # Update personal information
    patients_data[username]['personal_info'] = {
        'name': request.form['name'],
        'age': request.form['age'],
        'gender': request.form['gender'],
        'blood_group': request.form['blood_group'],
        'contact': request.form['contact'],
        'address': request.form['address'],
        'medical_history': request.form['medical_history'],
        'allergies': request.form['allergies'],
        'current_medications': request.form['current_medications']
    }
    
    flash('Patient data saved successfully!')
    return redirect(url_for('patient_dashboard'))

@app.route('/upload_report', methods=['POST'])
def upload_report():
    if 'username' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))
    
    username = session['username']
    
    if 'report' not in request.files:
        flash('No file selected')
        return redirect(url_for('patient_dashboard'))
    
    file = request.files['report']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('patient_dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{username}_{filename}")
        file.save(filepath)
        
        # Add report to patient's data
        report_data = {
            'filename': filename,
            'filepath': filepath,
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'report_type': request.form['report_type'],
            'notes': request.form['notes']
        }
        
        if username not in patients_data:
            patients_data[username] = {
                'personal_info': {},
                'reports': []
            }
        
        patients_data[username]['reports'].append(report_data)
        flash('Report uploaded successfully!')
    
    return redirect(url_for('patient_dashboard'))

@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'username' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '')
    
    # Filter patients based on search query
    filtered_patients = {}
    for username, data in patients_data.items():
        if search_query.lower() in username.lower() or \
           (data['personal_info'].get('name', '') and \
            search_query.lower() in data['personal_info'].get('name', '').lower()):
            filtered_patients[username] = data
    
    return render_template('doctor_dashboard.html', 
                          patients=filtered_patients,
                          search_query=search_query,
                          username=session['username'])

@app.route('/view_patient/<patient_username>')
def view_patient(patient_username):
    if 'username' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    if patient_username not in patients_data:
        flash('Patient not found')
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('view_patient.html', 
                          patient_data=patients_data[patient_username],
                          patient_username=patient_username)

@app.route('/download_report/<patient_username>/<filename>')
def download_report(patient_username, filename):
    if 'username' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))
    
    # Find the file path
    for report in patients_data[patient_username]['reports']:
        if report['filename'] == filename:
            return send_file(report['filepath'], as_attachment=True)
    
    flash('Report not found')
    return redirect(url_for('view_patient', patient_username=patient_username))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)