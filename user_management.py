"""
Enhanced user management system with registration requests
"""
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets
import hashlib

class UserManager:
    def __init__(self, db_path='data/users.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()

    def init_db(self):
        """Initialize user database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                organization TEXT,
                is_admin BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,

                -- User preferences
                email_notifications BOOLEAN DEFAULT 1,
                report_recipients TEXT,  -- JSON list of emails

                -- Email configuration (per user)
                smtp_server TEXT,
                smtp_port INTEGER,
                smtp_username TEXT,
                smtp_password TEXT,  -- Encrypted

                -- Usage limits
                daily_report_limit INTEGER DEFAULT 10,
                api_calls_today INTEGER DEFAULT 0,
                last_reset_date DATE
            )
        ''')

        # Registration requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registration_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                organization TEXT,
                reason TEXT,
                token TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'pending',  -- pending, approved, rejected
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                reviewed_by TEXT,
                admin_notes TEXT
            )
        ''')

        # Activity tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,  -- JSON
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # API usage tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                endpoint TEXT,
                method TEXT,
                response_code INTEGER,
                response_time_ms INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Report generation tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS report_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                report_type TEXT,
                countries TEXT,  -- JSON list
                status TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Create default admin if doesn't exist
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
        if cursor.fetchone()[0] == 0:
            admin_password = os.getenv('ADMIN_PASSWORD', 'changeme123')
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
            self._create_user_internal(
                cursor,
                'admin',
                self._hash_password(admin_password),
                admin_email,
                'Administrator',
                'System',
                is_admin=True
            )
            print(f"Created default admin user: admin / {admin_password}")

        conn.commit()
        conn.close()

    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256',
                                       password.encode('utf-8'),
                                       salt.encode('utf-8'),
                                       100000)
        return salt + ':' + pwd_hash.hex()

    def _verify_password(self, stored: str, provided: str) -> bool:
        """Verify password"""
        salt = stored.split(':')[0]
        pwd_hash = hashlib.pbkdf2_hmac('sha256',
                                       provided.encode('utf-8'),
                                       salt.encode('utf-8'),
                                       100000)
        return stored == salt + ':' + pwd_hash.hex()

    def _create_user_internal(self, cursor, username, password_hash, email,
                            full_name, organization, is_admin=False):
        """Internal method to create user"""
        cursor.execute('''
            INSERT INTO users (username, password, email, full_name, organization, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, email, full_name, organization, is_admin))

    def request_registration(self, email: str, full_name: str,
                           organization: str = None, reason: str = None) -> Dict:
        """Submit a registration request"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if request already exists
        cursor.execute('SELECT status FROM registration_requests WHERE email = ?', (email,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return {
                'success': False,
                'message': f'Request already exists with status: {existing[0]}'
            }

        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return {
                'success': False,
                'message': 'User with this email already exists'
            }

        # Create request
        token = secrets.token_urlsafe(32)
        cursor.execute('''
            INSERT INTO registration_requests (email, full_name, organization, reason, token)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, full_name, organization, reason, token))

        conn.commit()
        conn.close()

        return {
            'success': True,
            'message': 'Registration request submitted. An admin will review it soon.',
            'token': token
        }

    def get_pending_requests(self) -> List[Dict]:
        """Get all pending registration requests"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, email, full_name, organization, reason, requested_at
            FROM registration_requests
            WHERE status = 'pending'
            ORDER BY requested_at DESC
        ''')

        requests = []
        for row in cursor.fetchall():
            requests.append({
                'id': row[0],
                'email': row[1],
                'full_name': row[2],
                'organization': row[3],
                'reason': row[4],
                'requested_at': row[5]
            })

        conn.close()
        return requests

    def approve_registration(self, request_id: int, admin_username: str,
                           initial_password: str = None) -> Dict:
        """Approve a registration request and create user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get request details
        cursor.execute('''
            SELECT email, full_name, organization
            FROM registration_requests
            WHERE id = ? AND status = 'pending'
        ''', (request_id,))

        request = cursor.fetchone()
        if not request:
            conn.close()
            return {'success': False, 'message': 'Request not found or already processed'}

        email, full_name, organization = request

        # Generate username from email
        username = email.split('@')[0].lower()

        # Check if username exists and make unique if needed
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
        if cursor.fetchone()[0] > 0:
            username = f"{username}{secrets.token_hex(2)}"

        # Generate initial password if not provided
        if not initial_password:
            initial_password = secrets.token_urlsafe(12)

        # Create user
        try:
            self._create_user_internal(
                cursor, username,
                self._hash_password(initial_password),
                email, full_name, organization
            )

            # Update request status
            cursor.execute('''
                UPDATE registration_requests
                SET status = 'approved',
                    reviewed_at = CURRENT_TIMESTAMP,
                    reviewed_by = ?
                WHERE id = ?
            ''', (admin_username, request_id))

            conn.commit()
            conn.close()

            return {
                'success': True,
                'message': 'User created successfully',
                'username': username,
                'initial_password': initial_password
            }
        except Exception as e:
            conn.rollback()
            conn.close()
            return {'success': False, 'message': str(e)}

    def reject_registration(self, request_id: int, admin_username: str,
                          reason: str = None) -> Dict:
        """Reject a registration request"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE registration_requests
            SET status = 'rejected',
                reviewed_at = CURRENT_TIMESTAMP,
                reviewed_by = ?,
                admin_notes = ?
            WHERE id = ? AND status = 'pending'
        ''', (admin_username, reason, request_id))

        if cursor.rowcount == 0:
            conn.close()
            return {'success': False, 'message': 'Request not found or already processed'}

        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Request rejected'}

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, password, email, full_name, organization,
                   is_admin, is_active, email_notifications, report_recipients
            FROM users
            WHERE username = ? AND is_active = 1
        ''', (username,))

        user = cursor.fetchone()
        if not user or not self._verify_password(user[2], password):
            conn.close()
            return None

        # Update last login
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        ''', (user[0],))

        conn.commit()
        conn.close()

        return {
            'id': user[0],
            'username': user[1],
            'email': user[3],
            'full_name': user[4],
            'organization': user[5],
            'is_admin': bool(user[6]),
            'email_notifications': bool(user[8]),
            'report_recipients': json.loads(user[9]) if user[9] else [user[3]]
        }

    def get_user_email_config(self, user_id: int) -> Dict:
        """Get user's email configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT email, report_recipients, smtp_server, smtp_port,
                   smtp_username, smtp_password
            FROM users WHERE id = ?
        ''', (user_id,))

        user = cursor.fetchone()
        conn.close()

        if not user:
            return None

        # Use user's SMTP if configured, otherwise fall back to system default
        if user[2]:  # Has custom SMTP
            return {
                'recipients': json.loads(user[1]) if user[1] else [user[0]],
                'smtp_server': user[2],
                'smtp_port': user[3],
                'smtp_username': user[4],
                'smtp_password': user[5]  # Should be decrypted in production
            }
        else:
            # Use system default SMTP with user's recipients
            return {
                'recipients': json.loads(user[1]) if user[1] else [user[0]],
                'smtp_server': os.getenv('SMTP_SERVER'),
                'smtp_port': int(os.getenv('SMTP_PORT', 587)),
                'smtp_username': os.getenv('SMTP_USERNAME'),
                'smtp_password': os.getenv('SMTP_PASSWORD')
            }

    def update_user_email_config(self, user_id: int, recipients: List[str],
                                smtp_config: Dict = None) -> bool:
        """Update user's email configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if smtp_config:
            cursor.execute('''
                UPDATE users
                SET report_recipients = ?,
                    smtp_server = ?,
                    smtp_port = ?,
                    smtp_username = ?,
                    smtp_password = ?
                WHERE id = ?
            ''', (json.dumps(recipients), smtp_config.get('server'),
                 smtp_config.get('port'), smtp_config.get('username'),
                 smtp_config.get('password'), user_id))
        else:
            cursor.execute('''
                UPDATE users SET report_recipients = ? WHERE id = ?
            ''', (json.dumps(recipients), user_id))

        conn.commit()
        conn.close()
        return True

    def log_activity(self, user_id: int, action: str, details: Dict = None,
                    ip_address: str = None, user_agent: str = None):
        """Log user activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO user_activity (user_id, action, details, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, action, json.dumps(details) if details else None,
             ip_address, user_agent))

        conn.commit()
        conn.close()

    def log_api_usage(self, user_id: int, endpoint: str, method: str,
                     response_code: int, response_time_ms: int):
        """Log API usage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO api_usage (user_id, endpoint, method, response_code, response_time_ms)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, endpoint, method, response_code, response_time_ms))

        # Update daily API call counter
        cursor.execute('''
            UPDATE users
            SET api_calls_today = api_calls_today + 1
            WHERE id = ?
        ''', (user_id,))

        conn.commit()
        conn.close()

    def get_user_statistics(self, user_id: int, days: int = 30) -> Dict:
        """Get user activity statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since_date = datetime.now() - timedelta(days=days)

        # Activity count
        cursor.execute('''
            SELECT COUNT(*), action
            FROM user_activity
            WHERE user_id = ? AND timestamp > ?
            GROUP BY action
        ''', (user_id, since_date))

        activities = {row[1]: row[0] for row in cursor.fetchall()}

        # API usage
        cursor.execute('''
            SELECT COUNT(*), AVG(response_time_ms)
            FROM api_usage
            WHERE user_id = ? AND timestamp > ?
        ''', (user_id, since_date))

        api_stats = cursor.fetchone()

        # Report generation
        cursor.execute('''
            SELECT COUNT(*), report_type
            FROM report_history
            WHERE user_id = ? AND generated_at > ?
            GROUP BY report_type
        ''', (user_id, since_date))

        reports = {row[1]: row[0] for row in cursor.fetchall()}

        conn.close()

        return {
            'activities': activities,
            'api_calls': api_stats[0] if api_stats else 0,
            'avg_response_time': api_stats[1] if api_stats else 0,
            'reports_generated': reports
        }

    def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, email, full_name, organization,
                   is_admin, is_active, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        ''')

        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'full_name': row[3],
                'organization': row[4],
                'is_admin': bool(row[5]),
                'is_active': bool(row[6]),
                'created_at': row[7],
                'last_login': row[8]
            })

        conn.close()
        return users