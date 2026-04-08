"""
IMPROVED Excel Sync - Works with ANY columns
Automatically detects new/removed columns and syncs them
"""

import sqlite3
import pandas as pd
import os
from config import ACTIVE_CONFIG

DB_PATH = ACTIVE_CONFIG.DATABASE_PATH
TABLE = ACTIVE_CONFIG.DATA_TABLE
ID_COL = ACTIVE_CONFIG.USER_ID_COLUMN

# keep mapping of excel file -> sanitized->original
column_maps = {}

def get_excel_files():
    """Find all Excel files in current directory"""
    cwd = os.getcwd()
    files = []
    for f in os.listdir(cwd):
        if f.endswith(('.xlsx', '.xls')) and not f.startswith('~'):
            files.append(os.path.join(cwd, f))
    return files

def sync_excel_to_db(excel_file):
    """Read Excel and update database with new columns/values"""
    print(f"\n📄 Reading Excel: {excel_file}")
    
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"  ❌ Error reading Excel: {e}")
        return False
    
    print(f"  ✓ Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current table columns (lowercased for case-insensitive checks)
    cursor.execute(f"PRAGMA table_info({TABLE})")
    db_columns = {row[1].lower() for row in cursor.fetchall()}
    
    # Build sanitized mapping to avoid SQL errors
    def sanitize(name: str) -> str:
        # keep alphanumeric and underscores, replace spaces and remove punctuation
        import re
        s = name.strip()
        s = re.sub(r"\s+", "_", s)                # spaces -> underscore
        s = re.sub(r'[()\/\\"]', '', s)      # remove parentheses, slashes, quotes
        s = re.sub(r"[^0-9A-Za-z_]", "", s)       # keep only letters, numbers, underscore
        if re.match(r"^[0-9]", s):
            s = "_" + s
        return s or "col"
    
    orig_cols = list(df.columns)
    sanitized = {}
    used = set()
    for col in orig_cols:
        san = sanitize(col)
        # handle collisions
        i = 1
        base = san
        while san in used:
            san = f"{base}_{i}"
            i += 1
        used.add(san)
        sanitized[col] = san
    
    # mapping to convert back later
    reverse_map = {san: orig for orig, san in sanitized.items()}
    column_maps[excel_file] = reverse_map

    # rename dataframe columns to sanitized names for DB operations
    df = df.rename(columns=sanitized)
    excel_columns = set(df.columns)
    
    # Find new columns (compare lowercase values)
    new_columns = {col for col in excel_columns if col.lower() not in db_columns}
    
    if new_columns:
        print(f"\n  🆕 New columns found: {', '.join(new_columns)}")
        for col in new_columns:
            print(f"     Adding column: {col}")
            try:
                cursor.execute(f"ALTER TABLE {TABLE} ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError as e:
                if 'already exists' not in str(e):
                    print(f"     ⚠️  Error: {e}")
        conn.commit()
    
    # Update data from Excel
    print(f"\n  📊 Syncing data from Excel to Database...")
    
    if ID_COL not in df.columns:
        print(f"  ❌ Column '{ID_COL}' not found in Excel!")
        conn.close()
        return False
    
    # helper to normalize cell value
    def norm(v):
        # convert NaN to None
        if pd.isna(v):
            return None
        # convert Timestamp to ISO string
        if hasattr(v, 'isoformat') and hasattr(v, 'year'):
            try:
                return v.isoformat()
            except Exception:
                pass
        # if it's a float that represents an integer, return int
        if isinstance(v, float):
            if v.is_integer():
                return int(v)
        # if it's numeric string ending with .0, strip it
        if isinstance(v, str) and v.endswith('.0') and v.replace('.0','').isdigit():
            return v[:-2]
        return v
    
    update_count = 0
    for idx, row in df.iterrows():
        try:
            student_id = norm(row.get(ID_COL))
            
            # Check if exists in DB
            cursor.execute(f"SELECT 1 FROM {TABLE} WHERE {ID_COL} = ?", (student_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing record
                cols_to_update = [col for col in excel_columns if col != ID_COL]
                
                if cols_to_update:
                    set_clause = ', '.join([f'"{col}" = ?' for col in cols_to_update])
                    values = [norm(row[col]) for col in cols_to_update]
                    values.append(student_id)
                    
                    sql = f"UPDATE {TABLE} SET {set_clause} WHERE {ID_COL} = ?"
                    cursor.execute(sql, values)
                    update_count += 1
            else:
                # Insert new record
                cols_to_insert = [ID_COL] + [col for col in excel_columns if col != ID_COL]
                quoted = [f'"{c}"' for c in cols_to_insert]
                placeholders = ', '.join(['?' for _ in cols_to_insert])
                values = [norm(row[col]) for col in cols_to_insert]
                
                sql = f"INSERT INTO {TABLE} ({', '.join(quoted)}) VALUES ({placeholders})"
                cursor.execute(sql, values)
                update_count += 1
        
        except Exception as e:
            print(f"  ⚠️  Row {idx}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"  ✓ Updated/inserted {update_count} records")
    return True

def sync_db_to_excel(excel_file):
    """Update Excel with latest data from database"""
    print(f"\n💾 Updating Excel: {excel_file}")
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Read all data from DB
        df_db = pd.read_sql_query(f"SELECT * FROM {TABLE}", conn)
        # convert DB values to string so that assignments won't conflict
        df_db = df_db.fillna('').astype(str)
        
        # Read Excel to preserve formatting
        df_excel = pd.read_excel(excel_file)
        # start with all Excel cells as strings/object to prevent dtype issues
        result = df_excel.fillna('').astype(str)
        
        for col in df_db.columns:
            if col not in result.columns:
                result[col] = None
        
        # Update values from DB
        if ID_COL in df_db.columns and ID_COL in result.columns:
            db_map = dict(zip(df_db[ID_COL], range(len(df_db))))
            
            for col in df_db.columns:
                if col != ID_COL:
                    for idx in range(len(result)):
                        student_id = result.at[idx, ID_COL]
                        if student_id in db_map:
                            db_idx = db_map[student_id]
                            result.at[idx, col] = df_db.at[db_idx, col]
        
        # convert all values to string (avoid dtype/overflow issues)
        result = result.fillna('').astype(str)
        # ensure every column has object dtype to prevent pandas trying to coerce during to_excel
        for col in result.columns:
            result[col] = result[col].astype(object)
        # restore original column names if we have mapping
        reverse_map = column_maps.get(excel_file, {})
        if reverse_map:
            result = result.rename(columns=reverse_map)
        # Save back to Excel
        try:
            result.to_excel(excel_file, index=False)
            print(f"  ✓ Excel updated: {len(result)} rows, {len(result.columns)} columns")
        except Exception as w:
            # print dtypes for debugging
            print("  ❌ Failed to write Excel, dtypes:")
            print(result.dtypes)
            raise
    
    except Exception as e:
        print(f"  ❌ Error updating Excel: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

def main():
    """Two-way sync between Excel and Database"""
    print("=" * 70)
    print("IMPROVED EXCEL ↔️ DATABASE SYNC")
    print("=" * 70)
    
    excel_files = get_excel_files()
    
    if not excel_files:
        print("\n❌ No Excel files found!")
        return
    
    print(f"\nFound {len(excel_files)} Excel file(s):")
    for f in excel_files:
        print(f"  - {os.path.basename(f)}")
    
    for excel_file in excel_files:
        # Step 1: Excel → Database (import new columns and data)
        sync_excel_to_db(excel_file)
        
        # Step 2: Database → Excel (export latest data)
        sync_db_to_excel(excel_file)
    
    print("\n" + "=" * 70)
    print("✅ Sync Complete!")
    print("=" * 70)
    print("\n📊 To verify:")
    print(f"   python -c \"from app import app; from fastapi.testclient import TestClient")
    print(f"   c = TestClient(app); print(c.get('/api/schema').json()['columns'])\"")

if __name__ == '__main__':
    main()
