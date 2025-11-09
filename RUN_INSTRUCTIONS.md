# Step-by-Step Instructions to Run Hospital Queue Management System

## Prerequisites Check

First, make sure you have Python installed:
```powershell
python --version
```
If not installed, download from https://www.python.org/downloads/

---

## Option 1: Using SQLite (Simple - No XAMPP needed)

### Step 1: Open Terminal/PowerShell
```powershell
cd "C:\Users\Dhananjay Kasekar\Desktop\cyber batch p"
```

### Step 2: Install Dependencies
```powershell
pip install Flask
```
Or install all at once:
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Application
```powershell
python app.py
```

### Step 4: Access the Application
Open your browser and go to:
```
http://localhost:5000
```
or
```
http://127.0.0.1:5000
```

**That's it!** The database will be created automatically.

---

## Option 2: Using MySQL with XAMPP (For XAMPP setup)

### Step 1: Start XAMPP Services

1. Open **XAMPP Control Panel**
2. Click **Start** button for **Apache** (if needed)
3. Click **Start** button for **MySQL** (REQUIRED)
4. Both should show green "Running" status

### Step 2: Create Database (Using phpMyAdmin)

1. Open browser and go to: `http://localhost/phpmyadmin`
2. Click **"New"** in left sidebar
3. Database name: `hospital_queue`
4. Collation: `utf8mb4_general_ci`
5. Click **"Create"**

### Step 3: Import SQL File

1. In phpMyAdmin, select `hospital_queue` database
2. Click **"Import"** tab at top
3. Click **"Choose File"** → Select `database.sql`
4. Click **"Go"** button at bottom
5. Wait for "Import has been successfully finished" message

### Step 4: Open Terminal/PowerShell
```powershell
cd "C:\Users\Dhananjay Kasekar\Desktop\cyber batch p"
```

### Step 5: Install Python Dependencies
```powershell
pip install Flask mysql-connector-python
```
Or:
```powershell
pip install -r requirements.txt
```

### Step 6: Configure Database (if needed)

If your MySQL has a password, edit `app_mysql.py`:
- Open `app_mysql.py`
- Find `DB_CONFIG` section (around line 13)
- Update password if needed:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password_here',  # Change this if you set a password
    'database': 'hospital_queue',
    'charset': 'utf8mb4'
}
```

### Step 7: Run the MySQL Version
```powershell
python app_mysql.py
```

### Step 8: Access the Application
Open your browser and go to:
```
http://localhost:5000
```
or
```
http://127.0.0.1:5000
```

---

## Quick Start Commands (Copy-Paste)

### For SQLite (Easiest):
```powershell
cd "C:\Users\Dhananjay Kasekar\Desktop\cyber batch p"
pip install Flask
python app.py
```

### For MySQL (XAMPP):
```powershell
cd "C:\Users\Dhananjay Kasekar\Desktop\cyber batch p"
pip install Flask mysql-connector-python
python app_mysql.py
```

---

## What You'll See

After running the command, you should see:
```
 * Serving Flask app 'app' (or 'app_mysql')
 * Debug mode: on
WARNING: This is a development server...
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**Keep this terminal window open!** Closing it will stop the server.

---

## Default Login Credentials

- **Username**: `doctor`
- **Password**: `doctor123`

---

## Troubleshooting

### Error: "pip is not recognized"
```powershell
python -m pip install Flask
```

### Error: "python is not recognized"
Try:
```powershell
py app.py
```
or
```powershell
py app_mysql.py
```

### Error: "Port 5000 already in use"
- Close other Flask applications
- Or change port in the code:
  ```python
  app.run(debug=True, port=5001)
  ```
  Then access: `http://localhost:5001`

### Error: "MySQL connection failed"
- Make sure MySQL is running in XAMPP
- Check if database `hospital_queue` exists
- Verify username/password in `app_mysql.py`

### Error: "Module not found"
```powershell
pip install Flask mysql-connector-python
```

---

## Stopping the Server

Press `CTRL + C` in the terminal where Flask is running.

---

## Testing the Application

1. **Register a Patient**: Go to home page → Fill form → Submit
2. **View Queue**: Click "View Queue" link
3. **Doctor Login**: Click "Doctor Login" → Use credentials above
4. **Dashboard**: See statistics and manage patients

---

## File Structure

```
cyber batch p/
├── app.py              ← SQLite version (use: python app.py)
├── app_mysql.py        ← MySQL version (use: python app_mysql.py)
├── database.sql        ← Import this in phpMyAdmin
├── requirements.txt    ← Dependencies list
└── templates/          ← HTML templates
```

---

## Notes

- **SQLite version** (`app.py`): No setup needed, works immediately
- **MySQL version** (`app_mysql.py`): Requires XAMPP MySQL running
- Database is auto-created for SQLite
- Default doctor user is auto-created on first run
- Keep terminal open while using the application

