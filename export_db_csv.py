import sqlite3
import csv
from config import ACTIVE_CONFIG

DB = ACTIVE_CONFIG.DATABASE_PATH
TABLE = ACTIVE_CONFIG.DATA_TABLE
OUT = 'student_dataset_extended.csv'

def export_csv():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {TABLE}")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        for r in rows:
            writer.writerow(r)
    conn.close()
    print(f'Exported {len(rows)} rows to {OUT}')

if __name__ == '__main__':
    export_csv()
