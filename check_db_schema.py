import sqlite3

conn = sqlite3.connect('students_2024.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print(f"Tables: {tables}")

for table in tables:
    if table != 'sqlite_sequence':
        cur.execute(f'PRAGMA table_info({table})')
        cols = cur.fetchall()
        print(f"\n{table}: {len(cols)} columns")
        if len(cols) > 10:
            print(f"  Columns: {[c[1] for c in cols]}")
        else:
            for col in cols:
                print(f"  - {col[1]} ({col[2]})")
        
conn.close()
