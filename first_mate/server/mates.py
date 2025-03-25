"""
server/calendar.py

Server code for calendar work
"""

from datetime import datetime
import pyhtml as p
from flask import Blueprint, redirect, request

from first_mate.logic.data import save_data
from first_mate.logic.event_overlap import MatchInfo, Mate, find_mates
from first_mate.logic.ical_analysis import get_week_range
from first_mate.logic.user import User, get_user_by_zid
from first_mate.server.session import get_user
from first_mate.server.util import (
    error_page,
    navbar,
    profile_banner_html,
    week_offset_to_str,
)

from ..consts import LOCAL_TZ


mates = Blueprint("/mates", __name__)


def match_to_html(match: MatchInfo) -> p.div:
    timing = "Before" if match["before"] else "After"
    time_str = datetime.fromtimestamp(match["time"], LOCAL_TZ).strftime("%c")

    return p.div(
        p.p(
            f"{timing} {match['class_description']}",
            p.br(),
            f"At {time_str}",
        )
    )


def mate_to_html(us: User, mate: Mate) -> p.div:
    them = get_user_by_zid(mate["zid"])
    assert them is not None

    matches_html = [match_to_html(match) for match in mate["matches"]]

    return p.div(
        profile_banner_html(
            mate["zid"],
            link=True,
            you_liked=mate["zid"] in us["likes"],
            liked_you=us["zid"] in them["likes"],
        ),
        p.p("Not matched yet"),
        matches_html,
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

    mates = find_mates(user, start, end)

    mates_html = (
        [mate_to_html(user, mate) for mate in mates]
        if len(mates)
        else [
            p.p(p.i("No mates this week. Try checking another week")),
            # FIXME: If we're not feeling edgy, remove this image
            p.img(
                src="/static/no-bitches.jpg",
                alt="No bitches meme",
                width="100%",
                height="400px",
            ),
        ]
    )

    prev_week = p.a(href=f"?offset={week_offset - 1}")("Previous week")
    next_week = p.a(href=f"?offset={week_offset + 1}")("Next week")

    return str(
        p.html(
            p.head(
                p.title("Calendar view"),
                p.link(href="/static/root.css", rel="stylesheet"),
            ),
            p.body(
                navbar(True),
                p.h1("Your mate recommendations"),
                p.div(
                    prev_week,
                    week_str,
                    next_week,
                ),
                mates_html,
            ),
        )
    )


@mates.post("/like/<zid>")
def like_user(zid: str):
    """Called when the user likes a user"""
    user = get_user()

    if user is None:
        return redirect("/auth/login")

    if user["zid"] == zid:
        return str(
            error_page(
                "Error 400",
                "Error 400",
                "You can't like yourself",
                True,
            )
        ), 400

    # Ensure mate exists
    liked_user = get_user_by_zid(zid)

    if liked_user is None:
        return str(
            error_page(
                "Error 404",
                "Error 404",
                "That user doesn't exist",
                True,
            )
        ), 404

    # Add zid to liked list
    user["likes"].append(zid)
    save_data()

    return redirect("/mates")


@mates.post("/unlike/<zid>")
def unlike_user(zid: str):
    """Called when the user un-likes a user"""
    user = get_user()

    if user is None:
        return redirect("/auth/login")

    if zid not in user["likes"]:
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

    user["likes"].remove(zid)
    save_data()

    return redirect("/mates")
