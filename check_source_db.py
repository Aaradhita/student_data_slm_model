import sqlite3

conn = sqlite3.connect('students.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print(f"Tables in students.db: {tables}")

for table in tables:
    cur.execute(f'PRAGMA table_info({table})')
    cols = cur.fetchall()
    print(f"\n{table}: {len(cols)} columns")
    print(f"  Columns: {[c[1] for c in cols]}")
    
    # Check row count
    cur.execute(f'SELECT COUNT(*) FROM {table}')
    count = cur.fetchone()[0]
    print(f"  Rows: {count}")

conn.close()
