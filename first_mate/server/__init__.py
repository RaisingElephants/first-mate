"""
server.py

Entrypoint to the first-mate server.
"""
import os
import pyhtml as p
from flask import Flask, send_file
from .auth import auth


app = Flask(__name__)


app.register_blueprint(auth, url_prefix="/auth")


@app.get("/")
def root():
    return str(p.html(
        p.head(
            p.title("First-mate"),
            p.link(href="/static/root.css", rel="stylesheet"),
        ),
        p.body(
            p.h1("First Mate"),
            p.p("Hello, world!")
        )
    ))


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
