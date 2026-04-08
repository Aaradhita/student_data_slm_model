import sqlite3
import hashlib
from datetime import datetime
import os
try:
    import pandas as pd
except Exception:
    pd = None

from config import ACTIVE_CONFIG

DB_PATH = ACTIVE_CONFIG.DATABASE_PATH
TABLE = ACTIVE_CONFIG.DATA_TABLE
ID_COL = ACTIVE_CONFIG.USER_ID_COLUMN
NAME_COL = ACTIVE_CONFIG.USER_NAME_COLUMN

NEW_COLUMNS = [
    'Emergency_Contact',
    'Guardian_Name',
    'Hostel_Room',
    'Transportation_Mode',
    'LinkedIn_Profile',
    'Internship_Status',
    'Year_of_Passing',
    'Hobbies',
    'Blood_Group',
    'Nationality'
]

HOBBIES = ['Reading', 'Sports', 'Music', 'Travel', 'Coding', 'Drawing', 'Photography']
TRANSPORT = ['Bus', 'Walk', 'Bike', 'Car']
INTERNSHIP = ['Not Started', 'Ongoing', 'Completed']
BLOOD = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']


def md_hash(s: str) -> int:
    return int(hashlib.md5(s.encode('utf-8')).hexdigest()[:8], 16)


def ensure_columns(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({TABLE})")
    existing = [r[1] for r in cur.fetchall()]
    for col in NEW_COLUMNS:
        if col not in existing:
            print(f"Adding column: {col}")
            cur.execute(f"ALTER TABLE {TABLE} ADD COLUMN {col} TEXT")
    conn.commit()


def generate_values(register, name, join_date):
    h = md_hash(register)
    # Emergency contact: deterministic 10-digit
    ec = '9' + str(h % 10_000_000_00).zfill(9)
    guardian = f"Parent of {name}" if name else 'Parent'
    room = f"H{(h % 500) + 1}"
    transport = TRANSPORT[h % len(TRANSPORT)]
    linkedin = 'https://linkedin.com/in/' + (name.lower().replace(' ', '-') if name else register.lower())
    internship = INTERNSHIP[h % len(INTERNSHIP)]
    year_of_passing = ''
    if join_date:
        try:
            y = datetime.strptime(join_date, '%Y-%m-%d').year
            year_of_passing = str(y + 4)
        except Exception:
            year_of_passing = ''
    # hobbies: pick two
    h1 = HOBBIES[h % len(HOBBIES)]
    h2 = HOBBIES[(h // 3) % len(HOBBIES)]
    hobbies = f"{h1}, {h2}"
    blood = BLOOD[h % len(BLOOD)]
    nationality = 'Indian'
    return {
        'Emergency_Contact': ec,
        'Guardian_Name': guardian,
        'Hostel_Room': room,
        'Transportation_Mode': transport,
        'LinkedIn_Profile': linkedin,
        'Internship_Status': internship,
        'Year_of_Passing': year_of_passing,
        'Hobbies': hobbies,
        'Blood_Group': blood,
        'Nationality': nationality
    }


def populate_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_columns(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT {ID_COL}, {NAME_COL}, College_Joining_Date FROM {TABLE}")
    rows = cur.fetchall()
    print(f"Found {len(rows)} records to update")
    for r in rows:
        reg = str(r[ID_COL])
        name = r[NAME_COL] if NAME_COL in r.keys() else ''
        join_date = r['College_Joining_Date'] if 'College_Joining_Date' in r.keys() else None
        vals = generate_values(reg, name, join_date)
        set_clause = ', '.join([f"{c} = ?" for c in vals.keys()])
        params = list(vals.values()) + [reg]
        sql = f"UPDATE {TABLE} SET {set_clause} WHERE {ID_COL} = ?"
        cur.execute(sql, params)
    conn.commit()
    conn.close()
    print("Database population complete")


def update_excel():
    # Prefer to not overwrite original; write extended file
    src_files = ['student_dataset.xlsx', 'student_dataset.xls', 'student_dataset.csv', 'students_2024.xlsx']
    src = None
    for f in src_files:
        p = os.path.join(os.getcwd(), f)
        if os.path.exists(p):
            src = p
            break
    if pd is None:
        print('pandas not installed; skipping Excel update')
        return
    if src:
        print(f"Updating Excel: {src}")
        try:
            df = pd.read_excel(src)
        except Exception:
            try:
                df = pd.read_csv(src)
            except Exception:
                print('Could not read source dataset file; creating from DB')
                df = None
        if df is None:
            # create from DB
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(f"SELECT * FROM {TABLE}", conn)
            conn.close()
        # add columns if missing and populate by Register_Number
        if ID_COL not in df.columns:
            print(f"ID column {ID_COL} not in spreadsheet; skipping Excel update")
            return
        # Build map from DB for new columns
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"SELECT {ID_COL}, {', '.join(NEW_COLUMNS)} FROM {TABLE}")
        dbmap = {row[ID_COL]: {col: row[col] for col in NEW_COLUMNS} for row in cur.fetchall()}
        conn.close()
        for col in NEW_COLUMNS:
            if col not in df.columns:
                df[col] = pd.NA
            df[col] = df[col].astype(object)
        for idx, row in df.iterrows():
            reg = row.get(ID_COL)
            if reg in dbmap:
                for col in NEW_COLUMNS:
                    df.at[idx, col] = dbmap[reg].get(col, '')
        out = os.path.join(os.getcwd(), 'student_dataset_extended.xlsx')
        df.to_excel(out, index=False)
        print(f"Excel updated and saved to: {out}")
    else:
        # Create excel from DB
        print('No source spreadsheet found; creating student_dataset_extended.xlsx from DB')
        if pd is None:
            print('pandas not installed; cannot create spreadsheet')
            return
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(f"SELECT * FROM {TABLE}", conn)
        conn.close()
        out = os.path.join(os.getcwd(), 'student_dataset_extended.xlsx')
        df.to_excel(out, index=False)
        print(f"Excel created: {out}")


if __name__ == '__main__':
    print('Starting: add_more_columns.py')
    populate_db()
    update_excel()
    print('Done')
