# ECOFEAST - Technical Architecture & Design Document

## 🏗️ System Overview

ECOFEAST is a full-stack web application designed to reduce food waste by connecting surplus food donors with NGOs and logistics volunteers. The system uses a client-server architecture with a modular backend and responsive frontend.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                         │
│  ┌──────────────┬──────────────┬──────────────────────┐ │
│  │   Templates  │  CSS Styling │  JavaScript Utils    │ │
│  │ (Jinja2 HTML)│ (Responsive) │  (Vanilla JS/Fetch)  │ │
│  └──────────────┴──────────────┴──────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                         ↑↓ HTTP/REST
┌─────────────────────────────────────────────────────────  ┐
│                  APPLICATION LAYER                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Flask Application Factory              │  │
│  │ ┌─────────────────────────────────────────────────┐ │  │
│  │ │ Modular Blueprints (Route Handlers)            │ │   │
│  │ │ • auth (authentication)                        │ │   │
│  │ │ • main (public pages)                          │ │   │
│  │ │ • donor (food donation)                        │ │   │
│  │ │ • ngo (food requests)                          │ │   │
│  │ │ • logistics (delivery tracking)                │ │   │
│  │ │ • admin (administration)                       │ │   │
│  │ │ • api (AJAX endpoints)                         │ │   │
│  │ └─────────────────────────────────────────────────┘ │  │
│  │ ┌─────────────────────────────────────────────────┐ │  │
│  │ │       Business Logic & Utilities                │ │  │
│  │ │ • Input validation & sanitization              │ │   │
│  │ │ • Password hashing (bcrypt)                    │ │   │
│  │ │ • Location calculation (haversine)             │ │   │
│  │ │ • Notification generation                      │ │   
│  │ │ • Audit logging                                │ │   │
    │  │ └─────────────────────────────────────────────────┘ │  │
    │  │ ┌─────────────────────────────────────────────────┐ │ │
│  │ │          Access Control System                  │ │ │
│  │ │ • Role-Based Access Control (RBAC)             │ │ │
│  │ │ • Custom decorators (@role_required)           │ │ │
│  │ │ • Session management (Flask-Login)             │ │ │
│  │ └─────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                         ↑↓ SQL
┌─────────────────────────────────────────────────────────┐
│                   DATA LAYER                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              PostgreSQL Database                    │ │
│  │ ┌──────────        ┬──────────────┬──────────────────┐    │ │
│  │ │  Tables          │  Indexes     │  Foreign Keys    │    │ │
│  │ │ • users          │ • user_id    │ • Cascading      │    │ │
│  │ │ • donations      │ • created_at │ • Constraints    │    │ │
│  │ │ • food_requests  │ • status     │ • Integrity      │    │ │
│  │ │ • deliveries     │ • verified   │ • Relations      │    │ │
│  │ │ • notifications  │ • active     │ • Referential    │   │ │
│  │ │ • feedback       │              │                  │                │ │
│  │ │ • audit_logs     │              │                  │                │ │
│  │ └──────────        ┴──────────────┴──────────────────┘    │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                        ↑↓ API
┌─────────────────────────────────────────────────────────┐
│                 EXTERNAL SERVICES                       │
│  • Google Maps API (geolocation, distance)             │
│  • Email Service (can be integrated)                   │
│  • SMS Service (can be integrated)                     │
└─────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
foodwaste/backend/
├── app/
│   ├── __init__.py              # App factory, extension initialization
│   ├── models/
│   │   └── __init__.py          # All database models (8 models)
│   ├── blueprints/
│   │   ├── auth.py              # Authentication routes
│   │   ├── main.py              # Public pages routes
│   │   ├── donor.py             # Donor functionality
│   │   ├── ngo.py               # NGO functionality
│   │   ├── logistics.py         # Logistics functionality
│   │   ├── admin.py             # Admin dashboard
│   │   └── api.py               # AJAX API endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Main stylesheet (responsive)
│   │   └── js/
│   │       ├── main.js          # Global utilities
│   │       └── utils.js         # Role-specific utilities
│   ├── templates/
│   │   ├── base.html            # Master template
│   │   ├── index.html           # Homepage
│   │   ├── auth/                # Auth templates
│   │   ├── donor/               # Donor templates
│   │   ├── ngo/                 # NGO templates
│   │   ├── logistics/           # Logistics templates
│   │   └── admin/               # Admin templates
│   ├── decorators.py            # Custom decorators
│   └── config.py                # Configuration classes
├── requirements.txt             # Python dependencies
├── config.py                    # Configuration management
├── run.py                       # Application entry point
├── .env                         # Environment variables (create from .env.example)
├── .env.example                 # Example environment file
├── .gitignore                   # Git ignore rules
├── README.md                    # Project overview
├── QUICKSTART.md                # Quick setup guide
├── INSTALLATION_GUIDE.md        # Detailed installation
├── TESTING_GUIDE.md             # Testing procedures
├── API_REFERENCE.md             # API documentation
├── setup.bat / setup.sh         # Setup automation scripts
├── run.bat / run.sh             # Run scripts
└── create_db.bat / create_db.sh # Database creation scripts
```

---

## Core Components

### 1. Application Factory Pattern

**File:** `app/__init__.py`

**Purpose:** Creates and configures Flask application dynamically

**Key Code:**
```python
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    # ... more blueprints
    
    return app
```

**Benefits:**
- Allows multiple app instances with different configs
- Easy testing with test configuration
- Clean separation of concerns
- Scalable blueprint registration

---

### 2. Database Models

**File:** `app/models/__init__.py`

**Key Models:**

#### User Model (26 attributes)
- **Role:** ADMIN, DONOR, NGO, LOGISTICS
- **Verification:** is_verified, verification_date
- **Location:** latitude, longitude, city
- **Organization:** organization, registration_number
- **Security:** password_hash, bcrypt validation
- **Status:** is_active, deactivation_reason, deactivation_date

#### Donation Model (12 attributes)
- **Identification:** id, food_type, quantity
- **Details:** description, expiry_time
- **Timing:** pickup_date, pickup_time
- **Location:** address, city, latitude, longitude
- **Status:** status (6 states), approved_at, created_at
- **Relationship:** donor_id (Foreign Key)

#### FoodRequest Model (7 attributes)
- **Identification:** id, donation_id, ngo_id
- **Details:** quantity, status (pending/approved/rejected)
- **Notes:** admin_notes
- **Timing:** created_at, approved_at
- **Constraint:** Unique(donation_id, ngo_id) - prevents duplicate requests

#### Delivery Model (8 attributes)
- **Relationships:** donation_id, ngo_id, logistics_id
- **Status:** status (3 states)
- **Timing:** pickup_time, delivery_time
- **Timestamps:** created_at

#### Notification Model (6 attributes)
- **User:** user_id
- **Content:** message, notification_type
- **Reference:** related_entity_id
- **State:** is_read, created_at

#### Feedback Model (6 attributes)
- **User:** user_id
- **Content:** rating, comment
- **Reference:** delivery_id
- **Timing:** created_at

#### AuditLog Model (7 attributes)
- **User:** admin_id
- **Action:** action, entity_type, entity_id
- **Changes:** old_values (JSON), new_values (JSON)
- **Timing:** timestamp

---

### 3. Blueprint Architecture

**Pattern:** Modular blueprints with route grouping

**Benefits:**
- Separation of concerns
- Easy to maintain and extend
- Clear URL prefixes
- Per-blueprint error handling

**Example Structure:**
```python
# Blueprint registration
donation_bp = Blueprint('donor', __name__, url_prefix='/donor')

@donor_bp.route('/dashboard')
@role_required(Role.DONOR)
def dashboard():
    # Donor dashboard logic
    pass
```

---

### 4. Role-Based Access Control (RBAC)

**Implementation:** Custom decorators on top of Flask-Login

**Decorator Pattern:**
```python
@role_required(Role.ADMIN)
@login_required
def admin_function():
    # Only admin users can access
    pass

@roles_required([Role.DONOR, Role.NGO])
@login_required
def multi_role_function():
    # Multiple roles allowed
    pass
```

**Access Control Flow:**
1. User logs in
2. Role stored in session
3. Decorators check role on each request
4. 403 error if unauthorized

---

### 5. Authentication System

**File:** `app/blueprints/auth.py`

**Components:**
- Registration (email validation, password strength)
- Login (credential verification, role-based redirect)
- Password hashing (bcrypt, salted)
- Profile management

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character (!@#$%^&*)

**Regex Pattern:**
```python
pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$'
```

---

### 6. Notification System

**Architecture:** AJAX polling (30-second intervals)

**Workflow:**
```
User Action → Database Change → Notification Created → AJAX Poll → Show to User
               (e.g., approve)    (in notifications table)    (main.js)
```

**Notification Types:**
- `donation_approved`
- `donation_rejected`
- `request_approved`
- `request_rejected`
- `user_approved`
- `pickup_confirmed`
- `delivery_confirmed`

**Database-Driven:** Fully stored in database, survives refresh

---

### 7. Geolocation & Distance Calculation

**Technology:** Google Maps API + Haversine Formula

**Components:**

#### Frontend Map Picker
```javascript
// Place clickable map on listing creation
// User clicks map → updates lat/lon fields
// Marker shows selected location
```

#### Distance Calculation
```python
# Haversine formula
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    φ1 = radians(lat1)
    φ2 = radians(lat2)
    Δφ = radians(lat2 - lat1)
    Δλ = radians(lon2 - lon1)
    
    a = sin²(Δφ/2) + cos(φ1) × cos(φ2) × sin²(Δλ/2)
    return 2R × atan2(√a, √(1−a))
```

---

### 8. Audit Logging

**Purpose:** Track all admin actions for compliance

**Logged Actions:**
- User approvals/deactivations
- Donation approvals/rejections
- Request approvals/rejections
- Logistics assignments

**Schema:**
```
admin_id | action | entity_type | entity_id | old_values | new_values | timestamp
   2     | approve| user        |    5      | {is_v: 0}  | {is_v: 1}  | 2024-01-15
```

**Querying Example:**
```python
AuditLog.query.filter_by(admin_id=user_id).order_by(AuditLog.timestamp.desc()).all()
```

---

## Data Flows

### 1. Donation Workflow

```
Donor Creates Listing
    ↓
(PENDING) - Awaiting Admin Approval
    ↓
Admin Approves Donation
    ↓
(APPROVED) - Available for NGO Requests
    ↓
NGO Submits Request
    ↓
Admin Approves Request & Assigns Logistics
    ↓
(ASSIGNED) - Logistics Receives Assignment
    ↓
Logistics Confirms Pickup
    ↓
(PICKED_UP) - En Route to NGO
    ↓
NGO Confirms Delivery
    ↓
(DELIVERED) - Workflow Complete
```

### 2. User Registration Workflow

```
User Submits Registration Form
    ↓
Validation (email format, password strength)
    ↓
User Account Created (is_verified=False)
    ↓
For Donors/NGOs → Auto-verified
For NGOs/Logistics → Await Admin Approval
    ↓
(is_verified=True) - Can now login to dashboard
    ↓
Admin notified if manual approval needed
```

### 3. Notification Flow

```
Database Event (Status Change)
    ↓
Create Notification Record
    ↓
Set is_read = False
    ↓
JavaScript Polls /api/notifications/unread Every 30 Seconds
    ↓
Display Latest Notifications in UI
    ↓
User Clicks "Mark as Read"
    ↓
Set is_read = True in Database
```

---

## Security Architecture

### 1. Authentication Security
- **Password Storage:** bcrypt hashing with salt
- **Session Management:** Flask-Login with secure cookies
- **Session Timeout:** Configurable in production

### 2. Authorization Security
- **Role-Based Access:** Checked on every protected endpoint
- **Decorator Pattern:** Enforced at route level
- **View Protection:** Jinja2 template conditions

### 3. Input Validation
- **Frontend:** JavaScript validation with user feedback
- **Backend:** Server-side validation on all inputs
- **Regex Patterns:** Email, phone, password validation
- **Type Checking:** SQLAlchemy prevents type mismatches

### 4. SQL Injection Prevention
- **ORM Protection:** SQLAlchemy parameterizes all queries
- **No String Interpolation:** Never uses raw SQL
- **Prepared Statements:** All queries use ORM methods

### 5. CSRF Protection
- **Form Tokens:** Flask-WTF can be integrated
- **Same-Origin:** Browser enforces on AJAX calls
- **Content-Type:** Validates JSON/form submissions

### 6. Data Privacy
- **Password Hashing:** One-way encryption, cannot be reversed
- **Session Isolation:** Each user has independent session
- **Audit Trail:** Admin actions logged with admin_id

---

## Performance Considerations

### 1. Database Indexing

**Indexed Columns:**
```python
db.Index('idx_user_id', User.id)
db.Index('idx_created_at', Donation.created_at)
db.Index('idx_status', Donation.status)
db.Index('idx_is_verified', User.is_verified)
db.Index('idx_is_active', User.is_active)
```

**Query Optimization:**
- All searches use indexed columns
- Pagination prevents large result sets
- Foreign key relationships denormalized for speed

### 2. Frontend Performance

**Optimization Techniques:**
- Single CSS file (700 lines) vs. multiple files
- Vanilla JavaScript (no framework overhead)
- AJAX for partial page updates (not full refresh)
- Static file caching via browser cache
- Image optimization (if added)

### 3. Notification Polling

**Current:** 30-second interval polling
- Pros: Simple, no infrastructure needed
- Cons: Slight delay, server load

**Future:** WebSocket for real-time
- Pros: Instant notifications, better UX
- Cons: More complex infrastructure

---

## Scalability Considerations

### Horizontal Scaling
- Stateless application servers (scale easily)
- Shared PostgreSQL database
- Session store can move to Redis
- Static files to CDN

### Vertical Scaling
- Increase server RAM/CPU
- PostgreSQL tuning
- Connection pooling with pgBouncer
- Query optimization (EXPLAIN ANALYZE)

### Future Optimizations
- Caching layer (Redis) for notifications
- Message queue (RabbitMQ) for async tasks
- Search index (Elasticsearch) for fast text search
- Database read replicas for reporting

---

## Testing Architecture

### Unit Testing (Future)
```python
# Test individual functions
def test_user_password_validation():
    assert validate_password('weak') == False
    assert validate_password('Strong@123') == True
```

### Integration Testing (Future)
```python
# Test API endpoints
def test_donation_creation_flow():
    # Create donation
    # Approve donation
    # Request food
    # Verify status changes
```

### UI Testing (Manual in TESTING_GUIDE.md)
- Cross-browser testing
- Responsive design testing
- Form validation testing

---

## Deployment Checklist

### Pre-Production
- [ ] Change SECRET_KEY to secure random value
- [ ] Set DEBUG=False in .env
- [ ] Update DATABASE_URL to prod PostgreSQL
- [ ] Configure real Google Maps API key
- [ ] Setup email service (SendGrid/AWS SES)
- [ ] Enable HTTPS/SSL certificate
- [ ] Configure logging to file/service
- [ ] Setup automated backups
- [ ] Add rate limiting middleware
- [ ] Security audit (OWASP Top 10)

### Deployment Options
1. **Heroku** - Simplest, Platform as a Service
2. **AWS/Azure/GCP** - More control, VPS/containers
3. **DigitalOcean** - Affordable VPS
4. **Docker + Kubernetes** - Full containerization

---

## Monitoring & Maintenance

### Key Metrics
- Application response time
- Database query performance
- Error rates (4xx, 5xx)
- User authentication success rate
- Notification delivery time
- Server resource usage (CPU, RAM, Disk)

### Logging
- Error logs (Flask built-in)
- User action logs (audit trail)
- Database slow query logs
- Application performance logs

### Maintenance Tasks
- Regular database backups (daily)
- Security patches (monthly)
- Dependency updates (quarterly)
- Performance optimization (quarterly)
- User data cleanup (anonymize old data)

---

## Technology Stack Rationale

| Component | Choice | Why |
|-----------|--------|-----|
| **Backend** | Flask | Lightweight, Python, easy to learn |
| **Database** | PostgreSQL | Reliable, ACID, scaling capability |
| **Frontend** | Vanilla JS | No framework overhead, direct control |
| **Auth** | Flask-Login + bcrypt | Secure standard solution |
| **ORM** | SQLAlchemy | Prevention of SQL injection, relationships |
| **Maps** | Google Maps | Mature, reliable, good documentation |
| **Styling** | CSS3 + Flexbox | No framework dependency, responsive |
| **Deployment** | Docker ready | Containerization for cloud platforms |

---

## Known Limitations & Future Work

### Current Limitations
1. Image uploads not fully implemented
2. Email notifications only in-app
3. Polling instead of WebSocket
4. No rate limiting (add Flask-Limiter)
5. Manual backups needed

### Planned Enhancements
1. Image upload with verification photos
2. Email/SMS notifications (SendGrid/Twilio)
3. WebSocket real-time updates
4. Advanced filtering (dietary requirements)
5. Mobile native app (React Native)
6. Route optimization (Google Directions API)
7. Predictive analytics (food availability forecast)
8. Integration with government food donation programs

---

## Contributing Guidelines

### Adding New Feature
1. Create feature branch: `git checkout -b feature/new-feature`
2. Create database migration if needed
3. Implement backend logic (blueprint + model)
4. Create templates and forms
5. Add JavaScript utilities
6. Test thoroughly (TESTING_GUIDE.md)
7. Update documentation
8. Submit pull request

### Reporting Issues
1. Check TROUBLESHOOTING section
2. Review existing issues
3. Provide error message and logs
4. Specify reproduction steps
5. Include environment details

---

## Support & Contact

For technical support:
1. Check documentation files
2. Review source code comments
3. Test using TESTING_GUIDE.md
4. Check PostgreSQL logs
5. Review Flask application logs

---

**Architecture created with scalability, maintainability, and security in mind. Happy building! 🏗️**
