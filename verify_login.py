<<<<<<< HEAD
import requests
import sqlite3
import os

BASE_URL = 'http://127.0.0.1:5000'
DB_PATH = 'database.db'

def verify():
    print("--- Starting Verification ---")
    
    # 1. Check if DB exists and insert test user
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    try:
        con = sqlite3.connect(DB_PATH)
        con.execute("INSERT OR IGNORE INTO users (name, email, reg_id, password) VALUES ('Verification User', 'verify@test.com', 'VERIFY123', 'pass123')")
        con.commit()
        con.close()
        print("Test user 'VERIFY123' inserted/verified in DB.")
    except Exception as e:
        print(f"DB Error: {e}")
        return

    # 2. Attempt Login via POST
    s = requests.Session()
    data = {'reg_id': 'VERIFY123', 'password': 'pass123'}
    
    try:
        print(f"Attempting login at {BASE_URL}/login/credentials ...")
        r = s.post(f'{BASE_URL}/login/credentials', data=data, allow_redirects=False)
        
        if r.status_code == 302 and '/contest' in r.headers.get('Location', ''):
            print("✅ SUCCESS: Login redirected to /contest")
            
            # 3. Check if we can access /contest with the session
            r_contest = s.get(f'{BASE_URL}/contest')
            if "Verification User" in r_contest.text:
                print("✅ SUCCESS: User name found on contest page")
            else:
                print("❌ FAILURE: User name not found on contest page")
        else:
            print(f"❌ FAILURE: Login failed with status {r.status_code}")
            print(f"Location Header: {r.headers.get('Location')}")
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    verify()
=======
import requests
import sqlite3
import os

BASE_URL = 'http://127.0.0.1:5000'
DB_PATH = 'database.db'

def verify():
    print("--- Starting Verification ---")
    
    # 1. Check if DB exists and insert test user
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    try:
        con = sqlite3.connect(DB_PATH)
        con.execute("INSERT OR IGNORE INTO users (name, email, reg_id, password) VALUES ('Verification User', 'verify@test.com', 'VERIFY123', 'pass123')")
        con.commit()
        con.close()
        print("Test user 'VERIFY123' inserted/verified in DB.")
    except Exception as e:
        print(f"DB Error: {e}")
        return

    # 2. Attempt Login via POST
    s = requests.Session()
    data = {'reg_id': 'VERIFY123', 'password': 'pass123'}
    
    try:
        print(f"Attempting login at {BASE_URL}/login/credentials ...")
        r = s.post(f'{BASE_URL}/login/credentials', data=data, allow_redirects=False)
        
        if r.status_code == 302 and '/contest' in r.headers.get('Location', ''):
            print("✅ SUCCESS: Login redirected to /contest")
            
            # 3. Check if we can access /contest with the session
            r_contest = s.get(f'{BASE_URL}/contest')
            if "Verification User" in r_contest.text:
                print("✅ SUCCESS: User name found on contest page")
            else:
                print("❌ FAILURE: User name not found on contest page")
        else:
            print(f"❌ FAILURE: Login failed with status {r.status_code}")
            print(f"Location Header: {r.headers.get('Location')}")
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    verify()
>>>>>>> master
