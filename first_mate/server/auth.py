"""
server/auth.py

Server code for authentication.
"""

import pyhtml as p
from flask import Blueprint, redirect, request, session

from .util import error_page, list_to_checkboxes
from ..consts import DEGREES_LIST
from first_mate.logic.user import register_user


auth = Blueprint("/auth", __name__)


@auth.get("/register")
def register_page():
    return str(
        p.html(
            p.head(
                p.title("Login - First Mate"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                p.h1("Login - First Mate"),
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


@auth.post("/register")
def register_submit():
    zid = request.form["zid"]
    name = request.form["name"]
    password = request.form["password"]
    ical = request.form["ical"]
    degrees = request.form.getlist("degrees")

    session_id = register_user(zid, name, password, ical, degrees)
    if session_id is None:
        return str(error_page(
            "Register - Error",
            "Unable to register",
            "Perhaps the account already exists?",
        ))

    session["session_id"] = session_id

    return redirect("/")


@auth.get("/login")
def login():
    return str(
        p.html(
            p.head(
                p.title("Login - First Mate"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                p.h1("Login - First Mate"),
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
