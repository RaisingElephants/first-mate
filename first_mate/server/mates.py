"""
server/calendar.py

Server code for calendar work
"""

from datetime import datetime
import pyhtml as p
from flask import Blueprint, redirect

from first_mate.logic.event_overlap import MatchInfo, Mate, find_mates
from first_mate.logic.user import get_user_by_zid
from first_mate.server.session import get_user

from ..consts import LOCAL_TZ


mates = Blueprint("/mates", __name__)


def match_to_html(match: MatchInfo) -> p.div:
    timing = "Before" if match["before"] else "After"
    time_str = datetime.fromtimestamp(match["time"], LOCAL_TZ).strftime("%c")

    return p.div(
        p.p(f"{timing} {match['class_description']}"),
        p.p(f"At {time_str}"),
    )


def mate_to_html(mate: Mate) -> p.div:
    their_profile = get_user_by_zid(mate["zid"])
    assert their_profile is not None

    matches_html = [match_to_html(match) for match in mate["matches"]]

    return p.div(
        p.h2(their_profile["display_name"]),
        matches_html,
    )


@mates.get("/")
def show_potential_mates():
    user = get_user()

    if user is None:
        return redirect("/auth/login")

    # TODO: Determine these from form input
    start = datetime(2025, 3, 1)
    end = datetime.now()

    mates = find_mates(user, start, end)

    mates_html = [mate_to_html(mate) for mate in mates]

    return str(
        p.html(
            p.head(
                p.title("Calendar view"),
            ),
            p.body(
                p.h1("Your mate recommendations"),
                mates_html,
            ),
        )
    )
