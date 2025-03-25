"""
server.py

Entrypoint to the first-mate server.
"""

import os
import pyhtml as p
from flask import Flask, send_file

from first_mate.server.landing_page import render_page

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
    return render_page(logged_in)


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
