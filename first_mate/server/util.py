"""
server/util.py

Utility code
"""

from hashlib import sha256
from itertools import chain, repeat
import random

import pyhtml as p

from first_mate.logic.user import get_user_by_zid


def week_offset_to_str(offset: int) -> str:
    """Given a week offset, return a user-friendly display string

    Parameters
    ----------
    offset : int
        week offset. `0` is this week, `-1` is last week, and `1` is next week.

    Returns
    -------
    str
        string representing week offset.
    """
    match offset:
        case -1:
            return "Last week"
        case 1:
            return "Next week"
        case n if n < -1:
            return f"{-n} weeks ago"
        case n if n > 1:
            return f"{n} weeks from now"
        case _:
            return "This week"


def list_to_checkboxes(
    values: list[str],
    input_name: str,
) -> p.Tag:
    """
    Given a list of possible values, return a collections of
    checkboxes that allows users to select them.
    """

    html_values = [
        p.p(
            p.input(type="checkbox", name=input_name, id=value, value=value),
            p.label(for_=value)(value),
        )
        for value in values
    ]

    return p.div(html_values)


def navbar(logged_in: bool) -> p.nav:
    if logged_in:
        auth_options = [
            p.a(href="/calendar")(p.h2("My calendar")),
            p.a(href="/mates")(p.h2("Find mates")),
            p.a(href="/profile")(p.h2("My profile")),
            p.a(href="/auth/logout")(p.h2("Log out")),
        ]
    else:
        auth_options = [
            p.a("Register", href="/auth/register", Class="btn btn-primary"),
            p.a("Log In", href="/auth/login", Class="btn btn-outline"),
        ]

    # TODO: Make this only enabled in debug mode
    debug_options = [
        p.form(action="/debug/clear", _class="debug_button")(
            p.input(type="submit", value="Reset server"),
        )
    ]

    return p.nav(p.a(href="/")(p.h1("First Mate")), auth_options, debug_options)


def error_page(
    title: str,
    heading: str,
    text: str,
    logged_in: bool,
) -> p.html:
    return p.html(
        p.head(
            p.title(title),
            p.link(href="/static/root.css", rel="stylesheet"),
        ),
        p.body(
            navbar(logged_in),
            p.div(id="error-page")(
                p.h1(heading),
                p.p(text),
            ),
        ),
    )


def multiline_str_to_html(text: str) -> p.div:
    """Convert a multi-line string.

    Required since HTML ignores whitespace, so we need to convert each '\\n' to
    a `<br>` tag.

    Parameters
    ----------
    text : str
        text to convert to HTML

    Returns
    -------
    p.div
        HTML of multi-line string
    """
    return p.div(
        # https://stackoverflow.com/a/58718461/6335363
        list(
            chain.from_iterable(
                zip(
                    text.splitlines(),
                    repeat(p.br()),
                )
            )
        )
    )


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
        _class="profile-image",
    )


def profile_banner_html(
    zid: str,
    *,
    matched: bool = False,
    link: bool = False,
    is_me: bool = False,
) -> p.div:
    """Generate a banner for a user's profile

    Parameters
    ----------
    zid : str
        zID of profile to generate
    matched : bool
        Whether to show the private match-only data.

    Returns
    -------
    p.div
        HTML for profile banner
    """
    user_to_view = get_user_by_zid(zid)
    assert user_to_view is not None

    public_profile_text = p.div(_class="profile-description")(
        multiline_str_to_html(user_to_view["public_description"])
        if user_to_view["public_description"]
        else p.i("This user has not added a profile description")
    )

    if matched:
        display_name = f"{user_to_view['display_name']} - {zid}"
        private_profile_text = p.div(_class="profile-description")(
            [multiline_str_to_html(user_to_view["private_description"])]
            if user_to_view["private_description"]
            else [p.i("This user has not added a private profile description")]
        )
    else:
        display_name = user_to_view["display_name"]
        private_profile_text = []

    name_html = (
        p.a(href=f"/profile/{zid}")(display_name) if link else p.span(display_name)
    )

    if is_me:
        its_you_text = [
            p.p(
                p.i(
                    "It's you!"
                    if random.randint(0, 9)
                    else "Despite everything, it's still you."
                )
            )
        ]
    else:
        its_you_text = []

    return p.div(_class="profile-banner")(
        profile_image(zid, user_to_view["display_name"]),
        p.div(_class="profile-banner-inner")(
            p.h2(name_html),
            its_you_text,
            public_profile_text,
            private_profile_text,
        ),
    )
