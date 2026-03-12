from app import create_app, db
from app.models import User, Role
import os

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role}

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized.')

@app.cli.command()
def create_admin():
    """Create an admin user."""
    username = input('Admin username: ')
    email = input('Admin email: ')
    password = input('Admin password: ')
    
    if User.query.filter_by(username=username).first():
        print('Username already exists')
        return
    
    admin = User(
        username=username,
        email=email,
        full_name='Admin',
        phone='0000000000',
        role=Role.ADMIN,
        is_verified=True,
        is_active=True
    )
    admin.set_password(password)
    
    try:
        db.session.add(admin)
        db.session.commit()
        print(f'Admin user {username} created successfully')
    except Exception as e:
        db.session.rollback()
        print(f'Error creating admin: {e}')

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', True), host='0.0.0.0', port=5000)
