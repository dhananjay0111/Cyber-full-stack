# XAMPP Setup Guide for Hospital Queue Management System

## Step 1: Install and Start XAMPP

1. Download and install XAMPP from https://www.apachefriends.org/
2. Start XAMPP Control Panel
3. Start **Apache** and **MySQL** services

## Step 2: Create Database in phpMyAdmin

1. Open your browser and go to: `http://localhost/phpmyadmin`
2. Click on **"New"** in the left sidebar to create a new database
3. Database name: `hospital_queue`
4. Collation: `utf8mb4_general_ci`
5. Click **"Create"**

## Step 3: Import SQL File

### Method 1: Using phpMyAdmin (Recommended)
1. Select the `hospital_queue` database from the left sidebar
2. Click on the **"Import"** tab at the top
3. Click **"Choose File"** and select `database.sql`
4. Click **"Go"** at the bottom
5. You should see "Import has been successfully finished"

### Method 2: Using MySQL Command Line
```bash
# Open XAMPP MySQL command line or use any MySQL client
mysql -u root -p hospital_queue < database.sql
```

## Step 4: Configure Flask App for MySQL

1. **Option A: Use the MySQL version (Recommended)**
   - Rename `app_mysql.py` to `app.py` (backup the original SQLite version first)
   - Or keep both and run: `python app_mysql.py`

2. **Option B: Update database configuration**
   - Open `app_mysql.py`
   - Update the `DB_CONFIG` dictionary if needed:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': '',  # Change if you set a MySQL password
       'database': 'hospital_queue',
       'charset': 'utf8mb4'
   }
   ```

## Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask
- mysql-connector-python (for MySQL connection)

## Step 6: Run the Application

```bash
python app_mysql.py
```

Or if you renamed it:
```bash
python app.py
```

## Step 7: Access the Application

Open your browser and go to:
```
http://127.0.0.1:5000
```

## Default Login Credentials

- **Username**: `doctor`
- **Password**: `doctor123`

## Troubleshooting

### Error: "Access denied for user 'root'@'localhost'"
- Check if MySQL password is set in XAMPP
- Update the password in `DB_CONFIG` in `app_mysql.py`

### Error: "Unknown database 'hospital_queue'"
- Make sure you created the database in phpMyAdmin
- Verify the database name matches in `DB_CONFIG`

### Error: "Table doesn't exist"
- Make sure you imported the `database.sql` file
- Check phpMyAdmin to verify tables are created

### MySQL Service Won't Start
- Check if port 3306 is already in use
- Stop any other MySQL services running
- Check XAMPP error logs

### Connection Refused
- Make sure MySQL service is running in XAMPP Control Panel
- Verify MySQL is listening on port 3306

## Database Structure

After importing, you should have:

### `patients` table
- id (Primary Key)
- token_no
- name
- department
- symptoms
- status
- time_in
- time_out

### `users` table
- id (Primary Key)
- username
- password
- role

## Notes

- Default XAMPP MySQL username is `root` with no password
- If you set a MySQL password, update it in `app_mysql.py`
- The database will be stored in: `C:\xampp\mysql\data\hospital_queue\`
- Always keep XAMPP MySQL service running while using the application


