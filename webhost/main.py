from flask import Flask, request, render_template_string, redirect, url_for, session, Response, jsonify, stream_with_context
import db.verify
from ai.pdf_evaluate import evaluate
import json
import pymupdf

app = Flask(__name__, static_folder="webpages/build/assets", static_url_path="/assets")
app.config.update(
    SECRET_KEY="TEMP_CHANGE_TO_REAL_SECRET_KEY___uyfdggihdisdfbsDSAFUEPF", # change to .env file
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# refresh session cookie on all requests
@app.before_request
def refresh_session():
    session.modified = True

def get_html_file(name):
    """
        returns the file contents from /webhost/webpages/NAME
        requires the file extention, but not path to webpages
    """
    with open("./webhost/webpages/" + name, "r", encoding="utf-8") as file:
        return file.read()

@app.route("/")
def main_page():
    if (session.get("user") == None):
        return redirect(url_for("login"))
    return get_html_file("build/index.html")

@app.route("/api/get_user")
def get_user():
    if (session.get("user") == None):
        return {"error": "not logged in"}, 401
    return {"user": session["user"]}

def login_attempt(username, password):
    if db.verify.verifyAccount(username, password):

        session.clear()
        session["user"] = username

        return redirect(url_for('main_page'))

    return render_template_string(get_html_file("login.html"), result="failed")

@app.route("/login", methods=["GET", "POST"])
def login():
    result = None
    if request.method == "POST":
        t1 = request.form["username"]
        t2 = request.form["password"]
        return login_attempt(t1, t2) 
    return render_template_string(get_html_file("login.html"))

@app.route("/check_pdf_availability", methods=["GET"])
def check_pdf_availability():
    """If the server already have access to the pdf there is no need to send it over. We check the hashes"""
    hash = request.form["pdf_hash"]
    # look up hash in database if it is there return 1

    # for now just return -1
    return -1


@app.route("/grade_paper", methods=["POST"])
def grade_paper():
    if session.get("user") is None:
        return {"error": "not logged in"}

    file = request.files.get("pdfFile")
    if file is None:
        return {"error": "no pdf uploaded"}

    pdf_bytes = file.read()
    criteria = request.form.getlist("criteria")

    @stream_with_context
    def generate():
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
            for result in evaluate(doc, criteria):
                yield json.dumps(result) + "\n"
    return Response(generate(), mimetype="application/x-ndjson")
    

@app.route("/api/hello")
def hello():
    print("api/hello")
    if (session.get("user") == None):
        print("none")
        return jsonify({"user": ""})    
    print(session.get('user'))
    return jsonify({"user": session.get('user')})

@app.route("/api/login", methods=["POST"])
def tmp():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "")
    password = data.get("password", "")

    user = None
    if db.verify.verifyAccount(username, password):
        user = username

    if user:
        session["user"] = username
        return jsonify({"success": True})

    return jsonify({"success": False}), 401

@app.route("/api/grade_paper", methods=["POST"])
def ermm():
    print("test")
    return grade_paper()
