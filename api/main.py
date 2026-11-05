from flask import Flask, request, render_template_string, redirect, url_for, session, Response, jsonify, stream_with_context
import db.verify
import db.db
from ai.pdf_evaluate import evaluate
import json
import pymupdf

app = Flask(__name__, static_folder="webpages/build/assets",
            static_url_path="/assets")
app.config.update(
    # change to .env file
    SECRET_KEY="TEMP_CHANGE_TO_REAL_SECRET_KEY___uyfdggihdisdfbsDSAFUEPFAA",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)


# refres session cookie on all requests
@app.before_request
def refresh_session():
    session.modified = True


@app.route("/api/get_user")
def get_user():
    if (session.get("user") is None):
        return {"error": "not logged in"}, 401
    return {"user": session["user"]}


@app.route("/check_pdf_availability", methods=["GET"])
def check_pdf_availability():
    """If the server already have access to the pdf there is no need to send it over. We check the hashes"""
    hash = request.form["pdf_hash"]
    # look up hash in database if it is there return 1

    # for now just return -1
    return -1


@app.route("/api/get_session_username")
def get_session_username():
    print("api/hello")
    if (session.get("user") is None):
        print("none")
        return jsonify({"user": ""})
    print(session.get('user'))
    return jsonify({"user": session.get('user')})


@app.route("/api/login", methods=["POST"])
def api_login():
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


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json(silent=True) or {}

    # Account details for creating account
    username = data.get("username", "")
    password = data.get("password", "")

    print(username, password)
    print("Testing Testing")

    session['user'] = username

    if db.db.add_user(username, username, password):
        return jsonify({
            "success": True
        })

    return jsonify({
        "success": False
    })


@app.route("/api/grade_paper", methods=["POST"])
def api_grade_paper():
    if (session.get("user") is None):
        return "Not logged in", 403
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
