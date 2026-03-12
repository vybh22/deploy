from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from app.models import db, User, Role, Donation, DonationStatus
from config import config
import os
from datetime import datetime

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create tables
    with app.app_context():
        db.create_all()
        # Add is_available column if it doesn't exist (for existing databases)
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        if 'is_available' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN is_available BOOLEAN DEFAULT TRUE'))
            db.session.commit()
        # Add donor verification columns if they don't exist
        if 'donor_type' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN donor_type VARCHAR(30)'))
            db.session.commit()
        if 'verification_document' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN verification_document VARCHAR(500)'))
            db.session.commit()
        if 'phone_verified' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN phone_verified BOOLEAN DEFAULT FALSE'))
            db.session.commit()
        if 'ngo_document_type' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN ngo_document_type VARCHAR(50)'))
            db.session.commit()
        # Add logistics volunteer columns
        if 'government_id_type' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN government_id_type VARCHAR(30)'))
            db.session.commit()
        if 'government_id_document' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN government_id_document VARCHAR(500)'))
            db.session.commit()
        if 'profile_photo' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN profile_photo VARCHAR(500)'))
            db.session.commit()
        if 'vehicle_details' not in columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN vehicle_details VARCHAR(200)'))
            db.session.commit()
        # Add delivery verification columns
        delivery_columns = [col['name'] for col in inspector.get_columns('deliveries')]
        if 'pickup_id' not in delivery_columns:
            db.session.execute(text('ALTER TABLE deliveries ADD COLUMN pickup_id VARCHAR(20)'))
            db.session.commit()
        if 'pickup_otp' not in delivery_columns:
            db.session.execute(text('ALTER TABLE deliveries ADD COLUMN pickup_otp VARCHAR(10)'))
            db.session.commit()
        if 'delivery_otp' not in delivery_columns:
            db.session.execute(text('ALTER TABLE deliveries ADD COLUMN delivery_otp VARCHAR(10)'))
            db.session.commit()
        # Add available_quantity column for partial fulfillment
        donation_columns = [col['name'] for col in inspector.get_columns('donations')]
        if 'available_quantity' not in donation_columns:
            db.session.execute(text('ALTER TABLE donations ADD COLUMN available_quantity INTEGER'))
            # Initialize available_quantity to quantity for existing rows
            db.session.execute(text('UPDATE donations SET available_quantity = quantity WHERE available_quantity IS NULL'))
            db.session.commit()
        # Remove unique constraint on deliveries.donation_id if exists (for partial fulfillment)
        try:
            unique_constraints = inspector.get_unique_constraints('deliveries')
            for uc in unique_constraints:
                if 'donation_id' in uc.get('column_names', []):
                    db.session.execute(text(f'ALTER TABLE deliveries DROP CONSTRAINT {uc["name"]}'))
                    db.session.commit()
                    break
        except Exception:
            db.session.rollback()  # Constraint may not exist or already removed
    
    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.main import main_bp
    from app.blueprints.donor import donor_bp
    from app.blueprints.ngo import ngo_bp
    from app.blueprints.logistics import logistics_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(ngo_bp)
    app.register_blueprint(logistics_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    
    # Auto-expire donations whose expiry_time has passed
    @app.before_request
    def auto_expire_donations():
        try:
            now = datetime.now()
            expired = Donation.query.filter(
                Donation.expiry_time <= now,
                Donation.status.in_([DonationStatus.PENDING, DonationStatus.APPROVED])
            ).all()
            for donation in expired:
                donation.status = DonationStatus.EXPIRED
            if expired:
                db.session.commit()
        except Exception:
            db.session.rollback()

    # Context processor for global template variables
    @app.context_processor
    def inject_global_vars():
        return dict(
            google_maps_key=os.getenv('GOOGLE_MAPS_KEY', ''),
            utcnow=datetime.now()
        )
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Access denied'}, 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app
