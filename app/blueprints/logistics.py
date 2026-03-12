from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Delivery, Notification, Role, User, Feedback, FeedbackType, DonationStatus
from app.decorators import role_required
from datetime import datetime
import random

logistics_bp = Blueprint('logistics', __name__, url_prefix='/logistics')

@logistics_bp.route('/dashboard')
@role_required(Role.LOGISTICS)
def dashboard():
    """Logistics dashboard"""
    deliveries = Delivery.query.filter_by(logistics_id=current_user.id).order_by(Delivery.created_at.desc()).all()
    
    stats = {
        'total_assigned': len(deliveries),
        'completed': sum(1 for d in deliveries if d.status == 'delivered'),
        'in_progress': sum(1 for d in deliveries if d.status in ['assigned', 'picked_up']),
        'pending_pickup': sum(1 for d in deliveries if d.status == 'assigned'),
        'failed': sum(1 for d in deliveries if d.status == 'failed')
    }
    
    return render_template('logistics/dashboard.html', deliveries=deliveries, stats=stats)

@logistics_bp.route('/delivery/<int:delivery_id>')
@role_required(Role.LOGISTICS)
def view_delivery(delivery_id):
    """View delivery details with map"""
    delivery = Delivery.query.get_or_404(delivery_id)
    
    if delivery.logistics_id != current_user.id:
        flash('You do not have permission to view this delivery', 'error')
        return redirect(url_for('logistics.dashboard'))
    
    donation = delivery.donation
    donor = donation.donor
    ngo = delivery.ngo_recipient

    # Get existing feedback given by this volunteer for this delivery
    given_feedback = {}
    for fb in Feedback.query.filter_by(delivery_id=delivery.id, from_user_id=current_user.id).all():
        given_feedback[fb.feedback_type] = fb

    return render_template('logistics/view_delivery.html',
                         delivery=delivery,
                         donation=donation,
                         donor=donor,
                         ngo=ngo,
                         given_feedback=given_feedback)

@logistics_bp.route('/delivery/<int:delivery_id>/pickup', methods=['POST'])
@role_required(Role.LOGISTICS)
def confirm_pickup(delivery_id):
    """Confirm pickup with OTP verification"""
    delivery = Delivery.query.get_or_404(delivery_id)
    
    if delivery.logistics_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if delivery.status != 'assigned':
        return jsonify({'error': 'Invalid delivery status'}), 400
    
    # Verify pickup OTP
    data = request.get_json() or {}
    submitted_otp = data.get('otp', '')
    
    if delivery.pickup_otp:
        if not submitted_otp:
            return jsonify({'error': 'Pickup OTP is required. Ask the donor for the OTP.'}), 400
        if submitted_otp != delivery.pickup_otp:
            return jsonify({'error': 'Invalid OTP. Please check with the donor.'}), 400
    
    try:
        delivery.status = 'picked_up'
        delivery.pickup_time = datetime.now()
        delivery.pickup_otp = None  # Clear used OTP
        
        # Generate delivery OTP for NGO confirmation
        delivery.delivery_otp = str(random.randint(1000, 9999))
        
        # Update donation status only if all deliveries are picked up or further
        all_statuses = [d.status for d in delivery.donation.deliveries.all() if d.id != delivery.id]
        all_statuses.append('picked_up')  # include this delivery's new status
        if all(s in ('picked_up', 'delivered') for s in all_statuses):
            delivery.donation.status = 'picked_up'
        
        db.session.commit()
        
        # Notify donor and NGO
        notification = Notification(
            user_id=delivery.donation.donor_id,
            title='Pickup Confirmed',
            message=f'Your food donation has been picked up',
            notification_type='delivery',
            related_id=delivery.id
        )
        db.session.add(notification)
        
        ngo_notification = Notification(
            user_id=delivery.ngo_id,
            title='Delivery In Transit',
            message=f'Your food delivery is on the way. Pickup ID: {delivery.pickup_id}',
            notification_type='delivery',
            related_id=delivery.id
        )
        db.session.add(ngo_notification)
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to confirm pickup'}), 500

@logistics_bp.route('/delivery/<int:delivery_id>/deliver', methods=['POST'])
@role_required(Role.LOGISTICS)
def confirm_delivery(delivery_id):
    """Confirm delivery with OTP from NGO"""
    delivery = Delivery.query.get_or_404(delivery_id)
    
    if delivery.logistics_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if delivery.status != 'picked_up':
        return jsonify({'error': 'Invalid delivery status'}), 400
    
    # Verify delivery OTP
    data = request.get_json() or {}
    submitted_otp = data.get('otp', '')
    
    if delivery.delivery_otp:
        if not submitted_otp:
            return jsonify({'error': 'Delivery OTP is required. Ask the NGO for the OTP.'}), 400
        if submitted_otp != delivery.delivery_otp:
            return jsonify({'error': 'Invalid OTP. Please check with the NGO.'}), 400
    
    try:
        delivery.status = 'delivered'
        delivery.delivery_time = datetime.now()
        delivery.delivery_otp = None  # Clear used OTP
        
        # Update donation status only if ALL deliveries are now delivered
        all_statuses = [d.status for d in delivery.donation.deliveries.all() if d.id != delivery.id]
        all_statuses.append('delivered')  # include this delivery's new status
        if all(s == 'delivered' for s in all_statuses):
            delivery.donation.status = 'delivered'
        
        db.session.commit()
        
        # Notify donor and NGO
        donor_notification = Notification(
            user_id=delivery.donation.donor_id,
            title='Delivery Completed',
            message=f'Your food donation has been successfully delivered',
            notification_type='delivery',
            related_id=delivery.id
        )
        db.session.add(donor_notification)
        
        ngo_notification = Notification(
            user_id=delivery.ngo_id,
            title='Delivery Received',
            message=f'Your food delivery has been received',
            notification_type='delivery',
            related_id=delivery.id
        )
        db.session.add(ngo_notification)
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to confirm delivery'}), 500

@logistics_bp.route('/api/delivery/<int:delivery_id>/location', methods=['GET'])
@role_required(Role.LOGISTICS)
def get_delivery_locations(delivery_id):
    """Get donor and NGO locations for delivery"""
    delivery = Delivery.query.get_or_404(delivery_id)
    
    if delivery.logistics_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    donation = delivery.donation
    donor = donation.donor
    ngo = delivery.ngo_recipient
    
    return jsonify({
        'pickup_location': {
            'name': donor.full_name,
            'address': donation.pickup_address,
            'latitude': donation.latitude,
            'longitude': donation.longitude,
            'phone': donor.phone
        },
        'delivery_location': {
            'name': ngo.organization_name,
            'address': ngo.address,
            'latitude': ngo.latitude,
            'longitude': ngo.longitude,
            'phone': ngo.phone
        }
    })

@logistics_bp.route('/notifications')
@role_required(Role.LOGISTICS)
def notifications():
    """View notifications"""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('logistics/notifications.html', notifications=notifications)

@logistics_bp.route('/api/deliveries/active')
@role_required(Role.LOGISTICS)
def get_active_deliveries():
    """Get active deliveries for logistics"""
    deliveries = Delivery.query.filter_by(
        logistics_id=current_user.id,
    ).filter(Delivery.status.in_(['assigned', 'picked_up'])).all()
    
    return jsonify([{
        'id': d.id,
        'donation_id': d.donation_id,
        'status': d.status,
        'pickup_address': d.donation.pickup_address,
        'delivery_address': d.ngo_recipient.address,
        'created_at': d.created_at.isoformat()
    } for d in deliveries])


@logistics_bp.route('/feedback/<int:delivery_id>', methods=['POST'])
@role_required(Role.LOGISTICS)
def submit_feedback(delivery_id):
    """Submit feedback — Volunteer can rate Donor and NGO"""
    delivery = Delivery.query.get_or_404(delivery_id)

    if delivery.logistics_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if delivery.status != 'delivered':
        return jsonify({'error': 'Can only feedback on completed deliveries'}), 400

    data = request.get_json()
    feedback_type = data.get('feedback_type')
    rating = data.get('rating')
    comment = data.get('comment', '')

    if not rating or not feedback_type:
        return jsonify({'error': 'Rating and feedback type are required'}), 400

    if int(rating) < 1 or int(rating) > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    # Determine target user
    if feedback_type == FeedbackType.VOLUNTEER_TO_DONOR:
        to_user_id = delivery.donation.donor_id
    elif feedback_type == FeedbackType.VOLUNTEER_TO_NGO:
        to_user_id = delivery.ngo_id
    else:
        return jsonify({'error': 'Invalid feedback type for volunteer'}), 400

    # Check for duplicate
    existing = Feedback.query.filter_by(
        delivery_id=delivery.id,
        from_user_id=current_user.id,
        to_user_id=to_user_id
    ).first()
    if existing:
        return jsonify({'error': 'You have already submitted this feedback'}), 400

    try:
        feedback = Feedback(
            delivery_id=delivery.id,
            donation_id=delivery.donation_id,
            from_user_id=current_user.id,
            to_user_id=to_user_id,
            feedback_type=feedback_type,
            rating=int(rating),
            comment=comment
        )
        db.session.add(feedback)
        db.session.commit()
        return jsonify({'success': True})
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Failed to submit feedback'}), 500


@logistics_bp.route('/feedback/received')
@role_required(Role.LOGISTICS)
def feedback_received():
    """View feedback received from Donors and NGOs"""
    feedbacks = Feedback.query.filter_by(to_user_id=current_user.id).order_by(Feedback.created_at.desc()).all()
    return render_template('logistics/feedback.html', feedbacks=feedbacks)


@logistics_bp.route('/toggle-availability', methods=['POST'])
@role_required(Role.LOGISTICS)
def toggle_availability():
    """Toggle logistics volunteer availability status"""
    try:
        current_user.is_available = not current_user.is_available
        db.session.commit()
        status = 'available' if current_user.is_available else 'unavailable'
        return jsonify({'success': True, 'is_available': current_user.is_available, 'status': status})
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Failed to update availability'}), 500
