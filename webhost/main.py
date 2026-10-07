from flask import Flask, request, render_template_string, redirect, url_for, session, Response
import db.verify

app = Flask(__name__)
app.config.update(
    SECRET_KEY="TEMP_CHANGE_TO_REAL_SECRET_KEY___uyfdggihdisdfbsDSAFUEPFJPS", # change to .env file
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Strict",
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
    return render_template_string(get_html_file("main_page.html"))

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


@app.route("/grade_paper", methods=["POST"])
def grade_paper():
    text = request.get_data(as_text=True)
    mode = request.headers.get("Review-mode")
    print(text)
    print(mode)
    if (mode == "core_eval_standard"):
        return f"""Text is results: \r\n
                    Integrity and Reproducability: 10/10\n
                    Novelty and Signifiance: 10/10\n
                    Peer Review and Transparancy: 10/10\n
                    Output and Impact Metrics: 10/10\n
                """
    result = f"That paper lit: {text}"
    return Response(result, content_type="text/plain")
