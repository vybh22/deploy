from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Donation, FoodRequest, Notification, DonationStatus, Role, Delivery, Feedback, FeedbackType, User
from app.decorators import role_required
from datetime import datetime

ngo_bp = Blueprint('ngo', __name__, url_prefix='/ngo')

@ngo_bp.route('/dashboard')
@role_required(Role.NGO)
def dashboard():
    """NGO dashboard"""
    requests = FoodRequest.query.filter_by(ngo_id=current_user.id).order_by(FoodRequest.created_at.desc()).all()
    deliveries = Delivery.query.filter_by(ngo_id=current_user.id).order_by(Delivery.created_at.desc()).all()

    # Get existing feedback given by this NGO, keyed by (delivery_id, feedback_type)
    given_feedback = {}
    for fb in Feedback.query.filter_by(from_user_id=current_user.id).all():
        given_feedback[(fb.delivery_id, fb.feedback_type)] = fb

    stats = {
        'total_requests': len(requests),
        'approved_requests': sum(1 for r in requests if r.status == 'approved'),
        'rejected_requests': sum(1 for r in requests if r.status == 'rejected'),
        'total_deliveries': len(deliveries),
        'completed_deliveries': sum(1 for d in deliveries if d.status == 'delivered')
    }

    return render_template('ngo/dashboard.html', requests=requests, deliveries=deliveries,
                           stats=stats, given_feedback=given_feedback)

@ngo_bp.route('/browse')
@role_required(Role.NGO)
def browse_listings():
    """Browse available food listings"""
    # Show only approved donations
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get filter parameters
    search_query = request.args.get('q', '').strip()
    city_filter = request.args.get('city', '').strip()
    
    # Start with base query - exclude expired and fully allocated
    query = Donation.query.filter_by(status=DonationStatus.APPROVED).filter(
        Donation.expiry_time > datetime.now(),
        db.or_(Donation.available_quantity > 0, Donation.available_quantity.is_(None))
    )
    
    # Apply search filter (food type)
    if search_query:
        query = query.filter(Donation.food_type.ilike(f'%{search_query}%'))
    
    # Apply city filter
    if city_filter:
        query = query.filter(Donation.city.ilike(f'%{city_filter}%'))
    
    donations = query.paginate(page=page, per_page=per_page)
    
    return render_template('ngo/browse_listings.html', donations=donations)

@ngo_bp.route('/listing/<int:listing_id>')
@role_required(Role.NGO)
def view_listing(listing_id):
    """View listing details"""
    donation = Donation.query.get_or_404(listing_id)
    
    if donation.status != DonationStatus.APPROVED or donation.expiry_time <= datetime.now():
        flash('This listing is not available', 'error')
        return redirect(url_for('ngo.browse_listings'))
    
    # Check if already requested
    existing_request = FoodRequest.query.filter_by(
        donation_id=listing_id,
        ngo_id=current_user.id
    ).first()
    
    donor = donation.donor
    available = donation.available_quantity if donation.available_quantity is not None else donation.quantity
    
    return render_template('ngo/view_listing.html', donation=donation, donor=donor,
                           existing_request=existing_request, available_quantity=available)

@ngo_bp.route('/request/create', methods=['POST'])
@role_required(Role.NGO)
def create_request():
    """Create food request"""
    data = request.get_json()
    donation_id = data.get('donation_id')
    quantity = data.get('quantity')
    
    donation = Donation.query.get_or_404(donation_id)
    
    if donation.status != DonationStatus.APPROVED:
        return jsonify({'error': 'Donation not available'}), 400
    
    if donation.expiry_time <= datetime.now():
        return jsonify({'error': 'This donation has expired'}), 400
    
    # Check available quantity
    available = donation.available_quantity if donation.available_quantity is not None else donation.quantity
    if quantity > available:
        return jsonify({'error': f'Insufficient packets. Only {available} packets available.'}), 400
    
    # Check if already requested by this NGO
    existing = FoodRequest.query.filter_by(
        donation_id=donation_id,
        ngo_id=current_user.id
    ).first()
    
    if existing:
        return jsonify({'error': 'You already requested this donation'}), 400
    
    try:
        request_obj = FoodRequest(
            donation_id=donation_id,
            ngo_id=current_user.id,
            requested_quantity=quantity,
            status='pending'
        )
        db.session.add(request_obj)
        db.session.commit()
        
        # Notify donor and admin
        notification = Notification(
            user_id=donation.donor_id,
            title='New Food Request',
            message=f'{current_user.organization_name} requested {quantity} packets',
            notification_type='request',
            related_id=request_obj.id
        )
        db.session.add(notification)
        
        # Notify admins
        admin_users = User.query.filter_by(role=Role.ADMIN).all()
        for admin in admin_users:
            admin_notification = Notification(
                user_id=admin.id,
                title='New Food Request',
                message=f'{current_user.organization_name} requested {quantity} packets',
                notification_type='request',
                related_id=request_obj.id
            )
            db.session.add(admin_notification)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Request created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create request'}), 500

@ngo_bp.route('/request/<int:request_id>/status')
@role_required(Role.NGO)
def request_status(request_id):
    """Get request status"""
    food_request = FoodRequest.query.get_or_404(request_id)
    
    if food_request.ngo_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': food_request.id,
        'status': food_request.status,
        'donation_id': food_request.donation_id,
        'quantity': food_request.requested_quantity,
        'created_at': food_request.created_at.isoformat()
    })

@ngo_bp.route('/delivery/<int:delivery_id>/confirm', methods=['POST'])
@role_required(Role.NGO)
def confirm_delivery(delivery_id):
    """Confirm delivery received — NGO shares delivery OTP with volunteer who enters it"""
    delivery = Delivery.query.get_or_404(delivery_id)
    
    if delivery.ngo_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if delivery.status != 'picked_up':
        return jsonify({'error': 'Invalid delivery status'}), 400
    
    # Verify delivery OTP if one exists
    data = request.get_json() or {}
    otp = data.get('otp', '').strip()
    if delivery.delivery_otp:
        if not otp:
            return jsonify({'error': 'Delivery OTP is required'}), 400
        if otp != delivery.delivery_otp:
            return jsonify({'error': 'Invalid OTP. Please check and try again.'}), 400
    
    try:
        delivery.status = 'delivered'
        delivery.delivery_time = datetime.now()
        
        # Update donation status only if ALL deliveries are now delivered
        all_statuses = [d.status for d in delivery.donation.deliveries.all() if d.id != delivery.id]
        all_statuses.append('delivered')
        if all(s == 'delivered' for s in all_statuses):
            donation = delivery.donation
            donation.status = DonationStatus.DELIVERED
        
        db.session.commit()
        
        # Notify donor and logistics
        notification = Notification(
            user_id=delivery.donation.donor_id,
            title='Delivery Confirmed',
            message=f'Your food donation has been delivered to {current_user.organization_name}',
            notification_type='delivery',
            related_id=delivery.id
        )
        db.session.add(notification)
        
        if delivery.logistics_id:
            logistics_notification = Notification(
                user_id=delivery.logistics_id,
                title='Delivery Confirmed',
                message=f'{current_user.organization_name} confirmed receiving the delivery',
                notification_type='delivery',
                related_id=delivery.id
            )
            db.session.add(logistics_notification)
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to confirm delivery'}), 500

@ngo_bp.route('/feedback/<int:delivery_id>', methods=['POST'])
@role_required(Role.NGO)
def submit_feedback(delivery_id):
    """Submit feedback — NGO can rate Donor and Volunteer"""
    delivery = Delivery.query.get_or_404(delivery_id)

    if delivery.ngo_id != current_user.id:
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
    if feedback_type == FeedbackType.NGO_TO_DONOR:
        to_user_id = delivery.donation.donor_id
    elif feedback_type == FeedbackType.NGO_TO_VOLUNTEER:
        if not delivery.logistics_id:
            return jsonify({'error': 'No volunteer assigned to this delivery'}), 400
        to_user_id = delivery.logistics_id
    else:
        return jsonify({'error': 'Invalid feedback type for NGO'}), 400

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


@ngo_bp.route('/feedback/received')
@role_required(Role.NGO)
def feedback_received():
    """View feedback received from Donors and Volunteers"""
    feedbacks = Feedback.query.filter_by(to_user_id=current_user.id).order_by(Feedback.created_at.desc()).all()
    return render_template('ngo/feedback.html', feedbacks=feedbacks)

@ngo_bp.route('/notifications')
@role_required(Role.NGO)
def notifications():
    """View notifications"""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('ngo/notifications.html', notifications=notifications)
