"""
server.py

Entrypoint to the first-mate server.
"""
import pyhtml as p
from flask import Flask


app = Flask(__name__)


@app.get("/")
def root():
    return str(p.html(
        p.head(p.title("First-mate")),
        p.body(
            p.h1("First-mate"),
            p.p("Hello, world!")
        )
    ))
