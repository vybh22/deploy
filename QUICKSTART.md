# ECOFEAST Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Git

## Step 1: Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ecofeast_dev;

# Exit PostgreSQL
\q
```

## Step 2: Setup Python Environment

```bash
# Navigate to project folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings:
# - DATABASE_URL: postgresql://postgres:password@localhost:5432/ecofeast_dev
# - GOOGLE_MAPS_KEY: Your Google Maps API key
# - SECRET_KEY: A random secure key
# - JWT_SECRET_KEY: Another random secure key

# Generate secure keys:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 4: Initialize Database

```bash
# Create database tables
python run.py

# Create admin user
python run.py create_admin
# Enter username, email, password when prompted
```

## Step 5: Run Application

```bash
# Start Flask development server
python run.py

# Application will run at http://localhost:5000
```

## Test the Application

### Admin Account
- Username: (from setup)
- Password: (from setup)
- URL: http://localhost:5000/auth/login

### Register New Users
1. Go to http://localhost:5000/auth/register
2. Choose role: Donor, NGO, or Logistics
3. Fill in details and submit
4. Donors auto-verified
5. NGOs/Logistics need admin approval

### Workflow Test
1. **As Admin**: Approve pending users and donations
2. **As Donor**: Create a food listing
3. **As NGO**: Browse and request food
4. **As Logistics**: View and manage deliveries

## Troubleshooting

### PostgreSQL Connection Error
```
Error: could not connect to database
```
Solution: Ensure PostgreSQL is running and DATABASE_URL in .env is correct

### Port 5000 Already in Use
```
Error: Address already in use
```
Solution: Kill existing process or change port in run.py

### Import Errors
```
ModuleNotFoundError: No module named 'flask'
```
Solution: Activate virtual environment and reinstall requirements.txt

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
dropdb ecofeast_dev
createdb ecofeast_dev
python run.py
python run.py create_admin
```

## Default Test Credentials

After setup, you can test with:

**Admin:**
- Username: admin (or your chosen username)
- Password: (your chosen password)

**Create Test Donor:**
1. Register as Donor at /auth/register
2. Auto-verified
3. Login and create food listings

**Create Test NGO/Logistics:**
1. Register at /auth/register
2. As Admin, go to /admin/users
3. Approve the pending user
4. User can now login

## Important Files

- `run.py` - Application entry point
- `config.py` - Configuration settings
- `app/models/__init__.py` - Database models
- `app/blueprints/` - Route handlers
- `app/templates/` - HTML templates
- `app/static/` - CSS, JavaScript
- `.env` - Environment variables (create from .env.example)

## Development Commands

```bash
# Run with debug mode
FLASK_ENV=development python run.py

# Run with different port
python run.py --port=8000

# Database shell
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

## Next Steps

1. Get Google Maps API Key from https://cloud.google.com/maps-platform
2. Add it to .env file
3. Test location features
4. Customize branding and styling
5. Deploy to production (see README.md for production setup)

## Support

For issues or questions, refer to README.md or check Flask documentation at https://flask.palletsprojects.com/
