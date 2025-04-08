"""
server/calendar.py

Server code for calendar work
"""

import pyhtml as p
from flask import Blueprint, redirect, request

from first_mate.logic.data import save_data
from first_mate.logic.event_overlap import Mate, find_mates
from first_mate.logic.ical_analysis import get_week_range
from first_mate.logic.user import User, get_user_by_id
from first_mate.server.session import get_user
from first_mate.server.util import (
    error_page,
    generate_head,
    navbar,
    profile_banner_html,
    week_offset_to_str,
)


mates = Blueprint("/mates", __name__)


def mate_to_html(us: User, mate: Mate, week_offset: int) -> p.div:
    them = get_user_by_id(mate["id"])
    assert them is not None

    return profile_banner_html(
        mate["id"],
        link=week_offset,
        you_liked=mate["id"] in us["likes"],
        liked_you=us["id"] in them["likes"],
    )


@mates.get("/")
def show_potential_mates():
    user = get_user()

    if user is None:
        return redirect("/auth/login")

    # NOTE: Week offset is duplicated with /calendar, perhaps use helper
    # function?
    week_offset = int(request.args.get("offset", "0"))
    start, end = get_week_range(week_offset)
    week_str = f"{week_offset_to_str(week_offset)}, {start.strftime('%x')} - {end.strftime('%x')}"

    time_picker = p.div(_class="time-picker")(
        p.a(href=f"?offset={week_offset - 1}", _class="btn btn-outline")(
            "Previous week"
        ),
        week_str,
        p.a(href=f"?offset={week_offset + 1}", _class="btn btn-outline")("Next week"),
    )

    mates = find_mates(user, start, end)

    mates_html = (
        [mate_to_html(user, mate, week_offset) for mate in mates]
        if len(mates)
        else [
            p.p(p.i("No matches this week. Try checking another week")),
            # FIXME: If we're not feeling edgy, remove this image
            p.img(
                src="/static/no-bitches.jpg",
                alt="No bitches meme",
                style="width: 100%; height: 400px; border-radius: 20px; margin: 20px;",
            ),
        ]
    )

    return str(
        p.html(
            generate_head("Mates", ["/static/profile.css"]),
            p.body(
                navbar(True),
                p.h1("Your mate recommendations"),
                time_picker,
                mates_html,
            ),
        )
    )


@mates.post("/like/<int:id>")
def like_user(id: int):
    """Called when the user likes a user"""
    user = get_user()

    if user is None:
        return redirect("/auth/login")

    if user["id"] == id:
        return str(
            error_page(
                "Error 400",
                "Error 400",
                "You can't like yourself",
                True,
            )
        ), 400

    # Ensure mate exists
    liked_user = get_user_by_id(id)

    if liked_user is None:
        return str(
            error_page(
                "Error 404",
                "Error 404",
                "That user doesn't exist",
                True,
            )
        ), 404

    # Add user ID to liked list
    user["likes"].append(id)
    save_data()

    return redirect(f"/profile/{id}")


@mates.post("/unlike/<int:id>")
def unlike_user(id: int):
    """Called when the user un-likes a user"""
    user = get_user()

    if user is None:
        return redirect("/auth/login")

    if id not in user["likes"]:
        return str(
            error_page(
                "Error 400",
                "Error 400",
                (
                    "You can't unlike someone you never liked to begin with "
                    "- Sun Tsu, The Art of War"
                ),
                True,
            )
        ), 400

    user["likes"].remove(id)
    save_data()

    return redirect("/mates")
