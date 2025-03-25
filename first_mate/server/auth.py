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
from ..consts import DEGREES_LIST, dev
from first_mate.logic.user import login_user, logout_user, register_user


auth = Blueprint("/auth", __name__)


@auth.get("/register")
def register_page():
    if is_user_logged_in():
        return redirect("/")
    return str(
        p.html(
            p.head(
                p.title("Register - First Mate"),
                p.link(href="/static/root.css", rel="stylesheet"),
                p.link(href="/static/auth.css", rel="stylesheet"),
            ),
            p.body(
                navbar(False),
                p.main(
                    p.div(id="login-box")(
                        p.h1("Let's get you signed up"),
                        p.form(
                            p.div(_class="form-row")(
                                p.label(for_="zid")("Your zID"),
                                p.input(
                                    type="text",
                                    name="zid",
                                    id="zid",
                                    placeholder="z1234567",
                                    required=True,
                                ),
                            ),
                            p.div(_class="form-row")(
                                p.label(for_="name")("Your name"),
                                p.input(
                                    type="text",
                                    name="name",
                                    id="name",
                                    placeholder="Robin Banks",
                                    value="Robin Banks" if dev() else "",
                                    required=True,
                                ),
                            ),
                            p.div(_class="form-row")(
                                p.label(for_="password")("Your password"),
                                p.input(
                                    type="password",
                                    name="password",
                                    id="password",
                                    placeholder="••••••••",
                                    value="abc123ABC" if dev() else "",
                                    required=True,
                                ),
                            ),
                            p.div(
                                p.label(for_="ical")(
                                    "Your iCal link",
                                    p.br(),
                                    "You can access your calendar link from the 'Student timetable' page on MyUNSW.",
                                    p.br(),
                                ),
                                p.input(
                                    type="url",
                                    name="ical",
                                    id="ical",
                                    placeholder="webcal://my.unsw.edu.au/cal/pttd/ABCDEFGHIJ.ics",
                                    value=(
                                        "webcal://localhost:8000/sid.ics"
                                        if dev()
                                        else ""
                                    ),
                                    required=True,
                                ),
                            ),
                            p.div(
                                p.p("Select your degree(s)"),
                                list_to_checkboxes(DEGREES_LIST, "degrees"),
                            ),
                            p.p(
                                p.input(
                                    type="submit",
                                    value="Sign up",
                                    _class="btn btn-primary",
                                ),
                            ),
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
                p.title("Login - FirstMate"),
                p.link(href="/static/root.css", rel="stylesheet"),
                p.link(href="/static/auth.css", rel="stylesheet"),
            ),
            p.body(
                navbar(False),
                p.main(
                    p.div(id="login-box")(
                        p.h1("Sign in to FirstMate"),
                        p.form(
                            p.div(_class="form-row")(
                                p.label(for_="zid")("Your zID"),
                                p.input(
                                    type="text",
                                    name="zid",
                                    id="zid",
                                    placeholder="z1234567",
                                ),
                            ),
                            p.div(_class="form-row")(
                                p.label(for_="password")("Your password"),
                                p.input(
                                    type="password",
                                    name="password",
                                    id="password",
                                    placeholder="********",
                                    value="abc123ABC" if dev() else "",
                                ),
                            ),
                            p.div(
                                p.input(
                                    type="submit",
                                    value="Log in",
                                    _class="btn btn-primary",
                                ),
                            ),
                        ),
                    ),
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
