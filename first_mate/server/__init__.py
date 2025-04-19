"""
server.py

Entrypoint to the first-mate server.
"""

import os
from flask import Flask

from first_mate.consts import dev
from first_mate.server.landing import render_page

from .session import is_user_logged_in
from .auth import auth
from .debug import debug
from .mates import mates
from .profile import profile


app = Flask(__name__)


app.secret_key = os.getenv("FIRSTMATE_SECRET")

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(mates, url_prefix="/mates")
app.register_blueprint(profile, url_prefix="/profile")

if dev():
    app.register_blueprint(debug, url_prefix="/debug")


@app.get("/")
def root():
    logged_in = is_user_logged_in()
    return render_page(logged_in)
