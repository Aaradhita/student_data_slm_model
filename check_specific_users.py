import sqlite3

conn = sqlite3.connect('students_2024.db')
cur = conn.cursor()
for reg in ['REG1000', 'REG1198', 'DEMO001']:
    cur.execute('SELECT user_id, register_number, email FROM users WHERE register_number = ?', (reg,))
    row = cur.fetchone()
    print(reg, '=>', row)
conn.close()
