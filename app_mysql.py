from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# MySQL Database Configuration
# Update these values according to your XAMPP MySQL settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Default XAMPP MySQL password is empty
    'database': 'hospital_queue',
    'charset': 'utf8mb4',
    'autocommit': False
}

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        # Connect without specifying database
        config_without_db = {k: v for k, v in DB_CONFIG.items() if k not in ['database', 'autocommit']}
        conn = mysql.connector.connect(**config_without_db)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Error creating database: {e}")
        return False

def get_db_connection():
    """Create and return MySQL database connection"""
    try:
        # Try to connect
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        # If database doesn't exist, try to create it
        if e.errno == 1049:  # Unknown database error
            print(f"Database not found. Attempting to create database...")
            if create_database_if_not_exists():
                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    return conn
                except Error as e2:
                    print(f"Error connecting after database creation: {e2}")
                    return None
        else:
            print(f"Error connecting to MySQL: {e}")
            print(f"Please ensure:")
            print(f"  1. MySQL service is running in XAMPP")
            print(f"  2. Database '{DB_CONFIG['database']}' exists or can be created")
            print(f"  3. Username and password are correct")
        return None

def init_db():
    """Initialize database and create tables if they don't exist"""
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to database. Please check your MySQL configuration.")
        return
    
    cursor = conn.cursor()
    
    try:
        # Create patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                token_no VARCHAR(20) NOT NULL,
                name VARCHAR(100) NOT NULL,
                department VARCHAR(50) NOT NULL,
                symptoms TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'Waiting',
                time_in DATETIME NOT NULL,
                time_out DATETIME NULL,
                INDEX idx_status (status),
                INDEX idx_department (department),
                INDEX idx_time_in (time_in)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Insert default doctor user if not exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = %s', ('doctor',))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (username, password, role) 
                VALUES (%s, %s, %s)
            ''', ('doctor', 'doctor123', 'doctor'))
        
        conn.commit()
        print("Database initialized successfully!")
        
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        cursor.close()
        conn.close()

# Initialize database on startup
init_db()

def get_next_token(department):
    """Generate next token number for a department"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor()
    
    try:
        # Get the last token number for this department
        cursor.execute('''
            SELECT token_no FROM patients 
            WHERE department = %s 
            ORDER BY id DESC LIMIT 1
        ''', (department,))
        
        result = cursor.fetchone()
        
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
        
    except Error as e:
        print(f"Error generating token: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

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
        # Input validation
        name = request.form.get('name', '').strip()
        department = request.form.get('department', '').strip()
        symptoms = request.form.get('symptoms', '').strip()
        
        # Validate inputs
        if not name:
            flash('Please enter patient name', 'danger')
            return render_template('register.html')
        if not department:
            flash('Please select a department', 'danger')
            return render_template('register.html')
        if not symptoms:
            flash('Please describe the symptoms', 'danger')
            return render_template('register.html')
        
        # Generate token
        token_no = get_next_token(department)
        if not token_no:
            flash('Error generating token. Please try again.', 'danger')
            return render_template('register.html')
        
        time_in = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed. Please check if MySQL is running.', 'danger')
            return render_template('register.html')
        
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO patients (token_no, name, department, symptoms, status, time_in)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (token_no, name, department, symptoms, 'Waiting', time_in))
            conn.commit()
            flash(f'Patient registered successfully! Token: {token_no}', 'success')
            return render_template('success.html', token=token_no, name=name)
        except Error as e:
            print(f"Error inserting patient: {e}")
            conn.rollback()
            flash('Failed to register patient. Please try again.', 'danger')
            return render_template('register.html')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

@app.route('/queue')
def queue():
    conn = get_db_connection()
    if conn is None:
        return render_template('queue.html', patients=[], completed_patients=[])
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Get all patients including completed ones
        cursor.execute('''
            SELECT * FROM patients 
            ORDER BY 
                CASE status
                    WHEN 'In Consultation' THEN 1
                    WHEN 'Waiting' THEN 2
                    WHEN 'Completed' THEN 3
                    ELSE 4
                END,
                time_in DESC
        ''')
        patients = cursor.fetchall()
        
        # Get completed patients separately for the completed section
        cursor.execute('''
            SELECT * FROM patients 
            WHERE status = 'Completed'
            ORDER BY time_out DESC
            LIMIT 10
        ''')
        completed_patients = cursor.fetchall()
        
        return render_template('queue.html', patients=patients, completed_patients=completed_patients)
    except Error as e:
        print(f"Error fetching queue: {e}")
        return render_template('queue.html', patients=[], completed_patients=[])
    finally:
        cursor.close()
        conn.close()

@app.route('/api/queue')
def api_queue():
    """API endpoint for AJAX queue updates"""
    conn = get_db_connection()
    if conn is None:
        return jsonify([])
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Get all patients including completed ones
        cursor.execute('''
            SELECT * FROM patients 
            ORDER BY 
                CASE status
                    WHEN 'In Consultation' THEN 1
                    WHEN 'Waiting' THEN 2
                    WHEN 'Completed' THEN 3
                    ELSE 4
                END,
                time_in DESC
        ''')
        patients = cursor.fetchall()
        
        # Convert datetime objects to strings
        patients_list = []
        for patient in patients:
            # Handle datetime conversion safely
            time_in_str = None
            time_out_str = None
            
            try:
                if patient['time_in']:
                    if isinstance(patient['time_in'], str):
                        time_in_str = patient['time_in']
                    else:
                        time_in_str = patient['time_in'].strftime('%Y-%m-%d %H:%M:%S')
            except (KeyError, AttributeError):
                pass
            
            try:
                if patient.get('time_out'):
                    if isinstance(patient['time_out'], str):
                        time_out_str = patient['time_out']
                    else:
                        time_out_str = patient['time_out'].strftime('%Y-%m-%d %H:%M:%S')
            except (KeyError, AttributeError):
                pass
            
            patients_list.append({
                'id': patient['id'],
                'token_no': patient['token_no'],
                'name': patient['name'],
                'department': patient['department'],
                'symptoms': patient['symptoms'],
                'status': patient['status'],
                'time_in': time_in_str,
                'time_out': time_out_str
            })
        
        return jsonify(patients_list)
    except Error as e:
        print(f"Error fetching queue: {e}")
        return jsonify([])
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error='Please enter both username and password')
        
        conn = get_db_connection()
        if conn is None:
            return render_template('login.html', error='Database connection failed. Please check if MySQL is running.')
        
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('''
                SELECT * FROM users WHERE username = %s AND password = %s
            ''', (username, password))
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash(f'Welcome, {user["username"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid username or password')
        except Error as e:
            print(f"Error during login: {e}")
            return render_template('login.html', error='Database error. Please try again.')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    if conn is None:
        return render_template('dashboard.html', 
                             next_patient=None,
                             current_patient=None,
                             total_waiting=0,
                             total_today=0)
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Get next waiting patient
        cursor.execute('''
            SELECT * FROM patients 
            WHERE status = 'Waiting'
            ORDER BY time_in ASC
            LIMIT 1
        ''')
        next_patient = cursor.fetchone()
        
        # Get current patient in consultation
        cursor.execute('''
            SELECT * FROM patients 
            WHERE status = 'In Consultation'
            ORDER BY time_in ASC
            LIMIT 1
        ''')
        current_patient = cursor.fetchone()
        
        # Get statistics
        cursor.execute('''
            SELECT COUNT(*) as count FROM patients WHERE status = 'Waiting'
        ''')
        result = cursor.fetchone()
        total_waiting = result['count'] if result else 0
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM patients 
            WHERE DATE(time_in) = CURDATE()
        ''')
        result = cursor.fetchone()
        total_today = result['count'] if result else 0
        
        return render_template('dashboard.html', 
                             next_patient=next_patient,
                             current_patient=current_patient,
                             total_waiting=total_waiting,
                             total_today=total_today)
    except Error as e:
        print(f"Error fetching dashboard data: {e}")
        return render_template('dashboard.html', 
                             next_patient=None,
                             current_patient=None,
                             total_waiting=0,
                             total_today=0)
    finally:
        cursor.close()
        conn.close()

@app.route('/next_patient', methods=['POST'])
@login_required
def next_patient():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed. Please check if MySQL is running.', 'danger')
        return redirect(url_for('dashboard'))
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Get the next waiting patient
        cursor.execute('''
            SELECT * FROM patients 
            WHERE status = 'Waiting'
            ORDER BY time_in ASC
            LIMIT 1
        ''')
        patient = cursor.fetchone()
        
        if patient:
            # Update status to 'In Consultation'
            cursor.execute('''
                UPDATE patients SET status = 'In Consultation'
                WHERE id = %s
            ''', (patient['id'],))
            conn.commit()
            flash(f'Patient {patient["token_no"]} called for consultation', 'success')
        else:
            flash('No patients waiting in queue', 'info')
    except Error as e:
        print(f"Error calling next patient: {e}")
        conn.rollback()
        flash('Error calling next patient. Please try again.', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/complete_patient/<int:patient_id>', methods=['POST'])
@login_required
def complete_patient(patient_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed. Please check if MySQL is running.', 'danger')
        return redirect(url_for('dashboard'))
    
    time_out = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.cursor(dictionary=True)
    try:
        # First check if patient exists
        cursor.execute('SELECT * FROM patients WHERE id = %s', (patient_id,))
        patient = cursor.fetchone()
        
        if patient:
            cursor.execute('''
                UPDATE patients SET status = 'Completed', time_out = %s
                WHERE id = %s
            ''', (time_out, patient_id))
            conn.commit()
            flash(f'Consultation completed for {patient["token_no"]}', 'success')
        else:
            flash('Patient not found', 'danger')
    except Error as e:
        print(f"Error completing patient: {e}")
        conn.rollback()
        flash('Error completing consultation. Please try again.', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)


