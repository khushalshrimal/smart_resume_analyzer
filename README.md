# 🚀 Smart Resume Analyzer

A modern web-based **Resume Analyzer** built with **Flask**, **Tailwind CSS**, and **SQLite** that helps users evaluate their resumes by calculating an ATS score, identifying missing skills, providing improvement suggestions, and generating downloadable PDF reports.

The application also includes secure user authentication, resume history tracking, and a professional dashboard to monitor previous analyses.

---

# ✨ Features

## 🔐 Authentication

* User Registration
* Secure Login & Logout
* Session Management

## 📄 Resume Analysis

* Upload Resume in PDF format
* Extract Resume Text
* Rule-Based ATS Score Calculation
* Resume Strength Analysis
* Missing Skills Detection
* Personalized Improvement Suggestions

## 📊 Dashboard

* Total Resume Analyses
* Average ATS Score
* Highest ATS Score
* Resume History
* Recent Upload Activity

## 📑 Report Generation

* Professional ATS Report
* Download PDF Report
* Save Reports for Future Access

## 💾 Database

* User Accounts
* Resume Reports
* ATS Scores
* Report Generation Date & Time

---

# 🛠️ Tech Stack

### Frontend

* HTML5
* Tailwind CSS
* JavaScript

### Backend

* Python
* Flask

### Database

* SQLite

### Libraries Used

* PyMuPDF (Resume Text Extraction)
* FPDF (PDF Report Generation)
* Werkzeug (Password Hashing & Authentication)

---

# 📂 Project Structure

```text
Smart-Resume-Analyzer/
│
├── static/
│   ├── uploads/
│   ├── reports/
│   ├── images/
│   └── assets/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── analyzer.html
│   ├── history.html
│   ├── report.html
│   └── profile.html
│
├── app.py
├── database.py
├── resume_reports.db
├── requirements.txt
├── README.md
└── .gitignore
```

> **Note:** Update the folder structure above if your project contains additional files or folders.

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/Smart-Resume-Analyzer.git
```

```bash
cd Smart-Resume-Analyzer
```

---

## 2️⃣ Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate the environment:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Run the Application

```bash
python app.py
```

Visit:

```text
http://127.0.0.1:5000
```

---

# 📈 ATS Score Evaluation

The ATS score is calculated using a rule-based evaluation that checks important resume components such as:

* Contact Information
* Professional Summary
* Skills
* Education
* Work Experience
* Projects
* Certifications
* Technical Keywords
* Resume Formatting
* Overall Resume Completeness

Based on these checks, the system generates an ATS score and provides actionable suggestions for improvement.

---

# 🔄 Workflow

```text
User Login
      │
      ▼
Upload Resume (PDF)
      │
      ▼
Extract Resume Text
      │
      ▼
Analyze Resume
      │
      ├── Calculate ATS Score
      ├── Detect Missing Skills
      ├── Generate Suggestions
      │
      ▼
Generate PDF Report
      │
      ▼
Store Report in SQLite Database
      │
      ▼
Display Dashboard & Resume History
```

---

# 📊 Dashboard

The dashboard provides:

* 📄 Total Resume Reports
* ⭐ Average ATS Score
* 🏆 Highest ATS Score
* 🕒 Recent Resume Analyses
* 📥 Download Previous Reports

---

# 💾 Database

SQLite stores:

* User Details
* Login Credentials
* Resume Reports
* ATS Scores
* Resume Analysis Date & Time

---

# 📸 Screenshots

Add screenshots of your application here.

```
<img width="1892" height="895" alt="Screenshot 2026-06-17 171611" src="https://github.com/user-attachments/assets/96cd7f6c-84ed-45da-9bfc-572e3ef25ab7" />

Home Page

Login Page

Register Page

Resume Analyzer

Dashboard

ATS Report

PDF Report
```

---

# 🚀 Future Improvements

* Resume Templates
* Cover Letter Generator
* Dark/Light Theme Toggle
* Export Reports in Multiple Formats
* Email Report Sharing
* Resume Comparison
* Admin Dashboard
* Cloud Deployment
* Multi-language Support

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature-name
```

3. Commit your changes.

```bash
git commit -m "Add new feature"
```

4. Push the branch.

```bash
git push origin feature-name
```

5. Open a Pull Request.

---

# 👨‍💻 Author

**Khushal Shrimal**

Engineering Student | Python Developer | Flask Developer | Web Development Enthusiast

GitHub: https://github.com/khushalshrimal



---

# ⭐ Show Your Support

If you found this project helpful, please consider giving it a ⭐ on GitHub.

Your support helps the project reach more developers and motivates future improvements.

---

# 📄 License

This project is licensed under the **MIT License**.

Feel free to use, modify, and contribute to the project.
