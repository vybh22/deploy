# ECOFEAST - Testing & Verification Guide

## 🧪 Overview

This guide helps you verify that ECOFEAST is installed correctly and all features are working properly.

---

## Pre-Testing Checklist

Before testing, ensure:
- [ ] Python is installed (`python --version` shows 3.8+)
- [ ] PostgreSQL is running
- [ ] Virtual environment is activated
- [ ] All dependencies installed (`pip list | grep Flask`)
- [ ] `.env` file is configured
- [ ] Database created (`psql -U postgres -l | grep ecofeast_dev`)
- [ ] Flask app is running on http://localhost:5000

---

## 1. Basic Connectivity Tests

### Test 1.1: Application Starts

```bash
# Start the app
run.bat  # Windows
./run.sh # macOS/Linux
```

**Expected Result:**
```
* Running on http://127.0.0.1:5000
* Press CTRL+C to quit
```

**✅ Verification**: Open http://localhost:5000 in browser, see homepage

---

### Test 1.2: Database Connection

```bash
# From terminal in active environment
python -c "from app import db; from app.models import User; print(User.query.count())"
```

**Expected Result:**
```
0  # (or number of users if you've created any)
```

**✅ Verification**: No error message, number is returned

---

### Test 1.3: Static Files Loaded

1. Open http://localhost:5000 in browser
2. Press F12 (Developer Tools)
3. Go to "Network" tab
4. Refresh page

**✅ Verification**: 
- CSS file loaded (style.css, status 200)
- JS file loaded (main.js, status 200)
- No red "404" or "500" errors

---

## 2. Database Tests

### Test 2.1: Create Admin User

```bash
# Windows
venv\Scripts\activate
python run.py create_admin

# macOS/Linux
source venv/bin/activate
python run.py create_admin
```

Follow prompts (example):
```
Username: admin
Email: admin@ecofeast.com
Password: Admin@12345
```

**✅ Verification**: "Admin user created successfully" message

---

### Test 2.2: Verify Database Tables

```bash
# Connect to database
psql -U postgres -d ecofeast_dev

# List tables
\dt
```

**✅ Verification**: See these tables:
```
audit_logs
deliveries
feedback
food_requests
notifications
users
donations
```

Exit with `\q`

---

### Test 2.3: Query User Data

```bash
# In psql prompt
SELECT id, username, role, is_verified FROM users;
```

**✅ Verification**: See admin user you just created

---

## 3. Authentication Tests

### Test 3.1: Admin Login

1. Go to http://localhost:5000/auth/login
2. Enter:
   - Username: `admin`
   - Password: `Admin@12345`
3. Click "Login"

**✅ Verification**: Redirected to `/admin/dashboard`

---

### Test 3.2: Create Donor Account

1. Go to http://localhost:5000/auth/register
2. Fill form:
   - Username: `testdonor`
   - Email: `donor@test.com`
   - Full Name: `Test Donor`
   - Phone: `9876543210`
   - Role: **Restaurant/Hotel/Donor**
   - Address: `123 Main Street`
   - City: `Delhi`
   - Password: `TestDonor@123`
3. Click "Register"

**✅ Verification**: 
- Account created
- Auto-logged in
- Redirected to `/donor/dashboard`

---

### Test 3.3: Create NGO Account

1. Click Logout (top right)
2. Go to http://localhost:5000/auth/register
3. Fill form:
   - Username: `testngo`
   - Email: `ngo@test.com`
   - Full Name: `Test NGO`
   - Phone: `9876543211`
   - Role: **NGO**
   - Organization Name: `Test NGO Foundation`
   - Registration Number: `12345ABC`
   - City: `Delhi`
   - Password: `TestNGO@123`
4. Click "Register"

**✅ Verification**: 
- Account created
- Shows message: "Account pending admin approval"
- Cannot access dashboard yet

---

### Test 3.4: Admin Approves NGO

1. Login as admin (admin / Admin@12345)
2. Go to `/admin/manage_users`
3. Find "testngo"
4. Click "Approve" button

**✅ Verification**: 
- User status changes to "Verified"
- NGO can now login

---

## 4. Donation Workflow Tests

### Test 4.1: Donor Creates Listing

1. Login as testdonor
2. Go to `/donor/dashboard`
3. Click "Create New Listing"
4. Fill form:
   - Food Type: `Rice & Vegetables`
   - Quantity (packets): `50`
   - Description: `Fresh vegetables from restaurant`
   - Expiry Time: `Tomorrow 8:00 PM`
   - Pickup Date: `Today`
   - Pickup Time: `3:00 PM`
   - Address: `123 Main Street, Delhi`
5. **Click on map to set location** (map appears below form)
6. Click "Create Listing"

**✅ Verification**:
- Success message: "Donation created successfully"
- Listing appears in "My Listings" table
- Status shows: "PENDING"

---

### Test 4.2: Admin Approves Donation

1. Logout and login as admin
2. Go to `/admin/manage_donations`
3. Find the "Rice & Vegetables" donation (status: PENDING)
4. Click "Approve" button
5. In modal, enter reason: `Verified and ready for distribution`

**✅ Verification**:
- Donation status changes to "APPROVED"
- Notification sent to donor

---

### Test 4.3: Verify Notification

1. Logout and login as testdonor
2. Top right navbar shows notification icon with number
3. Click notification icon

**✅ Verification**:
- See notification: "Your donation has been approved"
- Shows timestamp

---

## 5. Request Workflow Tests

### Test 5.1: NGO Browses Listings

1. Logout and login as testngo (wait 10 seconds for session)
2. Go to `/ngo/dashboard`
3. Click "Browse Food"

**✅ Verification**:
- See "Rice & Vegetables" donation card
- Shows: quantity, expiry, city, distance
- "View Details" button available

---

### Test 5.2: NGO Requests Food

1. Click "View Details" on Rice donation
2. Fill in amount: `20` (packets)
3. Click "Request This Food"

**✅ Verification**:
- Success message: "Request submitted"
- Request appears in NGO dashboard with status "PENDING"
- Admin receives notification

---

### Test 5.3: Admin Approves Request

1. Logout and login as admin
2. Go to `/admin/manage_requests`
3. Find request from testngo
4. Click "Approve"
5. Select logistics: (click dropdown to select)
6. Click confirm

**✅ Verification**:
- Request status changes to "APPROVED"
- Delivery created
- Logistics volunteer assigned

---

## 6. Map & Geolocation Tests

### Test 6.1: Map Loads

1. Login as testdonor
2. Go to `/donor/dashboard`
3. Click "Create New Listing"
4. Scroll down to find map

**✅ Verification**:
- Google Map loads
- Default center is Delhi (or your location)
- Can see street names
- Zoom/pan works

---

### Test 6.2: Location Picker Works

1. (Same listing creation page)
2. Click on map somewhere
3. Scroll to see coordinates

**✅ Verification**:
- Red marker appears where you clicked
4. Form fields populate with latitude/longitude
5. Form shows clicked address

---

### Test 6.3: Delivery Map

1. Create a complete donation → request → approval → logistics assignment flow
2. Login as logistics user
3. Go to `/logistics/dashboard`
4. Click on assigned delivery

**✅ Verification**:
- Map loads
- Two markers show: pickup (green) and delivery (red) locations
- "Route" information visible
- "Confirm Pickup" button available

---

## 7. Admin Dashboard Tests

### Test 7.1: Dashboard Statistics

1. Login as admin
2. Go to `/admin/dashboard`

**✅ Verification**: See all stat cards:
- [ ] Total Donations: Shows number
- [ ] Total Users: Shows number
- [ ] Total NGOs: Shows number
- [ ] Total Donors: Shows number
- [ ] Deliveries Completed: Shows number
- [ ] Success Rate: Shows percentage
- [ ] Packets Delivered: Shows number
- [ ] Total Delivery Count: Shows number

---

### Test 7.2: Quick Actions

1. Same admin dashboard

**✅ Verification**: Three cards showing:
- [ ] Pending User Approvals (+ count)
- [ ] Pending Donation Approvals (+ count)
- [ ] Pending Request Approvals (+ count)

---

### Test 7.3: Analytics Reports

1. Go to `/admin/reports`

**✅ Verification**:
- [ ] Line chart loads (Daily Food Donations - last 30 days)
- [ ] Bar chart loads (NGO Distribution by Organization)
- [ ] Charts are responsive
- [ ] Charts update data correctly

---

## 8. User Management Tests

### Test 8.1: Approve Users

1. Go to `/admin/manage_users`

**✅ Verification**:
- [ ] All users listed in table
- [ ] Columns show: Username, Email, Role, Status
- [ ] "Approve" button for unverified users
- [ ] "Deactivate" button for active users
- [ ] Can filter by role (ALL, DONOR, NGO, LOGISTICS)

---

### Test 8.2: User Actions

1. Find an unverified user
2. Click "Approve"

**✅ Verification**:
- [ ] Status changes to "Verified"
- [ ] User can now login
- [ ] Notification sent to user

---

## 9. Notification Tests

### Test 9.1: Notifications Polling

1. Open app in two browser tabs/windows
   - Tab A: Admin account
   - Tab B: Donor account

2. In Tab A: Create a donation and approve it
3. In Tab B: Open notifications within 30 seconds

**✅ Verification**:
- [ ] Notification appears in Tab B
- [ ] Shows timestamp
- [ ] Can mark as read

---

### Test 9.2: Notification Types

**✅ Verify you receive notifications for:**
- [ ] Donation approved
- [ ] Request approved
- [ ] Pickup confirmed
- [ ] Delivery confirmed
- [ ] User account approved

---

## 10. Responsive Design Tests

### Test 10.1: Desktop (1920x1080)

1. Open http://localhost:5000
2. Press F12 (Developer Tools)
3. Click responsive design button

**✅ Verification**:
- [ ] All text readable
- [ ] Buttons clickable
- [ ] Images responsive
- [ ] No horizontal scroll
- [ ] Navigation works

---

### Test 10.2: Tablet (768px)

1. Select tablet size from responsive mode
2. Refresh

**✅ Verification**:
- [ ] Single column layout for content
- [ ] Dashboard sidebar hidden
- [ ] Hamburger menu appears
- [ ] Buttons touch-sized

---

### Test 10.3: Mobile (480px)

1. Select mobile size from responsive mode
2. Refresh

**✅ Verification**:
- [ ] Full width layout
- [ ] Large touch targets
- [ ] Text size readable
- [ ] No horizontal scroll
- [ ] Map works on mobile

---

## 11. Form Validation Tests

### Test 11.1: Password Validation

1. Go to `/auth/register`
2. Try these passwords:

| Password | Expected | Result |
|----------|----------|--------|
| `pass` | ❌ Too short | Error shown |
| `password` | ❌ No uppercase | Error shown |
| `PASSWORD` | ❌ No lowercase | Error shown |
| `Password1` | ❌ No special char | Error shown |
| `Password@1` | ✅ Valid | Accepted |

**✅ Verification**: Only valid password accepted

---

### Test 11.2: Email Validation

1. Go to `/auth/register`
2. Try these emails:

| Email | Expected | Result |
|-------|----------|--------|
| `test` | ❌ Invalid | Error shown |
| `test@` | ❌ Invalid | Error shown |
| `test@example.com` | ✅ Valid | Accepted |

---

## 12. API Endpoint Tests

### Test 12.1: Distance Calculation

```bash
curl -X POST http://localhost:5000/api/distance \
  -H "Content-Type: application/json" \
  -d '{
    "lat1": 28.6139,
    "lon1": 77.2090,
    "lat2": 28.7041,
    "lon2": 77.1025
  }'
```

**✅ Verification**: Returns distance in km

---

### Test 12.2: Donation Search

```bash
curl http://localhost:5000/api/search/donations?query=rice&city=delhi&page=1
```

**✅ Verification**: Returns JSON with donations

---

### Test 12.3: Dashboard Stats

```bash
curl http://localhost:5000/api/stats/dashboard
```

**✅ Verification**: Returns JSON with statistics

---

## 13. Error Handling Tests

### Test 13.1: 404 Error

1. Go to http://localhost:5000/nonexistent-page

**✅ Verification**: 
- [ ] "Page Not Found" page shown
- [ ] Error code: 404
- [ ] Link to homepage available

---

### Test 13.2: 403 Error

1. Login as testdonor
2. Try to access http://localhost:5000/admin/dashboard

**✅ Verification**:
- [ ] "Access Denied" page shown
- [ ] Error code: 403
- [ ] Redirected to home

---

### Test 13.3: Database Error Handling

1. Stop PostgreSQL service
2. Go to http://localhost:5000/admin/dashboard

**✅ Verification**:
- [ ] Error page shown (not blank page)
- [ ] "Database connection error" message
- [ ] Can still navigate to other pages

---

## 14. Performance Tests

### Test 14.1: Page Load Time

1. Open http://localhost:5000
2. Press F12 → Network tab
3. Refresh

**✅ Verification**:
- [ ] Page loads in < 2 seconds
- [ ] No failed requests (404, 500)
- [ ] Images load properly

---

### Test 14.2: Database Query Performance

```bash
# Login to database
psql -U postgres -d ecofeast_dev

# Test index usage
EXPLAIN SELECT * FROM users WHERE id = 1;
```

**✅ Verification**: Query uses "Index Scan" (not Seq Scan)

---

## 15. Security Tests

### Test 15.1: Password Hashing

```bash
# In Python console
from app import db
from app.models import User

user = User.query.first()
print(user.password_hash[:20])  # Should show bcrypt hash
```

**✅ Verification**: 
- [ ] Hash starts with `$2b` (bcrypt indicator)
- [ ] Not storing plain text password

---

### Test 15.2: Session Management

1. Login to application
2. Close browser
3. Reopen browser
4. Navigate to protected page

**✅ Verification**:
- [ ] Redirected to login page
- [ ] Session cleared

---

### Test 15.3: SQL Injection Prevention

1. Go to `/ngo/browse`
2. In search box, enter: `' OR '1'='1`
3. Search

**✅ Verification**:
- [ ] No SQL error shown
- [ ] Treated as search term
- [ ] No results found (expected)

---

## Final Verification Checklist

- [ ] All 15 test categories passed
- [ ] No error messages in console (F12 → Console)
- [ ] No 404 or 500 errors in network tab
- [ ] Database connections working
- [ ] Maps loading
- [ ] Forms validating
- [ ] Notifications working
- [ ] Responsive design responsive
- [ ] Auth flows complete
- [ ] Admin functions working

---

## Troubleshooting Test Failures

### "Map not loading"
- Check Google Maps API key in .env
- Verify API key has JavaScript Maps API enabled
- Check browser console for errors

### "Database connection failed"
- Verify PostgreSQL is running
- Check DATABASE_URL in .env matches actual setup
- Verify username/password correct

### "Notifications not appearing"
- Check browser console (F12) for JavaScript errors
- Verify app running with no errors in terminal
- Try refreshing page manually

### "Forms not submitting"
- Check browser console for JavaScript errors
- Verify form fields have correct names
- Try clearing cache (Ctrl+Shift+Delete)

---

**All tests passing? 🎉 Your ECOFEAST installation is complete and ready to use!**

For issues, check [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) Troubleshooting section.
