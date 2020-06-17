import os
from flask import Flask, session, redirect, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from decorator import login_required
from HashPassword import HashPassword


app = Flask(__name__)
os.environ['DATABASE_URL'] = "postgres://fhtmmpjjvejjxs:a4fc62fd0a563452b14a6900423cd903199060e28207fb93fc06ccf9ae034723@ec2-3-222-30-53.compute-1.amazonaws.com:5432/d11g6lfpjmbrjn"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    """
    Display the search box if the user is logged in
    :return: website with the search boxes
    render_template("index.html")
    """
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login route, where users can input their username and password
    :return: login page
    """
    session.clear()
    username = request.form.get("name")
    password = request.form.get("password")
    if request.method == "POST":
        if username is None:
            return render_template("error.html", message="Please provide username")
        elif password is None:
            return render_template("error.html", message="Please provide password")
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username})
        result = rows.fetchone()
        hash_password = HashPassword()
        if result is None or not hash_password.verify_password(stored_password=result[2],
                                                               provided_password=password):
            return render_template("error.html", message="Check username and password")
        session["user_id"] = result[0]
        session["user_name"] = result[1]
        return redirect("/")
    else:
        return render_template("login.html")
