from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/upload")
def upload():
    return "<h1>Upload Resume Page</h1>"

if __name__ == "__main__":
    app.run(debug=True)