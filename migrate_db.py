import sqlite3
import os

db_path = r'c:\Users\pol\Documents\GitHub\penjadwalan2\instance\database.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Rename table course to practicum
    print("Renaming table 'course' to 'practicum'...")
    cursor.execute("ALTER TABLE course RENAME TO practicum;")
    
    # 2. Rename column course_name to practicum_name
    print("Renaming column 'course_name' to 'practicum_name'...")
    cursor.execute("ALTER TABLE practicum RENAME COLUMN course_name TO practicum_name;")
    
    conn.commit()
    print("Migration successful!")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
    conn.rollback()
finally:
    conn.close()
