import sqlite3
import os
from auth.password_utils import PasswordManager

def create_users_table(db_path: str = "students_2024.db"):
    """Create users table with authentication fields"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                register_number TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                reset_token TEXT,
                reset_token_expires TIMESTAMP,
                UNIQUE(register_number)
            )
        """)
        
        # Add reset token columns if they don't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP")
            conn.commit()
            print("[+] Added reset token columns to users table")
        except sqlite3.OperationalError:
            pass  # Columns already exist
        
        conn.commit()
        print("[+] Users table created successfully")
        return True
    
    except sqlite3.OperationalError as e:
        print(f"Table may already exist: {e}")
        return True
    
    finally:
        conn.close()

def create_audit_log_table(db_path: str = "students_2024.db"):
    """Create audit log table for tracking access"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                resource TEXT,
                status TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        print("[+] Audit logs table created successfully")
        return True
    
    except sqlite3.OperationalError as e:
        print(f"Table may already exist: {e}")
        return True
    
    finally:
        conn.close()

def seed_demo_user(db_path: str = "students_2024.db"):
    """Add a demo user for testing"""
    from auth.auth_service import AuthService
    auth = AuthService(db_path)
    
    # Try to register demo user
    success = auth.register_user(
        register_number="DEMO001",
        password="demo@123",
        full_name="Demo Student",
        email="demo@student.com"
    )
    
    if success:
        print("[+] Demo user created (Register: DEMO001, Password: demo@123)")
    else:
        print("[!] Demo user already exists")
    
    return success

def initialize_database():
    """Initialize all necessary database tables"""
    print("[*] Initializing database...")
    create_users_table()
    create_audit_log_table()
    seed_demo_user()
    print("[+] Database initialization complete!\n")

if __name__ == "__main__":
    initialize_database()
