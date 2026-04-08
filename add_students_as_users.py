#!/usr/bin/env python
"""
Add students from dataset as login users
Allows you to login with any student's Register Number and a password
"""

import os
import sqlite3
from auth.password_utils import PasswordManager

def resolve_db_path(db_path: str) -> str:
    if os.path.exists(db_path):
        return db_path
    fallback = "students.db" if os.path.basename(db_path) == "students_2024.db" else "students_2024.db"
    if os.path.exists(fallback):
        return fallback
    return db_path

def add_students_as_users(db_path="students_2024.db", password="student123"):
    """
    Add all students from the dataset as login users
    Default password: student123 (change it!)
    """
    db_path = resolve_db_path(db_path)
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()
    
    try:
        # Get all students with valid register numbers
        cursor.execute("""
            SELECT Student_Name, Register_Number, Email_ID 
            FROM students
            WHERE Register_Number IS NOT NULL AND Register_Number != ''
        """)
        
        students = cursor.fetchall()
        print(f"\n📚 Found {len(students)} students. Adding as login users...\n")
        
        added = 0
        skipped = 0
        
        for name, register_no, email in students:
            # Skip if register number is None/empty
            if not register_no:
                skipped += 1
                continue
            
            # Check if user already exists
            cursor.execute(
                "SELECT user_id FROM users WHERE register_number = ?",
                (register_no,)
            )
            
            if cursor.fetchone():
                print(f"  ⏭️  Skipped: {register_no} ({name}) - Already exists")
                skipped += 1
                continue
            
            # Add user
            try:
                password_hash = PasswordManager.hash_password(password)
                cursor.execute("""
                    INSERT INTO users 
                    (register_number, password_hash, full_name, email, is_active, created_at)
                    VALUES (?, ?, ?, ?, 1, datetime('now'))
                """, (register_no, password_hash, name, email or "no-email@college.edu"))
                
                print(f"  ✅ Added: {register_no} ({name})")
                added += 1
            except Exception as e:
                print(f"  ❌ Failed: {register_no} - {str(e)}")
                skipped += 1
        
        conn.commit()
        
        print(f"\n" + "="*60)
        print(f"✅ SUCCESSFULLY ADDED {added} STUDENTS")
        print(f"⏭️  SKIPPED {skipped} (already exist)")
        print("="*60)
        print(f"\n🔑 Default Login Password for All Students: '{password}'")
        print(f"\n📝 To login:")
        print(f"   Register Number: (any from the list above)")
        print(f"   Password: {password}")
        print(f"\n⚠️  SECURITY NOTE: Change the default password in production!")
        print("="*60 + "\n")
        
        return added
    
    finally:
        conn.close()

def get_student_logins(db_path="students_2024.db"):
    """List all available student login accounts"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT register_number, full_name, email, created_at 
            FROM users 
            WHERE register_number != 'DEMO001'
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("\n❌ No student users found. Run add_students_as_users() first.\n")
            return
        
        print("\n" + "="*80)
        print("📋 AVAILABLE STUDENT LOGIN ACCOUNTS")
        print("="*80)
        print(f"{'Register Number':<15} {'Name':<25} {'Email':<35}")
        print("-"*80)
        
        for register, name, email, created in users:
            print(f"{register:<15} {name:<25} {email:<35}")
        
        print("-"*80)
        print(f"Total: {len(users)} student accounts\n")
        print("="*80 + "\n")
    
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("🎓 STUDENT PORTAL - ADD STUDENTS AS LOGIN USERS")
    print("="*60)
    
    # Option 1: Add students from dataset
    if len(sys.argv) > 1:
        password = sys.argv[1]
        print(f"\nUsing custom password: {password}")
    else:
        password = "student123"
        print(f"\nUsing default password: {password}")
    
    added = add_students_as_users(password=password)
    
    # Show all available logins
    print("\n" + "="*60)
    print("📍 CHECKING ALL AVAILABLE LOGINS...")
    print("="*60)
    get_student_logins()
    
    print("\n✅ Done! You can now login with any student's Register Number\n")
