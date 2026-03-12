from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import current_user
from app.models import db, ContactMessage, User, Role, Notification

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Home page"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/how-it-works')
def how_it_works():
    """How it works page"""
    return render_template('how-it-works.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        if not name or not email or not message:
            flash('All fields are required.', 'error')
            return redirect(url_for('main.contact'))
        
        contact_msg = ContactMessage(name=name, email=email, message=message)
        db.session.add(contact_msg)
        
        # Notify all admins
        admins = User.query.filter_by(role=Role.ADMIN).all()
        for admin in admins:
            notification = Notification(
                user_id=admin.id,
                title='New Contact Message',
                message=f'New message from {name} ({email})',
                notification_type='contact'
            )
            db.session.add(notification)
        
        db.session.commit()
        flash('Your message has been sent successfully! An admin will review it shortly.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html')

@main_bp.route('/api/user/status')
def user_status():
    """Get current user status"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user_id': current_user.id,
            'username': current_user.username,
            'role': current_user.role,
            'full_name': current_user.full_name
        })
    return jsonify({
        'authenticated': False
    })
