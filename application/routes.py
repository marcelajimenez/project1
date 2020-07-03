import os
import csv
from application import app, db, models
from flask import render_template, session, redirect, flash, jsonify
from flask_session import Session
from flask import request
from application.helpers.decorator import login_required
from application.helpers.HashPassword import HashPassword
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

Session(app)
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    """
    Display the search box if the user is logged in
    :return: website with the search boxes
    """
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login route, where users can input their username and password
    :return: login page
    """
    session.clear()
    username = request.form.get("username")
    password = request.form.get("password")
    if request.method == "POST":
        if not username:
            return render_template("error.html", message="Please provide username")
        elif not password:
            return render_template("error.html", message="Please provide password")
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username})
        db.commit()
        result = rows.fetchone()
        hash_password = HashPassword()
        if result is None or not hash_password.verify_password(stored_password=result[2],
                                                               provided_password=password):
            return render_template("error.html", message="Check username and password")
        session["user_id"] = result[0]
        session["username"] = result[1]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    The link where the user can register an account for the website
    :return: takes back the user to the login page to login with a new account created
    """
    session.clear()
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    if request.method == "POST":
        if not username:
            return render_template("error.html", message="Please provide username")
        try:
            check_user = db.execute("SELECT * FROM users WHERE username = :username",
                                    {"username": username}).fetchone()
            if check_user:
                return render_template("error.html", message="The username provided already exists")
            elif not password:
                return render_template("error.html", message="Please provide a password")
            elif not confirmation:
                return render_template("error.html", message="Please confirm password")
            elif not password == confirmation:
                return render_template("error.html", message="Passwords do not match, please check again")
        except:
            pass
        hash_password = HashPassword()
        hashed_password = hash_password.hash_password(password=password)
        # Insert into the database
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                   {"username": username, "password": hashed_password})
        db.commit()
        flash('Account created', 'info')
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """
    User logs out of the website
    :return: takes the user back to the home page
    """
    session.clear()
    return redirect("/")


@app.route("/search", methods=["GET"])
@login_required
def search():
    """
    Link where the user can search for book reviews using isbn, title, author
    :return: information on the book
    """
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()
    book = request.args.get("book")
    if not book:
        return render_template("error.html", message="Please provide a book")
    text = "%{}%".format(book).lower()
    db_result = db.execute("""SELECT isbn, LOWER(title), LOWER(author), year FROM books WHERE 
                        isbn LIKE :text OR title LIKE :text OR 
                        author LIKE :text LIMIT 10""", {"query": text})
    if db_result.rowcount == 0:
        return render_template("error.html", message="There are no books with this description")
    books = db_result.fetchall()
    return render_template("search.html", books=books)


@app.route("/book/<isbn>", methods=['GET', 'POST'])
@login_required
def book(isbn):
    """
    Function that saves the review from the user
    :return: the web page updated with the new review
    """
    if request.method == "POST":
        user = session["user_id"]
        rating = request.form.get("rating")
        comment = request.form.get("comment")
        db_result = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn})
        book_id = db_result.fetchone()
        book_id = book_id[0]
        row_check = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                               {"user_id": user, "book_id": book_id})
        if row_check.rowcount == 1:
            flash('You already submitted a review for this book', 'warning')
            return redirect("/book/" + isbn)
        rating = int(rating)
        db.execute("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES \
                    (:user_id, :book_id, :comment, :rating)",
                   {"user_id": user, "book_id": bookId, "comment": comment, "rating": rating})
        db.commit()
        flash('Review submitted!', 'info')
        return redirect("/book/" + isbn)
    else:
        row = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn", {"isbn": isbn})
        book_info = row.fetchall()
        key = os.getenv("GOODREADS_KEY")
        query = requests.get("https://www.goodreads.com/book/review_counts.json",
                             params={"key": key, "isbns": isbn})
        response = query.json()
        response = response['books'][0]
        book_info.append(response)
        row = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn})
        book = row.fetchone()  # (id,)
        book = book[0]
        results = db.execute("""
                            SELECT users.username, comment, rating, to_char(time, 'DD Mon YY - HH24:MI:SS') as time 
                            FROM users INNER JOIN reviews ON users.id = reviews.user_id \
                            WHERE book_id = :book ORDER BY time""", {"book": book})
        reviews = results.fetchall()
        return render_template("book.html", book_info=book_info, reviews=reviews)


@app.route("/api/<isbn>", methods=['GET'])
@login_required
def api_call(isbn):
    """
    Function that returns the json result if the user navigates with api call
    :param isbn: isbn code the code
    :return: json result
    """

    row = db.execute(""" 
                    SELECT title, author, year, isbn, COUNT(reviews.id) as review_count, 
                    AVG(reviews.rating) as average_score FROM books 
                    INNER JOIN reviews ON books.id = reviews.book_id \
                    WHERE isbn = :isbn GROUP BY title, author, year, isbn""",
                     {"isbn": isbn})
    if row.rowcount != 1:
        return jsonify({"Error": "Invalid book ISBN"}), 422
    tmp = row.fetchone()
    result = dict(tmp.items())
    result['average_score'] = float('%.2f' % (result['average_score']))
    return jsonify(result)
