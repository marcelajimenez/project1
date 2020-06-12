import os

from flask import Flask, session, redirect, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


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
def index():
    pass


@app.route("/login", method=["POST"])
def login():
    username = request.form.get("name")
    password = request.form.get("password")
    return render_template("login.html", username=username, password=password)
