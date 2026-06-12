from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os

app = Flask(__name__)

# Upload Folder Configuration
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create Upload Folder Automatically
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Function to Extract Text from PDF
def extract_text_from_pdf(pdf_path):

    text = ""

    reader = PdfReader(pdf_path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# Landing Page
@app.route("/")
def home():
    return render_template("landing.html")


# Upload Page
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        print("\nPOST Request Received\n")

        # Check File Exists
        if "resume" not in request.files:
            return "No file selected"

        file = request.files["resume"]

        # Check File Name
        if file.filename == "":
            return "Please select a file"

        # Save File
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(file_path)

        print("File Name:", file.filename)
        print("Saved At:", file_path)

        # Extract Resume Text
        resume_text = extract_text_from_pdf(file_path)

        print("\n========== RESUME TEXT ==========\n")
        print(resume_text)
        print("\n=================================\n")

        return f"""
        <h1>Upload Successful ✅</h1>
        <h3>File Name: {file.filename}</h3>

        <p>
            Resume uploaded and text extracted successfully.
        </p>

        <a href="/upload">
            Upload Another Resume
        </a>
        """

    return render_template("upload.html")


# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)