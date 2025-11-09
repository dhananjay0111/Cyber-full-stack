from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database initialization
def init_db():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    # Create patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_no TEXT NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            status TEXT DEFAULT 'Waiting',
            time_in TEXT NOT NULL,
            time_out TEXT
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Insert default doctor user if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('doctor',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (username, password, role) 
            VALUES (?, ?, ?)
        ''', ('doctor', 'doctor123', 'doctor'))
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def get_db_connection():
    conn = sqlite3.connect('hospital.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_next_token(department):
    """Generate next token number for a department"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the last token number for this department
    cursor.execute('''
        SELECT token_no FROM patients 
        WHERE department = ? 
        ORDER BY id DESC LIMIT 1
    ''', (department,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # Extract number from token (e.g., "CARDIO-001" -> 1)
        last_token = result[0]
        try:
            last_num = int(last_token.split('-')[-1])
            next_num = last_num + 1
        except:
            next_num = 1
    else:
        next_num = 1
    
    # Format token as DEPT-001, DEPT-002, etc.
    dept_code = department[:5].upper()
    token_no = f"{dept_code}-{next_num:03d}"
    return token_no

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        symptoms = request.form['symptoms']
        
        token_no = get_next_token(department)
        time_in = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO patients (token_no, name, department, symptoms, status, time_in)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (token_no, name, department, symptoms, 'Waiting', time_in))
        conn.commit()
        conn.close()
        
        return render_template('success.html', token=token_no, name=name)
    
    return render_template('register.html')

@app.route('/queue')
def queue():
    conn = get_db_connection()
    # Get all patients including completed ones
    patients = conn.execute('''
        SELECT * FROM patients 
        ORDER BY 
            CASE status
                WHEN 'In Consultation' THEN 1
                WHEN 'Waiting' THEN 2
                WHEN 'Completed' THEN 3
                ELSE 4
            END,
            time_in DESC
    ''').fetchall()
    
    # Get completed patients separately for the completed section
    completed_patients = conn.execute('''
        SELECT * FROM patients 
        WHERE status = 'Completed'
        ORDER BY time_out DESC
        LIMIT 10
    ''').fetchall()
    conn.close()
    
    return render_template('queue.html', patients=patients, completed_patients=completed_patients)

@app.route('/api/queue')
def api_queue():
    """API endpoint for AJAX queue updates"""
    conn = get_db_connection()
    # Get all patients including completed ones
    patients = conn.execute('''
        SELECT * FROM patients 
        ORDER BY 
            CASE status
                WHEN 'In Consultation' THEN 1
                WHEN 'Waiting' THEN 2
                WHEN 'Completed' THEN 3
                ELSE 4
            END,
            time_in DESC
    ''').fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    patients_list = []
    for patient in patients:
        # Handle SQLite Row object
        time_out = None
        try:
            time_out = patient['time_out'] if patient['time_out'] else None
        except (KeyError, IndexError):
            pass
        
        patients_list.append({
            'id': patient['id'],
            'token_no': patient['token_no'],
            'name': patient['name'],
            'department': patient['department'],
            'symptoms': patient['symptoms'],
            'status': patient['status'],
            'time_in': patient['time_in'],
            'time_out': time_out
        })
    
    return jsonify(patients_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    
    # Get next waiting patient
    next_patient = conn.execute('''
        SELECT * FROM patients 
        WHERE status = 'Waiting'
        ORDER BY time_in ASC
        LIMIT 1
    ''').fetchone()
    
    # Get current patient in consultation
    current_patient = conn.execute('''
        SELECT * FROM patients 
        WHERE status = 'In Consultation'
        ORDER BY time_in ASC
        LIMIT 1
    ''').fetchone()
    
    # Get statistics
    total_waiting = conn.execute('''
        SELECT COUNT(*) FROM patients WHERE status = 'Waiting'
    ''').fetchone()[0]
    
    total_today = conn.execute('''
        SELECT COUNT(*) FROM patients 
        WHERE DATE(time_in) = DATE('now')
    ''').fetchone()[0]
    
    conn.close()
    
    return render_template('dashboard.html', 
                         next_patient=next_patient,
                         current_patient=current_patient,
                         total_waiting=total_waiting,
                         total_today=total_today)

@app.route('/next_patient', methods=['POST'])
@login_required
def next_patient():
    conn = get_db_connection()
    
    # Get the next waiting patient
    patient = conn.execute('''
        SELECT * FROM patients 
        WHERE status = 'Waiting'
        ORDER BY time_in ASC
        LIMIT 1
    ''').fetchone()
    
    if patient:
        # Update status to 'In Consultation'
        conn.execute('''
            UPDATE patients SET status = 'In Consultation'
            WHERE id = ?
        ''', (patient['id'],))
        conn.commit()
    
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/complete_patient/<int:patient_id>', methods=['POST'])
@login_required
def complete_patient(patient_id):
    conn = get_db_connection()
    time_out = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn.execute('''
        UPDATE patients SET status = 'Completed', time_out = ?
        WHERE id = ?
    ''', (time_out, patient_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)


