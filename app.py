from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from job_roles import job_roles
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

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


# ---------------- ATS SCORE FUNCTION ----------------
def calculate_score(resume_text, selected_role):

    required_skills = job_roles[selected_role]
    text = resume_text.lower()

    # SKILLS (50%)
    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        if skill.lower() in text:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    skill_score = (len(matched_skills) / len(required_skills)) * 50

    # PROJECTS (20%)
    project_keywords = ["project", "built", "developed", "created", "designed"]
    project_score = 20 if any(word in text for word in project_keywords) else 5

    # EDUCATION (10%)
    education_keywords = ["btech", "b.tech", "bachelor", "degree", "university", "college"]
    education_score = 10 if any(word in text for word in education_keywords) else 5

    # ACHIEVEMENTS (10%)
    achievement_keywords = ["award", "certificate", "won", "hackathon", "rank"]
    achievement_score = 10 if any(word in text for word in achievement_keywords) else 3

    # FORMATTING (10%)
    formatting_score = 10

    total_score = round(
        skill_score +
        project_score +
        education_score +
        achievement_score +
        formatting_score
    )

    return total_score, matched_skills, missing_skills


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        print("\nPOST Request Received\n")

        # Job Role
        selected_role = request.form.get("job_role")

        if not selected_role:
            return "Please select a job role"

        # File check
        if "resume" not in request.files:
            return "No file selected"

        file = request.files["resume"]

        if file.filename == "":
            return "Please select a file"

        if not allowed_file(file.filename):
            return "Only PDF files allowed"

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(file_path)

        # Extract text
        try:
            resume_text = extract_text_from_pdf(file_path)
        except Exception as e:
            return f"Error reading PDF: {e}"

        if not resume_text.strip():
            return "Could not extract text from PDF"

        # SCORE CALCULATION
        score, matched_skills, missing_skills = calculate_score(
            resume_text,
            selected_role
        )

        # 🔥 SEND TO RESULT PAGE
        return render_template(
            "result.html",
            score=score,
            selected_role=selected_role,
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )

    return render_template("upload.html", job_roles=job_roles.keys())


if __name__ == "__main__":
    app.run(debug=True)