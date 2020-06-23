import os
from flask import Flask, session, redirect, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from decorator import login_required
from HashPassword import HashPassword

app = Flask(__name__)
os.environ[
    'DATABASE_URL'] = "postgres://fhtmmpjjvejjxs:a4fc62fd0a563452b14a6900423cd903199060e28207fb93fc06ccf9ae034723@ec2-3-222-30-53.compute-1.amazonaws.com:5432/d11g6lfpjmbrjn"

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    The link where the user can register an account for the website
    :return: takes back the user to the login page to login with a new account created
    """
    session.clear()
    username = request.form.get("name")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    if request.method == "POST":
        if username is None:
            return render_template("error.html", message="Please provide username")
        check_user = db.execute("SELECT * FROM users WHERE username = :username",
                                {"username": username}).fetchone()
        if check_user:
            return render_template("error.html", message="The username provided already exists")
        elif password is None:
            return render_template("error.html", message="Please provide a password")
        elif confirmation is None:
            return render_template("error.html", message="Please confirm password")
        elif not password == confirmation:
            return render_template("error.html", message="Passwords do not match, please check again")
        hash_password = HashPassword()
        hashed_password = hash_password.hash_password(password=password)
        # Insert into the database
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
                   {"username": username, "password": hashed_password})
        db.commit()
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
    book_input = request.args.get("book")
    if book_input is None:
        return render_template("error.html", message="Please provide a book")
    book_text = "%{}%".format(book).lower()
    db_result = db.execute("SELECT isbn, LOWER(title), LOWER(author), year FROM books WHERE \
                        isbn LIKE :book_text OR title LIKE :book_text OR \
                        author LIKE :book_text LIMIT 10", {"query": book_text})
    if db_result.rowcount == 0:
        return render_template("error.html", message="There are no books with this description")
    books = db_result.fetchall()
    return render_template("results.html", books=books)


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
        row = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn = :isbn", {"isbn": isbn})
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
        results = db.execute("SELECT users.username, comment, rating, \
                            to_char(time, 'DD Mon YY - HH24:MI:SS') as time \
                            FROM users \
                            INNER JOIN reviews \
                            ON users.id = reviews.user_id \
                            WHERE book_id = :book \
                            ORDER BY time", {"book": book})
        reviews = results.fetchall()
        return render_template("book.html", book_info=book_info, reviews=reviews)
