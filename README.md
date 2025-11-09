# Hospital Patient Queue Management System

A web-based patient queue management system built with Flask (Python backend) and Bootstrap (frontend).

## Features

- ✅ Patient Registration with auto-generated token numbers
- ✅ Real-time queue display with auto-refresh (every 10 seconds)
- ✅ Doctor/Admin dashboard
- ✅ Patient status management (Waiting → In Consultation → Completed)
- ✅ Department-wise token generation
- ✅ Statistics dashboard

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Icons**: Bootstrap Icons

## Installation & Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

### 3. Default Login Credentials

- **Username**: `doctor`
- **Password**: `doctor123`

## Project Structure

```
hospital-queue-system/
│
├── app.py                 # Main Flask application
├── hospital.db            # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
└── templates/            # HTML templates
    ├── base.html         # Base template with navigation
    ├── register.html     # Patient registration form
    ├── success.html      # Registration success page
    ├── queue.html        # Queue display page
    ├── login.html        # Doctor login page
    └── dashboard.html    # Doctor dashboard
```

## Usage

### For Patients:
1. Visit the home page
2. Fill out the registration form
3. Receive a token number
4. View the queue to see your position

### For Doctors:
1. Login using the doctor credentials
2. View dashboard with statistics
3. Click "Call Next Patient" to start consultation
4. Click "Mark as Completed" when done

## Database Schema

### Patients Table
- `id` - Primary key
- `token_no` - Auto-generated token (e.g., CARDIO-001)
- `name` - Patient name
- `department` - Department name
- `symptoms` - Patient symptoms
- `status` - Waiting / In Consultation / Completed
- `time_in` - Registration time
- `time_out` - Completion time

### Users Table
- `id` - Primary key
- `username` - Login username
- `password` - Login password
- `role` - User role (doctor/admin)

## API Endpoints

- `GET /` - Redirects to registration
- `GET /register` - Patient registration form
- `POST /register` - Submit patient registration
- `GET /queue` - Display patient queue
- `GET /api/queue` - JSON API for queue (AJAX)
- `GET /login` - Doctor login form
- `POST /login` - Authenticate doctor
- `GET /dashboard` - Doctor dashboard
- `POST /next_patient` - Call next patient
- `POST /complete_patient/<id>` - Complete patient consultation
- `GET /logout` - Logout

## Features Explained

### Token Generation
- Tokens are auto-generated based on department
- Format: `DEPT-001`, `DEPT-002`, etc.
- Example: `CARDIO-001`, `ORTHO-001`

### Auto-Refresh Queue
- Queue page automatically refreshes every 10 seconds
- Uses AJAX to fetch latest data without page reload
- Visual indicator shows refresh status

### Status Flow
1. **Waiting** - Patient registered, waiting for consultation
2. **In Consultation** - Doctor called the patient
3. **Completed** - Consultation finished

## Customization

### Add More Departments
Edit `templates/register.html` and add options to the department select dropdown.

### Change Auto-Refresh Interval
Edit `templates/queue.html` and change the `setInterval` value (currently 10000ms = 10 seconds).

### Modify Token Format
Edit the `get_next_token()` function in `app.py`.

## Notes

- Database is automatically created on first run
- Default doctor user is created automatically
- All times are stored in local timezone
- For production, change the `secret_key` in `app.py`

## License

This project is created for educational purposes.


