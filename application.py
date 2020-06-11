import os
from flask import Flask, session, redirect, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from harvard_class.project1.project1.HashPassword import HashPassword

app = Flask(__name__)
#os.environ['FLASK_DEBUG'] = 1
os.environ['GOODREADS_KEY'] = 'xRjIm68xlsyHJHEXN6MPw'
os.environ['DATABASE_URL'] = "postgres://fhtmmpjjvejjxs:a4fc62fd0a563452b14a6900423cd903199060e28207fb93fc06ccf9ae034723@ec2-3-222-30-53.compute-1.amazonaws.com:5432/d11g6lfpjmbrjn"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

# Check for environment variable
if not os.getenv('DATABASE_URL'):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["POST"])
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Function that takes in a post where the user reaches out the route via POST or GET and lets the user register
    for an account
    :return: error or a new user registered for an account
    """
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("error.html", message="Please provide a username")

        user_check = db.execute("SELECT * FROM users WHERE username = :username",
                               {"username": request.form.get("username")}).fetchone()
        if user_check:
            return render_template("error.html", message="This username already exists")
        elif not request.form.get("password"):
            return render_template("error.html", message="Please provide a password")
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="Confirm your password")
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error.html", message="Passwords do not match, please check again")
        hash_pass = HashPassword()
        hashed_password = hash_pass.hash_password(request.form.get("password"))

        # Insert new user into DB
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
                   {"username": request.form.get("username"),
                    "password": hashed_password})
        db.commit()
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    """
    Function that lets the user log in to the website, gets the username and password from the user's input and checks
    that they are both valid
    :return: an error if the username and password do not match, else logs in for the user
    """
    session.clear()
    username = request.form.get("username")
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("error.html", message="Please provide a username")
        elif not request.form.get("password"):
            return render_template("error.html", message="Please provide a password")
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username})
        result = rows.fetchone()
        hash_pass = HashPassword()
        if result == None or not hash_pass.verify_password(result[2], request.form.get("password")):
            return render_template("error.html", message="Invalid username and/or password")
        session["user_id"] = result[0]
        session["user_name"] = result[1]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout", methods=["POST"])
def index():
    return "Project 1: TODO"


@app.route("/search", methods=["POST"])
def index():
    return "Project 1: TODO"


@app.route("/api/<isbn>", methods=["POST"])
def index():
    return "Project 1: TODO"
