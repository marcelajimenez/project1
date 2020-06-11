from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User:
    """
    Class that defines what the user will input
    """
    def __init__(self, user, password):
        self.user = user
        self.password = password


def add_user(user, password):
    """
    Function that takes in the user name and password and adds it into the session
    """
    user = User(user=user, password=password)
    db.session.add(user)
