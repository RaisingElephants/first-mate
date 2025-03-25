"""
server/auth.py

Server code for authentication.
"""

import pyhtml as p
from flask import Blueprint, redirect, request

from first_mate.server.session import (
    clear_session,
    get_session,
    is_user_logged_in,
    set_session,
)

from .util import error_page, list_to_checkboxes, navbar
from ..consts import DEGREES_LIST
from first_mate.logic.user import login_user, logout_user, register_user


auth = Blueprint("/auth", __name__)


@auth.get("/register")
def register_page():
    if is_user_logged_in():
        return redirect("/")
    return str(
        p.html(
            p.head(
                p.title("Login - First Mate"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                navbar(False),
                p.h1("Login - First Mate"),
                p.div(id="login-box")(
                    p.form(
                        p.p(
                            p.label(for_="zid")("Your zID"),
                            p.input(
                                name="zid",
                                id="zid",
                                placeholder="z1234567",
                                value="z1234567",
                                required=True,
                            ),
                        ),
                        p.p(
                            p.label(for_="name")("Your name"),
                            p.input(
                                name="name",
                                id="name",
                                placeholder="Robin Banks",
                                value="Robin Banks",
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
                                value="abc123ABC",
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
                                value="http://127.0.0.1:8000/simple.ics",
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
    if is_user_logged_in():
        return redirect("/")
    zid = request.form["zid"]
    name = request.form["name"]
    password = request.form["password"]
    ical = request.form["ical"]
    degrees = request.form.getlist("degrees")

    session_id = register_user(zid, name, password, ical, degrees)
    if session_id is None:
        return str(
            error_page(
                "Register - Error",
                "Unable to register",
                "Perhaps the account already exists?",
                False,
            )
        )

    set_session(session_id)

    return redirect("/")


@auth.get("/login")
def login():
    if is_user_logged_in():
        return redirect("/")
    return str(
        p.html(
            p.head(
                p.title("Login - First Mate"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                navbar(False),
                p.h1("Login - First Mate"),
                p.div(id="login-box")(
                    p.form(
                        p.p(
                            p.label(for_="zid")("Your zID"),
                            p.input(
                                name="zid",
                                id="zid",
                                placeholder="z1234567",
                                value="z1234567",
                            ),
                        ),
                        p.p(
                            p.label(for_="password")("Your password"),
                            p.input(
                                type="password",
                                name="password",
                                id="password",
                                placeholder="********",
                                value="abc123ABC",
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


@auth.post("/login")
def login_submit():
    if is_user_logged_in():
        return redirect("/")
    zid = request.form["zid"]
    password = request.form["password"]

    session_id = login_user(zid, password)
    if session_id is None:
        return str(
            error_page(
                "Register - Error",
                "Unable to log in",
                "zID or password is incorrect",
                False,
            )
        )

    set_session(session_id)

    return redirect("/")


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    session = get_session()
    if session is None:
        return redirect("/")
    logout_user(session)
    clear_session()
    return redirect("/")
