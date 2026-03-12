# ECOFEAST - Complete Installation & Usage Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [User Roles & Workflows](#user-roles--workflows)
6. [Features Overview](#features-overview)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **RAM**: 2 GB minimum
- **Disk Space**: 500 MB minimum
- **Browser**: Modern browser with JavaScript enabled (Chrome, Firefox, Safari, Edge)

### Recommended
- **Python**: 3.10 or higher
- **PostgreSQL**: 14 or higher
- **RAM**: 4 GB or more
- **OS**: Windows 10+, macOS 10.15+, or Ubuntu 20.04+

---

## Installation Steps

### Windows Installation

#### Step 1: Install Prerequisites

1. **Install Python 3.8+**
   - Download from https://www.python.org/downloads/
   - During installation, CHECK "Add Python to PATH"
   - Click "Install Now"

2. **Install PostgreSQL 12+**
   - Download from https://www.postgresql.org/download/windows/
   - Default settings are fine
   - Remember the superuser password

3. **Install Git (Optional)**
   - Download from https://git-scm.com/
   - Use default settings

#### Step 2: Setup Database

1. Open Command Prompt or PowerShell
2. Navigate to the backend folder:
   ```cmd
   cd c:\Users\vaish\OneDrive\Pictures\Desktop\foodwaste\backend
   ```
3. Run database setup script:
   ```cmd
   create_db.bat
   ```
4. Enter PostgreSQL password when prompted

#### Step 3: Setup Application

1. In the same terminal:
   ```cmd
   setup.bat
   ```
2. Wait for all dependencies to install
3. When prompted, edit the `.env` file (use Notepad)

#### Step 4: Configure Environment

1. Open `.env` file (in backend folder) with Notepad
2. Update these values:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ecofeast_dev
   GOOGLE_MAPS_KEY=YOUR_API_KEY_HERE
   SECRET_KEY=generate-random-string-here
   JWT_SECRET_KEY=generate-another-random-string-here
   ```

#### Step 5: Run Application

1. In Command Prompt:
   ```cmd
   run.bat
   ```
2. You should see:
   ```
   Running on http://127.0.0.1:5000
   ```
3. Open http://localhost:5000 in your browser

---

### macOS/Linux Installation

#### Step 1: Install Prerequisites

```bash
# Install Homebrew (macOS only)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
# macOS:
brew install python@3.10

# Linux (Ubuntu/Debian):
sudo apt-get update
sudo apt-get install python3.10 python3-pip

# Install PostgreSQL
# macOS:
brew install postgresql

# Linux (Ubuntu/Debian):
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
# macOS:
brew services start postgresql

# Linux:
sudo service postgresql start
```

#### Step 2: Setup Database

```bash
# Navigate to project
cd ~/path/to/foodwaste/backend

# Make scripts executable
chmod +x create_db.sh
chmod +x setup.sh
chmod +x run.sh

# Create database
./create_db.sh
```

#### Step 3: Setup Application

```bash
./setup.sh
```

#### Step 4: Configure Environment

```bash
# Edit .env file
nano .env

# Or with your preferred editor
vi .env
```

Update the same values as Windows guide.

#### Step 5: Run Application

```bash
./run.sh
```

---

## Configuration

### Google Maps API Setup

1. Go to https://cloud.google.com/maps-platform
2. Sign in with Google account
3. Click "Get Started"
4. Enable these APIs:
   - Maps JavaScript API
   - Places API
   - Distance Matrix API
5. Create API Key
6. Copy API key to `.env` file:
   ```
   GOOGLE_MAPS_KEY=YOUR_API_KEY_HERE
   ```

### Generate Secure Keys

```bash
# Windows PowerShell or Git Bash
python -c "import secrets; print(secrets.token_urlsafe(32))"

# macOS/Linux
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use the output for:
- `SECRET_KEY`
- `JWT_SECRET_KEY`

### Database Connection String

Format: `postgresql://username:password@host:port/database`

Example:
```
postgresql://postgres:mypassword@localhost:5432/ecofeast_dev
```

---

## Running the Application

### Start Application

```bash
# Windows
run.bat

# macOS/Linux
./run.sh
```

### Access Application

1. Open browser
2. Go to http://localhost:5000
3. You should see the ECOFEAST homepage

### Default Ports

- **Flask App**: http://localhost:5000
- **PostgreSQL**: localhost:5432

### Create Admin User

```bash
# Windows
venv\Scripts\activate
python run.py create_admin

# macOS/Linux
source venv/bin/activate
python run.py create_admin
```

Follow prompts to create admin account

---

## User Roles & Workflows

### 1. Admin Workflow

**Setup:**
```bash
python run.py create_admin
# Enter: username, email, password
```

**Dashboard:** http://localhost:5000/admin/dashboard

**Responsibilities:**
- Approve/reject user registrations
- Approve/reject food donations
- Approve/reject food requests
- Assign logistics volunteers
- View analytics and reports
- Deactivate fraudulent users

**Steps:**
1. Login with admin credentials
2. Go to "Manage Users" to approve pending registrations
3. Go to "Manage Donations" to approve food listings
4. Go to "Manage Requests" to approve receiving requests
5. Assign logistics from "Request" approval
6. View "Reports" for analytics

---

### 2. Donor Workflow

**Registration:**
1. Go to http://localhost:5000/auth/register
2. Fill in details
3. Select role: "Restaurant/Hotel/Donor"
4. Click Register
5. Login (auto-verified)

**Dashboard:** http://localhost:5000/donor/dashboard

**Steps:**
1. Login with donor credentials
2. Click "Create Listing"
3. Fill in:
   - Food type
   - Quantity
   - Expiry time
   - Pickup date and time
   - Address
   - **Click map to set location**
4. Submit for approval
5. Wait for admin approval (notification sent)
6. View requests from NGOs
7. Food gets picked up and delivered
8. Provide feedback after delivery

---

### 3. NGO Workflow

**Registration:**
1. Go to http://localhost:5000/auth/register
2. Fill in organization details
3. Select role: "NGO"
4. Submit
5. Wait for admin approval

**Dashboard:** http://localhost:5000/ngo/dashboard

**Steps:**
1. Login (after admin approval)
2. Click "Browse Food"
3. Search/filter available food
4. Click on food listing
5. Enter quantity needed
6. Click "Request This Food"
7. Wait for admin approval
8. Receive notification when delivery assigned
9. Track delivery status
10. Confirm delivery when received
11. Provide feedback

---

### 4. Logistics Workflow

**Registration:**
1. Go to http://localhost:5000/auth/register
2. Enter organization details
3. Select role: "Logistics Volunteer"
4. Submit
5. Wait for admin approval

**Dashboard:** http://localhost:5000/logistics/dashboard

**Steps:**
1. Login (after admin approval)
2. View assigned deliveries
3. Click on delivery
4. See map with pickup and delivery locations
5. Click "Confirm Pickup" when food picked up
6. Navigate to NGO location
7. Delivery complete (NGO confirms)
8. See delivery history

---

## Features Overview

### Real-Time Notifications
- AJAX polling updates every 30 seconds
- Notifications for:
  - New food listings (for NGOs)
  - Donation approvals
  - Request approvals
  - Pickup confirmations
  - Delivery completions

### Geolocation Features
- Click map to set pickup location
- View routes for logistics
- Calculate distance between points
- Real-time location tracking

### Analytics Dashboard
- Total donations and deliveries
- Success rate percentage
- CO2 emissions reduction (kg)
- Food packets distributed
- User statistics
- Daily donation trends
- NGO distribution charts

### Security Features
- Password hashing with bcrypt
- CSRF protection
- Input validation
- Role-based access control
- Session management
- Audit logging

---

## Troubleshooting

### "PostgreSQL not found"
**Solution:**
1. Install PostgreSQL from https://www.postgresql.org/
2. Add PostgreSQL to PATH:
   - Windows: Search "Environment Variables"
   - Add: `C:\Program Files\PostgreSQL\14\bin`
3. Restart terminal
4. Try again

### "Port 5000 already in use"
**Solution:**
```bash
# Windows - Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

Or change port in `run.py`:
```python
if __name__ == '__main__':
    app.run(port=8000)  # Change port here
```

### "ModuleNotFoundError: No module named 'flask'"
**Solution:**
```bash
# Windows
venv\Scripts\activate
pip install -r requirements.txt

# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### "Database connection failed"
**Solution:**
1. Check PostgreSQL is running
2. Verify DATABASE_URL in .env:
   ```
   postgresql://postgres:YOUR_PASSWORD@localhost:5432/ecofeast_dev
   ```
3. Test connection:
   ```bash
   psql -U postgres -c "SELECT 1"
   ```

### "Map not loading"
**Solution:**
1. Get Google Maps API key from https://cloud.google.com/maps-platform
2. Add to .env:
   ```
   GOOGLE_MAPS_KEY=YOUR_KEY_HERE
   ```
3. Restart application
4. Check browser console for errors

### "Static files (CSS/JS) not loading"
**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Verify files exist in `app/static/`
4. Restart Flask application

### "Can't login with correct password"
**Solution:**
1. Reset admin user:
   ```bash
   python run.py create_admin
   ```
2. Use new credentials

### "Page shows 'Access Denied' (403)"
**Solution:**
1. Verify user is approved (admin check)
2. Check user role has access to page
3. Clear cookies and login again

---

## Production Deployment

### Before Deploying

1. Change SECRET_KEY and JWT_SECRET_KEY
2. Set DEBUG=False in .env
3. Update DATABASE_URL to production database
4. Enable HTTPS/SSL
5. Set SESSION_COOKIE_SECURE=True
6. Configure email service
7. Setup regular backups
8. Monitor logs

### Deploy to Heroku (Example)

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create ecofeast

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Initialize database
heroku run python run.py create_admin
```

---

## Support & Resources

### Documentation
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- PostgreSQL: https://www.postgresql.org/docs/

### Useful Commands

```bash
# See current database tables
psql -U postgres -d ecofeast_dev -c "\dt"

# Backup database
pg_dump -U postgres ecofeast_dev > backup.sql

# Restore database
psql -U postgres ecofeast_dev < backup.sql

# View logs
tail -f app.log

# Check Python version
python --version

# List installed packages
pip list
```

---

## Quick Reference

### File Locations
- **Configuration**: `backend/config.py`
- **Models**: `backend/app/models/__init__.py`
- **Routes**: `backend/app/blueprints/`
- **Templates**: `backend/app/templates/`
- **Static Files**: `backend/app/static/`
- **Environment**: `backend/.env`

### Important URLs
- Home: http://localhost:5000/
- Register: http://localhost:5000/auth/register
- Login: http://localhost:5000/auth/login
- Admin: http://localhost:5000/admin/dashboard
- Donor: http://localhost:5000/donor/dashboard
- NGO: http://localhost:5000/ngo/dashboard
- Logistics: http://localhost:5000/logistics/dashboard

---

**You're all set! Happy volunteering with ECOFEAST! 🌿💚**
