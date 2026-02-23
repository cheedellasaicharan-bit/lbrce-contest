# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

🔴 STEP 1: INSTALL REQUIRED SOFTWARE (ONE TIME)
1️⃣ Install Python

👉 https://www.python.org/downloads/

✔ Tick Add Python to PATH

Check:

python --version

2️⃣ Install VS Code

👉 https://code.visualstudio.com/

🔴 STEP 2: CREATE PROJECT FOLDER

Create folder on Desktop:

CSM_Coding_Contest


Open VS Code → Open Folder

🔴 STEP 3: CREATE PROJECT STRUCTURE
CSM_Coding_Contest
│
├── app.py
├── requirements.txt
├── database.db
│
├── templates
│   ├── login.html
│   ├── contest.html
│   ├── leaderboard.html
│   ├── admin_login.html
│   └── admin.html
│
└── static
    └── style.css

🔴 STEP 4: INSTALL REQUIRED LIBRARIES

Open terminal inside project:

pip install flask requests


Create requirements.txt

flask
requests

🔴 STEP 5: BACKEND (app.py – FULL FINAL CODE)
📄 app.py
from flask import Flask, render_template, request, jsonify, session
import sqlite3, requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "csm_secret"

# ---------------- CONFIG ----------------
ADMIN_USER = "admin"
ADMIN_PASS = "csm123"

CONTEST_START = datetime(2026, 2, 20, 10, 0, 0)
CONTEST_END   = datetime(2026, 2, 20, 13, 0, 0)

score_map = {"easy":10, "medium":20, "hard":30}

# ---------------- DATABASE ----------------
def db():
    return sqlite3.connect("database.db")

# ---------------- INIT DB (RUN ONCE) ----------------
@app.route("/initdb")
def initdb():
    con = db()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(roll TEXT PRIMARY KEY)")
    cur.execute("""
      CREATE TABLE IF NOT EXISTS submissions(
      roll TEXT, problem TEXT, score INTEGER)
    """)
    con.commit()
    return "DB READY"

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        roll = request.form["roll"]
        session["roll"] = roll
        con = db()
        con.execute("INSERT OR IGNORE INTO users VALUES(?)",(roll,))
        con.commit()
        return render_template("contest.html")
    return render_template("login.html")

# ---------------- SUBMIT CODE ----------------
@app.route("/submit", methods=["POST"])
def submit():
    now = datetime.now()
    if now < CONTEST_START or now > CONTEST_END:
        return jsonify({"output":"Contest Not Active"})

    roll = session.get("roll")
    data = request.json

    response = requests.post(
        "https://ce.judge0.com/submissions?wait=true",
        json={
            "source_code": data["code"],
            "language_id": data["language"],
            "stdin": ""
        }
    ).json()

    con = db()
    con.execute("""
    INSERT INTO submissions
    SELECT ?,?,?
    WHERE NOT EXISTS(
      SELECT 1 FROM submissions WHERE roll=? AND problem=?
    )
    """,(roll,data["problem"],score_map[data["problem"]],
         roll,data["problem"]))
    con.commit()

    return jsonify({"output":response.get("stdout","Error")})

# ---------------- LEADERBOARD ----------------
@app.route("/leaderboard")
def leaderboard():
    con = db()
    data = con.execute("""
    SELECT roll, SUM(score) FROM submissions
    GROUP BY roll ORDER BY SUM(score) DESC
    """).fetchall()
    return render_template("leaderboard.html", data=data)

# ---------------- ADMIN ----------------
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form["user"]==ADMIN_USER and request.form["pass"]==ADMIN_PASS:
            session["admin"]=True
            return render_template("admin.html")
    return render_template("admin_login.html")

@app.route("/download")
def download():
    con=db()
    data=con.execute("""
    SELECT roll, SUM(score) FROM submissions
    GROUP BY roll ORDER BY SUM(score) DESC
    """).fetchall()
    return "\n".join([f"{r},{s}" for r,s in data])

app.run()

🔴 STEP 6: STUDENT LOGIN PAGE
📄 templates/login.html
<h2>CSM Coding Contest</h2>
<form method="post">
<input name="roll" placeholder="Enter Roll Number" required>
<button>Start Contest</button>
</form>

🔴 STEP 7: CONTEST PAGE (FINAL)
📄 templates/contest.html
<h3>CSM Coding Contest</h3>

<h4 id="timer"></h4>

<select id="problem">
<option value="easy">Easy</option>
<option value="medium">Medium</option>
<option value="hard">Hard</option>
</select>

<textarea id="code" rows="15" cols="80"></textarea><br>

<select id="language">
<option value="50">C</option>
<option value="54">C++</option>
<option value="71">Python</option>
</select>

<button onclick="submit()">Submit</button>

<pre id="output"></pre>

<script>
let t=3*60*60;
setInterval(()=>{
 let h=Math.floor(t/3600),
 m=Math.floor((t%3600)/60),
 s=t%60;
 timer.innerText=`Time Left ${h}:${m}:${s}`;
 t--;
 if(t<=0) location.href="/leaderboard";
},1000);

function submit(){
 fetch("/submit",{
  method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({
   code:code.value,
   language:language.value,
   problem:problem.value
  })
 }).then(r=>r.json()).then(d=>{
  output.innerText=d.output;
 });
}

document.oncontextmenu=()=>false;
window.onbeforeunload=()=>true;
</script>

🔴 STEP 8: LEADERBOARD PAGE
📄 templates/leaderboard.html
<h2>Leaderboard</h2>
<table border="1">
<tr><th>Roll</th><th>Score</th></tr>
{% for r,s in data %}
<tr><td>{{r}}</td><td>{{s}}</td></tr>
{% endfor %}
</table>

🔴 STEP 9: ADMIN LOGIN PAGE
📄 templates/admin_login.html
<form method="post">
<input name="user" placeholder="Admin User">
<input name="pass" type="password" placeholder="Password">
<button>Login</button>
</form>

🔴 STEP 10: ADMIN PANEL
📄 templates/admin.html
<h2>Admin Panel</h2>
<a href="/leaderboard">View Leaderboard</a><br>
<a href="/download">Download Results</a Attached

🔴 STEP 11: RUN LOCALLY
python app.py


Open:

http://127.0.0.1:5000


Run DB once:

/initdb

🔴 STEP 12: DEPLOY (ONE LINK)
Best Option: Render

Go to https://render.com

New → Web Service

Upload project

Build:

pip install -r requirements.txt


Start:

python app.py


🎯 FINAL LINK:

https://yourcontest.onrender.com

🏁 FINAL EVENT CHECKLIST

✔ Problems added
✔ DB initialized
✔ Contest time set
✔ Admin password changed
✔ Mock test done
✔ ONE LINK shared

*Listed directory [CSM_Coding_Contest](file:///c:/Users/sai47/OneDrive/Desktop/CSM_Coding_Contest) *

*Edited relevant file*

*Edited relevant file*

*Viewed [app.py](file:///c:/Users/sai47/OneDrive/Desktop/CSM_Coding_Contest/app.py) *

### User Input

good

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*User accepted the command `pip install -r requirements.txt`*

*Checked command status*

*Edited relevant file*

*User accepted the command `python app.py`*

*Read URL content from /initdb *

*Read URL content from / *

*Edited relevant file*

*Edited relevant file*

### User Input

good

### Planner Response

Great! The application is ready.

Since the contest is scheduled to start at **10:00 AM today** (current time is 00:00), you won't be able to submit solutions right now because of this check in [app.py](cci:7://file:///c:/Users/sai47/OneDrive/Desktop/CSM_Coding_Contest/app.py:0:0-0:0):

```python
if now < CONTEST_START or now > CONTEST_END:
    return jsonify({"output":"Contest Not Active"})
```

To **test the submission flow now**, you can temporarily change the start time in [app.py](cci:7://file:///c:/Users/sai47/OneDrive/Desktop/CSM_Coding_Contest/app.py:0:0-0:0) to a past time, for example:

```python
# Change temporarily for testing
CONTEST_START = datetime(2026, 2, 19, 10, 0, 0) 
```

Once you've verified that submissions and the leaderboard work, remember to change it back to `2026, 2, 20` before deploying!

Do you want me to make this change for you so we can do a quick mock test?

### User Input

 yes


*Edited relevant file*

*Edited relevant file*

*User accepted the command `python app.py`*

*Edited relevant file*

### User Input

please provide a login accses with google and provide admin dashboard to see the users eperience and user results

*Edited relevant file*

*Edited relevant file*

### User Input

i need a complete website that full control under admin dashboard

*Edited relevant file*

*Edited relevant file*

### User Input

good

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*User accepted the command `pip install -r requirements.txt`*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*User accepted the command `python app.py`*

*Edited relevant file*

*Read URL content from /initdb *

*Edited relevant file*

*Read URL content from / *

*Edited relevant file*

*Viewed [task.md](file:///C:/Users/sai47/.gemini/antigravity/brain/b5857f4a-8efc-4bb3-a4c1-a88817e25593/task.md) *

*Edited relevant file*

### User Input

good

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

### User Input

good

*Viewed [task.md](file:///C:/Users/sai47/.gemini/antigravity/brain/b5857f4a-8efc-4bb3-a4c1-a88817e25593/task.md) *

*Edited relevant file*

*Edited relevant file*

### Planner Response

The CSM Coding Contest platform is fully set up and ready for deployment! 🚀

You have:
*   **Full Admin Control**: Manage problems, settings, and view results.
*   **Google Login**: Secure access for students.
*   **Deployment Ready**: [Procfile](cci:7://file:///c:/Users/sai47/OneDrive/Desktop/CSM_Coding_Contest/Procfile:0:0-0:0) and [requirements.txt](cci:7://file:///c:/Users/sai47/OneDrive/Desktop/CSM_Coding_Contest/requirements.txt:0:0-0:0) are set for Render.

If you need any more help or want to add more features later, just let me know. Good luck with the contest! 🏆