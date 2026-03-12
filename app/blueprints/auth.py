from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.models import db, User, Role, DonorType, Notification
from datetime import datetime
import re
import math
import urllib.parse
import urllib.request
import json
import random
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def geocode_address(address, city=''):
    """Geocode an address using Nominatim with progressive simplification"""
    import time
    
    # Build queries from most specific to most general
    queries = []
    full_query = f"{address}, {city}" if city else address
    queries.append(full_query)
    
    # Simplify: remove floor/plot/building details
    simplified = re.sub(r'\d+(st|nd|rd|th)\s*floor\b', '', address, flags=re.IGNORECASE)
    simplified = re.sub(r'\bfloor\s*\d+', '', simplified, flags=re.IGNORECASE)
    simplified = re.sub(r'\bplot\s*(no\.?:?\s*)?[\w\-]+,?\s*', '', simplified, flags=re.IGNORECASE)
    simplified = re.sub(r'\bdoor\s*(no\.?:?\s*)?[\w\-]+,?\s*', '', simplified, flags=re.IGNORECASE)
    simplified = re.sub(r'\bflat\s*(no\.?:?\s*)?[\w\-]+,?\s*', '', simplified, flags=re.IGNORECASE)
    simplified = re.sub(r'\b\d+[-/]\d+[-/]?\d*,?\s*', '', simplified)
    simplified = re.sub(r',\s*,', ',', simplified).strip().strip(',').strip()
    if simplified != address:
        queries.append(f"{simplified}, {city}" if city else simplified)
    
    # Try just the last 2-3 parts (area/locality + city)
    parts = [p.strip() for p in address.split(',') if p.strip()]
    if len(parts) > 2:
        area = ', '.join(parts[-2:])
        if city and city.lower() not in area.lower():
            area += f', {city}'
        queries.append(area)
    
    # City as last resort
    if city:
        queries.append(f'{city}, India')
    
    for query in queries:
        params = urllib.parse.urlencode({'format': 'json', 'q': query, 'limit': 1, 'countrycodes': 'in'})
        url = f'https://nominatim.openstreetmap.org/search?{params}'
        req = urllib.request.Request(url, headers={'User-Agent': 'EXCESSBITE/1.0', 'Accept-Language': 'en'})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                if data and len(data) > 0:
                    return float(data[0]['lat']), float(data[0]['lon'])
        except Exception as e:
            print(f'Geocoding failed for "{query}": {e}')
        time.sleep(1)  # Nominatim rate limit: 1 req/sec
    
    return None, None

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special char
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Valid"

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        data = request.form
        
        # Validation
        errors = []
        
        if not data.get('username'):
            errors.append('Username is required')
        elif len(data.get('username', '')) < 3:
            errors.append('Username must be at least 3 characters')
        elif User.query.filter_by(username=data.get('username')).first():
            errors.append('Username already exists')
        
        if not data.get('email'):
            errors.append('Email is required')
        elif not validate_email(data.get('email', '')):
            errors.append('Invalid email format')
        elif User.query.filter_by(email=data.get('email')).first():
            errors.append('Email already registered')
        
        if not data.get('password'):
            errors.append('Password is required')
        else:
            valid, msg = validate_password(data.get('password', ''))
            if not valid:
                errors.append(msg)
        
        if data.get('password') != data.get('password_confirm'):
            errors.append('Passwords do not match')
        
        if not data.get('full_name'):
            errors.append('Full name is required')
        
        if not data.get('phone'):
            errors.append('Phone number is required')
        
        if not data.get('role') or data.get('role') not in Role.ALL_ROLES:
            errors.append('Invalid role selected')
        
        # Donor-type-specific validation
        donor_type = data.get('donor_type', '')
        if data.get('role') == Role.DONOR:
            if not donor_type or donor_type not in DonorType.ALL_TYPES:
                errors.append('Please select a donor type')
            elif donor_type == DonorType.RESTAURANT:
                if not request.files.get('verification_document'):
                    errors.append('FSSAI license document is required for restaurant/hotel donors')
            elif donor_type == DonorType.COMPANY:
                if not request.files.get('verification_document'):
                    errors.append('GST certificate or business proof is required for company donors')
            elif donor_type == DonorType.INDIVIDUAL:
                if not session.get('phone_otp_verified'):
                    errors.append('Phone OTP verification is required for individual donors')
        
        # NGO document validation
        ngo_doc_type = data.get('ngo_document_type', '')
        ngo_doc_types_allowed = ['ngo_registration', 'trust_society', '80g_12a', 'government_id']
        if data.get('role') == Role.NGO:
            if not request.files.get('ngo_document'):
                errors.append('Please upload a verification document (NGO Registration Certificate, Trust/Society doc, 80G/12A Certificate, or Government NGO ID)')
            if not ngo_doc_type or ngo_doc_type not in ngo_doc_types_allowed:
                errors.append('Please select the type of document you are uploading')
        
        # Logistics volunteer validation
        govt_id_type = data.get('government_id_type', '')
        govt_id_types_allowed = ['aadhar', 'driving_license']
        if data.get('role') == Role.LOGISTICS:
            if not govt_id_type or govt_id_type not in govt_id_types_allowed:
                errors.append('Please select a Government ID type (Aadhar or Driving License)')
            if not request.files.get('government_id_document'):
                errors.append('Government ID document is required for logistics volunteers')
            if not request.files.get('profile_photo'):
                errors.append('Profile photo is required for logistics volunteers')
        
        if errors:
            return render_template('register.html', errors=errors, roles=Role.ALL_ROLES, donor_types=DonorType), 400
        
        # Handle document upload for donors and NGOs
        doc_path = None
        needs_doc = (
            (data.get('role') == Role.DONOR and donor_type in (DonorType.RESTAURANT, DonorType.COMPANY))
            or data.get('role') == Role.NGO
        )
        if needs_doc:
            file = request.files.get('ngo_document') if data.get('role') == Role.NGO else request.files.get('verification_document')
            if file and file.filename:
                from werkzeug.utils import secure_filename
                allowed_ext = {'pdf', 'jpg', 'jpeg', 'png'}
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                if ext not in allowed_ext:
                    return render_template('register.html', 
                                         errors=['Document must be PDF, JPG, or PNG'], 
                                         roles=Role.ALL_ROLES, donor_types=DonorType), 400
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
                os.makedirs(upload_dir, exist_ok=True)
                prefix = donor_type if data.get('role') == Role.DONOR else 'ngo'
                safe_name = secure_filename(f"{data.get('username')}_{prefix}_{file.filename}")
                file.save(os.path.join(upload_dir, safe_name))
                doc_path = f"uploads/documents/{safe_name}"
        
        # Handle logistics volunteer file uploads
        govt_id_path = None
        profile_photo_path = None
        if data.get('role') == Role.LOGISTICS:
            from werkzeug.utils import secure_filename
            allowed_ext = {'pdf', 'jpg', 'jpeg', 'png'}
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Government ID
            govt_file = request.files.get('government_id_document')
            if govt_file and govt_file.filename:
                ext = govt_file.filename.rsplit('.', 1)[-1].lower() if '.' in govt_file.filename else ''
                if ext not in allowed_ext:
                    return render_template('register.html',
                                         errors=['Government ID must be PDF, JPG, or PNG'],
                                         roles=Role.ALL_ROLES, donor_types=DonorType), 400
                safe_name = secure_filename(f"{data.get('username')}_govtid_{govt_file.filename}")
                govt_file.save(os.path.join(upload_dir, safe_name))
                govt_id_path = f"uploads/documents/{safe_name}"
            
            # Profile Photo
            photo_file = request.files.get('profile_photo')
            if photo_file and photo_file.filename:
                photo_ext = photo_file.filename.rsplit('.', 1)[-1].lower() if '.' in photo_file.filename else ''
                if photo_ext not in {'jpg', 'jpeg', 'png'}:
                    return render_template('register.html',
                                         errors=['Profile photo must be JPG or PNG'],
                                         roles=Role.ALL_ROLES, donor_types=DonorType), 400
                safe_name = secure_filename(f"{data.get('username')}_photo_{photo_file.filename}")
                photo_file.save(os.path.join(upload_dir, safe_name))
                profile_photo_path = f"uploads/documents/{safe_name}"
        
        # Create new user
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            full_name=data.get('full_name'),
            phone=data.get('phone'),
            role=data.get('role'),
            address=data.get('address', ''),
            city=data.get('city', ''),
            latitude=float(data.get('latitude')) if data.get('latitude') else None,
            longitude=float(data.get('longitude')) if data.get('longitude') else None,
            organization_name=data.get('organization_name', ''),
            organization_type=data.get('organization_type', ''),
            donor_type=donor_type if data.get('role') == Role.DONOR else None,
            verification_document=doc_path,
            phone_verified=(donor_type == DonorType.INDIVIDUAL and session.get('phone_otp_verified', False)) if data.get('role') == Role.DONOR else False,
            ngo_document_type=ngo_doc_type if data.get('role') == Role.NGO else None,
            government_id_type=govt_id_type if data.get('role') == Role.LOGISTICS else None,
            government_id_document=govt_id_path,
            profile_photo=profile_photo_path,
            vehicle_details=data.get('vehicle_details', '') if data.get('role') == Role.LOGISTICS else None,
        )
        
        # For NGOs: always geocode from their typed address to ensure accuracy
        if user.role == Role.NGO and user.address:
            geo_lat, geo_lng = geocode_address(user.address, user.city)
            if geo_lat is not None and geo_lng is not None:
                user.latitude = geo_lat
                user.longitude = geo_lng
        
        user.set_password(data.get('password'))
        
        # Verification logic based on donor type
        if user.role == Role.DONOR:
            if user.donor_type == DonorType.INDIVIDUAL:
                # Individual donors are auto-verified after OTP
                user.is_verified = True
                user.verification_date = datetime.now()
            else:
                # Restaurant/Company donors need admin document verification
                user.is_verified = False
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Create notification for admin if verification needed
            if not user.is_verified:
                admin_users = User.query.filter_by(role=Role.ADMIN).all()
                for admin in admin_users:
                    if user.role == Role.DONOR:
                        msg = f'{user.full_name} ({user.email}) registered as {user.donor_type} donor — document verification required'
                    elif user.role == Role.NGO:
                        doc_label = {'ngo_registration': 'NGO Registration Certificate', 'trust_society': 'Trust/Society Document', '80g_12a': '80G/12A Certificate', 'government_id': 'Government NGO ID'}.get(user.ngo_document_type, 'document')
                        msg = f'{user.full_name} ({user.organization_name}) registered as NGO — uploaded {doc_label} for verification'
                    elif user.role == Role.LOGISTICS:
                        id_label = {'aadhar': 'Aadhar Card', 'driving_license': 'Driving License'}.get(user.government_id_type, 'Government ID')
                        msg = f'{user.full_name} ({user.email}) registered as Logistics Volunteer — uploaded {id_label} for verification'
                    else:
                        msg = f'{user.full_name} ({user.email}) registered as {user.role}'
                    notification = Notification(
                        user_id=admin.id,
                        title=f'New {user.role.upper()} Registration',
                        message=msg,
                        notification_type='registration',
                        related_id=user.id
                    )
                    db.session.add(notification)
                db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            # Clear OTP session data
            session.pop('phone_otp', None)
            session.pop('phone_otp_verified', None)
            session.pop('phone_otp_number', None)
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', errors=['Registration failed. Please try again.'], roles=Role.ALL_ROLES, donor_types=DonorType), 500
    
    return render_template('register.html', roles=Role.ALL_ROLES, donor_types=DonorType)

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Generate and send OTP for phone verification (individual donors)"""
    data = request.get_json()
    phone = data.get('phone', '').strip()
    
    if not phone or len(phone) < 10:
        return jsonify({'error': 'Valid phone number is required'}), 400
    
    otp = str(random.randint(100000, 999999))
    session['phone_otp'] = otp
    session['phone_otp_number'] = phone
    session['phone_otp_verified'] = False
    
    # In production, integrate an SMS gateway (Twilio, MSG91, etc.) here.
    # For development, the OTP is returned in the response.
    if current_app.debug:
        return jsonify({'success': True, 'message': 'OTP sent to your phone', 'debug_otp': otp})
    
    return jsonify({'success': True, 'message': 'OTP sent to your phone'})

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify phone OTP"""
    data = request.get_json()
    entered_otp = data.get('otp', '').strip()
    
    stored_otp = session.get('phone_otp')
    if not stored_otp:
        return jsonify({'error': 'No OTP was sent. Please request a new one.'}), 400
    
    if entered_otp == stored_otp:
        session['phone_otp_verified'] = True
        return jsonify({'success': True, 'message': 'Phone verified successfully'})
    
    return jsonify({'error': 'Invalid OTP. Please try again.'}), 400

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Username and password required'), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return render_template('login.html', error='Invalid username or password'), 401
        
        if not user.check_password(password):
            return render_template('login.html', error='Invalid username or password'), 401
        
        if not user.is_active:
            return render_template('login.html', error='Your account has been deactivated'), 401
        
        login_user(user, remember=data.get('remember', False))
        
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        
        # Redirect based on role
        if user.role == Role.ADMIN:
            return redirect(url_for('admin.dashboard'))
        elif user.role == Role.DONOR:
            return redirect(url_for('donor.dashboard'))
        elif user.role == Role.NGO:
            return redirect(url_for('ngo.dashboard'))
        elif user.role == Role.LOGISTICS:
            return redirect(url_for('logistics.dashboard'))
        
        return redirect(url_for('main.home'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile"""
    if request.method == 'POST':
        data = request.form
        
        # Update user profile
        current_user.full_name = data.get('full_name', current_user.full_name)
        current_user.phone = data.get('phone', current_user.phone)
        current_user.address = data.get('address', current_user.address)
        current_user.city = data.get('city', current_user.city)
        
        # Update location if provided
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if latitude and longitude:
            try:
                current_user.latitude = float(latitude)
                current_user.longitude = float(longitude)
            except ValueError:
                pass  # Ignore invalid coordinates
        
        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update profile', 'error')
    
    return render_template('profile.html', user=current_user)
