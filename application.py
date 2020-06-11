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


@app.route("/login", methods=["POST"])
def login():
    return "Project 1: TODO"


@app.route("/logout", methods=["POST"])
def index():
    return "Project 1: TODO"


@app.route("/search", methods=["POST"])
def index():
    return "Project 1: TODO"


@app.route("/api/<isbn>", methods=["POST"])
def index():
    return "Project 1: TODO"
