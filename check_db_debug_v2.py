import sqlite3
import os

def check_db():
    db_path = "database.db"
    if not os.path.exists(db_path):
        print(f"Error: {db_path} does not exist.")
        return
        
    try:
        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        print("--- Users ---")
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        for row in users:
            print(dict(row))
        if not users: print("No users found.")
            
        print("\n--- Latest Submissions (Last 5) ---")
        cur.execute("SELECT id, user_email, problem_id, score, status, timestamp FROM submissions ORDER BY id DESC LIMIT 5")
        subs = cur.fetchall()
        for row in subs:
            print(dict(row))
        if not subs: print("No submissions found.")
            
        print("\n--- Problems ---")
        cur.execute("SELECT * FROM problems")
        probs = cur.fetchall()
        for row in probs:
            print(dict(row))
        if not probs: print("No problems found.")
            
        con.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
