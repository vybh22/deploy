# ECOFEAST - API Reference Documentation

## 📚 Overview

This document describes all API endpoints available in ECOFEAST. The API uses RESTful principles and returns JSON responses.

---

## Base URL

```
http://localhost:5000/api
```

For production, replace `localhost:5000` with your domain.

---

## Authentication

Currently, most endpoints require browser session authentication (Flask-Login). 

**For API integration (future)**, include JWT token in header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Response Format

### Success Response (200)
```json
{
  "success": true,
  "data": {...}
}
```

### Error Response (4xx, 5xx)
```json
{
  "success": false,
  "error": "Error message here",
  "status": 400
}
```

---

## Endpoints

### 📍 Notifications

#### Get Unread Notifications
```
GET /api/notifications/unread
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": 2,
      "message": "Your donation was approved",
      "notification_type": "donation_approved",
      "is_read": false,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

**Limit:** Returns 10 most recent

---

#### Mark Notification as Read
```
POST /api/notifications/{id}/read
```

**Parameters:**
- `id` (path, integer): Notification ID

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

---

#### Mark All Notifications as Read
```
POST /api/notifications/read-all
```

**Response:**
```json
{
  "success": true,
  "message": "All notifications marked as read",
  "count": 5
}
```

---

### 🗺️ Location & Distance

#### Calculate Distance Between Points
```
POST /api/distance
```

**Request Body:**
```json
{
  "lat1": 28.6139,
  "lon1": 77.2090,
  "lat2": 28.7041,
  "lon2": 77.1025
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "distance_km": 12.45,
    "distance_miles": 7.73
  }
}
```

---

#### Update User Location
```
POST /api/user/location/update
```

**Request Body:**
```json
{
  "latitude": 28.6139,
  "longitude": 77.2090,
  "city": "Delhi"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Location updated"
}
```

---

### 🍲 Donations

#### Search Donations
```
GET /api/search/donations?query=rice&city=delhi&page=1
```

**Query Parameters:**
- `query` (string, optional): Search term (food type, description)
- `city` (string, optional): Filter by city
- `page` (integer, default=1): Page number

**Response:**
```json
{
  "success": true,
  "data": {
    "donations": [
      {
        "id": 1,
        "donor_id": 2,
        "food_type": "Rice",
        "quantity": 50,
        "description": "Fresh rice from restaurant",
        "expiry_time": "2024-01-16T20:00:00",
        "pickup_date": "2024-01-15",
        "pickup_time": "15:00",
        "address": "123 Main St",
        "city": "Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "status": "APPROVED",
        "created_at": "2024-01-15T10:00:00"
      }
    ],
    "total_count": 45,
    "page": 1,
    "per_page": 10,
    "total_pages": 5
  }
}
```

---

#### Get Available Logistics
```
GET /api/logistics/available
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 5,
      "username": "john_logistics",
      "full_name": "John Doe",
      "phone": "9876543210",
      "current_deliveries": 2,
      "is_available": true
    }
  ]
}
```

---

### 📊 Dashboard Statistics

#### Get Admin Dashboard Stats
```
GET /api/stats/dashboard
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_donations": 45,
    "total_users": 120,
    "total_ngo": 15,
    "total_donors": 40,
    "total_logistics": 25,
    "deliveries_completed": 42,
    "success_rate": 93.33,
    "total_packets_delivered": 1250,
    "co2_reduction_kg": 1500,
    "pending_user_approvals": 3,
    "pending_donation_approvals": 5,
    "pending_request_approvals": 2
  }
}
```

---

### 👤 User

#### Get User Status
```
GET /api/user/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_authenticated": true,
    "username": "john_donor",
    "email": "john@example.com",
    "role": "DONOR",
    "is_verified": true,
    "avatar_url": "/static/avatars/john.jpg"
  }
}
```

---

#### Get User Profile
```
GET /api/user/profile
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "john_donor",
    "email": "john@example.com",
    "full_name": "John Donor",
    "phone": "9876543210",
    "role": "DONOR",
    "organization": "Pizza Palace",
    "address": "123 Main St",
    "city": "Delhi",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "is_verified": true,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

---

### 🎁 Deliveries

#### Get Delivery Location
```
GET /api/delivery/{id}/location
```

**Parameters:**
- `id` (path, integer): Delivery ID

**Response:**
```json
{
  "success": true,
  "data": {
    "pickup": {
      "latitude": 28.6139,
      "longitude": 77.2090,
      "address": "123 Main St (Donor)",
      "contact": "9876543210"
    },
    "delivery": {
      "latitude": 28.7041,
      "longitude": 77.1025,
      "address": "456 Oak Ave (NGO)",
      "contact": "9876543211"
    },
    "distance_km": 12.45,
    "estimated_time_minutes": 25
  }
}
```

---

#### Get Active Deliveries
```
GET /api/deliveries/active
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "donation": {
        "food_type": "Rice",
        "quantity": 50
      },
      "logistics": {
        "username": "john_logistics",
        "phone": "9876543210"
      },
      "ngo": {
        "organization": "Help Foundation",
        "phone": "9876543211"
      },
      "status": "ASSIGNED",
      "pickup_time": null,
      "delivery_time": null
    }
  ]
}
```

---

## HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Donation updated |
| 201 | Created | New donation created |
| 400 | Bad Request | Invalid form data |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | No permission (wrong role) |
| 404 | Not Found | Donation doesn't exist |
| 500 | Server Error | Database error |

---

## Common Error Responses

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Please log in to continue",
  "status": 401
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": "You do not have permission to perform this action",
  "status": 403
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Donation not found",
  "status": 404
}
```

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid donation ID provided",
  "status": 400
}
```

---

## Rate Limiting

Currently **not implemented**. For production:
- Recommend: 100 requests per minute per user
- Implement using: Flask-Limiter extension

---

## Pagination

Paginated endpoints support:

**Query Parameters:**
- `page` (integer, default=1): Page number
- `per_page` (integer, default=10): Items per page

**Response:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 45,
    "per_page": 10
  }
}
```

---

## Web Page Routes (Non-API)

### Authentication
```
GET  /auth/login
POST /auth/login
GET  /auth/register
POST /auth/register
GET  /auth/logout
GET  /auth/profile
POST /auth/profile
```

### Public Pages
```
GET /                           # Homepage
GET /about                      # About page
GET /how-it-works               # How it works
GET /contact                    # Contact page
```

### Donor Routes
```
GET  /donor/dashboard           # Donor dashboard
GET  /donor/listing/create      # Create listing page
POST /donor/listing/create      # Submit listing
GET  /donor/listing/<id>        # View listing
GET  /donor/listing/<id>/edit   # Edit listing page
POST /donor/listing/<id>/edit   # Update listing
POST /donor/listing/<id>/delete # Delete listing
GET  /donor/notifications       # View notifications
POST /donor/feedback/<id>       # Submit feedback
```

### NGO Routes
```
GET  /ngo/dashboard             # NGO dashboard
GET  /ngo/browse                # Browse listings
GET  /ngo/listing/<id>          # View listing details
POST /ngo/request/create        # Create request
GET  /ngo/notifications         # View notifications
POST /ngo/delivery/<id>/confirm # Confirm delivery
POST /ngo/feedback/<id>         # Submit feedback
```

### Logistics Routes
```
GET  /logistics/dashboard       # Logistics dashboard
GET  /logistics/delivery/<id>   # View delivery
POST /logistics/delivery/<id>/pickup  # Confirm pickup
GET  /logistics/notifications   # View notifications
```

### Admin Routes
```
GET  /admin/dashboard           # Admin dashboard
GET  /admin/users               # Manage users
POST /admin/user/<id>/approve   # Approve user
POST /admin/user/<id>/deactivate # Deactivate user
GET  /admin/donations           # Manage donations
POST /admin/donation/<id>/approve  # Approve donation
POST /admin/donation/<id>/reject   # Reject donation
GET  /admin/requests            # Manage requests
POST /admin/request/<id>/approve   # Approve request
POST /admin/request/<id>/reject    # Reject request
POST /admin/delivery/<id>/assign   # Assign logistics
GET  /admin/reports             # View reports
GET  /admin/audit_log           # View audit log
```

---

## Database Models Reference

### User Model
```
id (Integer, PK)
username (String, Unique)
email (String, Unique)
password_hash (String)
full_name (String)
phone (String)
role (Enum: ADMIN, DONOR, NGO, LOGISTICS)
organization (String)
registration_number (String)
address (String)
city (String)
latitude (Float)
longitude (Float)
is_verified (Boolean)
is_active (Boolean)
created_at (DateTime)
updated_at (DateTime)
```

### Donation Model
```
id (Integer, PK)
donor_id (Integer, FK -> User)
food_type (String)
quantity (Integer)
description (String)
expiry_time (DateTime)
pickup_date (Date)
pickup_time (Time)
address (String)
city (String)
latitude (Float)
longitude (Float)
status (Enum: PENDING, APPROVED, ASSIGNED, PICKED_UP, DELIVERED, CANCELLED)
approved_at (DateTime)
created_at (DateTime)
```

### FoodRequest Model
```
id (Integer, PK)
donation_id (Integer, FK -> Donation)
ngo_id (Integer, FK -> User)
quantity (Integer)
status (Enum: pending, approved, rejected)
admin_notes (String)
created_at (DateTime)
approved_at (DateTime)
```

### Delivery Model
```
id (Integer, PK)
donation_id (Integer, FK -> Donation)
ngo_id (Integer, FK -> User)
logistics_id (Integer, FK -> User)
status (Enum: assigned, in_progress, completed)
pickup_time (DateTime)
delivery_time (DateTime)
created_at (DateTime)
```

### Notification Model
```
id (Integer, PK)
user_id (Integer, FK -> User)
message (String)
notification_type (String)
related_entity_id (Integer)
is_read (Boolean)
created_at (DateTime)
```

### AuditLog Model
```
id (Integer, PK)
admin_id (Integer, FK -> User)
action (String)
entity_type (String)
entity_id (Integer)
old_values (JSON)
new_values (JSON)
timestamp (DateTime)
```

---

## Using API with JavaScript (Fetch)

### Example: Search Donations
```javascript
const searchDonations = async (query, city) => {
  const response = await fetch(
    `/api/search/donations?query=${query}&city=${city}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Donations:', data.data.donations);
  } else {
    console.error('Error:', data.error);
  }
};

// Usage
searchDonations('rice', 'delhi');
```

### Example: Calculate Distance
```javascript
const getDistance = async (lat1, lon1, lat2, lon2) => {
  const response = await fetch('/api/distance', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      lat1, lon1, lat2, lon2
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    return data.data.distance_km;
  }
};

// Usage
const distance = await getDistance(28.6139, 77.2090, 28.7041, 77.1025);
console.log(`Distance: ${distance} km`);
```

---

## Using API with cURL

### Example: Get Unread Notifications
```bash
curl -X GET http://localhost:5000/api/notifications/unread \
  -H "Content-Type: application/json" \
  -b "session=YOUR_SESSION_COOKIE"
```

### Example: Mark Notification as Read
```bash
curl -X POST http://localhost:5000/api/notifications/1/read \
  -H "Content-Type: application/json" \
  -b "session=YOUR_SESSION_COOKIE"
```

### Example: Search Donations
```bash
curl -X GET "http://localhost:5000/api/search/donations?query=rice&city=delhi" \
  -H "Content-Type: application/json" \
  -b "session=YOUR_SESSION_COOKIE"
```

---

## Extending the API

### Add New Endpoint

1. Create function in appropriate blueprint:
```python
@api.route('/new-endpoint', methods=['GET'])
@login_required
def new_endpoint():
    try:
        data = {...}
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

2. Add to documentation
3. Test with Postman or cURL

---

## API Testing Tools

### Postman
1. Download: https://www.postman.com/
2. Create new request
3. Enter endpoint URL
4. Set method (GET, POST, etc.)
5. Add headers and body
6. Send request

### cURL
```bash
# GET request
curl http://localhost:5000/api/endpoint

# POST request with JSON
curl -X POST http://localhost:5000/api/endpoint \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### Python Requests
```python
import requests

response = requests.get('http://localhost:5000/api/endpoint')
data = response.json()
print(data)
```

---

## Security Notes

1. **Authentication**: All endpoints require active session (logged in)
2. **Authorization**: Role-based access enforced
3. **SQL Injection**: Protected via SQLAlchemy ORM
4. **CSRF**: Protected via Flask-WTF
5. **Validation**: All inputs validated before processing

---

## Future API Enhancements

- [ ] JWT token-based authentication
- [ ] Rate limiting (100 req/min per user)
- [ ] API versioning (/api/v1/...)
- [ ] Advanced filtering (dietary restrictions, portion sizes)
- [ ] WebSocket support for real-time updates
- [ ] GraphQL endpoint
- [ ] OAuth 2.0 integration
- [ ] API documentation with Swagger/OpenAPI

---

## Support & Issues

For API issues:
1. Check [TESTING_GUIDE.md](TESTING_GUIDE.md)
2. Review browser console (F12)
3. Check Flask terminal output
4. Verify database connection
5. Check authentication status

---

**Happy coding with ECOFEAST! 🚀**
