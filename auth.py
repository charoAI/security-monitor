"""
Simple authentication system for Security Monitor
"""
import os
import hashlib
import secrets
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from datetime import datetime, timedelta
import json

class AuthManager:
    def __init__(self, auth_file='data/auth.json'):
        self.auth_file = auth_file
        self.ensure_auth_file()

    def ensure_auth_file(self):
        """Create auth file with default admin if it doesn't exist"""
        os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)

        if not os.path.exists(self.auth_file):
            # Create default admin user
            default_password = os.getenv('ADMIN_PASSWORD', 'changeme123')
            self.create_user('admin', default_password, is_admin=True)
            print(f"Created default admin user. Password: {default_password}")
            print("IMPORTANT: Change this password immediately!")

    def hash_password(self, password, salt=None):
        """Hash a password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256',
                                       password.encode('utf-8'),
                                       salt.encode('utf-8'),
                                       100000)
        return salt + ':' + pwd_hash.hex()

    def verify_password(self, stored_password, provided_password):
        """Verify a provided password against the stored one"""
        salt = stored_password.split(':')[0]
        return stored_password == self.hash_password(provided_password, salt)

    def load_users(self):
        """Load users from file"""
        if os.path.exists(self.auth_file):
            with open(self.auth_file, 'r') as f:
                return json.load(f)
        return {}

    def save_users(self, users):
        """Save users to file"""
        with open(self.auth_file, 'w') as f:
            json.dump(users, f, indent=2)

    def create_user(self, username, password, is_admin=False):
        """Create a new user"""
        users = self.load_users()

        if username in users:
            return False, "User already exists"

        users[username] = {
            'password': self.hash_password(password),
            'is_admin': is_admin,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }

        self.save_users(users)
        return True, "User created successfully"

    def authenticate(self, username, password):
        """Authenticate a user"""
        users = self.load_users()

        if username not in users:
            return False, "Invalid username or password"

        user = users[username]
        if not self.verify_password(user['password'], password):
            return False, "Invalid username or password"

        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self.save_users(users)

        return True, user

    def change_password(self, username, old_password, new_password):
        """Change user password"""
        users = self.load_users()

        if username not in users:
            return False, "User not found"

        if not self.verify_password(users[username]['password'], old_password):
            return False, "Invalid current password"

        users[username]['password'] = self.hash_password(new_password)
        self.save_users(users)

        return True, "Password changed successfully"

    def delete_user(self, username):
        """Delete a user"""
        users = self.load_users()

        if username not in users:
            return False, "User not found"

        if username == 'admin':
            return False, "Cannot delete admin user"

        del users[username]
        self.save_users(users)

        return True, "User deleted successfully"

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))

        if not session.get('is_admin', False):
            if request.is_json:
                return jsonify({'error': 'Admin privileges required'}), 403
            return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function