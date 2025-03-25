"""
server/calendar.py

Server code for calendar work
"""

from datetime import datetime
import pyhtml as p
from flask import Blueprint, redirect, request

from first_mate.logic.class_analysis import ClassEvent
from first_mate.logic.ical_analysis import find_class_events, get_week_range
from first_mate.server.session import get_user
from first_mate.server.util import navbar, week_offset_to_str

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

    week_offset = int(request.args.get("offset", "0"))
    start, end = get_week_range(week_offset)
    week_str = f"{week_offset_to_str(week_offset)}, {start.strftime('%x')} - {end.strftime('%x')}"
    calendar_events = find_class_events(user["calendar"], start, end)

    events_html = (
        [event_to_html(event) for event in calendar_events]
        if len(calendar_events)
        else [p.p(p.i("No events this week"))]
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
                p.h1("Your calendar"),
                p.div(
                    prev_week,
                    week_str,
                    next_week,
                ),
                events_html,
            ),
        )
    )
