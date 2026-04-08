#!/usr/bin/env python
"""
Copy students data from students.db to students_2024.db
Then add them as login users
"""

import sqlite3
from auth.password_utils import PasswordManager

def copy_students_to_new_db():
    """Copy students from students.db to students_2024.db"""
    print("\n📋 Copying students data from students.db → students_2024.db...")
    
    # Connect to both databases
    src_conn = sqlite3.connect('students.db')
    src_cursor = src_conn.cursor()
    
    dst_conn = sqlite3.connect('students_2024.db')
    dst_cursor = dst_conn.cursor()
    
    try:
        # Get column names from destination table
        dst_cursor.execute("PRAGMA table_info(students)")
        dst_columns = [row[1] for row in dst_cursor.fetchall()]
        
        # Get column names from source table
        src_cursor.execute("PRAGMA table_info(students)")
        src_columns = [row[1] for row in src_cursor.fetchall()]
        
        # Determine which columns to copy (only those that exist in both)
        columns_to_copy = [col for col in src_columns if col in dst_columns]
        
        # Get students from source with specific columns
        column_list = ", ".join(columns_to_copy)
        src_cursor.execute(f"SELECT {column_list} FROM students")
        students = src_cursor.fetchall()
        
        print(f"Found {len(students)} students to copy...")
        print(f"Copying {len(columns_to_copy)} columns: {columns_to_copy}")
        
        # Insert students with proper column mapping
        inserted = 0
        placeholders = ", ".join(["?" for _ in columns_to_copy])
        insert_columns = ", ".join(columns_to_copy)
        insert_query = f"INSERT OR IGNORE INTO students ({insert_columns}) VALUES ({placeholders})"
        
        for student in students:
            try:
                dst_cursor.execute(insert_query, student)
                inserted += 1
            except Exception as e:
                print(f"  ⚠️  Error inserting student: {e}")
        
        dst_conn.commit()
        print(f"✅ Successfully copied {inserted} students\n")
        
        return len(students)
    
    finally:
        src_conn.close()
        dst_conn.close()

def add_students_as_users(password="student123"):
    """Add students from students_2024.db as login users"""
    print(f"👤 Adding students as login users (password: '{password}')...\n")
    
    conn = sqlite3.connect('students_2024.db')
    cursor = conn.cursor()
    
    try:
        # Get all students
        cursor.execute("""
            SELECT Student_Name, Register_Number, Email_ID 
            FROM students
        """)
        
        students = cursor.fetchall()
        print(f"Found {len(students)} students\n")
        
        added = 0
        skipped = 0
        
        for idx, (name, register_no, email) in enumerate(students, 1):
            # Check if user already exists
            cursor.execute(
                "SELECT user_id FROM users WHERE register_number = ?",
                (register_no,)
            )
            
            if cursor.fetchone():
                skipped += 1
                continue
            
            # Add user
            try:
                password_hash = PasswordManager.hash_password(password)
                cursor.execute("""
                    INSERT INTO users 
                    (register_number, password_hash, full_name, email, is_active, created_at)
                    VALUES (?, ?, ?, ?, 1, datetime('now'))
                """, (register_no, password_hash, name, email or "student@college.edu"))
                
                if idx <= 5:  # Show first 5
                    print(f"  ✅ {register_no:<10} {name[:40]:<40}")
                elif idx == 6:
                    print(f"  ✅ ... and {len(students) - 5} more students")
                
                added += 1
            except Exception as e:
                print(f"  ❌ {register_no}: {str(e)}")
                skipped += 1
        
        conn.commit()
        
        print(f"\n" + "="*70)
        print(f"✅ SUCCESSFULLY ADDED {added} STUDENT LOGIN ACCOUNTS")
        print("="*70)
        print(f"\n🔑 Login Details for All Students:")
        print(f"   Register Number: (any student register number)")
        print(f"   Password: {password}")
        print(f"\n📝 Example:")
        print(f"   Register Number: (see first login from list above)")
        print(f"   Password: {password}")
        print("="*70 + "\n")
        
        return added
    
    finally:
        conn.close()

def show_available_logins():
    """Show available student logins"""
    conn = sqlite3.connect('students_2024.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT register_number, full_name, email
            FROM users 
            WHERE register_number != 'DEMO001'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        users = cursor.fetchall()
        
        if users:
            print("\n" + "="*70)
            print("📋 FIRST 5 STUDENT ACCOUNTS (use any of these to login)")
            print("="*70)
            for register, name, email in users:
                print(f"  Register: {register:<10} Name: {name:<35}")
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE register_number != 'DEMO001'")
            total = cursor.fetchone()[0]
            print(f"\n  ... and {total - 5} more student accounts available\n")
            print("="*70 + "\n")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎓 SETTING UP STUDENT PORTAL WITH REAL STUDENT DATA")
    print("="*70)
    
    # Step 1: Copy student data
    copy_students_to_new_db()
    
    # Step 2: Add students as users
    add_students_as_users(password="student123")
    
    # Step 3: Show available logins
    show_available_logins()
    
    print("✅ Setup complete! Restart the server to apply changes.\n")
    print("   Run: python app.py\n")
