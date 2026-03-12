from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt
from datetime import datetime

db = SQLAlchemy()

class Role:
    """Role constants"""
    ADMIN = 'admin'
    DONOR = 'donor'
    NGO = 'ngo'
    LOGISTICS = 'logistics'
    
    ALL_ROLES = [ADMIN, DONOR, NGO, LOGISTICS]

class DonorType:
    """Donor type constants — each type has different verification"""
    RESTAURANT = 'restaurant'
    COMPANY = 'company'
    INDIVIDUAL = 'individual'
    
    ALL_TYPES = [RESTAURANT, COMPANY, INDIVIDUAL]
    
    LABELS = {
        RESTAURANT: 'Restaurant / Hotel / Supermarket',
        COMPANY: 'Company / Corporate / Event Organizer',
        INDIVIDUAL: 'Individual Donor',
    }

class DonationStatus:
    """Donation status constants"""
    PENDING = 'pending'
    APPROVED = 'approved'
    ASSIGNED = 'assigned'
    PICKED_UP = 'picked_up'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'
    
    ALL_STATUSES = [PENDING, APPROVED, ASSIGNED, PICKED_UP, DELIVERED, CANCELLED, EXPIRED]

class User(UserMixin, db.Model):
    """User model with role-based access control"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Role.DONOR)
    
    # Profile information
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(100), index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Organization details (for NGO and Logistics)
    organization_name = db.Column(db.String(200))
    organization_type = db.Column(db.String(100))  # NGO type, Logistics volunteer, etc.
    registration_number = db.Column(db.String(100))
    
    # Donor-specific fields
    donor_type = db.Column(db.String(30))  # restaurant, company, individual
    verification_document = db.Column(db.String(500))  # uploaded doc path (FSSAI / GST / NGO doc)
    phone_verified = db.Column(db.Boolean, default=False)  # OTP-verified phone for individuals
    ngo_document_type = db.Column(db.String(50))  # type of NGO document uploaded
    
    # Logistics volunteer-specific fields
    government_id_type = db.Column(db.String(30))  # aadhar, driving_license
    government_id_document = db.Column(db.String(500))  # uploaded govt ID doc path
    profile_photo = db.Column(db.String(500))  # uploaded profile photo path
    vehicle_details = db.Column(db.String(200))  # e.g. Bike, Car, Auto
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_date = db.Column(db.DateTime)
    deactivation_reason = db.Column(db.Text)
    deactivation_date = db.Column(db.DateTime)
    
    # Logistics availability (only relevant for logistics volunteers)
    is_available = db.Column(db.Boolean, default=True, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    donations = db.relationship('Donation', backref='donor', lazy='dynamic', foreign_keys='Donation.donor_id')
    requests = db.relationship('FoodRequest', backref='ngo', lazy='dynamic', foreign_keys='FoodRequest.ngo_id')
    deliveries = db.relationship('Delivery', backref='logistics', lazy='dynamic', foreign_keys='Delivery.logistics_id')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    feedback_given = db.relationship('Feedback', lazy='dynamic', foreign_keys='Feedback.from_user_id', backref='from_user')
    feedback_received = db.relationship('Feedback', lazy='dynamic', foreign_keys='Feedback.to_user_id', backref='to_user')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def __repr__(self):
        return f'<User {self.username}>'

class Donation(db.Model):
    """Food donation listing"""
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Food details
    food_type = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)  # Number of packets
    available_quantity = db.Column(db.Integer)  # Remaining available packets
    unit = db.Column(db.String(50), default='packets')  # packets, kg, etc.
    
    # Expiry and pickup details
    expiry_time = db.Column(db.DateTime, nullable=False)
    pickup_date = db.Column(db.Date, nullable=False, index=True)
    pickup_start_time = db.Column(db.Time, nullable=False)
    pickup_end_time = db.Column(db.Time, nullable=False)
    
    # Location details
    pickup_address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(100), index=True)
    contact_number = db.Column(db.String(20), nullable=False)
    
    # Status tracking
    status = db.Column(db.String(50), default=DonationStatus.PENDING, index=True)
    admin_notes = db.Column(db.Text)
    
    # Image storage (file path or URL)
    image_url = db.Column(db.String(500))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    approved_at = db.Column(db.DateTime)
    
    # Relationships
    requests = db.relationship('FoodRequest', backref='donation', lazy='dynamic', cascade='all, delete-orphan')
    deliveries = db.relationship('Delivery', backref='donation', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='donation', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Donation {self.id}>'

class FoodRequest(db.Model):
    """NGO request for food"""
    __tablename__ = 'food_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id'), nullable=False, index=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Request details
    requested_quantity = db.Column(db.Integer, nullable=False)
    special_requirements = db.Column(db.Text)
    
    # Status tracking
    status = db.Column(db.String(50), default='pending', index=True)  # pending, approved, rejected
    admin_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    approved_at = db.Column(db.DateTime)
    
    __table_args__ = (db.UniqueConstraint('donation_id', 'ngo_id', name='unique_donation_ngo_request'),)
    
    def __repr__(self):
        return f'<FoodRequest {self.id}>'

class Delivery(db.Model):
    """Delivery tracking"""
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id'), nullable=False, index=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    logistics_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Delivery details
    pickup_id = db.Column(db.String(20), unique=True, index=True)  # e.g. EXB-1023
    pickup_otp = db.Column(db.String(6))  # OTP for donor to confirm pickup
    delivery_otp = db.Column(db.String(6))  # OTP for NGO to confirm delivery
    status = db.Column(db.String(50), default='assigned', index=True)
    pickup_confirmation_image = db.Column(db.String(500))
    delivery_confirmation_image = db.Column(db.String(500))
    
    # Tracking
    pickup_time = db.Column(db.DateTime)
    delivery_time = db.Column(db.DateTime)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # NGO relationship
    __table_args__ = (
        db.ForeignKeyConstraint(['ngo_id'], ['users.id']),
    )
    
    ngo_recipient = db.relationship('User', foreign_keys=[ngo_id], backref='received_deliveries')
    
    def __repr__(self):
        return f'<Delivery {self.id}>'

class Notification(db.Model):
    """In-app notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Notification content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # donation, request, delivery, approval, etc.
    
    # Reference to related object
    related_id = db.Column(db.Integer)  # donation_id, request_id, delivery_id, etc.
    
    # Status
    is_read = db.Column(db.Boolean, default=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    
    def __repr__(self):
        return f'<Notification {self.id}>'

class FeedbackType:
    """Feedback type constants for the directional feedback flow"""
    DONOR_TO_NGO = 'donor_to_ngo'
    DONOR_TO_VOLUNTEER = 'donor_to_volunteer'
    NGO_TO_DONOR = 'ngo_to_donor'
    NGO_TO_VOLUNTEER = 'ngo_to_volunteer'
    VOLUNTEER_TO_DONOR = 'volunteer_to_donor'
    VOLUNTEER_TO_NGO = 'volunteer_to_ngo'

    ALL_TYPES = [
        DONOR_TO_NGO, DONOR_TO_VOLUNTEER,
        NGO_TO_DONOR, NGO_TO_VOLUNTEER,
        VOLUNTEER_TO_DONOR, VOLUNTEER_TO_NGO
    ]

    LABELS = {
        DONOR_TO_NGO: 'Rate how quickly the NGO responded and handled the food donation',
        DONOR_TO_VOLUNTEER: 'Rate the pickup experience and professionalism',
        NGO_TO_DONOR: 'Rate food quality, packaging, and reliability of the donor',
        NGO_TO_VOLUNTEER: 'Rate delivery behavior and punctuality',
        VOLUNTEER_TO_DONOR: 'Report food condition and pickup coordination',
        VOLUNTEER_TO_NGO: 'Report cooperation and communication during delivery',
    }


class Feedback(db.Model):
    """Directional feedback between users involved in a donation delivery"""
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('deliveries.id'), nullable=False, index=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id'), nullable=False, index=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    feedback_type = db.Column(db.String(50), nullable=False)  # e.g. donor_to_ngo

    # Feedback details
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    # Prevent duplicate feedback for same pair on same delivery
    __table_args__ = (
        db.UniqueConstraint('delivery_id', 'from_user_id', 'to_user_id', name='unique_delivery_feedback'),
    )

    delivery = db.relationship('Delivery', backref=db.backref('feedbacks', lazy='dynamic'))

    def __repr__(self):
        return f'<Feedback {self.id} {self.feedback_type}>'

class ContactMessage(db.Model):
    """Contact form messages sent to admin"""
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    
    def __repr__(self):
        return f'<ContactMessage {self.id}>'

class AuditLog(db.Model):
    """Audit log for admin actions"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    admin = db.relationship('User', foreign_keys=[admin_id], backref='audit_logs')
    
    # Action details
    action = db.Column(db.String(200), nullable=False)
    entity_type = db.Column(db.String(100))
    entity_id = db.Column(db.Integer)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    
    def __repr__(self):
        return f'<AuditLog {self.id}>'
