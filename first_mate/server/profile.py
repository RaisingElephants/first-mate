"""
server/profile.py

Server code for showing user profiles.
"""

from datetime import datetime
import pyhtml as p
from flask import Blueprint, redirect, request

from first_mate.logic.class_analysis import ClassEvent
from first_mate.logic.data import save_data
from first_mate.logic.event_overlap import MatchInfo, get_matching_times
from first_mate.logic.ical_analysis import (
    download_ical,
    find_class_events,
    get_week_range,
)
from first_mate.logic.user import get_user_by_zid
from first_mate.server.session import get_user, is_user_logged_in
from first_mate.server.util import (
    error_page,
    navbar,
    profile_banner_html,
    profile_image,
    week_offset_to_str,
)

from ..consts import LOCAL_TZ


profile = Blueprint("/profile", __name__)


@profile.get("/")
def profile_root():
    user = get_user()
    if user is None:
        return redirect("/auth/login")
    return redirect(f"/profile/{user['zid']}")


def calendar_event_to_html(ev: ClassEvent) -> p.div:
    start_dt = datetime.fromtimestamp(ev["start"], LOCAL_TZ)
    end_dt = datetime.fromtimestamp(ev["end"], LOCAL_TZ)

    start_str = start_dt.strftime("%c")
    end_str = end_dt.strftime("%X")

    return p.div(_class="calendar-event")(
        p.h2(f"{ev['course_code']} {ev['class_type']}"),
        p.p(f"{start_str} - {end_str}"),
        p.p(ev["location"]),
    )


def match_to_html(match: MatchInfo) -> p.div:
    timing = "Before" if match["before"] else "After"
    time_str = datetime.fromtimestamp(match["time"], LOCAL_TZ).strftime("%c")

    return p.div(
        p.p(
            f"{timing} {match['class_description']}",
            p.br(),
            f"On {time_str}",
        )
    )


def schedule_matches_html(matches: list[MatchInfo]) -> p.div:
    """Make HTML to show schedule matches"""
    matches_html = [match_to_html(match) for match in matches]
    return p.div(matches_html)


@profile.get("/<zid>")
def profile_page(zid: str):
    them = get_user_by_zid(zid)
    if them is None:
        return str(
            error_page(
                "Profile - Error 404",
                "Error 404",
                "User not found",
                is_user_logged_in(),
            )
        ), 404

    me = get_user()
    if me is None:
        # Don't allow unauthorized users to view profile pages
        return redirect("/auth/login")

    # NOTE: Week offset is duplicated with /calendar, perhaps use helper
    # function?
    week_offset = int(request.args.get("offset", "0"))
    start, end = get_week_range(week_offset)
    week_str = f"{week_offset_to_str(week_offset)}, {start.strftime('%x')} - {end.strftime('%x')}"

    # We are that user
    its_me = zid == me["zid"]

    # Whether we have matched
    liked_you = me["zid"] in them["likes"]
    you_liked = zid in me["likes"]

    # Give edit option if it's us
    if its_me:
        edit_option = [p.a(href=f"/profile/{zid}/edit")("Edit profile")]
        calendar_events = find_class_events(me["calendar"], start, end)
        calendar_html = [
            p.h2("Your calendar"),
            p.p("Your calendar is not shown to other users"),
            *(
                [calendar_event_to_html(event) for event in calendar_events]
                if len(calendar_events)
                else [p.i("Your don't have any events this week.")]
            ),
        ]
    else:
        edit_option = []

        schedule_matches = get_matching_times(me, them, start, end)
        calendar_html = [
            p.h2("Your shared events"),
            (
                schedule_matches_html(schedule_matches)
                if len(schedule_matches)
                else p.i("Your schedules don't overlap this week.")
            ),
        ]

    banner_html = profile_banner_html(
        zid,
        its_you=its_me,
        liked_you=liked_you,
        you_liked=you_liked,
    )

    prev_week = p.a(href=f"?offset={week_offset - 1}")("Previous week")
    next_week = p.a(href=f"?offset={week_offset + 1}")("Next week")

    return str(
        p.html(
            p.head(
                p.title(f"Profile - {them['display_name']}"),
                p.link(href="/static/root.css", rel="stylesheet"),
                p.link(href="/static/profile.css", rel="stylesheet"),
            ),
            p.body(
                navbar(True),
                banner_html,
                edit_option,
                p.div(
                    prev_week,
                    week_str,
                    next_week,
                ),
                calendar_html,
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
                p.link(href="/static/profile.css", rel="stylesheet"),
            ),
            p.body(
                navbar(True),
                p.h1("Edit profile"),
                profile_image(zid, user["display_name"]),
                p.i("You can edit your profile picture using Gravatar"),
                p.form(
                    # Main profile edit
                    # Submit
                    p.div(_class="profile-edit-actions")(
                        p.input(type="submit", value="Save", name="save"),
                        p.input(type="submit", value="Cancel"),
                    ),
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
                ),
                p.form(action=f"/profile/{zid}/edit/calendar")(
                    p.label(for_="calendar-url")(p.p("Calendar URL")),
                    p.input(
                        type="url",
                        id="calendar-url",
                        name="calendar_url",
                        placeholder="webcal://example.com/calendar.ics",
                        required=True,
                    ),
                    p.input(type="submit", value="Update calendar"),
                ),
            ),
        )
    )


@profile.post("/<zid>/edit")
def profile_edit_submit(zid: str):
    # If save option not specified, discard changes
    if "save" not in request.form:
        return redirect(f"/profile/{zid}")

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


@profile.post("/<zid>/edit/calendar")
def profile_edit_calendar_submit(zid: str):
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

    calendar_url = request.form["calendar_url"]

    user["calendar"] = download_ical(calendar_url)
    save_data()

    return redirect(f"/profile/{zid}")
