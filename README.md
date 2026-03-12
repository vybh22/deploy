# ECOFEAST - Food Waste Reduction Platform

A comprehensive full-stack web application that connects surplus food donors with NGOs and logistics volunteers to reduce food waste and support underprivileged communities.

## Features

### Role-Based Access Control (RBAC)
- **Admin**: Approve/reject registrations, manage users, view analytics
- **Donor**: List surplus food, track donations, receive feedback
- **NGO**: Browse food listings, request donations, confirm deliveries
- **Logistics**: Manage pickups and deliveries with real-time tracking

### Core Functionality
- Real-time food listing and browsing
- Request approval workflow
- Geolocation tracking with Google Maps API
- Delivery status tracking (Pending → Approved → Assigned → Picked Up → Delivered)
- In-app notification system with AJAX polling
- Admin analytics dashboard with charts
- Audit logging for all admin actions
- Responsive design for desktop and mobile

### Security Features
- Password hashing with bcrypt
- CSRF protection
- Input validation (frontend + backend)
- SQL injection protection via SQLAlchemy ORM
- Role-based route protection
- Secure session management
- Environment variables for secrets

## Technology Stack

### Frontend
- HTML5
- CSS3 (Responsive Flexbox/Grid)
- Vanilla JavaScript (no frameworks)
- Fetch API for backend communication
- Google Maps API for geolocation
- Chart.js for analytics visualization

### Backend
- Python 3.x
- Flask with modular blueprint structure
- Flask-Login for authentication
- Flask-SQLAlchemy ORM
- Flask-Migrate for database migrations
- Flask-CORS for cross-origin requests

### Database
- PostgreSQL with proper indexing
- Relational schema with foreign key constraints
- Audit logging for compliance

## Project Structure

```
ecofeast/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── blueprints/      # Route blueprints
│   │   │   ├── auth.py      # Authentication routes
│   │   │   ├── main.py      # Public routes
│   │   │   ├── donor.py     # Donor routes
│   │   │   ├── ngo.py       # NGO routes
│   │   │   ├── logistics.py # Logistics routes
│   │   │   ├── admin.py     # Admin routes
│   │   │   └── api.py       # API endpoints
│   │   ├── static/
│   │   │   ├── css/         # Stylesheets
│   │   │   └── js/          # JavaScript files
│   │   └── templates/       # HTML templates
│   ├── run.py               # Application entry point
│   ├── config.py            # Configuration
│   └── requirements.txt     # Python dependencies
├── .env.example             # Environment variables template
└── README.md               # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb ecofeast_dev

# Or via PostgreSQL CLI
psql -U postgres
CREATE DATABASE ecofeast_dev;
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env with your configuration
# Replace DATABASE_URL with your actual database connection
# Replace GOOGLE_MAPS_KEY with your API key
# Change SECRET_KEY and JWT_SECRET_KEY for production
```

### 3. Database Migrations

```bash
# Initialize database
python run.py

# Create admin user
python run.py create_admin
# Follow the prompts to create your admin account
```

### 4. Run Application

```bash
# Development server
python run.py

# Application will be available at http://localhost:5000
```

## Usage

### Registration Flow
1. Visit http://localhost:5000/auth/register
2. Select your role (Donor, NGO, or Logistics)
3. Donors are auto-verified; NGOs and Logistics need admin approval
4. Login at http://localhost:5000/auth/login

### Workflow Example

#### As a Donor:
1. Login to dashboard
2. Click "Create Listing" to add surplus food
3. Pin location on map
4. Submit for approval
5. Wait for admin approval
6. Receive notifications when NGOs request your food

#### As an NGO:
1. Login to dashboard
2. Click "Browse Food" to see available donations
3. Submit requests for needed food
4. Wait for admin approval
5. Confirm delivery when food arrives

#### As Logistics:
1. Login to dashboard
2. View assigned deliveries
3. Navigate to pickup and delivery locations
4. Confirm pickup and delivery status

#### As Admin:
1. Login to dashboard
2. Review pending approvals
3. Approve or reject donations and requests
4. Assign logistics volunteers
5. View analytics and reports
6. Monitor audit logs

## Configuration

### Environment Variables (.env)

```
FLASK_ENV=development|production|testing
DEBUG=True|False
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/ecofeast_dev
SESSION_COOKIE_SECURE=True|False
GOOGLE_MAPS_KEY=your-google-maps-api-key
```

### Database Configuration (config.py)

Modify database URI based on your environment:
- **Development**: SQLite or local PostgreSQL
- **Production**: External PostgreSQL database

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `POST /auth/profile` - Update profile

### Donor
- `GET /donor/dashboard` - Donor dashboard
- `POST /donor/listing/create` - Create food listing
- `POST /donor/listing/<id>/edit` - Edit listing
- `POST /donor/listing/<id>/delete` - Delete listing
- `GET /donor/listing/<id>` - View listing details
- `POST /donor/feedback/<id>` - Submit feedback

### NGO
- `GET /ngo/dashboard` - NGO dashboard
- `GET /ngo/browse` - Browse food listings
- `GET /ngo/listing/<id>` - View listing
- `POST /ngo/request/create` - Create food request
- `POST /ngo/delivery/<id>/confirm` - Confirm delivery
- `POST /ngo/feedback/<id>` - Submit feedback

### Logistics
- `GET /logistics/dashboard` - Logistics dashboard
- `GET /logistics/delivery/<id>` - View delivery details
- `POST /logistics/delivery/<id>/pickup` - Confirm pickup
- `GET /api/delivery/<id>/location` - Get delivery locations

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - Manage users
- `POST /admin/user/<id>/approve` - Approve user
- `POST /admin/user/<id>/deactivate` - Deactivate user
- `GET /admin/donations` - Manage donations
- `POST /admin/donation/<id>/approve` - Approve donation
- `POST /admin/donation/<id>/reject` - Reject donation
- `GET /admin/requests` - Manage requests
- `POST /admin/request/<id>/approve` - Approve request
- `POST /admin/request/<id>/reject` - Reject request
- `POST /admin/delivery/<id>/assign` - Assign logistics

### API Utilities
- `GET /api/notifications/unread` - Get unread notifications
- `POST /api/notifications/<id>/read` - Mark as read
- `GET /api/stats/dashboard` - Get dashboard statistics
- `POST /api/user/location/update` - Update user location
- `POST /api/distance` - Calculate distance

## Security Considerations

### Production Deployment
1. Change `SECRET_KEY` and `JWT_SECRET_KEY` to strong random values
2. Set `DEBUG=False`
3. Set `SESSION_COOKIE_SECURE=True` (requires HTTPS)
4. Use environment-specific configurations
5. Enable CORS only for trusted domains
6. Implement rate limiting
7. Add HTTPS/SSL certificates
8. Use strong database passwords
9. Regular security audits and updates
10. Implement proper logging and monitoring

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character

## Database Schema

### Key Tables
- **users** - All users with role-based access
- **donations** - Food listings from donors
- **food_requests** - NGO requests for food
- **deliveries** - Delivery tracking
- **notifications** - In-app notifications
- **feedback** - User feedback
- **audit_logs** - Admin action tracking

## Performance Optimization

### Database Indexing
- Indexed on `user_id`, `created_at`, `status` for fast queries
- Foreign key constraints for data integrity
- Proper pagination for large datasets

### Caching Opportunities
- Cache user locations for map display
- Cache admin dashboard statistics (refresh every 5 minutes)
- Cache available donations list

## Future Enhancements

1. **Email Notifications** via SendGrid or similar
2. **SMS Notifications** via Twilio
3. **Real-time Updates** using WebSockets
4. **Mobile App** using React Native or Flutter
5. **Payment Integration** for optional donations
6. **Machine Learning** for demand prediction
7. **Carbon Credit Tracking** and certification
8. **Integration with Food Banks** and Government Programs
9. **Blockchain** for transparent tracking
10. **Gamification** with leaderboards and badges

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -U postgres

# Verify DATABASE_URL in .env
# Format: postgresql://username:password@localhost:5432/database_name
```

### Port Already in Use
```bash
# Change port in run.py or run with alternative port
python run.py --port=5001
```

### Map Not Loading
- Verify Google Maps API key in .env
- Check API key has necessary permissions enabled
- Ensure billing is enabled on Google Cloud Platform

### Static Files Not Loading
- Clear browser cache
- Check static files path in config.py
- Verify CSS/JS files exist in `app/static/`

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is open-source and available under the MIT License.

## Contact & Support

For issues, questions, or suggestions:
- Email: info@ecofeast.com
- GitHub Issues: [Project Repository]

## Acknowledgments

- Built with Flask, PostgreSQL, and Vanilla JavaScript
- Google Maps API for geolocation services
- Chart.js for analytics visualization
- Community supporters and contributors

---

**Together, we can reduce food waste and feed our communities.** 🌍💚
