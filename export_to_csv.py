"""
Export database to CSV file.
"""

import sqlite3
import csv
from config import ACTIVE_CONFIG

DB_PATH = ACTIVE_CONFIG.DATABASE_PATH
TABLE = ACTIVE_CONFIG.DATA_TABLE
OUTPUT_FILE = 'students_data_updated.csv'

def export_to_csv():
    """Export all data from database to CSV."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get all data
    cur.execute(f"SELECT * FROM {TABLE}")
    rows = cur.fetchall()
    
    if not rows:
        print(f"No data found in {TABLE}")
        conn.close()
        return
    
    # Get column names
    columns = [desc[0] for desc in cur.description]
    
    # Write to CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[col] for col in columns])
    
    conn.close()
    print(f"✓ Exported {len(rows)} records to {OUTPUT_FILE}")
    print(f"  Columns: {len(columns)}")
    print(f"  Columns list: {', '.join(columns[:10])}...")

if __name__ == '__main__':
    export_to_csv()
