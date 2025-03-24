"""
server/auth.py

Server code for authentication.
"""

import pyhtml as p
from flask import Blueprint, request

from .util import list_to_checkboxes
from ..consts import DEGREES_LIST




auth = Blueprint("/auth", __name__)


@auth.get("/register")
def register_page():
    return str(
        p.html(
            p.head(
                p.title("Register - First Mate"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                p.h1("Registration"),
                p.div(id="login-box")(
                    p.form(
                        p.p(
                            p.label(for_="zid")("Your zID"),
                            p.input(
                                name="zid",
                                id="zid",
                                placeholder="z1234567",
                                required=True,
                            ),
                        ),
                        p.p(
                            p.label(for_="name")("Your name"),
                            p.input(
                                name="name",
                                id="name",
                                placeholder="Robin Banks",
                                required=True,
                            ),
                        ),
                        p.p(
                            p.label(for_="password")("Your password"),
                            p.input(
                                type="password",
                                name="password",
                                id="password",
                                placeholder="********",
                                required=True,
                            ),
                        ),
                        p.p(
                            p.label(for_="ical")("Your UNSW calendar iCal link"),
                            p.input(
                                type="url",
                                name="ical",
                                id="ical",
                                placeholder="webcal://my.unsw.edu.au/cal/pttd/ABCDEFGHIJ.ics",
                                required=True,
                            ),
                        ),
                        p.div(
                            p.p("Select your degree(s)"),
                            list_to_checkboxes(DEGREES_LIST, "degrees"),
                        ),
                        p.p(
                            p.input(type="submit", value="Sign up"),
                        ),
                    ),
                ),
            ),
        )
    )


# @auth.post("/register")
# def register_submit():
#     zid = request.form["zid"]
#     name = request.form["name"]
#     password = request.form["password"]
#     ical = request.form["ical"]
#     degrees = request.form.getlist("degrees")
#
#     register


@auth.get("/login")
def login():
    return str(
        p.html(
            p.head(
                p.title("Login - First Mate"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                p.h1("Login"),
                p.div(id="login-box")(
                    p.form(
                        p.p(
                            p.label(for_="zid")("Your zID"),
                            p.input(name="zid", id="zid", placeholder="z1234567"),
                        ),
                        p.p(
                            p.label(for_="password")("Your password"),
                            p.input(
                                type="password",
                                name="password",
                                id="password",
                                placeholder="********",
                            ),
                        ),
                        p.p(
                            p.input(type="submit", value="Log in"),
                        ),
                    )
                ),
            ),
        )
    )
