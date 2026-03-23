import sqlite3
import os

def migrate_db():
    db_path = 'database.db'
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if gfr column already exists
        cursor.execute("PRAGMA table_info(health_record)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'gfr' not in columns:
            print("Adding 'gfr' column to 'health_record' table...")
            cursor.execute("ALTER TABLE health_record ADD COLUMN gfr FLOAT")
            conn.commit()
            print("Migration successful.")
        else:
            print("'gfr' column already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_db()
