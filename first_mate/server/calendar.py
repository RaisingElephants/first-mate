"""
server/calendar.py

Server code for calendar work
"""

from datetime import datetime
import pyhtml as p
from flask import Blueprint, redirect

from first_mate.logic.class_analysis import ClassEvent
from first_mate.logic.ical_analysis import find_class_events
from first_mate.server.session import get_user

from ..consts import LOCAL_TZ


calendar = Blueprint("/calendar", __name__)


def event_to_html(ev: ClassEvent) -> p.div:
    start_dt = datetime.fromtimestamp(ev["start"], LOCAL_TZ)
    end_dt = datetime.fromtimestamp(ev["end"], LOCAL_TZ)

    start_str = start_dt.strftime("%c")
    end_str = end_dt.strftime("%X")

    return p.div(
        p.h2(f"{ev['course_code']} {ev['class_type']}"),
        p.p(f"{start_str} - {end_str}"),
        p.p(ev["location"]),
    )


@calendar.get("/")
def show_calendar():
    user = get_user()

    if user is None:
        return redirect("/auth/login")

    # TODO: Determine these from form input
    start = datetime(2025, 3, 1)
    end = datetime.now()
    calendar = open("calendars/ben.ics").read()
    calendar_events = find_class_events(calendar, start, end)

    events_html = [event_to_html(event) for event in calendar_events]

    return str(
        p.html(
            p.head(
                p.title("Calendar view"),
            ),
            p.body(
                p.h1("Your calendar"),
                events_html,
            ),
        )
    )
