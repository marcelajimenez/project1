from functools import wraps
from flask import redirect, render_template, request, session


def login_required(f):
    """
    Decorate routes to require login
    """
    @wraps(f)
    def dec_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return dec_function