<<<<<<< HEAD
import sqlite3

DB_PATH = 'database.db'

def migrate():
    print(f"Connecting to {DB_PATH} for migration...")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    try:
        # Check if columns already exist
        cur.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cur.fetchall()]
        
        if 'reg_id' not in columns:
            print("Adding 'reg_id' column...")
            cur.execute("ALTER TABLE users ADD COLUMN reg_id TEXT")
            print("Creating unique index for 'reg_id'...")
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_reg_id ON users(reg_id)")
            
        if 'password' not in columns:
            print("Adding 'password' column...")
            cur.execute("ALTER TABLE users ADD COLUMN password TEXT")
            
        con.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    migrate()
=======
import sqlite3

DB_PATH = 'database.db'

def migrate():
    print(f"Connecting to {DB_PATH} for migration...")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    try:
        # Check if columns already exist
        cur.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cur.fetchall()]
        
        if 'reg_id' not in columns:
            print("Adding 'reg_id' column...")
            cur.execute("ALTER TABLE users ADD COLUMN reg_id TEXT")
            print("Creating unique index for 'reg_id'...")
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_reg_id ON users(reg_id)")
            
        if 'password' not in columns:
            print("Adding 'password' column...")
            cur.execute("ALTER TABLE users ADD COLUMN password TEXT")
            
        con.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    migrate()
>>>>>>> master
