from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, Response
import sqlite3, requests, json, os, csv, io, base64
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cse_aiml_secret_dev_key")

# ---------------- CONFIG ----------------
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "csm123")
JUDGE0_API_KEY = os.getenv("JUDGE0_API_KEY", "")


# ---------------- DATABASE ----------------
DB_PATH = "database.db"
IS_PG = os.getenv("DATABASE_URL") is not None

class DbWrapper:
    def __init__(self, conn, is_pg):
        self.conn = conn
        self.is_pg = is_pg
        self.pl = "%s" if is_pg else "?"

    def execute(self, query, params=None):
        # Handle parameter mismatch between SQLite (?) and PG (%s)
        # Note: This is a simple replacement. If queries use literal '?', 
        # more advanced parsing would be needed.
        query = query.replace("?", self.pl)
        if self.is_pg:
            cur = self.conn.cursor()
            cur.execute(query, params or ())
            return cur
        else:
            return self.conn.execute(query, params or ())

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        return self.conn.commit()

    def close(self):
        return self.conn.close()
    
    def fetchall(self):
        # Only used if the wrapper itself is treated like a cursor
        pass

def get_db():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print("DEBUG: Connecting to PostgreSQL")
        conn = psycopg2.connect(db_url, sslmode='require', cursor_factory=RealDictCursor)
        return DbWrapper(conn, True)
    else:
        print(f"DEBUG: Connecting to SQLite DB at {os.path.abspath(DB_PATH)}")
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        return DbWrapper(con, False)

# ---------------- AUTO INIT DB ----------------
def init_db():
    con = get_db()
    cur = con.cursor()
    
    # Check if we are using PostgreSQL
    is_pg = os.getenv("DATABASE_URL") is not None
    
    id_type = "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    ignore_clause = "ON CONFLICT DO NOTHING" if is_pg else "OR IGNORE"

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            name TEXT,
            email TEXT UNIQUE,
            roll TEXT,
            google_id TEXT,
            reg_id TEXT UNIQUE,
            password TEXT
        )
    """)

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS submissions (
            id {id_type},
            user_email TEXT,
            problem_id TEXT,
            score INTEGER,
            code TEXT,
            language TEXT,
            status TEXT DEFAULT 'submitted',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS problems (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            difficulty TEXT,
            score INTEGER
        )
    """)

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS test_cases (
            id {id_type},
            problem_id TEXT,
            input TEXT,
            expected_output TEXT,
            FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
        )
    """)

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Seed defaults
    if is_pg:
        cur.execute("INSERT INTO settings VALUES (%s, %s) ON CONFLICT (key) DO NOTHING", ("contest_start", "2026-01-01 00:00:00"))
        cur.execute("INSERT INTO settings VALUES (%s, %s) ON CONFLICT (key) DO NOTHING", ("contest_end", "2027-01-01 00:00:00"))
    else:
        cur.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", ("contest_start", "2026-01-01 00:00:00"))
        cur.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", ("contest_end", "2027-01-01 00:00:00"))
    
    # Update if already exists to ensure it's active
    param_char = "%s" if is_pg else "?"
    cur.execute(f"UPDATE settings SET value={param_char} WHERE key='contest_start'", ("2026-01-01 00:00:00",))
    cur.execute(f"UPDATE settings SET value={param_char} WHERE key='contest_end'", ("2027-01-01 00:00:00",))

    problems = [
        ("easy1", "Sum of Two Numbers", "Write a program that reads two integers from stdin (one per line) and prints their sum.", "easy", 10),
        ("medium1", "Factorial", "Write a program that reads an integer N from stdin and prints N! (factorial of N).", "medium", 20),
        ("hard1", "Shortest Path", "Given an adjacency matrix of a graph, find the shortest path between node 0 and node N-1 using BFS. Input: first line is N (nodes), next N lines are the adjacency matrix rows.", "hard", 30)
    ]
    
    for p in problems:
        if is_pg:
            cur.execute("INSERT INTO problems VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING", p)
        else:
            cur.execute("INSERT OR IGNORE INTO problems VALUES (?,?,?,?,?)", p)

    # Seed test cases
    test_cases = [
        ("easy1", "3\n5", "8"),
        ("easy1", "10\n20", "30"),
        ("easy1", "-1\n1", "0"),
        ("medium1", "5", "120"),
        ("medium1", "0", "1"),
        ("medium1", "10", "3628800"),
    ]
    for tc in test_cases:
        if is_pg:
            cur.execute("SELECT id FROM test_cases WHERE problem_id=%s AND input=%s", (tc[0], tc[1]))
            existing = cur.fetchone()
            if not existing:
                cur.execute("INSERT INTO test_cases (problem_id, input, expected_output) VALUES (%s,%s,%s)", tc)
        else:
            existing = cur.execute("SELECT id FROM test_cases WHERE problem_id=? AND input=?", (tc[0], tc[1])).fetchone()
            if not existing:
                cur.execute("INSERT INTO test_cases (problem_id, input, expected_output) VALUES (?,?,?)", tc)

    con.commit()
    con.close()

# Run on startup
try:
    init_db()
except Exception as e:
    print(f"CRITICAL: Database initialization failed: {e}")

# ---------------- HELPERS ----------------
def b64e(s):
    if s is None: return ""
    return base64.b64encode(str(s).encode()).decode()

def b64d(s):
    if not s: return ""
    try:
        return base64.b64decode(s).decode('utf-8', errors='replace')
    except:
        return str(s)


# ---------------- ID/PASSWORD LOGIN ----------------

# ---------------- HELPERS ----------------
def get_setting(key):
    con = get_db()
    res = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    con.close()
    return res['value'] if res else None

def is_contest_active():
    start_str = get_setting("contest_start") or "2026-01-01 00:00:00"
    end_str = get_setting("contest_end") or "2027-01-01 00:00:00"
    now = datetime.now()
    start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
    return start <= now <= end

def get_stats():
    """Get dashboard statistics."""
    con = get_db()
    total_users = con.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
    total_submissions = con.execute("SELECT COUNT(*) as c FROM submissions").fetchone()['c']
    total_problems = con.execute("SELECT COUNT(*) as c FROM problems").fetchone()['c']
    con.close()
    return {
        'total_users': total_users,
        'total_submissions': total_submissions,
        'total_problems': total_problems
    }

# ---------------- AUTH ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("contest"))
    return render_template("login.html")

@app.route("/login/credentials", methods=["POST"])
def login_credentials():
    reg_id = request.form.get("reg_id")
    password = request.form.get("password")

    if not reg_id or not password:
        flash("Registration ID and Password are required.", "error")
        return redirect(url_for("login"))

    con = get_db()
    user = con.execute("SELECT * FROM users WHERE reg_id=? AND password=?", (reg_id, password)).fetchone()
    con.close()

    if user:
        user_info = {
            'name': user['name'],
            'email': user['email'] or f"user_{reg_id}@example.com",
            'sub': f"reg_{reg_id}"
        }
        session["user"] = user_info
        session["email"] = user_info['email']
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("contest"))
    
    flash("Invalid Registration ID or Password.", "error")
    return redirect(url_for("login"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        reg_id = request.form.get("reg_id")
        email = request.form.get("email")
        new_password = request.form.get("new_password")

        if not reg_id or not email:
            flash("Registration ID and Email are required.", "error")
            return render_template("forgot_password.html")

        con = get_db()
        user = con.execute("SELECT * FROM users WHERE reg_id=? AND email=?", (reg_id, email)).fetchone()
        
        if not user:
            con.close()
            flash("Invalid combination of Registration ID and Email.", "error")
            return render_template("forgot_password.html")

        if new_password:
            con.execute("UPDATE users SET password=? WHERE reg_id=?", (new_password, reg_id))
            con.commit()
            con.close()
            flash("Password reset successfully! You can now login.", "success")
            return redirect(url_for("login"))
        
        con.close()
        return render_template("forgot_password.html", verified=True, reg_id=reg_id, email=email)

    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# ---------------- CONTEST ----------------
@app.route("/contest")
def contest():
    if "user" not in session:
        return redirect(url_for("login"))

    con = get_db()
    problems = con.execute("SELECT * FROM problems").fetchall()
    con.close()

    start_time = get_setting("contest_start")
    end_time = get_setting("contest_end")

    return render_template("contest.html",
                           user=session["user"],
                           problems=problems,
                           start_time=start_time,
                           end_time=end_time)

@app.route("/user/dashboard")
def user_dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    
    email = session.get("email")
    con = get_db()
    
    # User info
    user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    
    # Submissions
    submissions = con.execute("""
        SELECT s.*, p.title as problem_title 
        FROM submissions s
        JOIN problems p ON s.problem_id = p.id
        WHERE s.user_email = ? 
        ORDER BY s.timestamp DESC
    """, (email,)).fetchall()
    
    total_score = sum(s['score'] for s in submissions) if submissions else 0

    # Calculate Rank
    leaderboard = con.execute("""
        SELECT u.email, COALESCE(SUM(s.score), 0) as total_score
        FROM users u
        LEFT JOIN submissions s ON u.email = s.user_email
        GROUP BY u.email
        ORDER BY total_score DESC
    """).fetchall()
    
    rank = "N/A"
    for i, entry in enumerate(leaderboard):
        if entry['email'] == email:
            rank = i + 1
            break
    
    con.close()
    return render_template("user_dashboard.html", 
                           user=user, 
                           submissions=submissions, 
                           rank=rank, 
                           total_score=total_score)



@app.route("/user/change-password", methods=["POST"])
def change_password():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Not logged in"})
    
    email = session.get("email")
    new_password = request.form.get("new_password")
    
    if not new_password or len(new_password) < 4:
        flash("Password must be at least 4 characters long.", "error")
        return redirect(url_for("user_dashboard"))
        
    con = get_db()
    con.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
    con.commit()
    con.close()
    
    flash("Password updated successfully!", "success")
    return redirect(url_for("user_dashboard"))

@app.route("/submit", methods=["POST"])
def submit():
    if "user" not in session:
        return jsonify({"output": "Not Logged In", "status": "error"})

    if not is_contest_active():
        return jsonify({"output": "Contest is not active right now.", "status": "error"})

    email = session.get("email")
    data = request.json
    problem_id = data.get("problem")
    code = data.get("code", "")
    language_id = data.get("language")
    is_test = data.get("is_test", False)

    if not code.strip():
        return jsonify({"output": "Please write some code before submitting.", "status": "error"})

    con = get_db()
    prob = con.execute("SELECT * FROM problems WHERE id=?", (problem_id,)).fetchone()
    if not prob:
        con.close()
        return jsonify({"output": "Invalid Problem", "status": "error"})

    # Get test cases for this problem
    test_cases = con.execute("SELECT * FROM test_cases WHERE problem_id=?", (problem_id,)).fetchall()

    if not test_cases:
        # No test cases — just run the code and return output
        try:
            headers = {}
            if JUDGE0_API_KEY:
                headers["X-Auth-Token"] = JUDGE0_API_KEY

            response = requests.post(
                "https://ce.judge0.com/submissions?base64_encoded=true&wait=true",
                json={
                    "source_code": b64e(code),
                    "language_id": int(language_id),
                    "stdin": b64e("")
                },
                headers=headers,
                timeout=60
            ).json()

            stdout = b64d(response.get("stdout"))
            stderr = b64d(response.get("stderr"))
            compile_output = b64d(response.get("compile_output"))
            
            output = stdout or stderr or compile_output or "No output"
            status_desc = response.get("status", {}).get("description", response.get("message", "Unknown"))

            if not is_test:
                con.execute("""
                    INSERT INTO submissions (user_email, problem_id, score, code, language, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (email, problem_id, prob['score'], code, language_id, status_desc))
                con.commit()
            con.close()

            return jsonify({"output": output, "status": "success", "score": prob['score']})
        except Exception as e:
            con.close()
            return jsonify({"output": f"Execution error: {str(e)}", "status": "error"})
    else:
        # Run against test cases
        passed = 0
        total = len(test_cases)
        results = []

        for tc in test_cases:
            try:
                headers = {}
                if JUDGE0_API_KEY:
                    headers["X-Auth-Token"] = JUDGE0_API_KEY

                print(f"DEBUG: Judge0 request for test case {tc['id']}...")
                response = requests.post(
                    "https://ce.judge0.com/submissions?base64_encoded=true&wait=true",
                    json={
                        "source_code": b64e(code),
                        "language_id": int(language_id),
                        "stdin": b64e(tc['input']),
                        "expected_output": b64e(tc['expected_output'])
                    },
                    headers=headers,
                    timeout=60
                ).json()
                print(f"DEBUG: Judge0 response: {json.dumps(response, indent=2)}")

                status_desc = response.get("status", {}).get("description", response.get("message", "Unknown"))
                actual_out = b64d(response.get("stdout"))
                err = b64d(response.get("stderr")) or b64d(response.get("compile_output"))
                
                if status_desc == "Accepted":
                    passed += 1
                    results.append(f"Test {len(results)+1}: ✅ Passed")
                else:
                    results.append(f"Test {len(results)+1}: ❌ {status_desc}")
                    if actual_out:
                        results.append(f"   [Output]: {actual_out.strip()}")
                    if err:
                        results.append(f"   [Error]: {err.strip()}")
            except Exception as e:
                results.append(f"Test {len(results)+1}: ⚠️ System Error: {str(e)}")

        # Calculate partial score
        earned_score = int((passed / total) * prob['score']) if total > 0 else 0

        if not is_test:
            con.execute("""
                INSERT INTO submissions (user_email, problem_id, score, code, language, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (email, problem_id, earned_score, code, language_id, f"{passed}/{total} passed"))
            con.commit()
        con.close()

        output_text = "\n".join(results) + f"\n\nScore: {earned_score}/{prob['score']} ({passed}/{total} test cases passed)"
        return jsonify({"output": output_text, "status": "success" if passed == total else "partial", "score": earned_score})

# ---------------- ADMIN ----------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        # Check for both possible field names (from direct login vs contest tab)
        user = request.form.get("username") or request.form.get("user")
        pwd = request.form.get("password") or request.form.get("pass")
        
        if user == ADMIN_USER and pwd == ADMIN_PASS:
            session["admin"] = True
            flash("Welcome, Admin!", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials.", "error")
    return render_template("admin_login.html")

@app.route("/admin")
def admin():
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    con = get_db()
    leaderboard = con.execute("""
        SELECT u.id, u.name, u.email, u.reg_id, COALESCE(SUM(s.score), 0) as total_score
        FROM users u
        LEFT JOIN submissions s ON u.email = s.user_email
        GROUP BY u.email
        ORDER BY total_score DESC
    """).fetchall()

    settings = dict(con.execute("SELECT * FROM settings").fetchall())
    stats = get_stats()
    con.close()

    return render_template("admin_dashboard.html",
                           leaderboard=leaderboard,
                           settings=settings,
                           stats=stats)

@app.route("/admin/problems", methods=["GET", "POST"])
def admin_problems():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    con = get_db()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            try:
                con.execute("INSERT INTO problems VALUES (?,?,?,?,?)",
                            (request.form["id"], request.form["title"],
                             request.form["desc"], request.form["diff"], int(request.form["score"])))
                flash("Problem added successfully!", "success")
            except sqlite3.IntegrityError:
                flash("Problem ID already exists!", "error")
        elif action == "delete":
            con.execute("DELETE FROM test_cases WHERE problem_id=?", (request.form["id"],))
            con.execute("DELETE FROM problems WHERE id=?", (request.form["id"],))
            flash("Problem deleted.", "info")
        elif action == "add_test":
            con.execute("INSERT INTO test_cases (problem_id, input, expected_output) VALUES (?,?,?)",
                        (request.form["problem_id"], request.form["tc_input"], request.form["tc_output"]))
            flash("Test case added!", "success")
        elif action == "delete_test":
            con.execute("DELETE FROM test_cases WHERE id=?", (request.form["tc_id"],))
            flash("Test case deleted.", "info")
        elif action == "update":
            con.execute("""UPDATE problems SET title=?, description=?, difficulty=?, score=? WHERE id=?""",
                        (request.form["title"], request.form["desc"], request.form["diff"],
                         int(request.form["score"]), request.form["id"]))
            flash("Problem updated!", "success")
        con.commit()
        con.close()
        return redirect(url_for("admin_problems"))

    problems = con.execute("SELECT * FROM problems").fetchall()
    test_cases = con.execute("SELECT * FROM test_cases ORDER BY problem_id").fetchall()

    # Group test cases by problem
    tc_map = {}
    for tc in test_cases:
        pid = tc['problem_id']
        if pid not in tc_map:
            tc_map[pid] = []
        tc_map[pid].append(tc)

    con.close()
    return render_template("admin_problems.html", problems=problems, test_cases=tc_map)

@app.route("/admin/settings", methods=["POST"])
def admin_settings():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    con = get_db()
    con.execute("UPDATE settings SET value=? WHERE key='contest_start'", (request.form["start"],))
    con.execute("UPDATE settings SET value=? WHERE key='contest_end'", (request.form["end"],))
    con.commit()
    con.close()
    flash("Contest settings updated!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/users", methods=["POST"])
def admin_users():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    con = get_db()
    action = request.form.get("action")
    
    if action == "add":
        name = request.form.get("name")
        email = request.form.get("email")
        reg_id = request.form.get("reg_id")
        password = request.form.get("password")
        
        try:
            con.execute("""
                INSERT INTO users (name, email, reg_id, password)
                VALUES (?, ?, ?, ?)
            """, (name, email, reg_id, password))
            con.commit()
            flash(f"User {name} added successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Error: Email or Registration ID already exists.", "error")
            
    elif action == "delete":
        user_id = request.form.get("id")
        con.execute("DELETE FROM users WHERE id=?", (user_id,))
        con.commit()
        flash("User deleted successfully.", "info")
        
    con.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/download_csv")
def admin_download_csv():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    con = get_db()
    rows = con.execute("""
        SELECT s.id, u.name, s.user_email, s.problem_id, s.score, s.language, s.status, s.timestamp
        FROM submissions s
        LEFT JOIN users u ON s.user_email = u.email
        ORDER BY s.timestamp DESC
    """).fetchall()
    con.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Email", "Problem", "Score", "Language", "Status", "Timestamp"])
    for row in rows:
        writer.writerow([row['id'], row['name'], row['user_email'], row['problem_id'],
                         row['score'], row['language'], row['status'], row['timestamp']])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=contest_results.csv"}
    )

# ---------------- LEADERBOARD (PUBLIC) ----------------
@app.route("/leaderboard")
def leaderboard():
    if "user" not in session and not session.get("admin"):
        flash("Please login to view the leaderboard.", "info")
        return redirect(url_for("login"))
    con = get_db()
    rows = con.execute("""
        SELECT u.name, COALESCE(SUM(s.score), 0) as score 
        FROM users u
        LEFT JOIN submissions s ON u.email = s.user_email
        GROUP BY u.email 
        ORDER BY score DESC
    """).fetchall()
    data = [dict(r) for r in rows]
    con.close()
    return render_template("leaderboard.html", data=data)

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
