"""
server.py

Entrypoint to the first-mate server.
"""

import os
import pyhtml as p
from flask import Flask, send_file

from .session import is_user_logged_in
from .util import navbar
from .auth import auth
from .calendar import calendar
from .debug import debug
from .mates import mates
from .profile import profile


app = Flask(__name__)


# FIXME: Load from .env
app.secret_key = "top secret key"

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(calendar, url_prefix="/calendar")
app.register_blueprint(debug, url_prefix="/debug")
app.register_blueprint(mates, url_prefix="/mates")
app.register_blueprint(profile, url_prefix="/profile")


@app.get("/")
def root():
    logged_in = is_user_logged_in()
    return str(
        p.html(
            p.head(
                p.title("First-mate"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                navbar(logged_in),
                p.h1("First Mate - Raising Elephants"),
                p.div(class_="introduction")(
                    p.p(class_="about-page")(
                        "Our website aims to solve the problem that all UNSW "
                        "students face: making friends with people in their courses."
                    ),
                    p.img(class_="elephant")(
                        src="https://cdn.britannica.com/02/152302-050-1A984FCB/African-savanna-elephant.jpg",
                        alt="Elephant",
                    ),
                    p.p(class_="about-page")(
                        "This elephant used our website to find a friend in COMP1511. "
                        "Now it's happy and you can be too!"
                    ),
                ),
            ),
        ),
    )


@app.get("/static/<filename>")
def serve_static(filename):
    """
    Manually implement static directory because we couldn't convince Flask to
    actually load the data no matter what we tried :(

    Seriously I do not know why it was broken no matter what we did

    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    """
    file_path = os.path.join(os.getcwd(), "first_mate", "static", filename)
    return send_file(file_path)
