<<<<<<< HEAD
import sqlite3

def check_db():
    try:
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        print("--- Problems ---")
        cur.execute("SELECT * FROM problems")
        for row in cur.fetchall():
            print(dict(row))
        print("--- Submissions ---")
        cur.execute("SELECT * FROM submissions ORDER BY id DESC LIMIT 5")
        for row in cur.fetchall():
            print(dict(row))
        print("--- Settings ---")
        cur.execute("SELECT * FROM settings")
        for row in cur.fetchall():
            print(dict(row))
        con.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
=======
import sqlite3

def check_db():
    try:
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        print("--- Problems ---")
        cur.execute("SELECT * FROM problems")
        for row in cur.fetchall():
            print(dict(row))
        print("--- Submissions ---")
        cur.execute("SELECT * FROM submissions ORDER BY id DESC LIMIT 5")
        for row in cur.fetchall():
            print(dict(row))
        print("--- Settings ---")
        cur.execute("SELECT * FROM settings")
        for row in cur.fetchall():
            print(dict(row))
        con.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
>>>>>>> master
