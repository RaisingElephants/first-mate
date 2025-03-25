"""
server/profile.py

Server code for showing user profiles.
"""

import pyhtml as p
from hashlib import sha256
from flask import Blueprint, redirect, request

from first_mate.logic.data import save_data
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
    size = 200
    return p.img(
        src=f"https://gravatar.com/avatar/{hash}?s={size}",
        alt=f"Avatar image for {username}",
        class_="profile-image",
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
    user_to_view = get_user_by_zid(zid)
    if user_to_view is None:
        return str(
            error_page(
                "Profile - Error 404",
                "Error 404",
                "User not found",
                is_user_logged_in(),
            )
        ), 404

    public_profile_text = p.div(class_="profile-description")(
        multiline_str_to_html(user_to_view["public_description"])
        if user_to_view["public_description"]
        else p.i("This user has not added a profile description")
    )

    me = get_user()

    # We are that user
    # TODO: OR if we have matched with the user
    if me and zid == me["zid"]:
        private_profile_text = p.div(class_="profile-description")(
            [multiline_str_to_html(user_to_view["private_description"])]
            if user_to_view["private_description"]
            else [p.i("This user has not added a private profile description")]
        )
    else:
        private_profile_text = []

    if me and zid == me["zid"]:
        edit_option = [p.a(href=f"/profile/{zid}/edit")("Edit profile")]
    else:
        edit_option = []

    return str(
        p.html(
            p.head(
                p.title(f"Profile - {user_to_view['display_name']}"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                navbar(True),
                p.h1(user_to_view["display_name"]),
                profile_image(zid, user_to_view["display_name"]),
                public_profile_text,
                private_profile_text,
                edit_option,
            ),
        )
    )


@profile.get("/<zid>/edit")
def profile_edit_page(zid: str):
    user = get_user()
    if user is None:
        return redirect("/auth/login")
    if user["zid"] != zid:
        return str(
            error_page(
                "Edit Profile - Error 403",
                "Error 403",
                "You cannot edit a profile that isn't yours",
                True,
            )
        ), 403

    return str(
        p.html(
            p.head(
                p.title(f"Profile - {user['display_name']}"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                navbar(True),
                p.h1("Edit profile"),
                profile_image(zid, user["display_name"]),
                p.i("You can edit your profile picture using Gravatar"),
                p.form(
                    # Main profile edit
                    # Name
                    p.label(for_="edit-name")(p.p("Display name")),
                    p.input(
                        id="edit-name",
                        name="name",
                        placeholder="Display name",
                        value=user["display_name"],
                        required=True,
                    ),
                    # Profile description
                    p.label(for_="edit-public-description")(
                        p.p("Public profile description. This is shown to all users."),
                    ),
                    p.textarea(style="width: 100%; height: 200px;")(
                        id="edit-public-description",
                        name="public_description",
                        placeholder="Your public profile description",
                    )(user["public_description"]),
                    p.label(for_="edit-private-description")(
                        p.p(
                            "Public profile description. This is only shown to "
                            "users who you have matched with."
                        ),
                    ),
                    p.textarea(style="width: 100%; height: 200px;")(
                        id="edit-private-description",
                        name="private_description",
                        placeholder="Your private profile description",
                    )(user["private_description"]),
                    # TODO: Degrees
                    # Submit
                    p.input(type="submit", value="Save"),
                ),
            ),
        )
    )


@profile.post("/<zid>/edit")
def profile_edit_submit(zid: str):
    user = get_user()
    if user is None:
        return redirect("/auth/login")
    if user["zid"] != zid:
        return str(
            error_page(
                "Edit Profile - Error 403",
                "Error 403",
                "You cannot edit a profile that isn't yours",
                True,
            )
        ), 403

    display_name = request.form["name"]
    public_description = request.form["public_description"]
    private_description = request.form["private_description"]

    user["display_name"] = display_name
    user["public_description"] = public_description
    user["private_description"] = private_description
    save_data()

    return redirect(f"/profile/{zid}")
