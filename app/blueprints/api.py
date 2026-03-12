from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Notification, User, Donation, Delivery
from app.decorators import role_required
from app.models import Role
import math

api_bp = Blueprint('api', __name__, url_prefix='/api')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

@api_bp.route('/notifications/unread')
@login_required
def get_unread_notifications():
    """Get unread notifications for current user"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).all()
    
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.notification_type,
        'related_id': n.related_id,
        'created_at': n.created_at.isoformat()
    } for n in notifications])

@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'error': 'Failed to update notification'}), 500

@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'error': 'Failed to update notifications'}), 500

@api_bp.route('/distance', methods=['POST'])
@login_required
def calculate_route_distance():
    """Calculate distance between two locations"""
    data = request.get_json()
    
    lat1 = data.get('lat1')
    lon1 = data.get('lon1')
    lat2 = data.get('lat2')
    lon2 = data.get('lon2')
    
    if None in [lat1, lon1, lat2, lon2]:
        return jsonify({'error': 'Missing coordinates'}), 400
    
    try:
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        return jsonify({'distance_km': round(distance, 2)})
    except:
        return jsonify({'error': 'Failed to calculate distance'}), 500

@api_bp.route('/search/donations', methods=['GET'])
@login_required
def search_donations():
    """Search available donations"""
    query = request.args.get('q', '')
    city = request.args.get('city', '')
    page = request.args.get('page', 1, type=int)
    
    q = Donation.query.filter_by(status='approved')
    
    if query:
        q = q.filter(
            (Donation.food_type.ilike(f'%{query}%')) |
            (Donation.description.ilike(f'%{query}%'))
        )
    
    if city:
        q = q.filter(Donation.city.ilike(f'%{city}%'))
    
    donations = q.order_by(Donation.created_at.desc()).paginate(page=page, per_page=10)
    
    return jsonify({
        'total': donations.total,
        'pages': donations.pages,
        'current_page': page,
        'donations': [{
            'id': d.id,
            'food_type': d.food_type,
            'quantity': d.quantity,
            'city': d.city,
            'expiry_time': d.expiry_time.isoformat(),
            'donor_name': d.donor.full_name,
            'latitude': d.latitude,
            'longitude': d.longitude
        } for d in donations.items]
    })

@api_bp.route('/logistics/available', methods=['GET'])
@role_required(Role.ADMIN)
def get_available_logistics():
    """Get available logistics volunteers for assignment"""
    logistics_volunteers = User.query.filter_by(
        role=Role.LOGISTICS,
        is_verified=True,
        is_active=True
    ).all()
    
    return jsonify([{
        'id': l.id,
        'name': l.full_name,
        'phone': l.phone,
        'city': l.city,
        'active_deliveries': Delivery.query.filter_by(
            logistics_id=l.id
        ).filter(Delivery.status.in_(['assigned', 'picked_up'])).count()
    } for l in logistics_volunteers])

@api_bp.route('/stats/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics (publicly accessible)"""
    from sqlalchemy import func
    
    total_users = User.query.count()
    total_donors = User.query.filter_by(role=Role.DONOR).count()
    total_ngos = User.query.filter_by(role=Role.NGO).count()
    total_donations = Donation.query.count()
    total_deliveries = Delivery.query.count()
    completed_deliveries = Delivery.query.filter_by(status='delivered').count()
    
    food_statistics = db.session.query(
        func.sum(Donation.quantity),
        func.count(Donation.id)
    ).filter_by(status='delivered').first()
    
    delivered_packets = food_statistics[0] or 0
    delivered_donations = food_statistics[1] or 0
    
    return jsonify({
        'total_users': total_users,
        'total_donors': total_donors,
        'total_ngos': total_ngos,
        'total_donations': total_donations,
        'total_deliveries': total_deliveries,
        'completed_deliveries': completed_deliveries,
        'success_rate': round((completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0, 2),
        'delivered_packets': int(delivered_packets),
        'delivered_donations': delivered_donations,
        'co2_reduction': round(delivered_packets * 0.5 * 1.2, 2)
    })

@api_bp.route('/user/location/update', methods=['POST'])
@login_required
def update_user_location():
    """Update user location (skip NGOs — their location is their registered org address)"""
    if current_user.role == Role.NGO:
        return jsonify({'success': True, 'skipped': True})
    
    data = request.get_json()
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    city = data.get('city', '')
    
    if latitude is None or longitude is None:
        return jsonify({'error': 'Missing coordinates'}), 400
    
    try:
        current_user.latitude = latitude
        current_user.longitude = longitude
        if city:
            current_user.city = city
        db.session.commit()
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'error': 'Failed to update location'}), 500
@api_bp.route('/admin/delivery/<int:delivery_id>/assign', methods=['POST'])
@login_required
@role_required(Role.ADMIN)
def assign_logistics_to_delivery(delivery_id):
    """Assign logistics volunteer to delivery"""
    delivery = Delivery.query.get_or_404(delivery_id)
    
    data = request.get_json()
    logistics_id = data.get('logistics_id')
    
    # Verify logistics volunteer exists, is verified, and is available
    logistics = User.query.filter_by(id=logistics_id, role=Role.LOGISTICS, is_verified=True, is_active=True).first()
    
    if not logistics:
        return jsonify({'error': 'Invalid logistics volunteer'}), 400
    
    if not logistics.is_available:
        return jsonify({'error': 'This logistics volunteer is currently unavailable'}), 400
    
    try:
        delivery.logistics_id = logistics_id
        db.session.commit()
        
        # Notify logistics volunteer
        from app.models import Notification
        notification = Notification(
            user_id=logistics_id,
            title='New Delivery Assigned',
            message=f'A new delivery has been assigned to you: {delivery.donation.food_type}',
            notification_type='assignment',
            related_id=delivery_id
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to assign logistics'}), 500