from helpers import apology, login_required, generate_text, generate_response, generate_image, osu_user_info, osu_recently_ranked, set_secret_key_for_user, get_secret_key_for_user, encrypt, decrypt
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from flask_session import Session
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from cs50 import SQL
import os
import requests
import re

COMPLETIONS_ENDPOINT = 'https://api.openai.com/v1/completions'


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finalproj.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    keys = db.execute("SELECT name FROM keys WHERE user_id=?", session["user_id"])
    key_names = []
    for name in keys:
        key_names.append(name["name"])
    return render_template('index.html', key_names = key_names)

@app.route("/generate_image", methods=["POST"])
@login_required
def make_image():
    prompt = request.json["prompt"]
    image_url = generate_image(prompt)
    return jsonify({"image_url": image_url})


@app.route("/generate_image", methods=["GET"])
@login_required
def render_image_form():
    return render_template("image_gen.html")


@app.route('/completions', methods=["POST"])
@login_required
def completions():
    api_key = os.environ.get("API_KEY")
    user_input = request.form['text']
    completion = generate_text(COMPLETIONS_ENDPOINT, api_key, user_input)
    return user_input + completion

@app.route('/completions', methods=["GET"])
@login_required
def render_completions_form():
    return render_template("completion.html")

@app.route('/summary', methods=["GET", "POST"])
@login_required
def summary():
    if request.method == "POST":
        api_key = os.environ.get("API_KEY")
        text = request.form.get("tosumm")
        prompt = "Summarize the following text:\n" + text
        summ = generate_text(COMPLETIONS_ENDPOINT, api_key, prompt)
        return render_template('summarized.html', summ = summ)
    else:
        return render_template('summary.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = request.form.get("username")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        rows = db.execute("SELECT * FROM users WHERE username=?", username)
        if not (password == confirmation):
            return apology("Password and confirmation do not match.")
        if password == "" or username == "":
            return apology("Blank username or password.")
        if len(rows) > 0:
            return apology("Username already in use!")
        else:
            set_secret_key_for_user(username)
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            db.execute("INSERT INTO users (username, hash) VALUES(?,?)", username, hash)
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatbot():
    if request.method == "POST":
        api_key = os.environ.get("API_KEY")
        userin = request.form.get("message")
        response = generate_response(userin, api_key)
        return jsonify({"response": response})
    else:
        return render_template("chatbot.html")


@app.route("/osu-api-1", methods=["POST"])
@login_required
def osu_api_1():
    request_data = request.get_json()
    username = request_data["username"]
    response = osu_user_info(username)
    return {
        "username": response[0]["username"],
        "pp_rank": response[0]["pp_rank"],
        "pp_raw": response[0]["pp_raw"],
        "total_seconds_played": response[0]["total_seconds_played"],
        "level": response[0]["level"],
        "playcount": response[0]["playcount"],
        "user_id": response[0]["user_id"],
        "accuracy": response[0]["accuracy"]
    }

@app.route("/osu-api-2", methods=["POST"])
@login_required
def osu_api_2():
    recent_maps = osu_recently_ranked()
    return jsonify(recent_maps)

@app.route("/osu", methods=["GET"])
@login_required
def osu():
    api_key = os.environ.get("API_KEY_OSU")
    return render_template("osu.html", api_key=api_key)


@app.route("/new-key", methods=["POST"])
@login_required
def new_key():
    name = request.form['name']
    key = request.form['key']
    username = session['username']
    rows = db.execute("SELECT * FROM keys WHERE name=? AND user_id=?", name, session["user_id"])
    if name == "" or key == "":
        return apology("Blank input field")
    if len(rows)>0:
        return apology("Please try a unique name")
    else:
        secret_key = get_secret_key_for_user(username)
        encrypted = encrypt(key, secret_key)
        db.execute("INSERT INTO keys (user_id, name, key) VALUES (?,?,?)", session["user_id"], name, encrypted)
    return redirect("/")

@app.route("/any-api", methods=["GET"])
@login_required
def any_api():
    keys = db.execute("SELECT name FROM keys WHERE user_id=?", session["user_id"])
    key_names = []
    for name in keys:
        key_names.append(name["name"])
    return render_template("/any_api.html", key_names = key_names)

@app.route("/api_query", methods=["POST"])
@login_required
def api_query():
    secret_key = get_secret_key_for_user(session["username"])
    key_name = request.form.get('api_key')
    crypt_key = db.execute("SELECT key FROM keys WHERE name=? AND user_id=?", key_name, session["user_id"])
    crypt_key_val = crypt_key[0]["key"]
    api_key = decrypt(crypt_key_val, secret_key)
    key_param = request.form.get('key_param')
    endpoint = request.form.get('endpoint')
    params_in = request.form.get('params')
    if params_in:
        pairs = params_in.split(',')
        params = {}
        for pair in pairs:
            key, value = pair.split(':')
            params[key] = value

    data_list = request.form.get('data')
    if data_list:
        splits = data_list.split(',')
        data = {}
        for pair in splits:
            key, value = pair.split(':')
            data[key] = value

    http_method = request.form.get('http_method')


    if http_method == "get":
        headers = {
            "Content-Type": "application/json"
            }
        endpoint = endpoint + '?' + key_param + '=' + api_key
        response = requests.get(endpoint, headers=headers, params=params)
    elif http_method == "post":
        headers = {
            "Content-Type": "application/json",
            key_param: api_key
            }
        response = requests.post(endpoint, headers=headers, json=data)
    elif http_method == "get_params":
            response = requests.get(endpoint, params=params)
    elif http_method == "no_data":
            response = requests.get(endpoint)
    else:
        return "Invalid HTTP-format"
    if response.status_code == 200:
        # format output and return to user
        output = response.text
        outputf = re.sub(r',', '\n', output)
        return render_template("/api_response.html", output=outputf)
    else:
        print(response)
        return 'Error: API request unsuccessful'

@app.route("/delete-key", methods=["POST"])
@login_required
def delete_key():
    key_name = request.form["key_name"]
    db.execute("DELETE FROM keys WHERE name=? AND user_id=?", key_name, session["user_id"])
    flash("Key Deleted!")
    return redirect("/")


