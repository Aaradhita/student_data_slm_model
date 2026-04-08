"""
Populate new columns with realistic student data.
Uses deterministic seeding based on Register_Number for reproducibility.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from config import ACTIVE_CONFIG

DB_PATH = ACTIVE_CONFIG.DATABASE_PATH
TABLE = ACTIVE_CONFIG.DATA_TABLE
ID_COL = ACTIVE_CONFIG.USER_ID_COLUMN

# Real data pools
FIRST_NAMES = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Reyansh', 'Sai', 'Rohan',
               'Priya', 'Ananya', 'Diya', 'Isha', 'Sakshi', 'Kavya', 'Neha', 'Pooja']
LAST_NAMES = ['Sharma', 'Singh', 'Patel', 'Kumar', 'Gupta', 'Verma', 'Nair', 'Rao', 'Desai', 'Joshi']

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
HOBBIES_LIST = [
    ('Reading', 'Coding'),
    ('Sports', 'Music'),
    ('Travel', 'Photography'),
    ('Gaming', 'Cooking'),
    ('Drawing', 'Writing'),
    ('Dancing', 'Hiking'),
    ('Movies', 'Technology'),
    ('Yoga', 'Gardening'),
]
TRANSPORT = ['Bus', 'Walk', 'Bike', 'Auto', 'Car', 'Train']
INTERNSHIP_STATUSES = ['Not Started', 'Ongoing', 'Completed']
COMPANIES = [
    'TCS', 'Infosys', 'Wipro', 'Accenture', 'IBM', 'Google', 'Amazon',
    'Microsoft', 'Apple', 'Facebook', 'Adobe', 'Salesforce', 'Deloitte'
]
COUNTRIES = ['India', 'USA', 'Canada', 'UK', 'Australia', 'Singapore', 'Germany', 'Japan']

def seed_from_register(register_num: str) -> random.Random:
    """Create seeded RNG based on register number for reproducibility."""
    seed = sum(ord(c) for c in register_num)
    return random.Random(seed)

def generate_realistic_data(register: str, name: str, join_date_str: str) -> dict:
    """Generate realistic data for all new columns."""
    rng = seed_from_register(register)
    
    # Parse join date
    try:
        join_date = datetime.strptime(join_date_str, '%Y-%m-%d') if join_date_str else datetime.now()
    except:
        join_date = datetime.now()
    
    # Emergency Contact: realistic 10-digit Indian mobile number (9xxx)
    ec = '9' + ''.join(rng.choices('0123456789', k=9))
    
    # Guardian Name: Parent/Guardian + random suffix
    guardian_rel = rng.choice(['Mr.', 'Mrs.'])
    first = rng.choice(FIRST_NAMES)
    last = rng.choice(LAST_NAMES)
    guardian = f"{guardian_rel} {first} {last}"
    
    # Hostel Room: Building + Room number (realistic format)
    building = rng.choice(['A', 'B', 'C', 'D', 'E'])
    floor = rng.choice(range(1, 6))
    room = rng.choice(range(1, 11))
    hostel_room = f"{building}{floor}{room:02d}"
    
    # Transportation: realistic modes for campus
    transport = rng.choice(TRANSPORT)
    
    # LinkedIn Profile: realistic URL
    first_name = name.split()[0].lower() if name else register.lower()
    last_name = name.split()[-1].lower() if name and len(name.split()) > 1 else 'student'
    linkedin = f"https://linkedin.com/in/{first_name}-{last_name}-{register.lower()}"
    
    # Internship Status + Company (if internship started)
    internship = rng.choice(INTERNSHIP_STATUSES)
    if internship == 'Ongoing':
        company = rng.choice(COMPANIES)
        internship = f"Ongoing at {company}"
    elif internship == 'Completed':
        company = rng.choice(COMPANIES)
        internship = f"Completed at {company}"
    
    # Year of Passing: join_date year + 4 (standard 4-year program)
    year_of_passing = str(join_date.year + 4)
    
    # Hobbies: pick one pair
    hobbies_pair = rng.choice(HOBBIES_LIST)
    hobbies = f"{hobbies_pair[0]}, {hobbies_pair[1]}"
    
    # Blood Group
    blood = rng.choice(BLOOD_GROUPS)
    
    # Nationality: mostly Indian, some international
    nationality = rng.choice(COUNTRIES) if rng.random() < 0.85 else 'India'
    
    return {
        'Emergency_Contact': ec,
        'Guardian_Name': guardian,
        'Hostel_Room': hostel_room,
        'Transportation_Mode': transport,
        'LinkedIn_Profile': linkedin,
        'Internship_Status': internship,
        'Year_of_Passing': year_of_passing,
        'Hobbies': hobbies,
        'Blood_Group': blood,
        'Nationality': nationality
    }

def populate_realistic():
    """Update all student records with realistic data."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get all students
    cur.execute(f"SELECT {ID_COL}, {ACTIVE_CONFIG.USER_NAME_COLUMN}, College_Joining_Date FROM {TABLE}")
    rows = cur.fetchall()
    
    print(f"Populating {len(rows)} student records with realistic data...")
    
    for i, row in enumerate(rows):
        reg = str(row[ID_COL])
        name = row[ACTIVE_CONFIG.USER_NAME_COLUMN] if ACTIVE_CONFIG.USER_NAME_COLUMN in row.keys() else ''
        join_date = row['College_Joining_Date'] if 'College_Joining_Date' in row.keys() else None
        
        vals = generate_realistic_data(reg, name, join_date)
        
        set_clause = ', '.join([f"{c} = ?" for c in vals.keys()])
        params = list(vals.values()) + [reg]
        sql = f"UPDATE {TABLE} SET {set_clause} WHERE {ID_COL} = ?"
        cur.execute(sql, params)
        
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(rows)}")
    
    conn.commit()
    conn.close()
    print(f"✓ Successfully populated all {len(rows)} records")

if __name__ == '__main__':
    print('Starting: populate_realistic_data.py')
    populate_realistic()
    print('Done')
