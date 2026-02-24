<<<<<<< HEAD
import requests
import json

def test_submission():
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    # 1. Login
    login_url = f"{base_url}/login/credentials"
    # Using the reg_id found in the database: 20221A0510
    # I need to know the password. I'll check the database for it.
    # For now, I'll assume I can find it.
    
    # I'll use a simpler way: check the database for a user and then simulate their session.
    # Actually, I'll just use the reg_id and password I find in the DB.
    
    print("Getting user credentials from DB...")
    import sqlite3
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT reg_id, password FROM users LIMIT 1")
    user = cur.fetchone()
    con.close()
    
    if not user:
        print("No users found in DB. Cannot test submission.")
        return
        
    reg_id, password = user
    print(f"Logging in as {reg_id}...")
    
    login_data = {'reg_id': reg_id, 'password': password}
    resp = session.post(login_url, data=login_data)
    
    if resp.status_code == 200 and "Contest Arena" in resp.text:
        print("Login successful!")
    else:
        print(f"Login failed. Status: {resp.status_code}")
        # print(resp.text)
        return

    # 2. Run Code (Test)
    submit_url = f"{base_url}/submit"
    submit_payload = {
        "code": "#include <stdio.h>\nint main() { printf(\"Run Test\"); return 0; }",
        "language": "50",
        "problem": "easy1",
        "is_test": True
    }
    
    print("Submitting code...")
    resp = session.post(submit_url, json=submit_payload)
    
    print(f"Submit Status Code: {resp.status_code}")
    print(f"Submit Response: {resp.text}")
    
    print("Checking database for test submission...")
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    latest = con.execute("SELECT * FROM submissions ORDER BY id DESC LIMIT 1").fetchone()
    con.close()
    
    if latest and "Run Test" in latest['code']:
        print("❌ FAILED: Test submission was saved to DB!")
    else:
        print("✅ SUCCESS: Test submission was NOT saved to DB.")

if __name__ == "__main__":
    test_submission()
=======
import requests
import json

def test_submission():
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    # 1. Login
    login_url = f"{base_url}/login/credentials"
    # Using the reg_id found in the database: 20221A0510
    # I need to know the password. I'll check the database for it.
    # For now, I'll assume I can find it.
    
    # I'll use a simpler way: check the database for a user and then simulate their session.
    # Actually, I'll just use the reg_id and password I find in the DB.
    
    print("Getting user credentials from DB...")
    import sqlite3
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT reg_id, password FROM users LIMIT 1")
    user = cur.fetchone()
    con.close()
    
    if not user:
        print("No users found in DB. Cannot test submission.")
        return
        
    reg_id, password = user
    print(f"Logging in as {reg_id}...")
    
    login_data = {'reg_id': reg_id, 'password': password}
    resp = session.post(login_url, data=login_data)
    
    if resp.status_code == 200 and "Contest Arena" in resp.text:
        print("Login successful!")
    else:
        print(f"Login failed. Status: {resp.status_code}")
        # print(resp.text)
        return

    # 2. Run Code (Test)
    submit_url = f"{base_url}/submit"
    submit_payload = {
        "code": "#include <stdio.h>\nint main() { printf(\"Run Test\"); return 0; }",
        "language": "50",
        "problem": "easy1",
        "is_test": True
    }
    
    print("Submitting code...")
    resp = session.post(submit_url, json=submit_payload)
    
    print(f"Submit Status Code: {resp.status_code}")
    print(f"Submit Response: {resp.text}")
    
    print("Checking database for test submission...")
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    latest = con.execute("SELECT * FROM submissions ORDER BY id DESC LIMIT 1").fetchone()
    con.close()
    
    if latest and "Run Test" in latest['code']:
        print("❌ FAILED: Test submission was saved to DB!")
    else:
        print("✅ SUCCESS: Test submission was NOT saved to DB.")

if __name__ == "__main__":
    test_submission()
>>>>>>> master
