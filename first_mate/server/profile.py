"""
server/profile.py

Server code for showing user profiles.
"""

import pyhtml as p
from hashlib import sha256
from flask import Blueprint, redirect, request

from first_mate.logic.user import get_user_by_zid
from first_mate.server.session import get_user, is_user_logged_in
from first_mate.server.util import (
    error_page,
    multiline_str_to_html,
    navbar,
)


profile = Blueprint("/profile", __name__)


def profile_image(zid: str, username: str) -> p.img:
    """Use gravatar to create an image element for the given user

    Parameters
    ----------
    zid : str
        zID to get avatar for
    username : str
        Username to display in alt text

    Returns
    -------
    p.img
        Image element
    """
    email = f"{zid}@ad.unsw.edu.au"
    hash = sha256(email.encode()).hexdigest()
    return p.img(
        src=f"https://gravatar.com/avatar/{hash}",
        alt=f"Avatar image for {username}",
    )


@profile.get("/")
def profile_root():
    user = get_user()
    if user is None:
        return redirect("/auth/login")
    # /profile/{zid}
    return redirect(user["zid"])


@profile.get("/<zid>")
def profile_page(zid: str):
    user = get_user_by_zid(zid)
    if user is None:
        return str(
            error_page(
                "Profile - Error 404",
                "Error 404",
                "User not found",
                is_user_logged_in(),
            )
        )

    return str(
        p.html(
            p.head(
                p.title(f"Profile - {user['display_name']}"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                navbar(True),
                p.h1(user["display_name"]),
                profile_image(zid, user["display_name"]),
                multiline_str_to_html(user["profile_text"]),
            ),
        )
    )
