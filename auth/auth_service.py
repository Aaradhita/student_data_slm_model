import jwt
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from auth.password_utils import PasswordManager
import os

class AuthService:
    """Handle all authentication logic"""
    
    def __init__(self, db_path: str = "students_2024.db"):
        self.db_path = db_path
        self.secret_key = os.getenv("SECRET_KEY", "student-portal-secret-key-change-in-production")
        self.access_token_expire_minutes = 1440  # 24 hours instead of 15 minutes
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, user_id: int, register_number: str, 
                          dataset_id: int = 1) -> Tuple[str, int]:
        """Create JWT access token"""
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "user_id": user_id,
            "register_number": register_number,
            "dataset_id": dataset_id,
            "exp": int(exp.timestamp()),
            "iat": int(now.timestamp()),
            "jti": PasswordManager.generate_token(),
            "type": "access"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token, self.access_token_expire_minutes * 60
    
    def create_refresh_token(self, user_id: int, register_number: str) -> str:
        """Create JWT refresh token"""
        now = datetime.now(timezone.utc)
        exp = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "user_id": user_id,
            "register_number": register_number,
            "exp": int(exp.timestamp()),
            "iat": int(now.timestamp()),
            "jti": PasswordManager.generate_token(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            # jwt.decode automatically checks expiration, so we don't need to manually check
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError as e:
            return None
        except Exception as e:
            return None
    
    def login(self, register_number: str, password: str) -> Optional[dict]:
        """Authenticate user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user from database
            cursor.execute("""
                SELECT user_id, register_number, password_hash, full_name, email 
                FROM users 
                WHERE register_number = ?
            """, (register_number,))
            
            user = cursor.fetchone()
            
            if not user:
                return None
            
            user_id, reg_no, password_hash, full_name, email = user
            
            # Verify password
            if not PasswordManager.verify_password(password, password_hash):
                return None
            
            # Update last login
            cursor.execute("""
                UPDATE users 
                SET last_login = datetime('now') 
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            
            return {
                "user_id": user_id,
                "register_number": reg_no,
                "full_name": full_name,
                "email": email
            }
        
        finally:
            conn.close()
    
    def register_user(self, register_number: str, password: str, 
                     full_name: str, email: str) -> bool:
        """Register new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = PasswordManager.hash_password(password)
            
            cursor.execute("""
                INSERT INTO users 
                (register_number, password_hash, full_name, email, is_active, created_at)
                VALUES (?, ?, ?, ?, 1, datetime('now'))
            """, (register_number, password_hash, full_name, email))
            
            conn.commit()
            return True
        
        except sqlite3.IntegrityError:
            return False  # User already exists
        
        finally:
            conn.close()
    
    def request_password_reset(self, register_number: str) -> Optional[str]:
        """Generate password reset token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if user exists
            cursor.execute("SELECT user_id, email FROM users WHERE register_number = ?", (register_number,))
            user = cursor.fetchone()
            
            # If user does not exist, try to create a login account from the students dataset
            if not user:
                cursor.execute("SELECT Student_Name, Email_ID FROM students WHERE Register_Number = ?", (register_number,))
                student = cursor.fetchone()
                if not student:
                    return None
                full_name, email = student
                password_hash = PasswordManager.hash_password("student123")
                cursor.execute("""
                    INSERT INTO users 
                    (register_number, password_hash, full_name, email, is_active, created_at)
                    VALUES (?, ?, ?, ?, 1, datetime('now'))
                """, (register_number, password_hash, full_name, email or "student@college.edu"))
                conn.commit()
                user_id = cursor.lastrowid
            else:
                user_id, email = user
            
            # Generate reset token
            reset_token = PasswordManager.generate_token()
            reset_expires = datetime.now(timezone.utc) + timedelta(hours=24)
            
            # Store token
            cursor.execute("""
                UPDATE users 
                SET reset_token = ?, reset_token_expires = ? 
                WHERE user_id = ?
            """, (reset_token, reset_expires.isoformat(), user_id))
            
            conn.commit()
            return reset_token
        
        finally:
            conn.close()
    
    def verify_reset_token(self, register_number: str, reset_token: str) -> bool:
        """Verify reset token is valid and not expired"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT reset_token, reset_token_expires FROM users 
                WHERE register_number = ?
            """, (register_number,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            stored_token, expires_str = result
            
            # Check token matches
            if stored_token != reset_token:
                return False
            
            # Check expiration
            if expires_str:
                expires = datetime.fromisoformat(expires_str)
                if datetime.now(timezone.utc) > expires:
                    return False
            
            return True
        
        finally:
            conn.close()
    
    def reset_password(self, register_number: str, reset_token: str, new_password: str) -> bool:
        """Reset password with valid token"""
        # Verify token first
        if not self.verify_reset_token(register_number, reset_token):
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = PasswordManager.hash_password(new_password)
            
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, reset_token = NULL, reset_token_expires = NULL 
                WHERE register_number = ?
            """, (password_hash, register_number))
            
            conn.commit()
            return True
        
        finally:
            conn.close()
