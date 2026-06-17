from flask import Flask, render_template, request, redirect, session, url_for
from PyPDF2 import PdfReader
from job_roles import job_roles
from werkzeug.utils import secure_filename
import os
import re
import sqlite3
from flask import send_file
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "smart_resume_analyzer_secret"
@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("resume_reports.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
        """, (username, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")

        conn = sqlite3.connect("resume_reports.db")
        cursor = conn.cursor()

        try:

            cursor.execute("""
            INSERT INTO users(username,email,password)
            VALUES(?,?,?)
            """, (username, email, password))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()
            return render_template("register.html", error="Username or email already exists")

        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")

def create_table():

    conn = sqlite3.connect("resume_reports.db")

    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    file_name TEXT,

    predicted_role TEXT,

    ats_score INTEGER,

    matched_skills TEXT,

    missing_skills TEXT,

    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP

)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE,

    email TEXT UNIQUE,

    password TEXT

)
""")
    cursor.execute("PRAGMA table_info(reports)")
    report_columns = [column[1] for column in cursor.fetchall()]

    if "user_id" not in report_columns:
        cursor.execute("ALTER TABLE reports ADD COLUMN user_id INTEGER")

    conn.commit()
    conn.close()

create_table()


# Upload Folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"pdf"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ---------------- PDF TEXT EXTRACTION ----------------
def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


# ---------------- FILE VALIDATION ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
def save_report(
    user_id,
    file_name,
    predicted_role,
    score,
    matched_skills,
    missing_skills
):

    conn = sqlite3.connect("resume_reports.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO reports(

        user_id,
        file_name,
        predicted_role,
        ats_score,
        matched_skills,
        missing_skills

    )
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        user_id,
        file_name,
        predicted_role,
        score,
        ", ".join(matched_skills),
        ", ".join(missing_skills)
    ))

    conn.commit()
    conn.close()
    
#select role based on resume text
def detect_role(resume_text):

    text = resume_text.lower()

    best_role = ""
    best_score = 0

    for role, skills in job_roles.items():

        score = 0

        for skill in skills:

            if skill.lower() in text:
                score += 1

        if score > best_score:
            best_score = score
            best_role = role

    if not best_role:
        best_role = "Software Engineer"

    confidence = round((best_score / len(job_roles[best_role])) * 100)

    return best_role, confidence
# ---------------- ATS SCORE FUNCTION ----------------
def calculate_score(resume_text, selected_role):

    required_skills = job_roles[selected_role]
    text = resume_text.lower()

    matched_skills = []
    missing_skills = []

    # ---------- SKILLS (70%) ----------

    for skill in required_skills:

        pattern = r'\b' + re.escape(skill.lower()) + r'\b'

        if re.search(pattern, text):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    skill_score = (
        len(matched_skills) / len(required_skills)
    ) * 70

    # ---------- PROJECTS (10%) ----------

    project_keywords = [
        "project",
        "built",
        "developed",
        "created",
        "designed",
        "implemented"
    ]

    project_score = (
        10 if any(word in text for word in project_keywords)
        else 3
    )

    # ---------- EDUCATION (5%) ----------

    education_keywords = [
        "btech",
        "b.tech",
        "bachelor",
        "degree",
        "university",
        "college",
        "engineering"
    ]

    education_score = (
        5 if any(word in text for word in education_keywords)
        else 2
    )

    # ---------- ACHIEVEMENTS (5%) ----------

    achievement_keywords = [
        "award",
        "certificate",
        "certification",
        "won",
        "hackathon",
        "rank",
        "achievement"
    ]

    achievement_score = (
        5 if any(word in text for word in achievement_keywords)
        else 0
    )

    # ---------- FORMATTING (10%) ----------

    formatting_score = 0

    # Email
    if "@" in text:
        formatting_score += 3

    # Phone Number
    if re.search(r'\d{10}', text):
        formatting_score += 3

    # LinkedIn
    if "linkedin" in text:
        formatting_score += 2

    # GitHub
    if "github" in text:
        formatting_score += 2

    # ---------- FINAL SCORE ----------

    total_score = round(
        skill_score +
        project_score +
        education_score +
        achievement_score +
        formatting_score
    )

    return total_score, matched_skills, missing_skills


# ---------------- ROUTES ----------------
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        # File Check
        if "resume" not in request.files:
            return render_template("upload.html", error="No file selected")

        file = request.files["resume"]

        if file.filename == "":
            return render_template("upload.html", error="Please select a file")

        if not allowed_file(file.filename):
            return render_template("upload.html", error="Only PDF files are allowed")

        filename = secure_filename(file.filename)
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(file_path)

        # Extract Resume Text
        try:
            resume_text = extract_text_from_pdf(file_path)

            selected_role, confidence = detect_role(
                resume_text
            )

        except Exception as e:
            return render_template("upload.html", error=f"Error reading PDF: {e}")

        if not resume_text.strip():
            return render_template("upload.html", error="Could not extract text from PDF")

        # ATS Score
        score, matched_skills, missing_skills = calculate_score(
            resume_text,
            selected_role
        )

        save_report(
            session["user_id"],
            filename,
            selected_role,
            score,
            matched_skills,
            missing_skills
        )
        return render_template(
            "result.html",
            score=score,
            selected_role=selected_role,
            confidence=confidence,
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )

    return render_template(
        "upload.html",
        job_roles=job_roles.keys()
    )


@app.route("/download-report")
def download_report():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("resume_reports.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT file_name, predicted_role, ats_score, matched_skills, missing_skills
    FROM reports
    WHERE user_id = ?
    ORDER BY id DESC
    LIMIT 1
    """, (session["user_id"],))

    report = cursor.fetchone()

    conn.close()

    if not report:
        return redirect(url_for("history"))

    pdf_name = "ATS_Report.pdf"

    pdf = canvas.Canvas(pdf_name)

    pdf.drawString(
        100,
        800,
        "Smart Resume Analyzer"
    )

    pdf.drawString(
        100,
        770,
        f"File: {report[0]}"
    )

    pdf.drawString(
        100,
        740,
        f"Role: {report[1]}"
    )

    pdf.drawString(
        100,
        710,
        f"ATS Score: {report[2]}%"
    )

    pdf.drawString(
        100,
        670,
        "Matched Skills:"
    )

    pdf.drawString(
        120,
        650,
        report[3]
    )

    pdf.drawString(
        100,
        610,
        "Missing Skills:"
    )

    pdf.drawString(
        120,
        590,
        report[4]
    )

    pdf.save()

    return send_file(
        pdf_name,
        as_attachment=True
    )
@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("resume_reports.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, file_name, predicted_role, ats_score, upload_date
    FROM reports
    WHERE user_id = ?
    ORDER BY id DESC
    """, (session["user_id"],))

    reports = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        reports=reports
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("resume_reports.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM reports WHERE user_id=?",
        (session["user_id"],)
    )
    total_resumes = cursor.fetchone()[0]

    cursor.execute(
        "SELECT AVG(ats_score) FROM reports WHERE user_id=?",
        (session["user_id"],)
    )
    avg_score = cursor.fetchone()[0]

    cursor.execute(
        "SELECT MAX(ats_score) FROM reports WHERE user_id=?",
        (session["user_id"],)
    )
    highest_score = cursor.fetchone()[0]

    cursor.execute("""
        SELECT predicted_role, COUNT(*)
        FROM reports
        WHERE user_id=?
        GROUP BY predicted_role
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """, (session["user_id"],))

    role_data = cursor.fetchone()
    most_common_role = role_data[0] if role_data else "N/A"

    cursor.execute("""
        SELECT file_name, predicted_role, ats_score
        FROM reports
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 5
    """, (session["user_id"],))

    recent_reports = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_resumes=total_resumes,
        avg_score=round(avg_score, 1) if avg_score else 0,
        highest_score=highest_score if highest_score else 0,
        most_common_role=most_common_role,
        recent_reports=recent_reports
    )
 
if __name__ == "__main__":
    app.run(debug=True)
