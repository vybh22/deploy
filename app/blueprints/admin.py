from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import (db, User, Donation, FoodRequest, Delivery, Notification, 
                        DonationStatus, Role, AuditLog, Feedback, ContactMessage)
from app.decorators import role_required
from datetime import datetime
from sqlalchemy import func
import random

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def log_action(action, entity_type, entity_id, old_values=None, new_values=None):
    """Log admin action for audit trail"""
    try:
        log = AuditLog(
            admin_id=current_user.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values
        )
        db.session.add(log)
        db.session.commit()
    except:
        pass

@admin_bp.route('/dashboard')
@role_required(Role.ADMIN)
def dashboard():
    """Admin dashboard with analytics"""
    # Calculate statistics
    total_donations = Donation.query.count()
    total_users = User.query.count()
    total_donors = User.query.filter_by(role=Role.DONOR).count()
    total_ngos = User.query.filter_by(role=Role.NGO).count()
    total_logistics = User.query.filter_by(role=Role.LOGISTICS).count()
    
    # Deliveries
    total_deliveries = Delivery.query.count()
    completed_deliveries = Delivery.query.filter_by(status='delivered').count()
    delivery_success_rate = (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    
    # Food statistics
    total_packets = db.session.query(func.sum(Donation.quantity)).scalar() or 0
    delivered_packets = db.session.query(func.sum(Donation.quantity)).filter_by(
        status=DonationStatus.DELIVERED
    ).scalar() or 0
    
    # Calculate CO2 emissions reduction (basic: 1 packet = ~0.5 kg = ~1.2 kg CO2 if not wasted)
    co2_reduction = delivered_packets * 0.5 * 1.2
    
    stats = {
        'total_donations': total_donations,
        'total_users': total_users,
        'total_donors': total_donors,
        'total_ngos': total_ngos,
        'total_logistics': total_logistics,
        'total_deliveries': total_deliveries,
        'completed_deliveries': completed_deliveries,
        'delivery_success_rate': round(delivery_success_rate, 2),
        'total_packets': total_packets,
        'delivered_packets': delivered_packets,
        'co2_reduction': round(co2_reduction, 2)
    }
    
    # Expired count
    expired_donations = Donation.query.filter_by(status=DonationStatus.EXPIRED).count()
    stats['expired_donations'] = expired_donations

    # Recent activity
    recent_donations = Donation.query.order_by(Donation.created_at.desc()).limit(5).all()
    pending_approvals = Donation.query.filter_by(status=DonationStatus.PENDING).count()
    pending_user_approvals = User.query.filter_by(is_verified=False).filter(User.role != Role.DONOR).count()
    pending_requests = FoodRequest.query.filter_by(status='pending').count()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_donations=recent_donations,
                         pending_approvals=pending_approvals,
                         pending_user_approvals=pending_user_approvals,
                         pending_requests=pending_requests)

@admin_bp.route('/users')
@role_required(Role.ADMIN)
def manage_users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    
    query = User.query
    if role_filter and role_filter in Role.ALL_ROLES:
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/manage_users.html', users=users, role_filter=role_filter, roles=Role.ALL_ROLES)

@admin_bp.route('/user/<int:user_id>/approve', methods=['POST'])
@role_required(Role.ADMIN)
def approve_user(user_id):
    """Approve user registration"""
    user = User.query.get_or_404(user_id)
    
    if user.is_verified:
        return jsonify({'error': 'User already verified'}), 400
    
    try:
        user.is_verified = True
        user.verification_date = datetime.now()
        
        db.session.commit()
        log_action('approve_user', 'User', user_id, new_values={'is_verified': True})
        
        # Notify user
        notification = Notification(
            user_id=user_id,
            title='Registration Approved',
            message='Your registration has been approved!',
            notification_type='approval'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'error': 'Failed to approve user'}), 500

@admin_bp.route('/user/<int:user_id>/deactivate', methods=['POST'])
@role_required(Role.ADMIN)
def deactivate_user(user_id):
    """Deactivate user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400
    
    data = request.get_json()
    reason = data.get('reason', 'No reason provided')
    
    try:
        user.is_active = False
        user.deactivation_reason = reason
        user.deactivation_date = datetime.now()
        
        db.session.commit()
        log_action('deactivate_user', 'User', user_id, new_values={'is_active': False, 'reason': reason})
        
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'error': 'Failed to deactivate user'}), 500

@admin_bp.route('/donations')
@role_required(Role.ADMIN)
def manage_donations():
    """Manage donations"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Donation.query
    if status_filter and status_filter in DonationStatus.ALL_STATUSES:
        query = query.filter_by(status=status_filter)
    
    donations = query.order_by(Donation.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/manage_donations.html', 
                         donations=donations, 
                         status_filter=status_filter,
                         statuses=DonationStatus.ALL_STATUSES)

@admin_bp.route('/donation/<int:donation_id>/approve', methods=['POST'])
@role_required(Role.ADMIN)
def approve_donation(donation_id):
    """Approve food listing"""
    donation = Donation.query.get_or_404(donation_id)
    
    if donation.status != DonationStatus.PENDING:
        return jsonify({'error': 'Can only approve pending donations'}), 400
    
    data = request.get_json()
    notes = data.get('notes', '')
    
    try:
        donation.status = DonationStatus.APPROVED
        donation.approved_at = datetime.now()
        donation.admin_notes = notes
        
        db.session.commit()
        log_action('approve_donation', 'Donation', donation_id)
        
        # Notify donor that listing is approved
        notification = Notification(
            user_id=donation.donor_id,
            title='Donation Approved',
            message=f'Your {donation.food_type} listing has been approved!',
            notification_type='approval',
            related_id=donation_id
        )
        db.session.add(notification)
        
        # Notify NGOs that new food is available
        from app.models import User as UserModel
        ngos = UserModel.query.filter_by(role=Role.NGO, is_verified=True).all()
        for ngo in ngos:
            ngo_notif = Notification(
                user_id=ngo.id,
                title='New Food Available',
                message=f'{donation.food_type} available from {donation.donor.organization_name or donation.donor.full_name}',
                notification_type='donation',
                related_id=donation_id
            )
            db.session.add(ngo_notif)
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to approve donation'}), 500

@admin_bp.route('/donation/<int:donation_id>/reject', methods=['POST'])
@role_required(Role.ADMIN)
def reject_donation(donation_id):
    """Reject food listing"""
    donation = Donation.query.get_or_404(donation_id)
    
    if donation.status != DonationStatus.PENDING:
        return jsonify({'error': 'Can only reject pending donations'}), 400
    
    data = request.get_json()
    reason = data.get('reason', 'No reason provided')
    
    try:
        donation.status = DonationStatus.CANCELLED
        donation.admin_notes = reason
        
        db.session.commit()
        log_action('reject_donation', 'Donation', donation_id, new_values={'reason': reason})
        
        # Notify donor
        notification = Notification(
            user_id=donation.donor_id,
            title='Donation Rejected',
            message=f'Your {donation.food_type} listing was rejected: {reason}',
            notification_type='rejection',
            related_id=donation_id
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'error': 'Failed to reject donation'}), 500

@admin_bp.route('/requests')
@role_required(Role.ADMIN)
def manage_requests():
    """Manage food requests"""
    page = request.args.get('page', 1, type=int)
    
    requests = FoodRequest.query.order_by(FoodRequest.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/manage_requests.html', requests=requests)

@admin_bp.route('/request/<int:request_id>/approve', methods=['POST'])
@role_required(Role.ADMIN)
def approve_request(request_id):
    """Approve food request"""
    food_request = FoodRequest.query.get_or_404(request_id)
    
    if food_request.status != 'pending':
        return jsonify({'error': 'Can only approve pending requests'}), 400
    
    data = request.get_json()
    notes = data.get('notes', '')
    
    try:
        # Check available packets before approving
        available = food_request.donation.available_quantity
        if available is None:
            available = food_request.donation.quantity
        if food_request.requested_quantity > available:
            return jsonify({'error': f'Insufficient packets. Only {available} available out of {food_request.donation.quantity} total.'}), 400

        food_request.status = 'approved'
        food_request.approved_at = datetime.now()
        food_request.admin_notes = notes
        
        # Create delivery record with unique pickup ID
        pickup_id = f'EXB-{random.randint(1000, 9999)}'
        # Ensure uniqueness
        while Delivery.query.filter_by(pickup_id=pickup_id).first():
            pickup_id = f'EXB-{random.randint(1000, 9999)}'
        
        delivery = Delivery(
            donation_id=food_request.donation_id,
            ngo_id=food_request.ngo_id,
            pickup_id=pickup_id,
            status='assigned'
        )
        db.session.add(delivery)
        
        # Deduct requested quantity from available
        food_request.donation.available_quantity = available - food_request.requested_quantity
        
        # Only mark as fully assigned if no packets left
        if food_request.donation.available_quantity <= 0:
            food_request.donation.status = DonationStatus.ASSIGNED
        
        db.session.commit()
        log_action('approve_request', 'FoodRequest', request_id)
        
        # Notify NGO and Logistics
        notification = Notification(
            user_id=food_request.ngo_id,
            title='Request Approved',
            message=f'Your food request has been approved!',
            notification_type='approval',
            related_id=request_id
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({'success': True, 'delivery_id': delivery.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to approve request'}), 500

@admin_bp.route('/request/<int:request_id>/reject', methods=['POST'])
@role_required(Role.ADMIN)
def reject_request(request_id):
    """Reject food request"""
    food_request = FoodRequest.query.get_or_404(request_id)
    
    if food_request.status != 'pending':
        return jsonify({'error': 'Can only reject pending requests'}), 400
    
    data = request.get_json()
    reason = data.get('reason', 'No reason provided')
    
    try:
        food_request.status = 'rejected'
        food_request.admin_notes = reason
        
        db.session.commit()
        log_action('reject_request', 'FoodRequest', request_id, new_values={'reason': reason})
        
        # Notify NGO
        notification = Notification(
            user_id=food_request.ngo_id,
            title='Request Rejected',
            message=f'Your food request was rejected: {reason}',
            notification_type='rejection',
            related_id=request_id
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'error': 'Failed to reject request'}), 500

@admin_bp.route('/deliveries')
@role_required(Role.ADMIN)
def manage_deliveries():
    """Manage deliveries and assign logistics"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'assigned')
    
    query = Delivery.query.order_by(Delivery.created_at.desc())
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    deliveries = query.paginate(page=page, per_page=20)
    
    # Get all logistics volunteers (show availability status to admin)
    logistics_volunteers = User.query.filter_by(role=Role.LOGISTICS, is_verified=True, is_active=True).all()
    
    statuses = ['assigned', 'picked_up', 'delivered']
    
    return render_template('admin/manage_deliveries.html', 
                         deliveries=deliveries, 
                         logistics_volunteers=logistics_volunteers,
                         status_filter=status_filter,
                         statuses=statuses)

@admin_bp.route('/delivery/<int:delivery_id>/assign', methods=['POST'])
@role_required(Role.ADMIN)
def assign_logistics(delivery_id):
    """Assign logistics volunteer to delivery"""
    delivery = Delivery.query.get_or_404(delivery_id)
    
    data = request.get_json()
    logistics_id = data.get('logistics_id')
    
    logistics = User.query.filter_by(id=logistics_id, role=Role.LOGISTICS, is_verified=True).first()
    
    if not logistics:
        return jsonify({'error': 'Invalid logistics volunteer'}), 400
    
    try:
        delivery.logistics_id = logistics_id
        db.session.commit()
        log_action('assign_logistics', 'Delivery', delivery_id, new_values={'logistics_id': logistics_id})
        
        # Notify logistics
        notification = Notification(
            user_id=logistics_id,
            title='New Delivery Assigned',
            message=f'You have been assigned a new delivery',
            notification_type='assignment',
            related_id=delivery_id
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True})
    except:
        db.session.rollback()
        return jsonify({'error': 'Failed to assign logistics'}), 500

@admin_bp.route('/reports')
@role_required(Role.ADMIN)
def reports():
    """View reports"""
    # Daily donations
    daily_donations = db.session.query(
        func.date(Donation.created_at),
        func.count(Donation.id)
    ).group_by(func.date(Donation.created_at)).order_by(func.date(Donation.created_at).desc()).limit(30).all()
    
    # NGO distribution
    ngo_distributions = db.session.query(
        User.organization_name,
        func.count(Delivery.id)
    ).join(Delivery, User.id == Delivery.ngo_id).group_by(User.id).all()
    
    return render_template('admin/reports.html', 
                         daily_donations=daily_donations,
                         ngo_distributions=ngo_distributions)

@admin_bp.route('/audit-log')
@role_required(Role.ADMIN)
def audit_log():
    """View audit log"""
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('admin/audit_log.html', logs=logs)

@admin_bp.route('/contact-messages')
@role_required(Role.ADMIN)
def contact_messages():
    """View contact messages from visitors"""
    page = request.args.get('page', 1, type=int)
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).paginate(page=page, per_page=20)
    # Mark unread messages as read
    unread = ContactMessage.query.filter_by(is_read=False).all()
    for msg in unread:
        msg.is_read = True
    db.session.commit()
    return render_template('admin/contact_messages.html', messages=messages)

@admin_bp.route('/contact-messages/<int:message_id>/delete', methods=['POST'])
@role_required(Role.ADMIN)
def delete_contact_message(message_id):
    """Delete a contact message"""
    msg = ContactMessage.query.get_or_404(message_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'success')
    return redirect(url_for('admin.contact_messages'))

@admin_bp.route('/user/<int:user_id>/regeocode', methods=['POST'])
@role_required(Role.ADMIN)
def regeocode_user(user_id):
    """Re-geocode a user's address to fix their lat/lng coordinates"""
    from app.blueprints.auth import geocode_address
    user = User.query.get_or_404(user_id)
    if not user.address:
        flash(f'User {user.full_name} has no address to geocode.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    lat, lng = geocode_address(user.address, user.city)
    if lat is not None and lng is not None:
        old_lat, old_lng = user.latitude, user.longitude
        user.latitude = lat
        user.longitude = lng
        db.session.commit()
        log_action('regeocode_user', 'user', user.id,
                   old_values={'latitude': old_lat, 'longitude': old_lng},
                   new_values={'latitude': lat, 'longitude': lng})
        flash(f'Location updated for {user.full_name}: ({lat:.6f}, {lng:.6f})', 'success')
    else:
        flash(f'Could not geocode address for {user.full_name}. Try simplifying the address.', 'error')
    return redirect(url_for('admin.manage_users'))
