
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from cs50 import SQL
# import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
db = SQL("sqlite:///notes.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        user_notes_data = db.execute("SELECT note_title FROM notes WHERE user_id = ?", session["user_id"])
        note_titles = []
        note_content = ""
        if user_notes_data:
            for user_note in user_notes_data:
                note_titles.append(user_note['note_title'])
        note_content = db.execute("SELECT note_content FROM notes WHERE user_id = ?", session["user_id"])[0]['note_content']
        return render_template("index.html", note_content=note_content, note_titles=note_titles, username=username)
    else:
        if request.form['type'] == "save":
            # Save note content
            note_title = request.form["note_title"]
            note_content_updated = request.form["note_content_updated"]
            try:
                note_content_updated.decode("utf-8").replace("\u2022", "").encode("utf-8")
                note_content_updated.decode("utf-8").replace("\u200B", "").encode("utf-8")
            except Exception as e:
                print(e)
            else:
                note_content_updated.replace("\u2022", "").encode("utf-8")
                note_content_updated.replace("\u200B", "").encode("utf-8")
            print(note_content_updated)
            db.execute("UPDATE notes SET note_content = ? WHERE note_title = ?", note_content_updated, note_title)
            Message = {"Message": "Save successful"}
            return Message
        elif request.form['type'] == "switch":
            # Save old note content first
            try:
                cur_note_title = request.form["cur_note_title"]
                cur_note_content_updated = request.form["cur_note_content_updated"]
                db.execute("UPDATE notes SET note_content = ? WHERE note_title = ?", cur_note_content_updated, cur_note_title)
            except Exception as e:
                print(e)
            # Send new note content
            next_note_title = request.form["next_note_title"]
            print("next_note_title: ", next_note_title)
            next_note_content = db.execute("SELECT * FROM notes WHERE user_id = ? AND note_title = ?", session["user_id"], next_note_title)[0]['note_content']
            Message = {
                "next_note_content": next_note_content,
                "next_note_title": next_note_title
                }
            return Message
        elif request.form['type'] == "new_note":
            # Save old note content first
            cur_note_title = request.form["cur_note_title"]
            cur_note_content_updated = request.form["cur_note_content_updated"]
            if cur_note_title:
                db.execute("UPDATE notes SET note_content = ? WHERE note_title = ?", cur_note_content_updated, cur_note_title)
            # Create new note
            next_note_title = request.form["next_note_title"]
            db.execute("INSERT INTO notes (user_id, note_title, note_content) VALUES (?, ?, ?)", session["user_id"], next_note_title, "")
            Message = {
                "message": "Successfully created new note",
                "next_note_title": next_note_title
                }
            return Message
        elif request.form['type'] == "edit_title":
            # Edit value in SQL
            cur_note_title = request.form["cur_note_title"]
            next_note_title = request.form["next_note_title"]
            # Check current list of notes for duplicity
            user_notes_data = db.execute("SELECT * FROM notes WHERE user_id = ?", session["user_id"])
            note_titles = []
            note_content = ""
            if user_notes_data:
                for user_note in user_notes_data:
                    note_titles.append(user_note['note_title'].upper())
            if next_note_title.upper() in note_titles:
                return "Error: Title already exists", 400
            # Update database
            if next_note_title.replace(" ", "").replace("-", "").isalnum():
                db.execute("UPDATE notes SET note_title = ? WHERE note_title = ?", next_note_title, cur_note_title)
                Message = {
                    "message": "Successfully edited note title",
                    "next_note_title": next_note_title
                }
                return Message
            else:
                return "Error: Not alphanumeric", 400
        elif request.form['type'] == "setup_buttons":
            user_notes_data = db.execute("SELECT * FROM notes WHERE user_id = ?", session["user_id"])
            note_titles = []
            if user_notes_data:
                for user_note in user_notes_data:
                    note_titles.append(user_note['note_title'])
            Message = {
                "message": "Loaded buttons",
                "note_titles": note_titles
            }
            return Message
        elif request.form['type'] == "delete_note":
            note_to_delete = request.form["cur_note_title"]
            db.execute("DELETE FROM notes WHERE user_id = ? AND  note_title = ?", session["user_id"], note_to_delete)
            Message = {
                "message": "Deleted: " + note_to_delete
            }
            return Message

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        # Open register page
        return render_template("/register.html")
    else:
        # Check if entered username is alphanumeric)
        username = request.form.get("username")
        password = request.form.get("password")
        usernames = db.execute("SELECT username FROM users;")
        if not username.isalnum() or not password.isalnum():
            return "Error: Username and password must be alphanumeric", 400
        # Check if entered username is unique)
        for line in usernames:
            if username == line["username"]:
                return "Error: Duplicate username", 400
        confirmation = request.form.get("confirmation")
        # Check password confirmation and store to database
        if password == confirmation and username and password:
            password_hash = generate_password_hash(password)
            security_question = request.form.get("security_question")
            security_answer = request.form.get("security_answer")
            db.execute("INSERT INTO users (username, hash, security_question, security_answer) VALUES (?, ?, ?, ?)", username, password_hash, security_question, security_answer)
            flash("User registered successfully")
            # Add sample note for user
            add_sample_note(username)
            return redirect("/")
        else:
            return "Confirmation password does not match", 400


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    """Let user change password after security questions"""
    if request.method == "GET":
        security_questions_db = db.execute("SELECT username, security_question FROM users")
        security_questions_dict = {}
        for line in security_questions_db:
            security_questions_dict[line["username"]] = line["security_question"]
        return render_template("/forgot.html", security_questions_dict=security_questions_dict)
    if request.method == "POST":
        print("IN POST")
        username = request.form["username"]
        if request.form["type"] == "check_username":
            print("IN CHECK USERNAME")
            usernames = db.execute("SELECT username FROM users;")
            username_found = False
            for line in usernames:
                if username == line["username"]:
                    username_found = True
            if not username_found:
                Message = {
                    "message": "Error. Username not found"
                }
            else:
                security_question = db.execute("SELECT security_question FROM users WHERE username = ?", username)[0]["security_question"]
                Message = {
                    "message": "Username found",
                    "security_question": security_question
                }
            return Message
        if request.form["type"] == "change_password":
            # Verify entries
            forgot_security_answer = request.form["security_answer"]
            stored_security_answer = db.execute("SELECT security_answer FROM users WHERE username = ?", username)[0]["security_answer"]
            new_password = request.form["password"]
            new_confirmation = request.form["confirmation"]
            if new_password != new_confirmation:
                return "Password and confirmation do not match", 400
            if stored_security_answer.upper() != forgot_security_answer.upper():
                return "Incorrect security answer", 400
            # Store password if all is good
            new_password_hash = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = ? WHERE username = ?", new_password_hash, username)
            Message = {
                "message": "Success editing password"
            }
            return redirect("/")


def add_sample_note(username):
    user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
    note_title = "Sample Note"
    note_content = "Sample Text"
    db.execute("INSERT INTO notes (user_id, note_title, note_content) VALUES (?, ?, ?)", user_id, note_title, note_content)